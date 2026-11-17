"""Mix speech + music + sound effects for a rendered video, measured not guessed.

Reads <edit>/sound.json (written by the sound agent):

    {"video": "preview.mp4", "output": "mix.wav",
     "music": {"file": "brand/music/x.mp3", "gain_db": -12, "fade_in_s": 1, "fade_out_s": 2},
     "effects": [{"effect": "pop", "file": "brand/sfx/pop.wav", "contact_s": 5.1,
                  "event": "90% lands", "gain_db": -6}],
     "voice": {"file": "../voice/take1.mp3", "offset_s": 0.0, "gain_db": 0},   # commentary mode only
     "speech": {"highpass_hz": 70, "gain_db": 20, "compress": true},          # optional: condition a quiet mic first
     "sections": [{"name": "hook", "start": 0.0, "end": 4.2}]}

Steps: extract the speech track from the video; measure each effect's attack
(time to reach half its peak) and start it that much before `contact_s`;
duck music under speech with a sidechain compressor; sum; two-pass loudnorm
to -14 LUFS / -1 dBTP; write the mix and a report with measured levels per
section. `--mux <out.mp4>` writes the video with the new audio (video copied).

Usage:
    python helpers/sound_mix.py --edit-dir <edit> [--mux <out.mp4>]
"""

from __future__ import annotations

import argparse
import array
import json
import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET_I, TARGET_TP, TARGET_LRA = -14.0, -1.5, 11.0  # TP has 0.5 dB headroom: the AAC mux overshoots the wav by ~0.1 dB
DUCK = "threshold=0.03:ratio=8:attack=25:release=350:makeup=1"
SAMPLE_RATE = 48000


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def resolve(path_str: str, edit_dir: Path) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    for base in (edit_dir, REPO, Path.cwd()):
        if (base / p).exists():
            return (base / p).resolve()
    return (edit_dir / p).resolve()


# -------- measurement ------------------------------------------------------


def attack_seconds(samples: list[int] | array.array, sample_rate: int, fraction: float = 0.5) -> float:
    """Seconds from the start of a mono signal until it first reaches `fraction` of its peak."""
    peak = max((abs(s) for s in samples), default=0)
    if peak == 0:
        return 0.0
    threshold = peak * fraction
    for i, s in enumerate(samples):
        if abs(s) >= threshold:
            return i / sample_rate
    return 0.0


def measure_attack(audio_path: Path) -> float:
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio_path), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
        with wave.open(str(wav), "rb") as w:
            frames = w.readframes(w.getnframes())
            rate = w.getframerate()
        return attack_seconds(array.array("h", frames), rate)


def measure_ebur128(audio_path: Path, start: float | None = None, end: float | None = None) -> dict:
    af = []
    if start is not None and end is not None:
        af.append(f"atrim=start={start}:end={end},asetpts=PTS-STARTPTS")
    af.append("ebur128=peak=true:framelog=quiet")
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio_path), "-af", ",".join(af), "-f", "null", "-"],
                          capture_output=True, text=True)
    out = {}
    tail = proc.stderr[proc.stderr.rfind("Summary:"):] if "Summary:" in proc.stderr else ""
    for line in tail.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            out["integrated_lufs"] = float(line.split()[1])
        elif line.startswith("LRA:"):
            out["lra_lu"] = float(line.split()[1])
        elif line.startswith("Peak:"):
            out["true_peak_dbtp"] = float(line.split()[1])
    return out


def loudnorm_measure(audio_path: Path) -> dict | None:
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio_path), "-af",
                           f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True)
    s, e = proc.stderr.rfind("{"), proc.stderr.rfind("}")
    if s == -1 or e <= s:
        return None
    try:
        return json.loads(proc.stderr[s:e + 1])
    except json.JSONDecodeError:
        return None


# -------- graph ------------------------------------------------------------


def plan_effects(effects: list[dict], edit_dir: Path) -> tuple[list[dict], list[str]]:
    planned, skipped = [], []
    for fx in effects:
        path = resolve(fx["file"], edit_dir)
        if not path.exists():
            skipped.append(f"{fx.get('effect', '?')}: missing file {fx['file']}")
            continue
        attack = measure_attack(path)
        start = max(0.0, float(fx["contact_s"]) - attack)
        planned.append({**fx, "path": str(path), "attack_s": round(attack, 4), "start_s": round(start, 4)})
    return planned, skipped


