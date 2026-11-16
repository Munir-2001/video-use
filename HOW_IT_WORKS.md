# HOW_IT_WORKS.md — one video, start to finish

| # | I say / it does | File produced |
|---|---|---|
| 1 | I drop clips into `videos/2026-11-16_first-reel/` and add a line to `videos/index.md` (status: `raw`). | — |
| 1b | Or upload from the studio (“New video”): clips land at the folder top level, recordings in `voice/`, and `edit/brief.json` records the mode (voiceover / commentary / clips), the offset and my notes. | `edit/brief.json`, `videos/index.md` line |
| 2 | **"edit videos/2026-11-16_first-reel"** — inventory: ffprobe each clip, `transcribe_batch.py`, `pack_transcripts.py`, `fix_transcript.py` (vocabulary), **proofreader** (Haiku) → `fix_transcript.py --proposals`. | `edit/transcripts/*.json` (fixed; raw copy in `transcripts/raw/`), `edit/takes_packed.md`, `edit/proofread.json` |
| 3 | Pre-scan: slips, repeats, must-avoid phrasings listed. Then it describes what it sees and asks 2–4 questions shaped by the footage. | — |
| 4 | Strategy in 4–8 sentences. **It waits. I say "yes" (or change it).** | — |
| 5 | **editor** picks takes and cut ranges from `takes_packed.md`. | `edit/edl.json` |
| 6 | **planner** decides what is on screen per stretch and which motion card each graphic uses. | `edit/scenes.json` |
| 6b | Voice files? `voiceover.py transcribe` ran at inventory; in **voiceover** mode the editor cut the voice and the planner put `footage` under every stretch, so `voiceover.py build` renders the footage track under the cut voice. | `edit/voice_master.mp4`, `edit/edl_master.json` |
| 7 | **motion** ×N in parallel (one per slot) + **captions** + **sound** run together. | `edit/animations/slot_<id>/render.*` + `reasoning.md`, `edit/master.ass` (lower band on vertical, under the chin), `edit/sound.json` + mixed audio |
| 8 | `render.py --preview --no-loudnorm` composites: segments → overlays → captions last. Then `sound_mix.py --mux` adds the mix. | `edit/preview.mp4`, `edit/mix.wav`, `edit/sound_report.json`, `edit/preview_mixed.mp4` |
| 9 | **critic** checks every cut, caption occlusion, overlay timing, levels, readability, STYLE.md. Verdict + ranked fixes. Fix loop, max 3 passes. | `edit/critic.md` |
| 10 | I see the preview, EDL, scenes.json and verdict, in chat or in the dashboard (**"open the studio"**). I give notes in chat or pin them to timecodes in the dashboard. | `edit/feedback.json` (from the dashboard) |
| 11 | **"apply my notes"** — notes to `edit/feedback.json`, EDL/scenes updated, only changed scenes re-rendered, critic again. | `edit/feedback.json`, new `edit/preview.mp4` |
| 12 | I say "final". Full-res render, loudnorm pass. | `edit/final.mp4` |
| 13 | Persist: session appended to `edit/project.md`, approved EDL copied to `examples/`, `videos/index.md` status → `done`, commit. | `edit/project.md`, `examples/<slug>.edl.json` |

Side loops: **"process the inbox"** turns `cards/_inbox/` drops into `cards/*.md`. **"learn from my reviews"** proposes STYLE.md lines from repeated notes. **"where are we?"** = this table in 5 lines + last 3 decisions + `videos/index.md`.
