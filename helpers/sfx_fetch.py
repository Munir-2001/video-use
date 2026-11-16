"""Fetch a sound effect from Openverse (free, no key, CC0 / CC BY only) into brand/sfx.

Openverse is a search API over openly licensed audio (most effects come from
Freesound). Nothing here is paid. Anonymous requests are rate-limited, which is
fine for a handful of cues per video.

Usage:
    python helpers/sfx_fetch.py "cash register" --as cash_register
    python helpers/sfx_fetch.py "page flip" --as page_flip --license cc0 --max-seconds 2
    python helpers/sfx_fetch.py "cash register" --dry-run      # list candidates only

Writes brand/sfx/extra_<name>.mp3 (48 kHz) and appends the attribution line to
brand/sfx/CREDITS.md. CC BY sounds need that credit in the video description;
the sound agent copies the line into edit/sound_report.json.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SFX_DIR = REPO / "brand" / "sfx"
CREDITS = SFX_DIR / "CREDITS.md"
API = "https://api.openverse.org/v1/audio/"
USER_AGENT = "video-studio-sfx-fetch/1.0 (local, personal use)"
ALLOWED_LICENSES = ("cc0", "by")  # never NC / SA / ND
DEFAULT_MAX_SECONDS = 6.0


def safe_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")[:40] or "sfx"


def search_url(query: str, licenses: tuple[str, ...], page_size: int = 20) -> str:
    # no `category` filter: Openverse leaves most Freesound effects uncategorised, so the filter returns nothing
    params = {"q": query, "license": ",".join(licenses), "page_size": str(page_size)}
    return API + "?" + urllib.parse.urlencode(params)


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (fixed https host)
        return json.loads(resp.read().decode("utf-8"))


def rank(results: list[dict], max_seconds: float) -> list[dict]:
    """Keep allowed licences and short clips, in Openverse's relevance order;
    CC0 before CC BY at equal relevance is not needed: order is kept, licence is
    recorded. Duration comes in milliseconds."""
    out = []
    for r in results:
        lic = (r.get("license") or "").lower()
        if lic not in ALLOWED_LICENSES or not r.get("url"):
            continue
        dur_ms = r.get("duration")
        if dur_ms is not None and dur_ms / 1000.0 > max_seconds:
            continue
        out.append(r)
    return out


def credit_line(r: dict, name: str) -> str:
    lic = (r.get("license") or "").upper()
    ver = r.get("license_version") or ""
    creator = r.get("creator") or "unknown"
    title = r.get("title") or r.get("id")
    link = r.get("foreign_landing_url") or r.get("url")
    tag = "CC0" if lic == "CC0" else f"CC {lic} {ver}".strip()
    return f"- `extra_{name}.mp3` — \"{title}\" by {creator}, {tag}, via Openverse: {link}"


def download_as_mp3(url: str, dest: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "raw"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp, open(raw, "wb") as f:  # noqa: S310
            f.write(resp.read())
        res = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ac", "2", "-ar", "48000",
                              "-b:a", "192k", str(dest)], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"ffmpeg could not convert the download: {res.stderr.strip()[-300:]}")


def append_credit(line: str, credits_path: Path = CREDITS) -> None:
    text = credits_path.read_text() if credits_path.exists() else "# SFX Credits\n"
    if line in text:
        return
    if "## Openverse" not in text:
        text = text.rstrip("\n") + "\n\n## Openverse (fetched by helpers/sfx_fetch.py)\n"
    credits_path.write_text(text.rstrip("\n") + "\n" + line + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch a CC0/CC BY sound effect from Openverse into brand/sfx")
    ap.add_argument("query", help='what the cue sounds like, e.g. "cash register"')
    ap.add_argument("--as", dest="name", default=None, help="file name (default: from the query) -> brand/sfx/extra_<name>.mp3")
    ap.add_argument("--license", choices=["cc0", "by", "cc0,by"], default="cc0,by")
    ap.add_argument("--max-seconds", type=float, default=DEFAULT_MAX_SECONDS)
    ap.add_argument("--pick", type=int, default=0, help="index in the ranked list (default 0)")
    ap.add_argument("--dry-run", action="store_true", help="list candidates, download nothing")
    args = ap.parse_args()

    name = safe_name(args.name or args.query)
    licenses = tuple(args.license.split(","))
    try:
        data = fetch_json(search_url(args.query, licenses))
    except Exception as exc:  # network, rate limit, bad JSON
        sys.exit(f"Openverse search failed ({exc}); use the bundled palette in brand/sfx instead")
    ranked = rank(data.get("results", []), args.max_seconds)
    if not ranked:
        sys.exit(f"no {args.license} sound under {args.max_seconds}s for {args.query!r}; try another wording or the bundled palette")
    for i, r in enumerate(ranked[:10]):
        dur = (r.get("duration") or 0) / 1000.0
        print(f"  [{i}] {dur:4.1f}s  {r.get('license','?').upper():<4} {r.get('title','')[:50]!r} by {r.get('creator','?')}")
    if args.dry_run:
        return
    pick = ranked[min(args.pick, len(ranked) - 1)]
    dest = SFX_DIR / f"extra_{name}.mp3"
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    download_as_mp3(pick["url"], dest)
    line = credit_line(pick, name)
    append_credit(line)
    print(f"saved {dest.relative_to(REPO)}  ({pick.get('license','').upper()})\n{line}")


if __name__ == "__main__":
    main()
