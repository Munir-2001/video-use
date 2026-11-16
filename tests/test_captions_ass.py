"""Unit tests for helpers/captions_ass.py (word-synced .ass captions)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

import captions_ass as ca  # noqa: E402

STYLE = {
    "fonts": {"display": {"family": "Inter", "weight": 800, "file": "brand/fonts/does-not-exist.ttf", "fallback": "Helvetica Neue"}},
    "colors": {"caption_base": "#F5F5F7", "caption_highlight": "#FFD166", "caption_outline": "#000000"},
    "captions": {
        "case": "sentence", "words_per_cue": {"target": 2, "max": 3}, "font": "display",
        "size_px_1080w": 64, "size_px_1080x1920": 72,
        "highlight": {"scale": 1.12, "color": "caption_highlight", "base_color": "caption_base"},
        "outline_px": 4, "shadow_px": 2,
        "position": {"vertical": {"anchor": "middle", "y_fraction": 0.5}, "horizontal": {"anchor": "bottom", "y_fraction": 0.84}},
        "max_width_fraction": 0.8,
    },
    "safe_areas": {"vertical": {"bottom_clear_fraction": 0.2, "right_clear_px": 140}, "horizontal": {}},
    "profiles": {"vertical": {"width": 1080, "height": 1920}, "horizontal": {"width": 1920, "height": 1080}},
}


def w(text, start, end):
    return {"type": "word", "text": text, "start": start, "end": end, "speaker_id": "S0"}


def test_ass_colour_is_bgr_with_alpha():
    assert ca.ass_colour("#FFD166") == "&H0066D1FF"
    assert ca.ass_colour("#000000", 0x80) == "&H80000000"


def test_ass_time_format():
    assert ca.ass_time(0) == "0:00:00.00"
    assert ca.ass_time(61.234) == "0:01:01.23"


def test_cues_use_output_timeline_offsets_across_two_ranges(tmp_path):
    tdir = tmp_path / "transcripts"
    tdir.mkdir()
    (tdir / "A.json").write_text(json.dumps({"words": [w("Hello", 10.0, 10.3), w("world.", 10.4, 10.8), w("Bye", 20.0, 20.4)]}))
    (tdir / "B.json").write_text(json.dumps({"words": [w("Second", 5.0, 5.4), w("take.", 5.5, 5.9)]}))
    edl = {"ranges": [{"source": "A", "start": 10.0, "end": 11.0}, {"source": "B", "start": 5.0, "end": 6.0}]}

    cues = ca.output_cues(edl, tdir, 2, 3)

    assert [[x["text"] for x in c["words"]] for c in cues] == [["Hello", "world."], ["Second", "take."]]
    assert cues[0]["words"][0]["start"] == 0.0
    assert abs(cues[1]["words"][0]["start"] - 1.0) < 1e-9  # 5.0 - 5.0 + offset 1.0


def test_one_event_per_word_with_highlight_on_current_word_only():
    cue = {"start": 0.0, "end": 1.0, "words": [{"text": "Hello", "start": 0.0, "end": 0.4}, {"text": "world", "start": 0.5, "end": 1.0}]}
    layout = ca.layout_for(STYLE, "vertical", 1080, 1920)

    events = ca.word_events(cue, layout, "&H0066D1FF", "&H00F7F5F5", 112)

    assert len(events) == 2
    assert events[0][2].count("\\c&H0066D1FF") == 1 and "}Hello{" in events[0][2]
    assert "}world{" in events[1][2]
    assert events[0][1] == 0.5 and events[1][0] == 0.5


def test_vertical_layout_is_middle_band_and_clear_of_right_edge():
    layout = ca.layout_for(STYLE, "vertical", 1080, 1920)

    assert layout["an"] == 5 and layout["y"] == 960
    assert layout["margin_r"] >= 140 and layout["font_size"] == 72


def test_horizontal_layout_is_bottom_anchored():
    layout = ca.layout_for(STYLE, "horizontal", 1920, 1080)

    assert layout["an"] == 2 and layout["y"] == int(round(1080 * 0.84))


def test_build_ass_keeps_sentence_case_and_warns_on_missing_font():
    cues = [{"start": 0.0, "end": 0.6, "words": [{"text": "Hello", "start": 0.0, "end": 0.3}, {"text": "there.", "start": 0.3, "end": 0.6}]}]

    text, warnings = ca.build_ass(cues, STYLE, "vertical", 1080, 1920)

    assert "PlayResX: 1080" in text and "PlayResY: 1920" in text
    assert "Style: Cap,Helvetica Neue,72," in text
    assert "Hello" in text and "HELLO" not in text
    assert warnings and "font file missing" in warnings[0]
    assert text.count("Dialogue:") == 2


def test_layout_y_fraction_override_and_validation():
    style = STYLE
    assert ca.layout_for(style, "vertical", 1080, 1920)["y"] == 960
    assert ca.layout_for(style, "vertical", 1080, 1920, y_fraction=0.68)["y"] == 1306
    try:
        ca.layout_for(style, "vertical", 1080, 1920, y_fraction=1.2)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_brand_default_band_is_under_the_chin_not_the_middle():
    import json
    from pathlib import Path
    brand = json.loads((Path(__file__).resolve().parent.parent / "brand" / "style.json").read_text())
    v = brand["captions"]["position"]["vertical"]
    assert 0.62 <= v["y_fraction"] <= 0.74 and v["band"][1] <= 0.80
