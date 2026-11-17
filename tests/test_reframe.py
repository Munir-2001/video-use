"""Unit tests for helpers/reframe.py crop geometry (no ffmpeg)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

import reframe as rf  # noqa: E402


def test_landscape_to_vertical_takes_full_height_column_and_reports_upscale():
    box = rf.crop_box(1920, 1080, 1080, 1920)

    assert box == {"x": 656, "y": 0, "w": 608, "h": 1080, "upscale": 1.78}


def test_crop_follows_the_face_and_clamps_to_the_frame():
    left = rf.crop_box(1920, 1080, 1080, 1920, x_frac=0.3)
    edge = rf.crop_box(1920, 1080, 1080, 1920, x_frac=0.0)

    assert left["x"] == 272 and edge["x"] == 0


def test_vertical_to_horizontal_takes_full_width_band():
    box = rf.crop_box(1080, 1920, 1920, 1080, y_frac=0.35)

    assert box["w"] == 1080 and box["h"] == 608 and box["y"] == 368 and box["upscale"] == 1.78


def test_4k_landscape_to_vertical_needs_no_upscale():
    box = rf.crop_box(3840, 2160, 1080, 1920)

    assert box["w"] == 1214 and box["upscale"] == 0.89  # 2160 * 9/16 = 1215, rounded down to even


def test_ffmpeg_command_crops_then_scales_and_copies_audio():
    cmd = rf.ffmpeg_command(Path("a.mov"), Path("b.mp4"), {"x": 656, "y": 0, "w": 608, "h": 1080}, 1080, 1920)

    assert cmd[cmd.index("-vf") + 1].startswith("crop=608:1080:656:0,scale=1080:1920") and "-c:a" in cmd and cmd[cmd.index("-c:a") + 1] == "copy"
