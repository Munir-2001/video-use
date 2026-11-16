"""Local studio dashboard: browse every video, its edit (EDL, scenes, captions,
sound, critic), the cards, the rules and the decisions. Leave timecoded notes
on a preview; they land in <video>/edit/feedback.json, which "apply my notes"
reads.

Pure stdlib. Serves studio/ (HTML/JS/CSS) plus a JSON API and media files
with HTTP Range support (video seeking in Safari/Chrome).

Usage:
    python helpers/studio_ui.py                 # http://127.0.0.1:8765
    python helpers/studio_ui.py --port 9000
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO = Path(__file__).resolve().parent.parent
STUDIO_DIR = REPO / "studio"
VIDEOS_DIR = REPO / "videos"
CARDS_DIR = REPO / "cards"
MEDIA_ROOTS = ("videos", "cards", "brand", "examples", "static")
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
PREVIEW_PRIORITY = ("final.mp4", "preview_mixed.mp4", "preview_subs.mp4", "preview.mp4")
THUMB_NAME = "thumb.jpg"
ASS_DIALOGUE = re.compile(r"^Dialogue:\s*\d+,([^,]+),([^,]+),[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,(.*)$")
ASS_HL = re.compile(r"\{\\c[^}]*\}(.*?)\{\\r\}")
ASS_TAGS = re.compile(r"\{[^}]*\}")
_PROBE_CACHE: dict[tuple[str, float], dict] = {}


# -------- parsing helpers (pure) --------------------------------------------


def ass_time_to_s(t: str) -> float:
    h, m, s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_ass_events(text: str) -> list[dict]:
    """Dialogue lines -> [{start, end, text, hl}] where hl is the highlighted word index."""
    events = []
    for line in text.splitlines():
        m = ASS_DIALOGUE.match(line.strip())
        if not m:
            continue
        raw = m.group(3)
        hl_match = ASS_HL.search(raw)
        hl_word = hl_match.group(1) if hl_match else None
        plain = ASS_TAGS.sub("", raw).strip()
        words = plain.split()
        hl = words.index(hl_word) if hl_word in words else -1
        events.append({"start": round(ass_time_to_s(m.group(1)), 3), "end": round(ass_time_to_s(m.group(2)), 3),
                       "text": plain, "hl": hl})
    return events


def parse_index(text: str) -> list[dict]:
    """videos/index.md lines `- YYYY-MM-DD · slug · status (note)` -> dicts."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        parts = [p.strip() for p in line[2:].split("·")]
        if len(parts) < 3:
            continue
        status, _, note = parts[2].partition("(")
        out.append({"date": parts[0], "slug": parts[1], "status": status.strip(), "note": note.rstrip(")").strip()})
    return out


def parse_card(text: str, path: Path) -> dict:
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), path.stem)
    fields = {}
    for key in ("kind", "from", "what", "use when", "avoid when", "prompt"):
        m = re.search(rf"\*\*{re.escape(key)}:\*\*\s*(.+)", text)
        fields[key.replace(" ", "_")] = m.group(1).strip() if m else ""
    return {"file": path.name, "title": title, **fields}


def parse_decisions(text: str, limit: int = 50) -> list[dict]:
    out = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        date, _, title = head.partition("·")
        out.append({"date": date.strip(), "title": title.strip(), "body": body.strip()})
        if len(out) >= limit:
            break
    return out


def parse_style_rules(text: str) -> list[dict]:
    out, section = [], ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.startswith("- "):
            m = re.match(r"- (.+?)\s*\((\d{4}-\d{2}-\d{2}) · (\w+)\)\s*$", line)
            if m:
                out.append({"section": section, "rule": m.group(1), "date": m.group(2), "origin": m.group(3)})
            else:
                out.append({"section": section, "rule": line[2:].strip(), "date": "", "origin": ""})
    return out


def read_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text()) if path.exists() else None
    except json.JSONDecodeError:
        return {"_error": f"invalid JSON: {path.name}"}


# -------- media probing -----------------------------------------------------


