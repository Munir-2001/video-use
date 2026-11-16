"""Build word-synced karaoke captions (.ass) from an EDL + transcripts + brand style.

For every caption cue (2-3 words, chunked like render.py), one Dialogue event
is written per word: the word being spoken is drawn in the highlight colour
and scaled up, the rest of the cue in the base colour. Times are on the
OUTPUT timeline (SKILL.md Hard Rule 5):
    out = word.start - segment_start + segment_offset

Placement comes from brand/style.json: vertical profiles put the cue in the
lower band under the chin (STYLE.md, ≈ 68 % down), horizontal near the bottom; margins keep the right
edge clear. Fonts are named by family; libass loads them from brand/fonts/
(render.py passes fontsdir) or the system. A missing brand font file is
reported loudly and the fallback family is used.

Usage:
    python helpers/captions_ass.py <edl.json>                      # -> <edit>/master.ass
    python helpers/captions_ass.py <edl.json> -o edit/master.ass --profile vertical
    python helpers/captions_ass.py <edl.json> --width 1080 --height 1920
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRAND_STYLE = REPO / "brand" / "style.json"
PUNCT_BREAK = set(".,!?;:")
MIN_CUE_S = 0.35      # a cue shorter than this reads as a flash
PAUSE_BREAK_S = 0.3   # a gap this long between words ends the cue
MIN_WORD_EVENT_S = 0.12
ANCHOR_TO_AN = {"middle": 5, "bottom": 2, "top": 8}


# -------- style -------------------------------------------------------------


def load_style(path: Path = BRAND_STYLE) -> dict:
    if not path.exists():
        sys.exit(f"brand style not found: {path}")
    return json.loads(path.read_text())


def ass_colour(hex_rgb: str, alpha: int = 0) -> str:
    """#RRGGBB -> &HAABBGGRR (ASS byte order)."""
    h = hex_rgb.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"bad colour {hex_rgb!r}")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper().replace("&H", "&H")


def resolve_colour(style: dict, key_or_hex: str) -> str:
    colours = style.get("colors", {})
    return colours.get(key_or_hex, key_or_hex)


def font_for_captions(style: dict) -> tuple[str, list[str]]:
    """Return (family_to_use, warnings)."""
    caps = style.get("captions", {})
    fonts = style.get("fonts", {})
    spec = fonts.get(caps.get("font", "display"), {})
    family = spec.get("family", "Helvetica")
    file_rel = spec.get("file")
    warnings: list[str] = []
    if file_rel and not (REPO / file_rel).exists():
        fallback = spec.get("fallback", "Helvetica")
        warnings.append(
            f"font file missing: {file_rel} - using fallback family {fallback!r}. "
            f"Drop the .ttf into brand/fonts/ to use {family!r}."
        )
        return fallback, warnings
    return family, warnings


def layout_for(style: dict, profile: str, width: int, height: int,
               y_fraction: float | None = None) -> dict:
    """Caption anchor for a profile. `y_fraction` overrides the brand default
    (a clip framed low needs the band moved); must be strictly between 0 and 1."""
    caps = style.get("captions", {})
    pos = dict(caps.get("position", {}).get(profile, {"anchor": "middle", "y_fraction": 0.68}))
    if y_fraction is not None:
        if not 0.0 < y_fraction < 1.0:
            raise ValueError(f"y_fraction must be between 0 and 1, got {y_fraction}")
        pos["y_fraction"] = y_fraction
    safe = style.get("safe_areas", {}).get(profile, {})
    max_w = float(caps.get("max_width_fraction", 0.8))
    side = int(round(width * (1 - max_w) / 2))
    right_clear = int(safe.get("right_clear_px", 0))
    size_key = "size_px_1080x1920" if profile == "vertical" else "size_px_1080w"
    return {
        "an": ANCHOR_TO_AN.get(pos.get("anchor", "middle"), 5),
        "x": width // 2 - (right_clear // 2 if profile == "vertical" else 0),
        "y": int(round(height * float(pos.get("y_fraction", 0.68)))),
        "margin_l": side,
        "margin_r": max(side, right_clear),
        "font_size": int(caps.get(size_key, 64)),
    }


# -------- timeline ----------------------------------------------------------


def words_in_range(transcript: dict, t_start: float, t_end: float) -> list[dict]:
    out = []
    for w in transcript.get("words", []):
        if w.get("type") != "word":
            continue
        ws, we = w.get("start"), w.get("end")
        if ws is None or we is None or we <= t_start or ws >= t_end:
            continue
        out.append(w)
    return out


def chunk_words(words: list[dict], target: int = 2, max_words: int = 3) -> list[list[dict]]:
    """Same rules as render.chunk_words, parametrised by the brand's words-per-cue."""
    words = [w for w in words if (w.get("text") or "").strip()]
    chunks: list[list[dict]] = []
    current: list[dict] = []
    for i, w in enumerate(words):
        current.append(w)
        text = w["text"].strip()
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 0.0
        dur = w["end"] - current[0]["start"]
        if (
            nxt is None
            or text[-1] in PUNCT_BREAK
            or gap >= PAUSE_BREAK_S
            or len(current) >= max_words
            or (len(current) >= target and dur >= MIN_CUE_S)
        ):
            chunks.append(current)
            current = []
    return chunks


