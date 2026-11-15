"""Transcribe a video locally with Parakeet (parakeet-mlx, Apple Silicon).

Extracts mono 16kHz audio via ffmpeg, runs NVIDIA Parakeet TDT 0.6B v3
through MLX on-device, and writes a Scribe-shaped JSON to
<edit_dir>/transcripts/<video_stem>.json:

    {
      "model": "...", "language_code": "...", "text": "...",
      "words": [
        {"type": "word",    "text": "Hello", "start": 0.16, "end": 0.48, "speaker_id": "S0"},
        {"type": "spacing", "text": " ",     "start": 0.48, "end": 0.56, "speaker_id": "S0"},
        ...
      ]
    }

Every gap between consecutive words gets a synthesized "spacing" entry so
pack_transcripts.py can break phrases on silence and render.py can chunk
captions. There is no diarization: speaker_id is always "S0". Parakeet
returns clean text (no um/uh) - cuts rely on silence gaps and repeats.

Cached: if the output file already exists, transcription is skipped.
No API key. Nothing leaves the machine.

Usage:
    python helpers/transcribe.py <video_path>
    python helpers/transcribe.py <video_path> --edit-dir /custom/edit
    python helpers/transcribe.py <video_path> --audio-track 1
"""

from __future__ import annotations

import argparse
import array
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


DEFAULT_MODEL = "mlx-community/parakeet-tdt-0.6b-v3"
SPEAKER_ID = "S0"
# Long takes are decoded in chunks so memory stays flat; overlap lets the
# library stitch the seams without dropping or doubling words.
CHUNK_DURATION_S = 120.0
CHUNK_OVERLAP_S = 15.0
SILENT_PEAK_DBFS = -60.0

_MODEL = None
_MODEL_LOCK = threading.Lock()
# MLX arrays are bound to the thread that created them, so every model call
# (load and inference) runs on this single worker thread. transcribe_batch.py
# still extracts audio in parallel; only the GPU work is serialized.
_INFERENCE_THREAD = ThreadPoolExecutor(max_workers=1, thread_name_prefix="parakeet")


def load_api_key() -> str:
    """Kept for transcribe_batch.py, which still imports and passes it.

    Parakeet runs locally; there is no key. Returns an empty string.
    """
    return ""


def model_id() -> str:
    return os.environ.get("PARAKEET_MODEL", DEFAULT_MODEL)


def _get_model():
    """Load the Parakeet model once per process. Call only on the inference thread."""
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is None:
            try:
                from parakeet_mlx import from_pretrained
            except ImportError as exc:  # pragma: no cover - environment error
                raise RuntimeError(
                    "parakeet-mlx is not installed. Run: uv pip install -r requirements-studio.txt "
                    f"(or pip install parakeet-mlx). Import error: {exc}"
                ) from exc
            _MODEL = from_pretrained(model_id())
        return _MODEL


def _transcribe_on_inference_thread(audio_path: Path):
    model = _get_model()
    return model.transcribe(
        str(audio_path),
        chunk_duration=CHUNK_DURATION_S,
        overlap_duration=CHUNK_OVERLAP_S,
    )