def probe(path: Path) -> dict:
    key = (str(path), path.stat().st_mtime)
    if key in _PROBE_CACHE:
        return _PROBE_CACHE[key]
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height,r_frame_rate:format=duration,size", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=20).stdout
        data = json.loads(out or "{}")
        st = (data.get("streams") or [{}])[0]
        fr = st.get("r_frame_rate", "0/1")
        num, _, den = fr.partition("/")
        fps = round(int(num) / max(1, int(den or 1)), 2) if num.isdigit() else 0
        info = {"width": st.get("width"), "height": st.get("height"), "fps": fps,
                "duration": round(float(data.get("format", {}).get("duration", 0) or 0), 2),
                "size_mb": round(int(data.get("format", {}).get("size", 0) or 0) / 1048576, 1)}
    except Exception as exc:  # ffprobe missing or file unreadable
        info = {"error": str(exc)[:120]}
    _PROBE_CACHE[key] = info
    return info


def ensure_thumb(video: Path, edit_dir: Path) -> Path | None:
    thumb = edit_dir / THUMB_NAME
    if thumb.exists() and thumb.stat().st_mtime >= video.stat().st_mtime:
        return thumb
    edit_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", str(video), "-frames:v", "1",
                        "-vf", "scale=480:-2", str(thumb)], check=True, timeout=30, capture_output=True)
        return thumb
    except Exception:
        return None


# -------- scanning ----------------------------------------------------------


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def scan_video(folder: Path, index: dict[str, dict]) -> dict:
    edit = folder / "edit"
    clips = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
    preview = next((edit / n for n in PREVIEW_PRIORITY if (edit / n).exists()), None)
    date, _, slug = folder.name.partition("_")
    meta = index.get(slug) or index.get(folder.name) or {}
    thumb_src = preview or (clips[0] if clips else None)
    thumb = ensure_thumb(thumb_src, edit) if thumb_src else None
    edl = read_json(edit / "edl.json")
    return {
        "folder": folder.name, "date": date, "slug": slug or folder.name,
        "status": meta.get("status", "raw" if clips else "empty"), "note": meta.get("note", ""),
        "clips": [{"name": c.name, "url": "/media/" + rel(c), **probe(c)} for c in clips],
        "preview": "/media/" + rel(preview) if preview else None,
        "preview_name": preview.name if preview else None,
        "thumb": "/media/" + rel(thumb) if thumb else None,
        "duration": (edl or {}).get("total_duration_s") if isinstance(edl, dict) else None,
        "has": {n: (edit / n).exists() for n in ("edl.json", "scenes.json", "sound.json", "sound_report.json",
                                                    "master.ass", "critic.md", "project.md", "feedback.json",
                                                    "takes_packed.md")},
    }


def scan_videos() -> list[dict]:
    if not VIDEOS_DIR.is_dir():
        return []
    index_text = (VIDEOS_DIR / "index.md").read_text() if (VIDEOS_DIR / "index.md").exists() else ""
    index = {e["slug"]: e for e in parse_index(index_text)}
    folders = sorted((p for p in VIDEOS_DIR.iterdir() if p.is_dir()), reverse=True)
    return [scan_video(f, index) for f in folders]


def video_detail(folder_name: str) -> dict | None:
    folder = VIDEOS_DIR / folder_name
    if not folder.is_dir() or ".." in folder_name:
        return None
    edit = folder / "edit"
    base = scan_video(folder, {e["slug"]: e for e in parse_index((VIDEOS_DIR / "index.md").read_text())}
                      if (VIDEOS_DIR / "index.md").exists() else {})
    ass = (edit / "master.ass").read_text() if (edit / "master.ass").exists() else ""
    animations = []
    if (edit / "animations").is_dir():
        for slot in sorted(p for p in (edit / "animations").iterdir() if p.is_dir()):
            render = next((slot / n for n in ("render.mov", "render.mp4", "render.webm") if (slot / n).exists()), None)
            animations.append({"slot": slot.name,
                               "render": "/media/" + rel(render) if render else None,
                               "landing": "/media/" + rel(slot / "landing.png") if (slot / "landing.png").exists() else None,
                               "reasoning": (slot / "reasoning.md").read_text() if (slot / "reasoning.md").exists() else ""})
    return {
        **base,
        "edl": read_json(edit / "edl.json"),
        "scenes": read_json(edit / "scenes.json"),
        "sound": read_json(edit / "sound.json"),
        "sound_report": read_json(edit / "sound_report.json"),
        "captions": parse_ass_events(ass),
        "critic": (edit / "critic.md").read_text() if (edit / "critic.md").exists() else "",
        "project": (edit / "project.md").read_text() if (edit / "project.md").exists() else "",
        "takes_packed": (edit / "takes_packed.md").read_text() if (edit / "takes_packed.md").exists() else "",
        "feedback": read_json(edit / "feedback.json") or {"notes": []},
        "animations": animations,
    }


