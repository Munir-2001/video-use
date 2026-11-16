# DECISIONS.md

Append-only, newest first. Format: `## date · title` then Why / Trade-off / Alternatives / Status.

## 2026-11-16 · Captions: bigger and moving (word pop + cue rise), still pure ASS
**Why:** My note on the first composited frame: the title at the top works as a hook, and the captions should be bigger with moving words, like the reference. `brand/style.json` → captions 96 px on 1080x1920 (80 px on 1080p) and a `motion` block: the spoken word pops from 86 % to 112 % in 120 ms, each cue rises 28 px with an 80 ms fade. `captions_ass.py` writes these as ASS `\t`, `\move`, `\fad` tags, so libass animates them during the burn-in: no extra render pass, no HyperFrames for captions. WrapStyle 0 so a long cue wraps to two lines instead of overflowing at the bigger size.
**Trade-off:** ASS motion is limited to scale, position and alpha; a card-style caption (white card beside the face) stays a planner graphic. Pop and rise values are brand settings, not per video.
**Alternatives:** HyperFrames caption groups (deterministic but a second render per video), Remotion (no).
**Status:** done; re-burned on the test clip.

## 2026-11-16 · Captions move from the middle band to under the chin; "catchy text" is a separate title layer
**Why:** On the test clip the middle-band rule put the caption across my nose. For TikTok/Instagram the readable, non-blocking spot is the lower band: centre ≈ 68 % down (HyperFrames' own guidance says 600–700 px from the bottom on 1080x1920), above the bottom 20 % platform UI and ≥ 140 px clear on the right. `brand/style.json` → `captions.position.vertical.y_fraction = 0.68`, `band = [0.64, 0.72]`; `captions_ass.py --y-fraction` overrides per video when a clip is framed low. Every card that reserved "y 0.42–0.58" now reserves 0.64–0.72 (milestone rail moved to 0.56, step grid to 0.18–0.62, third comment chip to 0.46). The 26 reference frames show that "catchy" text is not the subtitle: it is a 2–4 word kinetic title with one accent word, or a card beside the face. Those stay in the planner → motion layer (cards `kinetic-title-accent-word`, `caption-card-beside-face`); captions are the readability layer and never repeat the title's words while it is up.
**Trade-off:** A fixed band assumes a centred head. No face detection yet; the critic extracts frames and flags occlusion, and `--y-fraction` is the manual fix. If it comes up repeatedly, add a free local face box (OpenCV Haar) to the pre-scan.
**Alternatives:** Keep the middle band (blocks the face), bottom of frame (hidden by the TikTok caption/progress UI), per-word face tracking (overkill for single-head clips).
**Status:** done; STYLE.md Captions rules updated; verified by re-burning the test clip. Same commit: first real HyperFrames render (`edit/animations/title-01/`, ProRes 4444 alpha, 5.7 s) composited through `render.py` overlays; `motion.md` now records the gotchas (px not em, absolute `-o`, pix_fmt 12le, overlay size = base size).

## 2026-11-16 · Studio dashboard: local, stdlib server, vanilla JS, no Framer Motion
**Why:** I want to see every video, its cut, scenes, captions, sound and critic verdict in one place, and leave timecoded notes. `helpers/studio_ui.py` scans the repo and serves `studio/` on 127.0.0.1:8765 with a JSON API and Range-capable media; notes save to `videos/<folder>/edit/feedback.json`, which "apply my notes" reads.
**Trade-off:** No React/Framer Motion. Framer Motion is a React UI-animation library; it would add Node tooling and a build step to a read-mostly dashboard, and it cannot render video deterministically (that is HyperFrames' job). Micro-animations are CSS. If the UI grows (editing EDLs in place), revisit with Vite + React.
**Alternatives:** Next.js app (heavy), Streamlit (Python, but ugly timelines), static HTML export (no notes).
**Status:** done; tested in Chrome on the test clip.

## 2026-11-16 · Model routing: Sonnet executes, Opus/Fable plans
**Why:** My rule: the editing work runs on Sonnet; planning and judgment run on the bigger models. `editor`, `motion`, `captions`, `sound` → `model: sonnet`. `planner`, `designer`, `critic` → `model: opus`. `proofreader` → `haiku`. The main session (Fable) does inventory, conversation, strategy and orchestration.
**Trade-off:** Take selection on Sonnet is cheaper and fast; if its EDLs need too many critic fixes, move `editor` to opus.
**Alternatives:** Everything on the main model (slow, costly); everything on Sonnet (critic too soft).
**Status:** done.

## 2026-11-16 · Agents written; captions as .ass; sound mixed by helper; ffmpeg needs libass
**Why:** Eight agents in `.claude/agents/` (editor, planner, motion, captions, sound, designer, critic, proofreader). Two new helpers make the mechanical agents deterministic: `helpers/captions_ass.py` (word-synced karaoke .ass, one event per word) and `helpers/sound_mix.py` (attack-offset effects, sidechain duck, two-pass loudnorm, measured report). `helpers/render.py` got one minimal change: an `.ass` subtitles file is burned without `force_style` and with `fontsdir=brand/fonts`.
**Trade-off:** Homebrew's default `ffmpeg` formula on this Mac is built without libass, so no caption burn-in works (upstream `.srt` included). Fix: `brew install ffmpeg-full` (keg-only; `/opt/homebrew/opt/ffmpeg-full/bin` first on PATH via `source .envrc.studio`). Installed 2026-11-16; burn-in verified on the test clip.
**Alternatives:** HyperFrames-rendered caption overlays (no libass needed) — kept as fallback if ffmpeg-full is refused.
**Status:** done; captions burn in with brand placement.

## 2026-11-16 · Transcript fixer: vocabulary list first, then one cheap Haiku pass
**Why:** Parakeet mis-hears proper nouns ("Muni Rabasi", "clot code"). Captions must show the right names. A deterministic vocabulary list in `brand/style.json` catches the known ones for free; a Haiku sub-agent catches the rest cheaply.
**Trade-off:** A model pass can over-correct. Guard rails: text-only swaps, word count unchanged, proper nouns and homophones only, corrections written to a side file, raw transcript never modified.
**Alternatives:** No fixing (wrong names in captions); a bigger model (costlier, same guard rails needed).
**Status:** planned for step 4 as `helpers/fix_transcript.py` + captions agent step.

## 2026-11-16 · Deferred items
- **DeepFilterNet denoise:** skipped. No prebuilt wheel for Python 3.13 on Apple Silicon; needs a Rust toolchain. Fallback if needed: ffmpeg `afftdn` behind a `--denoise` flag. Status: deferred.
- **Speaker diarization:** Parakeet does not diarize; every word is `S0`. Fine for single-head clips, which is all I make. Status: accepted.
- **HeyGen cloud features** inside the installed `media-use` skill: never used (paid). Status: excluded by rule.

## 2026-11-16 · Sub-agent roster (editor, planner, motion, captions, sound, designer, critic)
**Why:** One main session that does everything loses context on long edits. Seven narrow agents with written briefs, run in a fixed order, keep each step auditable (EDL, scenes.json, sound.json, master.ass, reasoning.md).
**Trade-off:** More files, more hand-offs. Accepted because every hand-off is a reviewable artifact.
**Alternatives:** Upstream's single editor + critic pair.
**Status:** planned for step 4 as `.claude/agents/<name>.md`.

## 2026-11-16 · Studio structure on top of an untouched upstream
**Why:** I want to pull upstream improvements later. All studio files are additions (`CLAUDE.md`, `STYLE.md`, `brand/`, `cards/`, `examples/`, `videos/`, `.claude/agents/`); upstream files change only where transcription or `.ass` captions require it.
**Trade-off:** `pyproject.toml` stays untouched, so studio Python deps live in `requirements-studio.txt` and must be installed separately after `uv sync`.
**Alternatives:** Edit upstream freely (merge conflicts later).
**Status:** done.

## 2026-11-16 · HyperFrames for animations, telemetry disabled
**Why:** HyperFrames renders HTML/CSS (GSAP, Lottie) to video locally and supports transparent overlays, which the motion agent needs for graphics over my face. Installed via `npx skills add heygen-com/hyperframes`.
**Trade-off:** The CLI sends usage telemetry by default. Disabled with `npx hyperframes telemetry disable`; `HYPERFRAMES_NO_TELEMETRY=1` is the env fallback. The skill files also ask agents to send "usage beacons" and feedback reports; the motion agent is told not to.
**Alternatives:** Remotion (React, heavier), Manim (vendored upstream, math-flavoured), PIL+ffmpeg (used for simple cards).
**Status:** done.

## 2026-11-16 · Parakeet (parakeet-mlx) replaces ElevenLabs Scribe
**Why:** Free, local, no key. Model `mlx-community/parakeet-tdt-0.6b-v3`; ~2 s per 30 s clip on this Mac after a one-time 1.2 GB download.
**Trade-off:** No diarization (speaker_id always `S0`), no filler words (clean text), 80 ms timestamp resolution. `helpers/transcribe.py` writes the exact Scribe JSON shape with synthesized `spacing` gaps so `pack_transcripts.py` and `render.py` work unchanged. MLX arrays are thread-bound, so inference runs on one dedicated thread; `transcribe_batch.py` still extracts audio in parallel.
**Alternatives:** whisper.cpp / mlx-whisper (slower, phrase-first), hosted Scribe (paid).
**Status:** done, tested on a real 31 s clip.

## 2026-11-16 · Fork browser-use/video-use as the base
**Why:** It already has the right shape: transcript → packed takes → EDL → per-segment render → captions last, with hard production rules written down.
**Trade-off:** Opinionated upstream; I keep my changes additive to stay mergeable.
**Alternatives:** Build from scratch; a GUI editor with an API.
**Status:** done. Fork at github.com/Munir-2001/video-use, upstream remote kept.
