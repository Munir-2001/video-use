"""Unit tests for helpers/voiceover.py (pure planning, no ffmpeg)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

import voiceover as vo  # noqa: E402


def test_audio_cut_filter_trims_each_range_and_concats_in_order():
    ranges = [{"source": "take1", "start": 1.0, "end": 3.5}, {"source": "take2", "start": 0.2, "end": 1.0}]

    f = vo.audio_cut_filter(ranges, {"take1": 0, "take2": 1})

    assert f.startswith("[0:a]atrim=start=1.000:end=3.500,asetpts=PTS-STARTPTS[a0];[1:a]atrim=start=0.200:end=1.000")
    assert f.endswith("[a0][a1]concat=n=2:v=0:a=1[voice]")


def test_plan_fills_gaps_with_background_and_clamps_to_total():
    stretches = [
        {"id": "s2", "start": 4.0, "end": 9.0, "layout": "screen", "footage": {"file": "phone.mp4", "in_s": 12.0}},
        {"id": "s1", "start": 1.0, "end": 3.0, "layout": "face_full"},
        {"id": "s3", "start": 9.0, "end": 30.0, "layout": "screen", "footage": {"file": "b.mov", "fit": "cover"}},
    ]

    plan = vo.plan_video_track(stretches, total=12.0)

    assert [(p["kind"], p["start"], p["end"]) for p in plan] == [
        ("background", 0.0, 1.0), ("background", 1.0, 3.0), ("background", 3.0, 4.0),
        ("footage", 4.0, 9.0), ("footage", 9.0, 12.0)]
    assert plan[3]["file"] == "phone.mp4" and plan[3]["in_s"] == 12.0 and plan[3]["fit"] == "contain"
    assert plan[4]["fit"] == "cover" and plan[4]["in_s"] == 0.0


def test_plan_overlap_keeps_earlier_stretch_and_advances_in_point():
    stretches = [
        {"id": "a", "start": 0.0, "end": 5.0, "footage": {"file": "a.mp4"}},
        {"id": "b", "start": 3.0, "end": 8.0, "footage": {"file": "b.mp4", "in_s": 10.0}},
    ]

    plan = vo.plan_video_track(stretches, total=8.0)

    assert [(p["start"], p["end"]) for p in plan] == [(0.0, 5.0), (5.0, 8.0)]
    assert plan[1]["in_s"] == 12.0  # trimmed 2 s off the head, so the in-point moves 2 s too


def test_segment_command_background_and_footage_shapes(tmp_path):
    (tmp_path / "clip.mp4").write_bytes(b"x")
    bg = vo.segment_command({"kind": "background", "start": 0, "end": 1.5}, tmp_path, 1080, 1920, 30, "#0B0B0F", tmp_path / "o.mp4")
    ft = vo.segment_command({"kind": "footage", "start": 0, "end": 2.0, "file": "clip.mp4", "in_s": 3.25, "fit": "cover"},
                            tmp_path, 1080, 1920, 30, "#0B0B0F", tmp_path / "o.mp4")

    assert "color=c=0x0B0B0F:s=1080x1920:r=30:d=1.500" in " ".join(bg) and "-t 1.500" in " ".join(bg)
    assert ft[ft.index("-ss") + 1] == "3.250" and "crop=1080:1920" in ft[ft.index("-vf") + 1]
    assert "tpad=stop_mode=clone:stop_duration=2.000" in ft[ft.index("-vf") + 1]


def test_edl_master_keeps_overlays_and_subtitles(tmp_path):
    edl = {"version": 1, "profile": "vertical", "sources": {"take1": "/v/take1.mp3"},
           "ranges": [{"source": "take1", "start": 1, "end": 4}, {"source": "take1", "start": 6, "end": 8.5}],
           "grade": "none", "overlays": [{"file": "animations/t/render.mov", "start_in_output": 0.5, "duration": 2}],
           "subtitles": "master.ass"}

    m = vo.edl_master_from(edl, tmp_path / "voice_master.mp4", vo.edl_total(edl["ranges"]))

    assert m["ranges"] == [{"source": "voice_master", "start": 0.0, "end": 5.5, "beat": "ALL", "quote": "",
                            "reason": m["ranges"][0]["reason"]}]
    assert m["overlays"] == edl["overlays"] and m["subtitles"] == "master.ass" and m["total_duration_s"] == 5.5


def test_load_brief_defaults_and_validates_mode(tmp_path):
    assert vo.load_brief(tmp_path)["mode"] == "clips"
    (tmp_path / "edit").mkdir()
    (tmp_path / "edit" / "brief.json").write_text(json.dumps({"mode": "karaoke"}))
    try:
        vo.load_brief(tmp_path)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_split_top_stretch_anchors_footage_at_the_bottom(tmp_path):
    (tmp_path / "c.mp4").write_bytes(b"x")
    plan = vo.plan_video_track([{"id": "s", "start": 0, "end": 2, "layout": "split_top", "footage": {"file": "c.mp4"}}], 2.0)
    cmd = vo.segment_command(plan[0], tmp_path, 1080, 1920, 30, "#0B0B0F", tmp_path / "o.mp4")

    assert plan[0]["anchor"] == "bottom" and "pad=1080:1920:(ow-iw)/2:oh-ih:0x0B0B0F" in cmd[cmd.index("-vf") + 1]
