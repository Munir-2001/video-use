"""Unit tests for helpers/fix_transcript.py (vocabulary + proofreader proposals)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

from fix_transcript import apply_proposals, apply_vocabulary, fix_one  # noqa: E402


def word(text, start):
    return {"type": "word", "text": text, "start": start, "end": start + 0.1, "speaker_id": "S0"}


def spacing(start):
    return {"type": "spacing", "text": " ", "start": start, "end": start, "speaker_id": "S0"}


def take(*texts):
    out = []
    for i, t in enumerate(texts):
        out.append(word(t, i * 0.2))
        out.append(spacing(i * 0.2 + 0.1))
    return out[:-1]


VOCAB = {
    "fixes": [{"heard": "clot code", "say": "Claude Code"}, {"heard": "Muni Rabasi", "say": "Munir Abbasi"}],
    "always_capitalize": ["Claude", "Innova"],
}


def test_multiword_fix_keeps_count_and_trailing_punctuation():
    words = take("using", "clot", "code.", "We")

    fixed, changes = apply_vocabulary(words, VOCAB)

    assert [w["text"] for w in fixed if w["type"] == "word"] == ["using", "Claude", "Code.", "We"]
    assert len(fixed) == len(words)
    assert [c["by"] for c in changes] == ["vocabulary", "vocabulary"]


def test_vocabulary_match_is_case_insensitive_and_does_not_mutate_input():
    words = take("CLOT", "Code")

    fixed, _ = apply_vocabulary(words, VOCAB)

    assert words[0]["text"] == "CLOT"
    assert fixed[0]["text"] == "Claude"


def test_always_capitalize_fixes_case_only_on_exact_words():
    words = take("innova", "innovation")

    fixed, changes = apply_vocabulary(words, VOCAB)

    assert fixed[0]["text"] == "Innova"
    assert fixed[2]["text"] == "innovation"
    assert len(changes) == 1


def test_proposal_applies_when_old_matches():
    words = take("there", "house")

    fixed, applied, rejected = apply_proposals(words, [{"index": 0, "old": "there", "new": "their"}])

    assert fixed[0]["text"] == "their" and applied and not rejected


def test_proposal_rejected_on_mismatch_spacing_index_or_multiword():
    words = take("there", "house")

    _, applied, rejected = apply_proposals(words, [
        {"index": 0, "old": "their", "new": "there"},
        {"index": 1, "old": " ", "new": "x"},
        {"index": 0, "old": "there", "new": "over there"},
        {"index": 99, "old": "there", "new": "their"},
    ])

    assert not applied and len(rejected) == 4


def test_fix_one_keeps_raw_copy_and_is_idempotent(tmp_path):
    tdir = tmp_path / "transcripts"
    tdir.mkdir()
    path = tdir / "clip.json"
    path.write_text(json.dumps({"text": "x", "words": take("clot", "code")}))

    first = fix_one(path, VOCAB)
    second = fix_one(path, VOCAB)

    raw = json.loads((tdir / "raw" / "clip.json").read_text())
    fixed = json.loads(path.read_text())
    assert raw["words"][0]["text"] == "clot"
    assert fixed["words"][0]["text"] == "Claude" and fixed["text"] == "Claude Code"
    assert len(first["changes"]) == len(second["changes"]) == 2
    assert (tdir / "raw" / "clip.corrections.json").exists()


def test_fix_one_keeps_prior_proofreader_fixes_on_rerun(tmp_path):
    tdir = tmp_path / "transcripts"
    tdir.mkdir()
    path = tdir / "clip.json"
    path.write_text(json.dumps({"text": "x", "words": take("there", "house")}))

    fix_one(path, VOCAB, proposals=[{"index": 0, "old": "there", "new": "their"}])
    fix_one(path, VOCAB)

    assert json.loads(path.read_text())["words"][0]["text"] == "their"
