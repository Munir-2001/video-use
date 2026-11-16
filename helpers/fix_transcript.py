"""Fix mis-heard words in a transcript without touching its timing.

Two layers, both word-for-word (the word count never changes, so every
timestamp and caption cue stays valid):

  1. Vocabulary: `brand/style.json` -> vocabulary.fixes, a list of
     {"heard": "clot code", "say": "Claude Code"}. Matched case-insensitively
     over consecutive words, punctuation on the last word preserved.
     `always_capitalize` fixes case on exact matches.
  2. Proposals: a JSON list from the proofreader sub-agent,
     [{"index": 12, "old": "there", "new": "their"}, ...]. Each is validated:
     the index must hold `old`, `new` must be a single token. Rejected
     proposals are reported, never applied.

The first run copies the raw transcript to transcripts/raw/<name>.json and
every later run re-applies from that copy, so fixes are idempotent and
reversible. A log of applied changes lands next to it as
transcripts/raw/<name>.corrections.json (outside the packer's *.json glob).

Usage:
    python helpers/fix_transcript.py --edit-dir <dir>                 # vocabulary on every transcript
    python helpers/fix_transcript.py --edit-dir <dir> --proposals p.json --source <name>
    python helpers/fix_transcript.py --edit-dir <dir> --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BRAND_STYLE = Path(__file__).resolve().parent.parent / "brand" / "style.json"
TOKEN_RE = re.compile(r"^[^\s]+$")
TRAILING_PUNCT_RE = re.compile(r"([.,!?;:]+)$")


def load_vocabulary(style_path: Path = BRAND_STYLE) -> dict:
    if not style_path.exists():
        return {"fixes": [], "always_capitalize": []}
    data = json.loads(style_path.read_text())
    vocab = data.get("vocabulary", {})
    return {
        "fixes": [f for f in vocab.get("fixes", []) if f.get("heard") and f.get("say")],
        "always_capitalize": list(vocab.get("always_capitalize", [])),
    }


def _split_punct(text: str) -> tuple[str, str]:
    m = TRAILING_PUNCT_RE.search(text)
    if not m:
        return text, ""
    return text[: m.start()], m.group(1)


def _word_indices(words: list[dict]) -> list[int]:
    return [i for i, w in enumerate(words) if w.get("type") == "word"]


def apply_vocabulary(words: list[dict], vocab: dict) -> tuple[list[dict], list[dict]]:
    """Return (new_words, changes). Never mutates the input."""
    out = [dict(w) for w in words]
    changes: list[dict] = []
    idx = _word_indices(out)

    for fix in sorted(vocab["fixes"], key=lambda f: -len(f["heard"].split())):
        heard = fix["heard"].split()
        say = fix["say"].split()
        if len(heard) != len(say):
            print(f"  skip vocabulary fix (word count differs): {fix['heard']!r} -> {fix['say']!r}")
            continue
        n = len(heard)
        pos = 0
        while pos + n <= len(idx):
            window = idx[pos : pos + n]
            bare = [_split_punct(out[i]["text"])[0].lower() for i in window]
            if bare == [h.lower() for h in heard]:
                for k, i in enumerate(window):
                    _, punct = _split_punct(out[i]["text"])
                    new_text = say[k] + (punct if k == n - 1 else "")
                    if out[i]["text"] != new_text:
                        changes.append({"index": i, "old": out[i]["text"], "new": new_text, "by": "vocabulary"})
                        out[i] = {**out[i], "text": new_text}
                pos += n
            else:
                pos += 1

    caps = {c.lower(): c for c in vocab["always_capitalize"] if " " not in c}
    for i in idx:
        bare, punct = _split_punct(out[i]["text"])
        if bare.lower() in caps and bare != caps[bare.lower()]:
            new_text = caps[bare.lower()] + punct
            changes.append({"index": i, "old": out[i]["text"], "new": new_text, "by": "capitalize"})
            out[i] = {**out[i], "text": new_text}
    return out, changes


def apply_proposals(words: list[dict], proposals: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (new_words, applied, rejected). Never mutates the input."""
    out = [dict(w) for w in words]
    applied: list[dict] = []
    rejected: list[dict] = []
    for p in proposals:
        i, old, new = p.get("index"), p.get("old"), p.get("new")
        reason = None
        if not isinstance(i, int) or i < 0 or i >= len(out):
            reason = "index out of range"
        elif out[i].get("type") != "word":
            reason = "index is not a word"
        elif not isinstance(old, str) or out[i]["text"] != old:
            reason = f"old text mismatch (have {out[i].get('text')!r})"
        elif not isinstance(new, str) or not TOKEN_RE.match(new):
            reason = "new must be a single token without spaces"
        if reason:
            rejected.append({**p, "reason": reason})
            continue
        applied.append({"index": i, "old": old, "new": new, "by": "proofreader"})
        out[i] = {**out[i], "text": new}
    return out, applied, rejected


