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


def test_word_events_pop_and_rise_tags():
    cue = {"start": 1.0, "end": 2.0, "words": [w("Hello", 1.0, 1.4), w("world", 1.4, 2.0)]}
    layout = {"an": 5, "x": 470, "y": 1306}

    ev = ca.word_events(cue, layout, "&H0066D1FF", "&H00F7F5F5", 112,
                        {"pop_ms": 120, "pop_from": 0.86, "rise_px": 28, "fade_in_ms": 80})

    first, second = ev[0][2], ev[1][2]
    assert "\\move(470,1334,470,1306,0,120)" in first and "\\fad(80,0)" in first
    assert "\\fscx86\\fscy86\\t(0,120,\\fscx112\\fscy112)" in first
    assert "\\pos(470,1306)" in second and "\\move" not in second


def test_word_events_no_motion_is_static():
    cue = {"start": 1.0, "end": 2.0, "words": [w("Hello", 1.0, 1.4)]}
    ev = ca.word_events(cue, {"an": 5, "x": 1, "y": 2}, "&H0066D1FF", "&H00F7F5F5", 112,
                        {"pop_ms": 0, "rise_px": 0, "fade_in_ms": 0})
    assert "\\t(" not in ev[0][2] and "\\pos(1,2)" in ev[0][2]


def test_voice_cues_shift_by_offset_and_stop_at_total():
    tr = {"words": [w("Hello", 0.0, 0.4), w("world", 0.5, 0.9), w("again", 5.0, 5.4)]}

    cues = ca.voice_cues(tr, offset_s=2.0, total_s=6.0, target=2, max_words=3)

    assert cues[0]["start"] == 2.0 and cues[0]["words"][1]["end"] == 2.9
    assert len(cues) == 1  # "again" would start at 7.0, past the 6 s video


def test_output_cues_per_stretch_caption_overrides(tmp_path):
    import json
    (tmp_path / "t.json").write_text(json.dumps({"words": [w("Fifty", 0.0, 0.4), w("free", 0.5, 0.9), w("backlinks", 1.0, 1.4),
                                                            w("Comment", 3.0, 3.4), w("backlinks", 3.5, 3.9)]}))
    edl = {"ranges": [{"source": "t", "start": 0.0, "end": 5.0}]}
    style = {**STYLE, "captions": {**STYLE["captions"], "presets": {"giant": {"words_per_cue": {"target": 1, "max": 1}, "size_px": 140, "y_fraction": 0.68}}},
             "layouts": {"split_top": {"caption": {"y_fraction": 0.44, "size_px": 56}}}}
    scenes = {"stretches": [{"id": "s1", "start": 0.0, "end": 2.0, "layout": "split_top"},
                            {"id": "s2", "start": 2.0, "end": 5.0, "layout": "face_full", "caption": "giant"}]}

    cues = ca.output_cues(edl, tmp_path, 2, 3, scenes, style)

    assert [len(c["words"]) for c in cues] == [2, 1, 1, 1]
    assert cues[0]["caption"]["y_fraction"] == 0.44 and cues[2]["caption"]["size_px"] == 140
    text, _ = ca.build_ass(cues, style, "vertical", 1080, 1920)
    assert "\\pos(470,845)\\fad" in text or "\\move(470,873,470,845" in text  # 0.44 * 1920 = 845
    assert "{\\r}" not in text  # a reset would drop the per-cue \\fs override
    assert "\\fs140}" in text and "\\fs56}" in text


