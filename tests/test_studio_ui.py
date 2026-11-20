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


def _mp(fields, files):
    """Build a multipart/form-data body the way a browser does."""
    b = "xyzBOUNDARY42"
    out = b""
    for k, v in fields.items():
        out += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    for k, (fname, data) in files.items():
        out += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fname}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + data + b"\r\n"
    return out + f"--{b}--\r\n".encode(), b


def test_parse_multipart_fields_and_binary_files():
    body, b = _mp({"slug": "My Reel", "mode": "voiceover"}, {"voice": ("take 1.mp3", b"\x00\xff\r\n--not-a-boundary\r\n")})

    parts = ui.parse_multipart(body, b)

    assert [(p["name"], p["filename"]) for p in parts] == [("slug", None), ("mode", None), ("voice", "take 1.mp3")]
    assert parts[0]["data"] == b"My Reel" and parts[2]["data"] == b"\x00\xff\r\n--not-a-boundary\r\n"


def test_save_upload_creates_folder_voice_subdir_brief_and_index(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "VIDEOS_DIR", tmp_path)
    body, b = _mp({"slug": "My Reel!", "mode": "voiceover", "notes": "voice over the phone clip"},
                  {"footage": ("IMG_0001.MOV", b"vid"), "voice": ("take 1.mp3", b"aud"), "other": ("notes.txt", b"x")})

    r = ui.save_upload(ui.parse_multipart(body, b))

    folder = tmp_path / r["folder"]
    assert r["folder"].endswith("_my-reel") and r["footage"] == ["IMG_0001.MOV"] and r["voice"] == ["voice/take_1.mp3"]
    assert r["skipped"] == ["notes.txt"] and (folder / "IMG_0001.MOV").read_bytes() == b"vid" and (folder / "voice" / "take_1.mp3").exists()
    brief = json.loads((folder / "edit" / "brief.json").read_text())
    assert brief["mode"] == "voiceover" and brief["notes"] == "voice over the phone clip" and brief["voice_offset_s"] == 0.0
    assert "· my-reel · raw (uploaded from the studio: 1 clip(s), 1 voice file(s), mode voiceover)" in (tmp_path / "index.md").read_text()


def test_save_upload_into_existing_folder_merges_brief_and_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "VIDEOS_DIR", tmp_path)
    (tmp_path / "2026-11-16_x").mkdir()
    ui.write_brief(tmp_path / "2026-11-16_x", "clips", ["a.mp4"], [])
    body, b = _mp({"mode": "commentary", "voice_offset_s": "2.5"}, {"voice": ("v.m4a", b"a")})

    r = ui.save_upload(ui.parse_multipart(body, b), "2026-11-16_x")

    assert r["brief"]["footage"] == ["a.mp4"] and r["brief"]["voice"] == ["voice/v.m4a"] and r["brief"]["mode"] == "commentary" and r["brief"]["voice_offset_s"] == 2.5
    for bad in ("../x", "a/b"):
        try:
            ui.save_upload([], bad)
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_parse_ass_events_accepts_explicit_highlight_close():
    ass = "[Events]\nDialogue: 0,0:00:01.00,0:00:01.50,Cap,,0,0,0,,{\\an5\\pos(1,2)\\fs64}a {\\c&H002A50F4\\fscx86\\fscy86}b{\\c&H00F7F5F5\\fscx100\\fscy100} c\n"

    ev = ui.parse_ass_events(ass)

    assert ev[0]["text"] == "a b c" and ev[0]["hl"] == 1


# -------- new-reel funnel ----------------------------------------------------

KINDS = {"types": {"explainer": {"label": "Explainer"}}, "goals": {"views": {"label": "Views"}}, "statuses": ["idea"]}


def _funnel(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "VIDEOS_DIR", tmp_path)
    kinds = tmp_path / "reel_kinds.json"
    kinds.write_text(json.dumps(KINDS))
    monkeypatch.setattr(ui, "REEL_KINDS_PATH", kinds)


def test_clean_plan_validates_type_goal_and_splits_links():
    plan = ui.clean_plan({"idea": "  Scrape leads with Claude Code ", "type": "explainer", "goal": "views",
                          "links": "https://a\n\nhttps://b", "cta_keyword": "Scrape"}, KINDS)

    assert plan["idea"] == "Scrape leads with Claude Code" and plan["links"] == ["https://a", "https://b"]
    assert plan["audience"] == "" and plan["cta_keyword"] == "Scrape"
    for bad in ({"idea": "", "type": "explainer", "goal": "views"}, {"idea": "x", "type": "nope", "goal": "views"},
                {"idea": "x", "type": "explainer", "goal": "nope"}):
        try:
            ui.clean_plan(bad, KINDS)
            assert False, f"expected ValueError for {bad}"
        except ValueError:
            pass