def output_cues(edl: dict, transcripts_dir: Path, target: int, max_words: int) -> list[dict]:
    """Cues on the output timeline: [{start, end, words: [{text, start, end}]}]."""
    cues: list[dict] = []
    seg_offset = 0.0
    for r in edl["ranges"]:
        seg_start, seg_end = float(r["start"]), float(r["end"])
        seg_dur = seg_end - seg_start
        tr_path = transcripts_dir / f"{r['source']}.json"
        if not tr_path.exists():
            print(f"  no transcript for {r['source']}, no captions for this segment")
            seg_offset += seg_dur
            continue
        transcript = json.loads(tr_path.read_text())
        for chunk in chunk_words(words_in_range(transcript, seg_start, seg_end), target, max_words):
            ws = []
            for w in chunk:
                a = max(0.0, max(seg_start, w["start"]) - seg_start) + seg_offset
                b = max(0.0, min(seg_end, w["end"]) - seg_start) + seg_offset
                ws.append({"text": re.sub(r"\s+", " ", w["text"]).strip(), "start": a, "end": max(b, a + 0.05)})
            cue_start, cue_end = ws[0]["start"], ws[-1]["end"]
            if cue_end - cue_start < MIN_CUE_S:
                cue_end = cue_start + MIN_CUE_S
            cues.append({"start": cue_start, "end": cue_end, "words": ws})
        seg_offset += seg_dur
    cues.sort(key=lambda c: c["start"])
    # a cue may not run into the next one
    for i in range(len(cues) - 1):
        cues[i]["end"] = min(cues[i]["end"], cues[i + 1]["start"])
    return cues


# -------- ASS writer --------------------------------------------------------


def ass_time(seconds: float) -> str:
    cs = int(round(max(0.0, seconds) * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, c = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def escape_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def word_events(cue: dict, layout: dict, highlight: str, base: str, scale: int) -> list[tuple[float, float, str]]:
    """One event per word: that word highlighted + scaled, the others base."""
    events = []
    words = cue["words"]
    for k, w in enumerate(words):
        start = w["start"] if k > 0 else cue["start"]
        end = words[k + 1]["start"] if k + 1 < len(words) else cue["end"]
        if end - start < MIN_WORD_EVENT_S and k + 1 < len(words):
            end = min(start + MIN_WORD_EVENT_S, cue["end"])
        parts = []
        for j, other in enumerate(words):
            t = escape_text(other["text"])
            if j == k:
                parts.append(f"{{\\c{highlight}\\fscx{scale}\\fscy{scale}}}{t}{{\\r}}")
            else:
                parts.append(t)
        text = f"{{\\an{layout['an']}\\pos({layout['x']},{layout['y']})}}" + " ".join(parts)
        events.append((start, end, text))
    return events


def build_ass(cues: list[dict], style: dict, profile: str, width: int, height: int,
              y_fraction: float | None = None) -> tuple[str, list[str]]:
    caps = style.get("captions", {})
    hl = caps.get("highlight", {})
    layout = layout_for(style, profile, width, height, y_fraction)
    family, warnings = font_for_captions(style)
    base_hex = resolve_colour(style, hl.get("base_color", "caption_base"))
    hl_hex = resolve_colour(style, hl.get("color", "caption_highlight"))
    outline_hex = resolve_colour(style, "caption_outline")
    scale = int(round(float(hl.get("scale", 1.12)) * 100))
    bold = -1 if style.get("fonts", {}).get(caps.get("font", "display"), {}).get("weight", 700) >= 600 else 0

    header = [
        "[Script Info]",
        "; Word-synced captions built by helpers/captions_ass.py (video studio)",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,{family},{layout['font_size']},{ass_colour(base_hex)},{ass_colour(hl_hex)},"
        f"{ass_colour(outline_hex)},{ass_colour(outline_hex, 0x80)},{bold},0,0,0,100,100,0,0,1,"
        f"{int(caps.get('outline_px', 4))},{int(caps.get('shadow_px', 2))},{layout['an']},"
        f"{layout['margin_l']},{layout['margin_r']},0,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    lines = list(header)
    for cue in cues:
        for start, end, text in word_events(cue, layout, ass_colour(hl_hex), ass_colour(base_hex), scale):
            lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,{text}")
    return "\n".join(lines) + "\n", warnings


# -------- main --------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Build word-synced .ass captions from an EDL")
    ap.add_argument("edl", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None, help="default: <edit>/master.ass")
    ap.add_argument("--style", type=Path, default=BRAND_STYLE)
    ap.add_argument("--profile", choices=["vertical", "horizontal"], default=None,
                    help="default: edl['profile'] if present, else vertical")
    ap.add_argument("--width", type=int, default=None)
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--y-fraction", type=float, default=None,
                    help="override the caption band centre (0-1 of frame height); default from brand/style.json")
    args = ap.parse_args()

    edl_path = args.edl.resolve()
    if not edl_path.exists():
        sys.exit(f"edl not found: {edl_path}")
    edl = json.loads(edl_path.read_text())
    edit_dir = edl_path.parent
    style = load_style(args.style)

    profile = args.profile or edl.get("profile") or "vertical"
    prof = style.get("profiles", {}).get(profile, {})
    width = args.width or int(prof.get("width", 1080 if profile == "vertical" else 1920))
    height = args.height or int(prof.get("height", 1920 if profile == "vertical" else 1080))

    wpc = style.get("captions", {}).get("words_per_cue", {})
    cues = output_cues(edl, edit_dir / "transcripts", int(wpc.get("target", 2)), int(wpc.get("max", 3)))
    text, warnings = build_ass(cues, style, profile, width, height, args.y_fraction)

    out = (args.output or (edit_dir / "master.ass")).resolve()
    out.write_text(text, encoding="utf-8")
    n_words = sum(len(c["words"]) for c in cues)
    for w in warnings:
        print(f"WARNING: {w}")
    print(f"master ASS -> {out} ({len(cues)} cues, {n_words} word events, {profile} {width}x{height})")


if __name__ == "__main__":
    main()