def scan_cards() -> list[dict]:
    if not CARDS_DIR.is_dir():
        return []
    return [parse_card(p.read_text(), p) for p in sorted(CARDS_DIR.glob("*.md")) if not p.name.startswith("_")]


def state() -> dict:
    style = (REPO / "STYLE.md").read_text() if (REPO / "STYLE.md").exists() else ""
    decisions = (REPO / "DECISIONS.md").read_text() if (REPO / "DECISIONS.md").exists() else ""
    how = (REPO / "HOW_IT_WORKS.md").read_text() if (REPO / "HOW_IT_WORKS.md").exists() else ""
    return {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "videos": scan_videos(), "cards": scan_cards(), "style": parse_style_rules(style),
            "decisions": parse_decisions(decisions), "how": how,
            "inbox": sorted(p.name for p in (CARDS_DIR / "_inbox").iterdir() if p.is_file() and p.name != "links.md")
            if (CARDS_DIR / "_inbox").is_dir() else []}


def write_feedback(folder_name: str, notes: list[dict]) -> Path:
    if ".." in folder_name or "/" in folder_name:
        raise ValueError("bad folder")
    edit = VIDEOS_DIR / folder_name / "edit"
    edit.mkdir(parents=True, exist_ok=True)
    clean = []
    for n in notes:
        t = float(n.get("t", 0))
        text = str(n.get("text", "")).strip()[:2000]
        if text:
            clean.append({"t": round(max(0.0, t), 3), "text": text, "created": n.get("created") or
                          datetime.now(timezone.utc).isoformat(timespec="seconds"), "done": bool(n.get("done", False))})
    path = edit / "feedback.json"
    path.write_text(json.dumps({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "notes": clean},
                               indent=2, ensure_ascii=False))
    return path


# -------- HTTP --------------------------------------------------------------


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STUDIO_DIR), **kw)

    def log_message(self, fmt, *args):  # quieter
        if "/media/" not in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def send_json(self, obj, status=HTTPStatus.OK):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)
        if path == "/api/state":
            return self.send_json(state())
        if path.startswith("/api/video/"):
            d = video_detail(path[len("/api/video/"):])
            return self.send_json(d if d else {"error": "not found"}, HTTPStatus.OK if d else HTTPStatus.NOT_FOUND)
        if path.startswith("/media/"):
            return self.serve_media(path[len("/media/"):])
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        if path.startswith("/api/feedback/"):
            try:
                out = write_feedback(path[len("/api/feedback/"):], body.get("notes", []))
            except ValueError as exc:
                return self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return self.send_json({"ok": True, "file": rel(out)})
        return self.send_json({"error": "unknown endpoint"}, HTTPStatus.NOT_FOUND)

    def serve_media(self, relpath: str):
        target = (REPO / relpath).resolve()
        if not str(target).startswith(str(REPO)) or relpath.split("/")[0] not in MEDIA_ROOTS or not target.is_file():
            return self.send_json({"error": "forbidden"}, HTTPStatus.FORBIDDEN)
        size = target.stat().st_size
        ctype = self.guess_type(str(target))
        if target.suffix.lower() == ".mov":
            ctype = "video/quicktime"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng and rng.startswith("bytes="):
            a, _, b = rng[6:].partition("-")
            start = int(a) if a else max(0, size - int(b))
            end = int(b) if (b and a) else size - 1
            end = min(end, size - 1)
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with open(target, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = f.read(min(1 << 20, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                remaining -= len(chunk)


def main() -> None:
    ap = argparse.ArgumentParser(description="Serve the studio dashboard")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"studio dashboard: {url}  (repo: {REPO})")
    if not args.no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
