"""Studio: render.py burns .ass captions with their own styles (no force_style)."""

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "helpers" / "render.py"
SPEC = importlib.util.spec_from_file_location("video_use_render_ass", MODULE_PATH)
assert SPEC and SPEC.loader
render = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render)


def test_srt_keeps_force_style(tmp_path):
    srt = tmp_path / "master.srt"
    srt.write_text("")

    f = render.subtitles_filter(srt)

    assert f.startswith("subtitles='")
    assert "force_style=" in f


def test_ass_has_no_force_style(tmp_path):
    ass = tmp_path / "master.ass"
    ass.write_text("")

    f = render.subtitles_filter(ass)

    assert "force_style=" not in f
    assert "master.ass" in f


def test_ass_points_libass_at_brand_fonts(tmp_path, monkeypatch):
    fonts = tmp_path / "fonts"
    fonts.mkdir()
    monkeypatch.setattr(render, "BRAND_FONTS_DIR", fonts)
    ass = tmp_path / "master.ass"
    ass.write_text("")

    f = render.subtitles_filter(ass)

    assert "fontsdir='" in f and str(fonts) in f


def test_colon_in_path_is_escaped(tmp_path):
    ass = tmp_path / "a:b.ass"
    ass.write_text("")

    f = render.subtitles_filter(ass)

    assert r"a\:b.ass" in f