def test_create_reel_makes_folder_brief_plan_and_idea_index_line(tmp_path, monkeypatch):
    _funnel(tmp_path, monkeypatch)

    r = ui.create_reel({"idea": "Five Claude Code hooks I use daily", "type": "explainer", "goal": "views", "audience": "devs"})

    folder = tmp_path / r["folder"]
    assert r["folder"].endswith("_five-claude-code-hooks-i-use-daily") and (folder / "assets").is_dir()
    brief = json.loads((folder / "edit" / "brief.json").read_text())
    assert brief["plan"]["type"] == "explainer" and brief["plan"]["audience"] == "devs" and brief["mode"] == "clips"
    assert "· five-claude-code-hooks-i-use-daily · idea (Five Claude Code hooks I use daily)" in (tmp_path / "index.md").read_text()
    try:
        ui.create_reel({"idea": "Five Claude Code hooks I use daily", "type": "explainer", "goal": "views"})
        assert False, "expected ValueError on a duplicate folder"
    except ValueError:
        pass


def test_write_plan_keeps_voice_fields_and_merges(tmp_path, monkeypatch):
    _funnel(tmp_path, monkeypatch)
    folder = tmp_path / "2026-11-20_x"
    folder.mkdir()
    ui.write_brief(folder, "voiceover", ["a.mp4"], ["voice/v.m4a"], 1.5, "keep")

    brief = ui.write_plan(folder, {"idea": "one", "type": "explainer", "goal": "views"})
    brief = ui.write_plan(folder, {"offer": "the list"})

    assert brief["mode"] == "voiceover" and brief["voice_offset_s"] == 1.5 and brief["notes"] == "keep"
    assert brief["plan"]["idea"] == "one" and brief["plan"]["offer"] == "the list"


def test_set_index_status_replaces_line_keeps_note_or_appends(tmp_path, monkeypatch):
    _funnel(tmp_path, monkeypatch)
    (tmp_path / "index.md").write_text("# videos\n\n- 2026-11-20 · x · idea (my idea)\n")
    folder = tmp_path / "2026-11-20_x"

    ui.set_index_status(folder, "scripted")
    assert "- 2026-11-20 · x · scripted (my idea)" in (tmp_path / "index.md").read_text()
    assert ui.index_status(folder) == "scripted"

    ui.set_index_status(folder, "assets", "all 3 screens dropped")
    assert "- 2026-11-20 · x · assets (all 3 screens dropped)" in (tmp_path / "index.md").read_text()

    ui.set_index_status(tmp_path / "2026-11-21_y", "idea", "new")
    assert (tmp_path / "index.md").read_text().endswith("- 2026-11-21 · y · idea (new)\n")


SCRIPT = """# Title

## Say this
Hi.

## Assets to capture
| # | file | what | highlight on which word | type |
|---|---|---|---|---|
| 1 | `01_readme.png` | GitHub README | "Scrapling" | screenshot |
| 2 | 02_config.png | ~/.claude.json | "MCP" | screenshot |

## Recording notes
- none
"""


def test_parse_assets_table_reads_rows_only_from_its_section():
    rows = ui.parse_assets_table(SCRIPT)

    assert [r["file"] for r in rows] == ["01_readme.png", "02_config.png"] and rows[1]["highlight"] == '"MCP"'
    assert ui.parse_assets_table("# no table\n| a | b | c | d | e |\n") == []


def test_asset_upload_maps_beat_matches_names_and_advances_status(tmp_path, monkeypatch):
    _funnel(tmp_path, monkeypatch)
    folder = tmp_path / "2026-11-20_x"
    folder.mkdir()
    (folder / "script.md").write_text(SCRIPT)
    (tmp_path / "index.md").write_text("- 2026-11-20 · x · scripted (idea)\n")

    body, b = _mp({"beat": "2"}, {"file": ("Screenshot 2026.png", b"png"), "junk": ("notes.txt", b"x")})
    r = ui.save_asset_upload(ui.parse_multipart(body, b), "2026-11-20_x")
    assert r["saved"] == ["Screenshot_2026.png"] and r["skipped"] == ["notes.txt"]
    assert r["assets"]["rows"][1]["dropped"] == "Screenshot_2026.png" and r["assets"]["rows"][0]["dropped"] is None
    assert not r["assets"]["complete"] and ui.index_status(folder) == "scripted"

    body, b = _mp({}, {"file": ("01_README.png", b"png")})
    r = ui.save_asset_upload(ui.parse_multipart(body, b), "2026-11-20_x")
    assert r["assets"]["rows"][0]["dropped"] == "01_README.png" and r["assets"]["complete"] and r["assets"]["extra"] == []
    assert ui.index_status(folder) == "assets"
    manifest = json.loads((folder / "assets" / "manifest.json").read_text())
    assert manifest["items"] == [{"beat": "2", "file": "Screenshot_2026.png", "added": manifest["items"][0]["added"]}]


def test_clip_upload_moves_a_planned_reel_to_raw(tmp_path, monkeypatch):
    _funnel(tmp_path, monkeypatch)
    r = ui.create_reel({"idea": "x", "type": "explainer", "goal": "views"})
    body, b = _mp({"mode": "clips"}, {"footage": ("take.mov", b"vid")})

    ui.save_upload(ui.parse_multipart(body, b), r["folder"])

    assert ui.index_status(tmp_path / r["folder"]) == "raw"


def test_effective_status_moves_planned_reels_forward_only():
    assert ui.effective_status("idea", True, False, False) == "scripted"
    assert ui.effective_status("idea", True, True, False) == "assets"
    assert ui.effective_status("scripted", True, True, True) == "raw"
    assert ui.effective_status("idea", False, False, False) == "idea"
    assert ui.effective_status("preview", True, True, True) == "preview"
