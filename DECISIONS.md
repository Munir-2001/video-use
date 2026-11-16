# DECISIONS.md

Append-only, newest first. Format: `## date · title` then Why / Trade-off / Alternatives / Status.

## 2026-11-16 · Principle: Claude edits, helpers execute (and the one gap closed: cue grouping)
**Why:** My rule: the videos are edited by Claude, not by scripts; scripts are tools that agents use. Audit of the helpers: `render.py`, `sound_mix.py`, `voiceover.py build`, `fix_transcript.py`, `transcribe*.py`, `studio_ui.py` are deterministic executors of decisions written by agents (`edl.json` by the editor, `scenes.json` by the planner, `sound.json` by the sound agent, `brief.json` by me). The one helper that was still deciding something editorial was `captions_ass.py`, whose 2–3 word grouping is a rule, not a judgment. Now the captions agent reviews the cues and may write `edit/captions_plan.json` (explicit word-index cues with optional presets); the helper draws exactly that. `--dump-words` prints the indexed word list to plan from. The principle is one line in CLAUDE.md. The two smoke folders have hand-written `edl.json`/`scenes.json` as stand-ins; real videos never do.
**Trade-off:** One more file the captions agent may write; the automatic grouping stays as the starting point so simple videos cost nothing extra.
**Alternatives:** Let the agent emit the .ass directly (loses the brand motion and layout code), keep the rule-based grouping as final (contradicts the principle).
**Status:** done; tested.

## 2026-11-16 · Openverse for extra sound effects; a writer agent so the script shapes the edit
**Why:** The bundled palette has no cue for things like a cash register. `helpers/sfx_fetch.py` searches Openverse (free, no key, CC0 / CC BY only, sound_effect category, ≤ 6 s), downloads one match as 48 kHz mp3 into `brand/sfx/extra_<name>.mp3` and appends the attribution to CREDITS.md; the sound agent may fetch at most two per video and copies credits into `sound_report.json`. Music generation (MusicGen) was offered and declined for now: I drop a track myself. Second: the user's workflow starts with a script, not a clip. A **writer** agent (opus) writes `script.md` with the hook, named beats pre-mapped to cards and layouts, the CTA and recording notes, so the recording already contains the beats the planner needs and the pauses the editor cuts on.
**Trade-off:** Openverse anonymous rate limits are low but enough; CC BY sounds need the credit in the description. The script is a plan, not a contract: the transcript decides the real timings.
**Alternatives:** HeyGen catalogue (cloud sign-in, excluded), generating effects (none of the local tools do it), writing scripts in chat without a file (nothing for the planner to read).
**Status:** done; sfx_fetch verified live on "cash register".

## 2026-11-16 · Brand assets in place: fonts (Inter, JetBrains Mono, Instrument Serif) and the sfx palette
**Why:** Captions and PIL cards were falling back to Helvetica and the sound agent had no effects. Fonts downloaded from their official repos (rsms/inter 4.1 static TTFs, JetBrains Mono 2.304, Instrument Serif from google/fonts), all OFL, licences alongside; `brand/style.json` gains a `serif` entry for the one italic accent word in editorial cards. The 19 Pixabay effects bundled with the HyperFrames media-use skill are copied into `brand/sfx/` under the palette names (whoosh_short/long, click, tick, pop, soft_impact, riser, ding) plus `extra_*` for typing, sparkle, chime, glitch, bass hit; Pixabay licence, CREDITS.md kept.
**Trade-off:** Assets are tracked in git (≈ 2.5 MB) so a fresh clone works; no music yet, because picking a track is my call (drop one into `brand/music/`).
**Alternatives:** System fonts (not Inter on every machine), freesound.org per effect (licence per file).
**Status:** done; captions re-burned with Inter on the smoke clip.