def speech_filter(speech: dict) -> str:
    """Condition a quiet or boomy speech track before the mix (sound.json `speech`):
    {"highpass_hz": 70, "gain_db": 20, "compress": true, "limit": true}. Decided by
    the sound agent from the measured raw level; a laptop mic at -37 LUFS needs it."""
    parts = []
    if speech.get("highpass_hz"):
        parts.append(f"highpass=f={int(speech['highpass_hz'])}")
    if speech.get("compress", False):
        parts.append("acompressor=threshold=-24dB:ratio=3:attack=10:release=150:makeup=1")
    if speech.get("gain_db"):
        parts.append(f"volume={float(speech['gain_db'])}dB")
    if speech.get("limit", True):
        parts.append("alimiter=limit=0.891:attack=5:release=50")  # -1 dBTP ceiling
    return ",".join(parts) or "anull"


def build_filter(speech_dur: float, music: dict | None, effects: list[dict],
                 voice: dict | None = None) -> tuple[list[str], str]:
    """Return (ffmpeg inputs after the speech input, filter_complex).

    `voice` (commentary mode, from brief.json): {path, offset_s, gain_db}. The
    recording starts `offset_s` into the video and the video's own sound is
    ducked under it with the same sidechain the music uses."""
    inputs: list[str] = []
    parts: list[str] = []
    mix_labels = ["[sp]"]
    parts.append("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[sp0][key]")
    idx = 1
    if voice:
        inputs += ["-i", voice["path"]]
        delay_ms = int(round(float(voice.get("offset_s", 0.0)) * 1000))
        gain = float(voice.get("gain_db", 0.0))
        parts.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB,"
                     f"adelay={delay_ms}|{delay_ms},asplit=2[vo][vkey]")
        parts.append(f"[sp0][vkey]sidechaincompress={DUCK}[sp]")
        mix_labels.append("[vo]")
        idx += 1
    else:
        parts.append("[sp0]anull[sp]")
    if music:
        inputs += ["-stream_loop", "-1", "-i", music["path"]]
        fi, fo = float(music.get("fade_in_s", 1.0)), float(music.get("fade_out_s", 2.0))
        gain = float(music.get("gain_db", -12))
        parts.append(
            f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{speech_dur:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={fi},afade=t=out:st={max(0.0, speech_dur - fo):.3f}:d={fo},volume={gain}dB[mu]"
        )
        parts.append(f"[mu][key]sidechaincompress={DUCK}[md]")
        mix_labels.append("[md]")
        idx += 1
    else:
        parts.append("[key]anullsink")
    for fx in effects:
        inputs += ["-i", fx["path"]]
        delay_ms = int(round(fx["start_s"] * 1000))
        gain = float(fx.get("gain_db", -6))
        parts.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB,adelay={delay_ms}|{delay_ms}[fx{idx}]")
        mix_labels.append(f"[fx{idx}]")
        idx += 1
    parts.append(f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=first:normalize=0[mix]")
    return inputs, ";".join(parts)


# -------- main -------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Mix speech, music and effects; two-pass loudnorm; report levels")
    ap.add_argument("--edit-dir", type=Path, required=True)
    ap.add_argument("--sound", type=Path, default=None, help="default: <edit>/sound.json")
    ap.add_argument("--mux", type=Path, default=None, help="write the video with the mixed audio here")
    args = ap.parse_args()

    edit_dir = args.edit_dir.resolve()
    spec_path = (args.sound or edit_dir / "sound.json").resolve()
    if not spec_path.exists():
        sys.exit(f"sound spec not found: {spec_path}")
    spec = json.loads(spec_path.read_text())

    video = resolve(spec["video"], edit_dir)
    if not video.exists():
        sys.exit(f"video not found: {video}")
    out_wav = resolve(spec.get("output", "mix.wav"), edit_dir)

    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]).stdout.strip())

    music = None
    if spec.get("music") and spec["music"].get("file"):
        mpath = resolve(spec["music"]["file"], edit_dir)
        if mpath.exists():
            music = {**spec["music"], "path": str(mpath)}
        else:
            print(f"  music file missing, mixing without music: {spec['music']['file']}")

    effects, skipped = plan_effects(spec.get("effects", []), edit_dir)
    for s in skipped:
        print(f"  skipped effect: {s}")

    voice = None
    if spec.get("voice") and spec["voice"].get("file"):
        vpath = resolve(spec["voice"]["file"], edit_dir)
        if vpath.exists():
            voice = {**spec["voice"], "path": str(vpath)}
        else:
            print(f"  voice file missing, mixing without it: {spec['voice']['file']}")

    with tempfile.TemporaryDirectory() as tmp:
        speech = Path(tmp) / "speech.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "2", "-ar", str(SAMPLE_RATE),
             *(["-af", speech_filter(spec["speech"])] if spec.get("speech") else []), "-c:a", "pcm_s16le", str(speech)])
        inputs, graph = build_filter(dur, music, effects, voice)
        premix = Path(tmp) / "premix.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(speech), *inputs, "-filter_complex", graph,
             "-map", "[mix]", "-ar", str(SAMPLE_RATE), "-c:a", "pcm_s24le", str(premix)])

        m = loudnorm_measure(premix)
        if m is None:
            sys.exit("loudnorm measurement failed")
        ln = (f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(premix), "-af", ln, "-ar", str(SAMPLE_RATE), "-c:a", "pcm_s24le", str(out_wav)])

        report = {
            "video": str(video), "output": str(out_wav), "duration_s": round(dur, 3),
            "speech_track": measure_ebur128(speech),
            "music": None if music is None else {"file": music["path"], "gain_db": music.get("gain_db", -12)},
            "voice": None if voice is None else {"file": voice["path"], "offset_s": float(voice.get("offset_s", 0.0)),
                                                 "gain_db": float(voice.get("gain_db", 0.0))},
            "effects": [{k: v for k, v in fx.items() if k != "path"} | {"file": fx["path"]} for fx in effects],
            "skipped": skipped,
            "premix_measured": {"integrated_lufs": float(m["input_i"]), "true_peak_dbtp": float(m["input_tp"]), "lra_lu": float(m["input_lra"])},
            "final": measure_ebur128(out_wav),
            "sections": [],
        }
        if music is not None:
            # the music bed alone, after ducking, so the sound agent can verify it sits under speech
            bed = Path(tmp) / "bed.wav"
            bed_inputs, bed_graph = build_filter(dur, music, [])
            bed_graph = bed_graph.replace("[sp][md]amix=inputs=2:duration=first:normalize=0[mix]", "[sp]anullsink;[md]anull[mix]")
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(speech), *bed_inputs, "-filter_complex", bed_graph, "-map", "[mix]", str(bed)])
            report["music"]["bed_after_duck"] = measure_ebur128(bed)
            sp, bd = report["speech_track"].get("integrated_lufs"), report["music"]["bed_after_duck"].get("integrated_lufs")
            if sp is not None and bd is not None:
                report["music"]["bed_under_speech_db"] = round(bd - sp, 1)
        for sec in spec.get("sections", []):
            report["sections"].append({"name": sec["name"], "start": sec["start"], "end": sec["end"],
                                       **measure_ebur128(out_wav, float(sec["start"]), float(sec["end"]))})

    (edit_dir / "sound_report.json").write_text(json.dumps(report, indent=2))
    f = report["final"]
    print(f"mix -> {out_wav.name}: I={f.get('integrated_lufs')} LUFS, TP={f.get('true_peak_dbtp')} dBTP, "
          f"{len(effects)} effects, music={'yes' if music else 'no'}, voice={'yes' if voice else 'no'}")
    for fx in effects:
        print(f"  {fx['effect']:<12} contact {fx['contact_s']:>7.3f}s  attack {fx['attack_s']:.3f}s  start {fx['start_s']:>7.3f}s  <- {fx.get('event', '')}")
    for sec in report["sections"]:
        print(f"  section {sec['name']:<14} [{sec['start']:.1f}-{sec['end']:.1f}] I={sec.get('integrated_lufs')} LUFS TP={sec.get('true_peak_dbtp')}")

    if args.mux:
        mux_out = args.mux.resolve()
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(out_wav), "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(mux_out)])
        print(f"muxed -> {mux_out}")


if __name__ == "__main__":
    main()
