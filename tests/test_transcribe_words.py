"""Unit tests for the Parakeet token -> Scribe-shaped words conversion."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "helpers"))

from transcribe import interleave_spacing, tokens_to_words  # noqa: E402


@dataclass
class Tok:
    text: str
    start: float
    end: float


REQUIRED_KEYS = {"type", "text", "start", "end", "speaker_id"}


def test_leading_space_starts_a_new_word_and_subwords_merge():
    # Arrange: " web" + " ag" + "ent" as Parakeet emits them
    toks = [Tok(" web", 1.2, 1.44), Tok(" ag", 1.44, 1.68), Tok("ent", 1.68, 1.84)]

    # Act
    words = tokens_to_words(toks)

    # Assert
    assert [w["text"] for w in words] == ["web", "agent"]
    assert words[1]["start"] == 1.44 and words[1]["end"] == 1.84


def test_punctuation_joins_text_but_does_not_extend_end():
    toks = [Tok(" was", 2.72, 2.96), Tok("ted", 2.96, 3.12), Tok(".", 3.28, 3.52), Tok(" We", 3.52, 3.68)]

    words = tokens_to_words(toks)

    assert words[0]["text"] == "wasted."
    assert words[0]["end"] == 3.12
    assert words[1]["text"] == "We"


def test_whitespace_only_token_breaks_the_word():
    # "Step 1," arrives as ' Step', ' ', '1', ','
    toks = [Tok(" Step", 5.0, 5.3), Tok(" ", 5.3, 5.4), Tok("1", 5.4, 5.6), Tok(",", 5.6, 5.7)]

    words = tokens_to_words(toks)

    assert [w["text"] for w in words] == ["Step", "1,"]


def test_every_entry_has_exact_shape_and_speaker_s0():
    toks = [Tok(" a", 0.0, 0.1), Tok(" b", 0.5, 0.6)]

    entries = interleave_spacing(tokens_to_words(toks))

    assert [e["type"] for e in entries] == ["word", "spacing", "word"]
    for e in entries:
        assert set(e.keys()) == REQUIRED_KEYS
        assert e["speaker_id"] == "S0"


def test_spacing_covers_gap_and_is_clamped_to_non_negative():
    toks = [Tok(" a", 0.0, 0.5), Tok(" b", 0.4, 0.9), Tok(" c", 1.2, 1.3)]

    entries = interleave_spacing(tokens_to_words(toks))

    overlap_gap, real_gap = entries[1], entries[3]
    assert overlap_gap["start"] == 0.5 and overlap_gap["end"] == 0.5
    assert real_gap["start"] == 0.9 and real_gap["end"] == 1.2
