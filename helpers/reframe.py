"""Reframe a clip to another aspect ratio by cropping (never stretching).

A laptop webcam records 16:9; a reel is 9:16. This cuts the tallest 9:16 column
out of the frame at the x position the agent chooses (where the face is), then
scales it to the profile size. Audio is copied untouched. Works the other way
too (vertical -> horizontal, cropping top/bottom).

Usage:
    python helpers/reframe.py videos/<folder>/laptop.mov --to vertical            # centred column
    python helpers/reframe.py videos/<folder>/laptop.mov --to vertical --x 0.40   # column centred at 40 % of the width
    python helpers/reframe.py clip.mov --to horizontal --y 0.35                   # band centred at 35 % of the height

Writes <stem>_vertical.mp4 (or _horizontal) next to the source and prints the
crop and the upscale factor; above 1.5x the agent should say the clip will look soft.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRAND_STYLE = REPO / "brand" / "style.json"
PROFILES = {"vertical": (1080, 1920), "horizontal": (1920, 1080)}


def probe(path: Path) -> tuple[int, int]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def crop_box(src_w: int, src_h: int, target_w: int, target_h: int, x_frac: float = 0.5, y_frac: float = 0.5) -> dict:
    """Largest box with the target aspect inside the source, centred at
    (x_frac, y_frac) and clamped to the frame. Returns crop + upscale factor."""
    if not (0.0 <= x_frac <= 1.0 and 0.0 <= y_frac <= 1.0):
        raise ValueError("x and y must be fractions between 0 and 1")
    target_aspect = target_w / target_h
    if src_w / src_h > target_aspect:      # source wider than target: full height, crop sides
        h = src_h
        w = int(round(h * target_aspect))
    else:                                   # source taller: full width, crop top/bottom
        w = src_w
        h = int(round(w / target_aspect))
    w, h = w - w % 2, h - h % 2
    x = int(round(x_frac * src_w - w / 2))
    y = int(round(y_frac * src_h - h / 2))
    x = max(0, min(x, src_w - w))
    y = max(0, min(y, src_h - h))
    return {"x": x, "y": y, "w": w, "h": h, "upscale": round(target_w / w, 2)}


def ffmpeg_command(src: Path, dest: Path, box: dict, target_w: int, target_h: int, fps: int | None = None) -> list[str]:
    vf = f"crop={box['w']}:{box['h']}:{box['x']}:{box['y']},scale={target_w}:{target_h}:flags=lanczos,setsar=1"
    if fps:
        vf += f",fps={fps}"
    return ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(dest)]


def main() -> None:
    ap = argparse.ArgumentParser(description="Crop a clip to another aspect ratio (no stretching)")
    ap.add_argument("clip", type=Path)
    ap.add_argument("--to", choices=list(PROFILES), required=True)
    ap.add_argument("--x", type=float, default=0.5, help="horizontal centre of the crop as a fraction of the width (where the face is)")
    ap.add_argument("--y", type=float, default=0.5, help="vertical centre of the crop as a fraction of the height")
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--style", type=Path, default=BRAND_STYLE)
    ap.add_argument("--fps", type=int, default=None, help="constant frame rate for the output (default: the profile's fps; phone/laptop clips are often variable-rate)")
    args = ap.parse_args()

    src = args.clip.resolve()
    if not src.exists():
        sys.exit(f"clip not found: {src}")
    prof = json.loads(args.style.read_text()).get("profiles", {}).get(args.to, {}) if args.style.exists() else {}
    target_w, target_h = int(prof.get("width", PROFILES[args.to][0])), int(prof.get("height", PROFILES[args.to][1]))
    src_w, src_h = probe(src)
    box = crop_box(src_w, src_h, target_w, target_h, args.x, args.y)
    dest = (args.output or src.with_name(f"{src.stem}_{args.to}.mp4")).resolve()
    fps = args.fps or int(prof.get("fps", 30))
    subprocess.run(ffmpeg_command(src, dest, box, target_w, target_h, fps), check=True)
    note = "  WARNING: upscale above 1.5x, the clip will look soft; record closer or in portrait next time" if box["upscale"] > 1.5 else ""
    print(f"{src.name} {src_w}x{src_h} -> {dest.name} {target_w}x{target_h}: crop {box['w']}x{box['h']} at ({box['x']},{box['y']}), "
          f"upscale {box['upscale']}x, {fps} fps constant{note}")


if __name__ == "__main__":
    main()
