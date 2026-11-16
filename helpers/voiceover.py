"""Separate voice recordings over footage (studio addition).

A video folder may carry a `voice/` subfolder with recordings (mp3, m4a, wav)
next to the raw clips, and `edit/brief.json` saying how they relate:

    {"mode": "voiceover" | "commentary" | "clips",
     "footage": ["phone.mp4"], "voice": ["voice/take1.mp3"],
     "voice_offset_s": 0.0, "notes": "..."}

- voiceover:  the voice is the timeline. The editor cuts the voice transcript
              (EDL ranges over the voice source); the planner says which clip
              plays under each stretch (`footage` in scenes.json); `build`
              renders `edit/voice_master.mp4` (footage + cut voice) and
              `edit/edl_master.json` (one range over the master, same overlays
              and subtitles), which render.py then composites as usual.
- commentary: the clip is the timeline and keeps its own sound; the voice is
              added by sound_mix.py (`voice` entry in sound.json) and ducks
              the clip under it. Nothing to build here.
- clips:      no voice files; the normal pipeline.

Usage:
    python helpers/voiceover.py transcribe videos/<folder>   # voice/*.mp3 -> edit/transcripts/<stem>.json
    python helpers/voiceover.py build videos/<folder>        # edl.json + scenes.json -> voice_master.mp4 + edl_master.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parent.parent
BRAND_STYLE = REPO / "brand" / "style.json"
AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".aac", ".aiff", ".aif", ".flac", ".ogg"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
MODES = ("voiceover", "commentary", "clips")
GAP_KIND, FOOTAGE_KIND = "background", "footage"
MIN_SEGMENT_S = 0.04  # one frame at 25 fps; shorter plan entries are dropped


# -------- brief / files -----------------------------------------------------


def load_brief(folder: Path) -> dict:
    p = folder / "edit" / "brief.json"
    if not p.exists():
        return {"mode": "clips", "footage": [], "voice": [], "voice_offset_s": 0.0}
    brief = json.loads(p.read_text())
    if brief.get("mode") not in MODES:
        raise ValueError(f"brief.json mode must be one of {MODES}, got {brief.get('mode')!r}")
    return brief


def voice_files(folder: Path) -> list[Path]:
    vdir = folder / "voice"
    if not vdir.is_dir():
        return []
    return sorted(p for p in vdir.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTS)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {res.stderr.strip()[-600:]}")
    return res


def media_duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout
    return float(out.strip() or 0.0)


# -------- pure planning -----------------------------------------------------


def edl_total(ranges: list[dict]) -> float:
    return round(sum(float(r["end"]) - float(r["start"]) for r in ranges), 3)


def audio_cut_filter(ranges: list[dict], source_index: dict[str, int]) -> str:
    """ffmpeg filter_complex that trims every EDL range from its voice input and
    concatenates them in order -> [voice]. `source_index` maps EDL source name to
    the ffmpeg input index."""
    parts, labels = [], []
    for k, r in enumerate(ranges):
        idx = source_index[r["source"]]
        parts.append(f"[{idx}:a]atrim=start={float(r['start']):.3f}:end={float(r['end']):.3f},asetpts=PTS-STARTPTS[a{k}]")
        labels.append(f"[a{k}]")
    parts.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[voice]")
    return ";".join(parts)


def plan_video_track(stretches: list[dict], total: float) -> list[dict]:
    """Turn planner stretches (output-timeline seconds, optional `footage`
    {file, in_s, fit}) into a gapless list of segments covering [0, total]:
    footage segments where a stretch names a clip, background segments elsewhere.
    Overlaps are resolved by the earlier stretch; everything is clamped to total."""
    plan: list[dict] = []
    cursor = 0.0
    for s in sorted(stretches, key=lambda s: float(s["start"])):
        start = max(cursor, float(s["start"]))
        end = min(total, float(s["end"]))
        if end - start < MIN_SEGMENT_S:
            continue
        if start - cursor >= MIN_SEGMENT_S:
            plan.append({"kind": GAP_KIND, "start": round(cursor, 3), "end": round(start, 3)})
        foot = s.get("footage") or {}
        if foot.get("file"):
            skip = start - float(s["start"])  # if an overlap trimmed the head, advance the in-point too
            plan.append({"kind": FOOTAGE_KIND, "start": round(start, 3), "end": round(end, 3),
                         "file": foot["file"], "in_s": round(float(foot.get("in_s", 0.0)) + skip, 3),
                         "fit": foot.get("fit", "contain"), "stretch": s.get("id")})
        else:
            plan.append({"kind": GAP_KIND, "start": round(start, 3), "end": round(end, 3), "stretch": s.get("id")})
        cursor = end
    if total - cursor >= MIN_SEGMENT_S:
        plan.append({"kind": GAP_KIND, "start": round(cursor, 3), "end": round(total, 3)})
    return plan


def video_filter(width: int, height: int, fps: int, bg_hex: str, fit: str, dur: float) -> str:
    colour = "0x" + bg_hex.lstrip("#")
    if fit == "cover":
        fitting = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    else:
        fitting = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                   f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:{colour}")
    # tpad clones the last frame if the clip is shorter than the stretch, so concat timing never drifts
    return f"{fitting},fps={fps},setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration={dur:.3f}"


def segment_command(seg: dict, folder: Path, width: int, height: int, fps: int, bg_hex: str, out: Path) -> list[str]:
    dur = float(seg["end"]) - float(seg["start"])
    enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-an", "-t", f"{dur:.3f}", str(out)]
    if seg["kind"] == GAP_KIND:
        colour = "0x" + bg_hex.lstrip("#")
        return ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                f"color=c={colour}:s={width}x{height}:r={fps}:d={dur:.3f}", *enc]
    src = (folder / seg["file"]).resolve() if not Path(seg["file"]).is_absolute() else Path(seg["file"])
    if not src.exists():
        raise FileNotFoundError(f"footage not found: {src}")
    vf = video_filter(width, height, fps, bg_hex, seg.get("fit", "contain"), dur)
    if src.suffix.lower() in IMAGE_EXTS:
        return ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", f"{dur:.3f}", "-i", str(src), "-vf", vf, *enc]
    return ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{float(seg['in_s']):.3f}", "-i", str(src), "-vf", vf, *enc]


def edl_master_from(edl: dict, master: Path, total: float) -> dict:
    """The EDL render.py composites: one range over the voice master, same
    overlays/grade/subtitles. Captions still come from the original edl.json."""
    return {
        "version": edl.get("version", 1),
        "profile": edl.get("profile", "vertical"),
        "sources": {"voice_master": str(master)},
        "ranges": [{"source": "voice_master", "start": 0.0, "end": total, "beat": "ALL",
                    "quote": "", "reason": "voice master built by voiceover.py from edl.json + scenes.json"}],
        "grade": edl.get("grade", "none"),
        "overlays": edl.get("overlays", []),
        "subtitles": edl.get("subtitles", "master.ass"),
        "total_duration_s": total,
        "_from": "edl.json",
    }


# -------- commands ----------------------------------------------------------


def cmd_transcribe(folder: Path) -> list[Path]:
    from transcribe import transcribe_one  # local Parakeet, same shape as the clip transcripts

    files = voice_files(folder)
    if not files:
        print(f"no voice files in {folder / 'voice'}")
        return []
    edit = folder / "edit"
    out = []
    for f in files:
        print(f"voice: {f.name}")
        out.append(transcribe_one(f, edit))
    return out


def cmd_build(folder: Path, style_path: Path = BRAND_STYLE) -> tuple[Path, Path]:
    edit = folder / "edit"
    brief = load_brief(folder)
    if brief["mode"] != "voiceover":
        sys.exit(f"brief.json mode is {brief['mode']!r}; build is only for voiceover mode")
    edl = json.loads((edit / "edl.json").read_text())
    scenes = json.loads((edit / "scenes.json").read_text()) if (edit / "scenes.json").exists() else {"stretches": []}
    style = json.loads(style_path.read_text())
    profile = edl.get("profile", "vertical")
    prof = style.get("profiles", {}).get(profile, {})
    width, height, fps = int(prof.get("width", 1080)), int(prof.get("height", 1920)), int(prof.get("fps", 30))
    bg_hex = style.get("colors", {}).get("background", "#0B0B0F")

    ranges = edl["ranges"]
    total = edl_total(ranges)
    plan = plan_video_track(scenes.get("stretches", []), total)
    n_foot = sum(1 for p in plan if p["kind"] == FOOTAGE_KIND)
    if n_foot == 0:
        print("WARNING: no stretch names footage; the master will be brand background under the voice")

    sources = {name: Path(path) for name, path in edl["sources"].items()}
    used = []
    for r in ranges:
        if r["source"] not in used:
            used.append(r["source"])
    for name in used:
        if not sources[name].exists():
            sys.exit(f"voice source not found: {sources[name]}")
    master = edit / "voice_master.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        # 1. cut voice
        voice_wav = tmpd / "voice_cut.wav"
        inputs = []
        for name in used:
            inputs += ["-i", str(sources[name])]
        run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
             audio_cut_filter(ranges, {n: i for i, n in enumerate(used)}),
             "-map", "[voice]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(voice_wav)])
        # 2. video track, one segment per plan entry, then lossless concat
        seg_paths = []
        for i, seg in enumerate(plan):
            out = tmpd / f"seg_{i:03d}.mp4"
            run(segment_command(seg, folder, width, height, fps, bg_hex, out))
            seg_paths.append(out)
            print(f"  {seg['kind']:<10} {seg['start']:>7.2f}-{seg['end']:<7.2f} {seg.get('file', '')}")
        concat_list = tmpd / "concat.txt"
        concat_list.write_text("".join(f"file '{p}'\n" for p in seg_paths))
        video_track = tmpd / "video.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(video_track)])
        # 3. mux
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_track), "-i", str(voice_wav),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
             "-movflags", "+faststart", str(master)])

    edl_master = edit / "edl_master.json"
    edl_master.write_text(json.dumps(edl_master_from(edl, master, total), indent=2) + "\n")
    got = media_duration(master)
    print(f"voice master -> {master.name} ({got:.2f}s, planned {total:.2f}s, {n_foot} footage segment(s)); EDL -> {edl_master.name}")
    if abs(got - total) > 0.1:
        print(f"WARNING: master is {got - total:+.2f}s off the EDL total")
    return master, edl_master


def main() -> None:
    ap = argparse.ArgumentParser(description="Voice recordings over footage: transcribe voice/*, build the voice master")
    ap.add_argument("command", choices=["transcribe", "build"])
    ap.add_argument("folder", type=Path, help="videos/<folder>")
    ap.add_argument("--style", type=Path, default=BRAND_STYLE)
    args = ap.parse_args()
    folder = args.folder.resolve()
    if not folder.is_dir():
        sys.exit(f"not a folder: {folder}")
    if args.command == "transcribe":
        cmd_transcribe(folder)
    else:
        cmd_build(folder, args.style)


if __name__ == "__main__":
    main()
