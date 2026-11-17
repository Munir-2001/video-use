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