def test_unknown_caption_preset_fails_loudly():
    try:
        ca.stretch_caption({"id": "s1", "caption": "huge"}, STYLE)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_captions_plan_overrides_automatic_grouping(tmp_path):
    import json
    (tmp_path / "t.json").write_text(json.dumps({"words": [w("Comment", 0.0, 0.3), w("backlinks", 0.4, 0.9), w("and", 1.0, 1.2),
                                                            w("I", 1.3, 1.4), w("send", 1.5, 1.9)]}))
    edl = {"ranges": [{"source": "t", "start": 0.0, "end": 3.0}]}
    style = {**STYLE, "captions": {**STYLE["captions"], "presets": {"big": {"size_px": 120, "y_fraction": 0.64}}}}
    plan = {"cues": [{"i": [0, 1], "preset": "big"}, {"i": [3, 4]}]}

    cues = ca.output_cues(edl, tmp_path, 2, 3, None, style, plan)

    assert [[x["text"] for x in c["words"]] for c in cues] == [["Comment", "backlinks"], ["I", "send"]]  # "and" dropped on purpose
    assert cues[0]["caption"]["size_px"] == 120 and "caption" not in cues[1]
    try:
        ca.output_cues(edl, tmp_path, 2, 3, None, style, {"cues": [{"i": [0, 2]}, {"i": [1, 3]}]})
        assert False, "overlap should fail"
    except ValueError:
        pass


def test_captions_plan_keeps_punctuated_words_in_one_cue(tmp_path):
    import json
    (tmp_path / "t.json").write_text(json.dumps({"words": [w("name,", 0.0, 0.3), w("site,", 0.4, 0.7), w("email,", 0.8, 1.2)]}))
    edl = {"ranges": [{"source": "t", "start": 0.0, "end": 2.0}]}

    cues = ca.output_cues(edl, tmp_path, 2, 3, None, STYLE, {"cues": [{"i": [0, 2]}]})

    assert len(cues) == 1 and [x["text"] for x in cues[0]["words"]] == ["name,", "site,", "email,"]


def test_word_events_never_overlap_even_for_very_short_words():
    cue = {"start": 1.0, "end": 1.5, "words": [w("a", 1.0, 1.03), w("b", 1.05, 1.08), w("c", 1.10, 1.5)]}

    ev = ca.word_events(cue, {"an": 5, "x": 1, "y": 2}, "&H0066D1FF", "&H00F7F5F5", 112, {"pop_ms": 0, "rise_px": 0, "fade_in_ms": 0})

    for (s0, e0, _), (s1, e1, _) in zip(ev, ev[1:]):
        assert e0 <= s1


def test_cue_preset_can_change_colour_outline_and_shadow():
    style = {**STYLE, "colors": {**STYLE["colors"], "ink": "#141418", "accent": "#F4502A"}}
    cue = {"start": 1.0, "end": 1.6, "words": [w("It's", 1.0, 1.2), w("called", 1.25, 1.6)],
           "caption": {"color": "ink", "highlight": "accent", "outline_px": 0, "shadow_px": 0, "size_px": 64}}

    text, _ = ca.build_ass([cue], style, "vertical", 1080, 1920)

    assert "\\fs64\\c&H00181414\\bord0\\shad0}" in text          # ink, no outline, no shadow on the panel
    assert "{\\c&H002A50F4" in text and "{\\c&H00181414\\fscx100" in text  # flame highlight, ink restore


def test_soft_shadow_fields_emit_blur_and_shadow_alpha():
    cue = {"start": 1.0, "end": 1.6, "words": [w("Comment", 1.0, 1.3)], "caption": {"shadow_px": 2, "shadow_blur": 3, "shadow_alpha": 0.55}}

    text, _ = ca.build_ass([cue], STYLE, "vertical", 1080, 1920)

    assert "\\shad2\\blur3\\4a&H73&}" in text


def test_wide_cue_gets_a_fixed_balanced_break_in_every_event():
    cue = {"start": 1.0, "end": 2.0, "words": [w("Second,", 1.0, 1.3), w("stealth", 1.35, 1.7), w("fetchers.", 1.75, 2.0)],
           "caption": {"size_px": 96}}

    text, _ = ca.build_ass([cue], STYLE, "vertical", 1080, 1920)
    events = [l for l in text.splitlines() if l.startswith("Dialogue")]

    assert len(events) == 3 and all("\\N" in e for e in events)
    assert all(e.count("\\N") == 1 for e in events) and "WrapStyle: 2" in text
    assert ca.break_index([w("a", 0, 1), w("b", 1, 2)], 64, 864) is None  # short cue: one line
