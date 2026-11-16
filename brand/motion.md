# brand/motion.md — how things move

The reference frames in `cards/_inbox/` and `~/Desktop/claudesampleimages/` are stills of a **moving** video. Every card describes a motion, not a layout. This file is the shared grammar; cards add the specifics. Planner, motion, designer and critic read it.

Marked **(seen)** = read directly off the frame sequence (timecodes on the player: 3:59, 4:04, 4:09, 6:13, 6:39…). Marked **(assumed)** = the obvious reading of the stills; replace with measured values the first time a screen recording of a reference is dropped into `cards/_inbox/` (the designer measures from frames).

## 1. Everything builds, holds, changes, exits
- A graphic is never a static slide. It **enters** (build), **holds** while I talk, gets at least one **internal change** every ≤ 3 s while on screen (a word lands, a card fills, a counter ticks, a check appears), then **exits** on a word boundary. (seen: step cards fill one by one between 04:0x frames; the milestone rail gains a check per beat.)
- Nothing on screen is static for more than 3 s unless it is my face. (rule)
- One new element per 3 s, never two at once. (STYLE.md)

## 2. Timing and easing
- Small elements pop in 170 ms (scale 0.8→1 + fade), swaps and morphs take 250 ms, small fades (titles, pills) 125 ms; cubic ease-out in / ease-in out. No linear, no bounce, no overshoot, no motion blur. (seen 2026-11-16: ref-backlinks-reel.mp4 at 24 fps — card pop 4 frames, card swap 6 frames, grid morph 6 frames, title fade 3 frames, CTA pill 3 frames)
- Large panels and windows: enter 350 ms, exit 250 ms. (assumed from the stills; brand/style.json `motion`; measure from a screen recording)
- A word or card lands **on the spoken onset** of its word, never on a metronome. Titles land word by word: "a" → "helper," → "another copy of Claude" across ~5 s of speech. (seen: ref-09 → ref-10)
- Counters count up over ~300 ms with one soft tick; numerals pop at 220 px. (seen: "04", "15", "36", "1 billion")
- Typewriter text at ~18 characters per second, cursor blinking 1 Hz, starts on my first word. (seen: "Here are screenshots of things I love. Write de|")
- Typed prompts in a chat composer: ~24 characters per second, each word appearing as I say it (typing follows the speech, not a clock); the send button turns accent just before the last word. (seen 2026-11-16: ref-backlinks-reel.mp4, 15 characters in 0.625 s)
- Fast list reels change something every 0.6–1.5 s (a card, a swap, a highlight). (seen 2026-11-16: ref-backlinks-reel.mp4)

## 3. Enters and exits by element
| element | enter | exit |
|---|---|---|
| kinetic title | each word scale 0.92→1 + fade | all words fade together |
| card beside face / comment bubble | fade + 60 px slide from its side | fade |
| step card row | whole row slides up 120 px + fade; each card fills top→bottom on its beat | all cards fade |
| milestone rail / timeline | rail + empty slots together; fills on beats; check pops 150 ms after fill | fade |
| window / device mockup | slide up 80 px + fade; content inside builds after the frame lands | hard cut back to footage |
| colour full-frame (prompt card on colour) | **hard cut** onto the colour, card slides up 80 px | hard cut back |
| face reveal in a device frame | frame holds, my face scales 1.0→1.04 then settles | hard cut |
| node / tree diagram | root first, children fan out one per beat, edges draw 200 ms before each child | fade |
| icon formation → grid (seen) | tiles build the number's digits in batches over ~1 s; on the cue word all tiles tween to a 5x10 grid, 250 ms ease-out | hard cut |
| chapter header over a grid (seen) | kicker swaps hard, title fades 125 ms, count pill pops 125 ms starting 170 ms after the title; grid dims to 25 % except the chapter's tiles (2 px accent outline), instant | hard cut on the next chapter |
| item card over a grid (seen) | scale 0.8→1 + fade 170 ms on the item's name; next item: old card up 60 px + fade while the new rises into the same spot, 250 ms | hard cut on a chapter change |
| giant one-word caption + CTA pill (seen) | words swap hard per word (0.125–0.5 s each); pill slides up 20 px + fade 125 ms once; mono tagline hard-appears ~1.5 s later | hard cut with the shot |
| chat composer (seen) | frame hard-cuts in empty; attachment body then header fade 125 ms apart; prompt types with my words at ~24 cps | hard cut (to the reel's first frame for a loop) |
| editorial title / end card | hard cut onto the card; line 2 lands on its word 350 ms; numeral counts 300 ms; checklist rows tick one per beat (assumed from stills; measure from a screen recording) | hard cut |

Transitions between shots are **hard cuts** (STYLE.md). Fades are for elements inside a shot, never between shots.

## 4. What stays still
- My face: no zooms, no punch-ins faked in post. Changing how big I am is a hard-cut reframe (split_top crop ↔ face_full), never an animated zoom. (seen 2026-11-16: ref-backlinks-reel.mp4, the face never scales within a shot)
- Backgrounds: flat colour or dark panel. Dot grids and rails are static; only their fills move.
- Captions move on their own track (word pop + cue rise, see brand/style.json `captions.motion`), never slide with a graphic.

## 4b. Split-top layout (seen 2026-11-16: ref-backlinks-reel.mp4)
On 9:16 the top half (y 0–0.50; the reference's edge measured at 240/480 px) is a flat panel with a faint static dot grid that holds every graphic; my footage fills the bottom half, cropped, never zoomed. Graphics stay inside the panel and never cross the edge. Captions sit on the panel's bottom edge (centre y ≈ 0.465), 2–3 words, above my face. Shots switch between split_top and face_full with hard cuts on word boundaries; the CTA/payoff goes face_full with giant one-word captions. Reference panel is light (#F5F5F7-like) with orange; brand default is #15161C with #FFD166, light variant allowed. `brand/style.json` has the `split_top` layout (panel 0.50, captions 0.465) and the `giant` caption preset; the planner names them per stretch.

## 5. Engagement rhythm for an explainer (30–60 s vertical)
1. **Hook (0–3 s)**: title lands on my first strong word; face full.
2. **Name the thing (3–10 s)**: one card or mockup enters beside me and builds while I describe it.
3. **Show it (10–40 s)**: the diagram / steps / timeline; a change on every beat I name; my face in a corner PiP.
4. **Payoff (last 5 s)**: a single big word or number; everything else gone.
5. **Loop seam (optional)**: the last frame hard-cuts back to the hook's opening state, so the replay looks continuous. (seen 2026-11-16: ref-backlinks-reel.mp4 ends on its first frame)
A viewer should see something change roughly every 2–3 s and never wait for a graphic that is already finished.

## 6. Sound ties to motion
Every visible land (card fill, check pop, counter) may carry one soft effect; max ~8 per 30 s; nothing for enters that are fades only. (STYLE.md, brand/sfx README)