def count_audio_tracks(video_path: Path) -> int:
    """How many audio streams the container holds."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(video_path)],
        capture_output=True, text=True,
    )
    return len([ln for ln in out.stdout.splitlines() if ln.strip()])


def peak_dbfs(wav_path: Path) -> float:
    """Peak level of a 16-bit PCM wav, in dBFS. -inf for digital silence."""
    peak = 0
    with wave.open(str(wav_path), "rb") as w:
        while frames := w.readframes(1 << 16):
            samples = array.array("h", frames)
            peak = max(peak, max(samples), -min(samples))
    return 20 * math.log10(peak / 32768) if peak > 0 else float("-inf")


def extract_audio(video_path: Path, dest: Path, audio_track: int = 0) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-map", f"0:a:{audio_track}",
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _is_punctuation(text: str) -> bool:
    return bool(text) and not any(ch.isalnum() for ch in text)


def tokens_to_words(tokens: list) -> list[dict]:
    """Merge Parakeet sub-word tokens into word entries.

    A token whose text starts with a space begins a new word. Tokens without a
    leading space (sub-word pieces and punctuation) attach to the current word.
    Punctuation joins the word's text but does not extend its end time, so the
    silence after a sentence stays visible as a spacing gap.
    """
    words: list[dict] = []
    current: dict | None = None
    pending_break = False  # a whitespace-only token means "next token starts a word"

    def close() -> None:
        if current is not None and current["text"]:
            words.append(dict(current))

    for tok in tokens:
        text = tok.text
        if not text.strip():
            pending_break = True
            continue
        starts_word = text.startswith(" ") or pending_break or current is None
        pending_break = False
        piece = text.strip() if starts_word else text
        if starts_word and not _is_punctuation(piece):
            close()
            current = {
                "type": "word",
                "text": piece,
                "start": round(float(tok.start), 3),
                "end": round(float(tok.end), 3),
                "speaker_id": SPEAKER_ID,
            }
            continue
        if current is None:
            # Leading punctuation with no word yet: start a word anyway.
            current = {
                "type": "word",
                "text": piece,
                "start": round(float(tok.start), 3),
                "end": round(float(tok.end), 3),
                "speaker_id": SPEAKER_ID,
            }
            continue
        current = {**current, "text": current["text"] + piece}
        if not _is_punctuation(piece):
            current = {**current, "end": round(float(tok.end), 3)}
    close()
    return words


def interleave_spacing(words: list[dict]) -> list[dict]:
    """Insert a "spacing" entry between every pair of consecutive words."""
    out: list[dict] = []
    for i, w in enumerate(words):
        out.append(w)
        if i + 1 < len(words):
            nxt = words[i + 1]
            gap_start = w["end"]
            gap_end = max(nxt["start"], gap_start)
            out.append({
                "type": "spacing",
                "text": " ",
                "start": gap_start,
                "end": gap_end,
                "speaker_id": SPEAKER_ID,
            })
    return out


def run_parakeet(audio_path: Path) -> dict:
    """Transcribe a 16 kHz mono wav and return the Scribe-shaped payload."""
    result = _INFERENCE_THREAD.submit(_transcribe_on_inference_thread, audio_path).result()
    tokens = [tok for sentence in result.sentences for tok in sentence.tokens]
    words = tokens_to_words(tokens)
    return {
        "model": model_id(),
        "language_code": "auto",
        "text": result.text.strip(),
        "words": interleave_spacing(words),
    }


def transcript_path(edit_dir: Path, video: Path, audio_track: int = 0) -> Path:
    """Where a video's transcript lands (track 0 keeps the plain name)."""
    suffix = "" if audio_track == 0 else f".track{audio_track}"
    return edit_dir / "transcripts" / f"{video.stem}{suffix}.json"


def transcribe_one(
    video: Path,
    edit_dir: Path,
    api_key: str = "",
    language: str | None = None,
    num_speakers: int | None = None,
    verbose: bool = True,
    audio_track: int = 0,
) -> Path:
    """Transcribe a single video. Returns path to transcript JSON.

    Cached: returns existing path immediately if the transcript already exists.
    `api_key`, `language` and `num_speakers` are accepted for CLI/batch
    compatibility and ignored: Parakeet v3 auto-detects language and does not
    diarize.
    """
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcript_path(edit_dir, video, audio_track)

    if out_path.exists():
        if verbose:
            print(f"cached: {out_path.name}")
        return out_path

    if verbose:
        print(f"  extracting audio from {video.name}", flush=True)

    n_tracks = count_audio_tracks(video)
    if n_tracks > 1 and verbose:
        print(f"  note: {video.name} has {n_tracks} audio tracks, using track "
              f"{audio_track + 1} (--audio-track to change)", flush=True)

    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / f"{video.stem}.wav"
        extract_audio(video, audio, audio_track)

        peak = peak_dbfs(audio)
        if peak < SILENT_PEAK_DBFS:
            raise RuntimeError(
                f"track {audio_track + 1} of {video.name} is silent "
                f"(peak {peak:.1f} dBFS) - not transcribing. "
                + (f"The file has {n_tracks} audio tracks; try --audio-track "
                   + " or ".join(str(i) for i in range(n_tracks) if i != audio_track) + "."
                   if n_tracks > 1 else "Check the source audio.")
            )

        if verbose:
            print(f"  transcribing {video.stem}.wav with {model_id()}", flush=True)
        payload = run_parakeet(audio)

    payload = {**payload, "source": video.name, "audio_track": audio_track}
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    dt = time.time() - t0

    if verbose:
        kb = out_path.stat().st_size / 1024
        n_words = sum(1 for w in payload["words"] if w["type"] == "word")
        print(f"  saved: {out_path.name} ({kb:.1f} KB) in {dt:.1f}s")
        print(f"    words: {n_words}")

    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe a video locally with Parakeet (MLX)")
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument(
        "--edit-dir",
        type=Path,
        default=None,
        help="Edit output directory (default: <video_parent>/edit)",
    )
    ap.add_argument(
        "--language",
        type=str,
        default=None,
        help="Accepted for compatibility; Parakeet v3 auto-detects the language.",
    )
    ap.add_argument(
        "--num-speakers",
        type=int,
        default=None,
        help="Accepted for compatibility; Parakeet does not diarize (speaker_id is always S0).",
    )
    ap.add_argument(
        "--audio-track",
        type=int,
        default=0,
        help="Zero-based audio track to transcribe (OBS: 0 = game, 1 = mic).",
    )
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")

    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()

    transcribe_one(
        video=video,
        edit_dir=edit_dir,
        api_key=load_api_key(),
        language=args.language,
        num_speakers=args.num_speakers,
        audio_track=args.audio_track,
    )


if __name__ == "__main__":
    main()
