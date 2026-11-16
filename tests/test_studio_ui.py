"""Unit tests for helpers/studio_ui.py parsers and feedback writer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

import studio_ui as ui  # noqa: E402


def test_parse_ass_events_extracts_times_text_and_highlight():
    ass = ("[Events]\n"
           "Dialogue: 0,0:00:00.55,0:00:00.71,Cap,,0,0,0,,{\\an5\\pos(470,960)}{\\c&H0066D1FF\\fscx112\\fscy112}video{\\r} of me,\n"
           "Dialogue: 0,0:01:02.00,0:01:02.50,Cap,,0,0,0,,video {\\c&H0066D1FF}of{\\r} me,\n")

    ev = ui.parse_ass_events(ass)

    assert ev[0] == {"start": 0.55, "end": 0.71, "text": "video of me,", "hl": 0}
    assert ev[1]["start"] == 62.0 and ev[1]["hl"] == 1


def test_parse_index_reads_date_slug_status_note():
    rows = ui.parse_index("# x\n- 2026-11-16 · test-clip · transcribed (31 s mic test)\n- bad line\n")

    assert rows == [{"date": "2026-11-16", "slug": "test-clip", "status": "transcribed", "note": "31 s mic test"}]


def test_parse_card_fields(tmp_path):
    p = tmp_path / "pop.md"
    p.write_text("# Number pop\n\n- **kind:** motion\n- **from:** ref-1\n- **what:** a number pops\n- **use when:** numbers\n- **avoid when:** never\n- **prompt:** do it\n")

    c = ui.parse_card(p.read_text(), p)

    assert c["title"] == "Number pop" and c["kind"] == "motion" and c["use_when"] == "numbers" and c["prompt"] == "do it"


def test_parse_style_rules_and_decisions():
    rules = ui.parse_style_rules("## Captions\n- Sentence case. (2026-11-16 · seed)\n## Sound\n- Music −12 dB. (2026-11-16 · rule)\n")
    decs = ui.parse_decisions("# D\n\n## 2026-11-16 · Fork\n**Why:** x\n\n## 2026-11-15 · Older\nbody\n")

    assert rules[0] == {"section": "Captions", "rule": "Sentence case.", "date": "2026-11-16", "origin": "seed"}
    assert rules[1]["section"] == "Sound"
    assert [d["title"] for d in decs] == ["Fork", "Older"] and decs[0]["body"] == "**Why:** x"


def test_write_feedback_sorts_and_drops_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "VIDEOS_DIR", tmp_path)
    (tmp_path / "2026-11-16_x").mkdir()

    out = ui.write_feedback("2026-11-16_x", [{"t": 5.2, "text": "late cut"}, {"t": 1, "text": "   "}])

    data = json.loads(out.read_text())
    assert out.name == "feedback.json" and data["notes"] == [{"t": 5.2, "text": "late cut", "created": data["notes"][0]["created"], "done": False}]


def test_write_feedback_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "VIDEOS_DIR", tmp_path)
    try:
        ui.write_feedback("../etc", [])
        assert False, "expected ValueError"
    except ValueError:
        pass
