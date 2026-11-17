# ROADMAP.md — feedback and improvement list

Everything the user said after reviewing a reel, with status. Newest review at the top. Items move to `done` with the commit that closed them; rules that came out of a review are also dated lines in `STYLE.md`.

## Review of 2026-11-17_scrapling (first real reel, 2026-11-17)

Verdict from the user: "not bad, significant room for improvement; the animations are the focus, not the face."

| # | feedback (user's words, shortened) | what it means for the system | status |
|---|---|---|---|
| 1 | "The script is a bit broken, sounds stupid, out of sync. Correct grammar, don't skip words, make sure what I'm saying makes sense." | The writer wrote telegraphic beats ("First, adaptive selectors.") instead of spoken sentences. Writer rule: complete natural sentences a person would say, read-aloud test, named beats inside the sentences, no fragments, no skipped words. | done 2026-11-17 (writer.md) |
| 2 | "Whenever I plan the content script, tell me the assets to put." | The writer ends every script with an "Assets to capture" list (screenshots and recordings, one per beat, exact page and what to highlight) and the folder `videos/<folder>/assets/`. The planner uses them as real screens with camera moves. | done 2026-11-17 (writer.md, planner.md, motion.md, assets/ convention) |
| 3 | "Tighter sync with the audio and the things on screen." | Every named thing gets a visible mark on its own spoken word (box, flash, band); nothing on screen changes on a word that was not said; beats start 120 ms before the onset so they are landed on the word. | done 2026-11-17 (planner.md, brand/motion.md, STYLE.md) |
| 4 | "The outline can be better." | Captions on the paper panel are plain ink with no outline; captions over the face are white with a soft shadow and a thin edge, not a 4 px black outline. Per-preset colour/outline/shadow in captions. | done 2026-11-17 (captions_ass.py presets) |
| 5 | "Moving windows — as much animation as possible, it has the highest retention." | Windows drift slightly while they hold, swap by sliding (not hard cuts) when the next window replaces the previous one, the cursor moves inside; camera moves (push in / pan / ease back) on screenshots. | done 2026-11-17 (brand/motion.md, window card) |
| 6 | "Switch between my talking head and pure footage: a couple of seconds of my face for something important, then remove my video for the informational part and show the animation." | Planner rhythm: face_full for the hook, opinions and the CTA; graphic_full (no face) for informational stretches, up to ~8 s as long as something changes every ≤ 3 s; split_top in between; change the layout every 5–8 s. | done 2026-11-17 (planner.md, STYLE.md) |
| 7 | "Change the scenery every 5–8 seconds." | Same rule as 6, as a STYLE line the critic checks. | done 2026-11-17 |
| 8 | "I will drop more reels tomorrow." | `cards/_inbox/` → "process the inbox"; the designer measures timings from video and updates cards + `brand/motion.md`. Ask for one with lively window transitions. | waiting for drops |
| 9 | Music: "I don't know about the music right now." | Undecided. `brand/music/` empty; the mixer ducks a bed automatically once a file is there. Options if wanted: a track the user picks, or local MusicGen (2 GB install). | open |
| 10 | Face sharpness (laptop 1080p crop, upscaled 1.78x). | Not a priority for the user. Phone portrait or iPhone-as-camera on the Mac fixes it. | user's call |
| 11 | Critic's two open STYLE questions: pill + tagline 1.6 s apart; CTA captions 100 px above the head. | Need a yes/no. | open |
| 12 | (from the re-plan) Optional polish the critic listed: card 03 empty for 1.4 s before "MCP"; graphic_full cards could be 1.15x larger and centred; 29.74 content nudge. | Motion-agent tweaks, next pass or next reel. | open |

## Next reel checklist (what changes next time)
1. "write a script for <topic>" → natural spoken script + assets list → user captures the screenshots/recordings into `videos/<folder>/assets/` and records with the pauses.
2. Planner plans real screens with camera moves and marks every named word; layouts rotate every 5–8 s; face for the personal lines, animation-only for the informational ones.
3. Captions: ink on paper, soft white over the face.
4. Windows drift, slide and show a cursor; every change lands on its word.