## 2026-11-16 · Palette decided (Paper & Flame); captions stay 2–3 words, bigger for hook/CTA; screen windows get zoom beats
**Why:** I asked for one recognisable palette and said 2–3 words per cue, kept big, is the look I want, and described the move I want in explainers: a live window above my head with the screen moving inside, and on the word that names something the view inside the window pushes in on it. Palette: paper #F3EEE4 panels with ink #141418 text, flame #F4502A as the only accent, cobalt #1F5BFF for a second emphasis, near-black for full-frame cards; caption highlight is the flame too. Every card's hex codes were swapped; `icon-grid-chapters` defaults to the paper panel. Captions: the `giant` preset becomes `big` (2–3 words, 120 px, y 0.64); STYLE.md now says one word per cue is never used, and has a Palette line. Screen windows: `window-mockup-slide-up` gains a live-screen variant with `zoom_beats`; the planner writes `graphic.kind = "screen_window"` + `footage` + `zoom_beats` (box per named element), the motion agent animates the inner view in HyperFrames (350 ms push-in, accent ring, ease back) while the frame and my face stay still.
**Trade-off:** Orange is what both references use, so it is not unique on its own; the paper panel + ink + flame combination and the fixed layout grammar are what make the reels recognisable. Zoom boxes need the planner to look at a frame of the recording, which costs a little time per beat.
**Alternatives:** Yellow on dark (the designer's first guess; cold), one-word captions (I rejected them), zooming the whole frame (banned: my face never zooms).
**Status:** done; the studio dashboard keeps its own dark theme for now.

## 2026-11-16 · Cards and motion timings measured from a real reference reel (designer run)
**Why:** First reference as video, not stills: a 15 s "50 free backlinks" reel plus a 9-slide dark editorial carousel. The designer measured at 24 fps: card pop 170 ms, item swap 250 ms (old card up 60 px + fade, new rises into place), small fades 125 ms, grid morph 250 ms, typing ≈ 24 chars/s following the speech, panel edge at exactly y 0.50, split captions at y 0.465, giant word ≈ 150 px at y 0.64 with the CTA pill at 0.715; face size changes only by hard-cut reframe; fast list reels change something every 0.6–1.5 s; the reel loops by cutting back to its first frame. `brand/motion.md` lines moved from (assumed) to (seen); `brand/style.json` gains `motion.pop_ms/swap_ms/fade_ms` and the measured split_top / giant numbers. Cards: new `icon-grid-chapters` (split-top panel, number of tiles → grid, chapter header with dimmed grid, item card pop/swap, loop ending) and `giant-word-cta-caption`; merged chat-box typing into `prompt-card-on-colour`, the dark editorial title/end card into `kinetic-title-accent-word`, and `beat-map-sheet` into `two-panel-compare-counter` to stay at the 12-card cap. STYLE.md gains a dated exception line for the split and giant caption styles.
**Trade-off:** The reference is orange on a light panel; the cards are written in the brand's yellow-on-dark with a light variant noted. The palette is still my call (see the open question in chat). The brand has no serif face, so the carousel's italic serif line is weight/colour contrast until a serif is added.
**Alternatives:** Keep the reference's exact look (someone else's identity), more cards than 12 (dilutes the planner's choices).
**Status:** done; drops deleted from the inbox; not yet used in a real edit.

## 2026-11-16 · split_top layout, caption presets, per-stretch caption styles (from the backlinks reel reference)
**Why:** The reference reel uses one layout almost throughout: a graphic panel in the top ~47 % of the 9:16 frame with the speaker below, small captions at the panel's bottom edge, and, when the face goes full frame, one giant word per cue with a CTA pill. One caption style per video cannot do that. `brand/style.json` gains layout `split_top` (panel top 0.47, its own caption block) and `captions.presets` (`giant`: 1 word per cue, 140 px, y 0.68; `panel`). `captions_ass.py` reads `edit/scenes.json` automatically: words are grouped per stretch and each stretch's words-per-cue / size / band come from its `caption` preset or its layout, written as per-event ASS overrides. `voiceover.py` anchors footage at the bottom for split_top stretches. The planner may set `"caption": "giant"` on a stretch.
**Trade-off:** Per-stretch styles regroup cues at stretch boundaries, so the planner should start stretches on sentence boundaries. The panel itself (dot grid, title) is a motion-agent graphic, not drawn by the caption layer.
**Alternatives:** Two caption files per video (messy), styling captions in HyperFrames (a second render), one global giant mode (unreadable on long sentences).
**Status:** done; verified on the voice-over smoke clip (giant word at 0.68, panel line at 0.44, footage anchored low).

## 2026-11-16 · Motion grammar: the references are a moving video, so cards describe motion, not layouts
**Why:** My reminder: the 26 reference frames are stills of animated explainers; what makes them engaging is the movement (titles landing word by word, step cards filling on beats, rails gaining checks, counters ticking, hard cuts onto colour) and the diagrams building piece by piece. `brand/motion.md` now holds the shared grammar (build / hold / change every ≤ 3 s / exit on a word boundary; enter and exit per element type; what stays still; the engagement rhythm for a 30–60 s explainer), with each line marked (seen) from the frame sequence or (assumed) until a screen recording is measured. The designer orders frames by the player timecode to read builds, measures real recordings at 8 fps, and must write trigger / enter / hold changes / exit / what-stays-still into every card. The planner writes `beats` (the spoken words on which each graphic changes) into each brief; the motion agent lands a visible change on every beat and extracts a frame per beat; the critic fails any graphic that is static for 3 s or lands a change > 150 ms off its beat.
**Trade-off:** Stills cannot give exact durations; the (assumed) values are brand defaults until a reference recording is dropped. More checks for the critic means slightly longer QC.
**Alternatives:** Download the reference video (not done: dependency and terms), per-card motion only (no shared rhythm), trusting the model's defaults (produces static slides).
**Status:** done; no card rewritten yet, the designer applies this on the next "process the inbox" and when writing new cards.

## 2026-11-16 · Separate voice recordings: upload in the studio, two modes, voice master built by ffmpeg
**Why:** I record commentary on my phone as an MP3 and shoot the clips separately. The studio Library now has a "New video" form (clips + voice files + mode + offset + notes) posting to `POST /api/upload[/<folder>]`, parsed by a 30-line multipart reader (stdlib `cgi` is gone in Python 3.13); clips land at the folder top level (upstream layout), recordings in `voice/`, and `edit/brief.json` records the relationship. Two modes. **voiceover**: the recording is the timeline: `voiceover.py transcribe` makes the voice words part of the inventory, the editor cuts the voice, the planner names a clip and in-point per stretch, and `voiceover.py build` renders `voice_master.mp4` (footage segments, background in gaps, cut voice) plus `edl_master.json` for render.py, so overlays, captions, mix and critic run unchanged. **commentary**: the clip is the timeline and keeps its sound; `sound_mix.py` gets a `voice` entry (delay to offset, clip ducked under the voice) and `captions_ass.py --words-from --offset` captions my words.
**Trade-off:** Uploads are read into memory (cap 4 GB), fine on a local Mac. The voice master is an intermediate re-encode (libx264 CRF 18) before render.py re-encodes again; acceptable for reels, revisit for long videos. No automatic clip-to-sentence matching: the planner decides from `brief.notes`.
**Alternatives:** Multi-source EDL ranges with separate audio (would change upstream render.py, which is off limits), a drop folder watcher (no feedback, no metadata), HyperFrames `<audio>` tracks (would move the cut out of the EDL).
**Status:** done; unit-tested; smoke-tested on the test clip with its own audio exported as a voice file.

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
