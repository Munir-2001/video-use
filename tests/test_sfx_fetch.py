"""Unit tests for helpers/sfx_fetch.py (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

import sfx_fetch as sf  # noqa: E402


def test_search_url_filters_to_free_licences():
    url = sf.search_url("cash register", ("cc0", "by"))

    assert url.startswith("https://api.openverse.org/v1/audio/?")
    assert "q=cash+register" in url and "license=cc0%2Cby" in url and "category" not in url


def test_rank_drops_restrictive_licences_long_clips_and_missing_files():
    results = [
        {"id": "a", "license": "by-nc", "url": "u", "duration": 1000},
        {"id": "b", "license": "cc0", "url": "u", "duration": 9000},
        {"id": "c", "license": "by", "url": None, "duration": 1000},
        {"id": "d", "license": "cc0", "url": "u", "duration": 1500},
        {"id": "e", "license": "by", "url": "u", "duration": None},
    ]

    kept = sf.rank(results, max_seconds=6.0)

    assert [r["id"] for r in kept] == ["d", "e"]


def test_credit_line_and_append_once(tmp_path):
    r = {"title": "Cash Register", "creator": "Ana", "license": "by", "license_version": "4.0",
         "foreign_landing_url": "https://freesound.org/s/1/"}
    line = sf.credit_line(r, "cash_register")
    credits = tmp_path / "CREDITS.md"
    credits.write_text("# SFX Credits\n\nbundled stuff\n")

    sf.append_credit(line, credits)
    sf.append_credit(line, credits)

    text = credits.read_text()
    assert line == '- `extra_cash_register.mp3` — "Cash Register" by Ana, CC BY 4.0, via Openverse: https://freesound.org/s/1/'
    assert text.count(line) == 1 and "## Openverse" in text and text.startswith("# SFX Credits")


def test_safe_name():
    assert sf.safe_name("Cash Register!!") == "cash_register" and sf.safe_name("") == "sfx"