def rebuild_text(words: list[dict]) -> str:
    return " ".join(w["text"] for w in words if w.get("type") == "word")


def fix_one(
    transcript_path: Path,
    vocab: dict,
    proposals: list[dict] | None = None,
    dry_run: bool = False,
) -> dict:
    raw_dir = transcript_path.parent / "raw"
    raw_path = raw_dir / transcript_path.name
    log_path = raw_dir / f"{transcript_path.stem}.corrections.json"

    if raw_path.exists():
        base = json.loads(raw_path.read_text())
    else:
        base = json.loads(transcript_path.read_text())

    words, changes = apply_vocabulary(base.get("words", []), vocab)

    prior: list[dict] = []
    if log_path.exists():
        prior = [c for c in json.loads(log_path.read_text()).get("changes", []) if c.get("by") == "proofreader"]
    words, applied_prior, _ = apply_proposals(words, prior)
    changes += applied_prior

    rejected: list[dict] = []
    if proposals:
        words, applied, rejected = apply_proposals(words, proposals)
        changes += applied

    fixed = {**base, "words": words, "text": rebuild_text(words)}
    summary = {"file": transcript_path.name, "changes": changes, "rejected": rejected}

    if not dry_run:
        raw_dir.mkdir(parents=True, exist_ok=True)
        if not raw_path.exists():
            raw_path.write_text(json.dumps(base, indent=2, ensure_ascii=False))
        transcript_path.write_text(json.dumps(fixed, indent=2, ensure_ascii=False))
        log_path.write_text(json.dumps({"source": transcript_path.name, "changes": changes}, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply vocabulary and proofreader fixes to transcripts")
    ap.add_argument("--edit-dir", type=Path, required=True)
    ap.add_argument("--proposals", type=Path, default=None, help="JSON list of {index, old, new} from the proofreader")
    ap.add_argument("--source", type=str, default=None, help="Transcript stem the proposals apply to (required with --proposals)")
    ap.add_argument("--style", type=Path, default=BRAND_STYLE)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    transcripts_dir = args.edit_dir.resolve() / "transcripts"
    if not transcripts_dir.is_dir():
        sys.exit(f"no transcripts directory at {transcripts_dir}")
    if args.proposals and not args.source:
        sys.exit("--proposals needs --source <transcript stem>")

    vocab = load_vocabulary(args.style)
    proposals = json.loads(args.proposals.read_text()) if args.proposals else None
    if proposals is not None and not isinstance(proposals, list):
        sys.exit("proposals file must be a JSON list")

    targets = sorted(transcripts_dir.glob("*.json"))
    if args.source:
        targets = [t for t in targets if t.stem == args.source]
        if not targets:
            sys.exit(f"no transcript named {args.source}.json in {transcripts_dir}")

    for t in targets:
        summary = fix_one(t, vocab, proposals if t.stem == args.source else None, dry_run=args.dry_run)
        tag = "would change" if args.dry_run else "changed"
        print(f"{t.name}: {len(summary['changes'])} {tag}, {len(summary['rejected'])} rejected")
        for c in summary["changes"]:
            print(f"  [{c['index']}] {c['old']!r} -> {c['new']!r}  ({c['by']})")
        for r in summary["rejected"]:
            print(f"  x [{r.get('index')}] {r.get('old')!r} -> {r.get('new')!r}: {r['reason']}")


if __name__ == "__main__":
    main()
