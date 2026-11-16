# HOW_IT_WORKS.md — one video, start to finish

| # | I say / it does | File produced |
|---|---|---|
| 1 | I drop clips into `videos/2026-11-16_first-reel/` and add a line to `videos/index.md` (status: `raw`). | — |
| 2 | **"edit videos/2026-11-16_first-reel"** — inventory: ffprobe each clip, `transcribe_batch.py`, `pack_transcripts.py`, `fix_transcript.py` (vocabulary + Haiku pass). | `edit/transcripts/*.json`, `edit/takes_packed.md`, `edit/transcripts/*.corrections.json` |
| 3 | Pre-scan: slips, repeats, must-avoid phrasings listed. Then it describes what it sees and asks 2–4 questions shaped by the footage. | — |
| 4 | Strategy in 4–8 sentences. **It waits. I say "yes" (or change it).** | — |
| 5 | **editor** picks takes and cut ranges from `takes_packed.md`. | `edit/edl.json` |
| 6 | **planner** decides what is on screen per stretch and which motion card each graphic uses. | `edit/scenes.json` |
| 7 | **motion** ×N in parallel (one per slot) + **captions** + **sound** run together. | `edit/animations/slot_<id>/render.*` + `reasoning.md`, `edit/master.ass`, `edit/sound.json` + mixed audio |
| 8 | `render.py --preview` composites: segments → overlays → captions last. | `edit/preview.mp4` |
| 9 | **critic** checks every cut, caption occlusion, overlay timing, levels, readability, STYLE.md. Verdict + ranked fixes. Fix loop, max 3 passes. | `edit/critic.md` |
| 10 | I see the preview, EDL, scenes.json and verdict. I give notes. | — |
| 11 | **"apply my notes"** — notes to `edit/feedback.json`, EDL/scenes updated, only changed scenes re-rendered, critic again. | `edit/feedback.json`, new `edit/preview.mp4` |
| 12 | I say "final". Full-res render, loudnorm pass. | `edit/final.mp4` |
| 13 | Persist: session appended to `edit/project.md`, approved EDL copied to `examples/`, `videos/index.md` status → `done`, commit. | `edit/project.md`, `examples/<slug>.edl.json` |

Side loops: **"process the inbox"** turns `cards/_inbox/` drops into `cards/*.md`. **"learn from my reviews"** proposes STYLE.md lines from repeated notes. **"where are we?"** = this table in 5 lines + last 3 decisions + `videos/index.md`.
