# brand/motion.md — how things move

The reference frames in `cards/_inbox/` and `~/Desktop/claudesampleimages/` are stills of a **moving** video. Every card describes a motion, not a layout. This file is the shared grammar; cards add the specifics. Planner, motion, designer and critic read it.

Marked **(seen)** = read directly off the frame sequence (timecodes on the player: 3:59, 4:04, 4:09, 6:13, 6:39…). Marked **(assumed)** = the obvious reading of the stills; replace with measured values the first time a screen recording of a reference is dropped into `cards/_inbox/` (the designer measures from frames).

## 1. Everything builds, holds, changes, exits
- A graphic is never a static slide. It **enters** (build), **holds** while I talk, gets at least one **internal change** every ≤ 3 s while on screen (a word lands, a card fills, a counter ticks, a check appears), then **exits** on a word boundary. (seen: step cards fill one by one between 04:0x frames; the milestone rail gains a check per beat.)
- Nothing on screen is static for more than 3 s unless it is my face. (rule)
- One new element per 3 s, never two at once. (STYLE.md)

## 2. Timing and easing
- Enter 350 ms, exit 250 ms, cubic ease-out in / ease-in out. No linear, no bounce, no overshoot, no motion blur. (assumed from the stills; brand/style.json `motion`)
- A word or card lands **on the spoken onset** of its word, never on a metronome. Titles land word by word: "a" → "helper," → "another copy of Claude" across ~5 s of speech. (seen: ref-09 → ref-10)
- Counters count up over ~300 ms with one soft tick; numerals pop at 220 px. (seen: "04", "15", "36", "1 billion")
- Typewriter text at ~18 characters per second, cursor blinking 1 Hz, starts on my first word. (seen: "Here are screenshots of things I love. Write de|")

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

Transitions between shots are **hard cuts** (STYLE.md). Fades are for elements inside a shot, never between shots.

## 4. What stays still
- My face: no zooms, no punch-ins faked in post. (assumed: the reference uses them sparingly; we keep cuts, not zooms)
- Backgrounds: flat colour or dark panel. Dot grids and rails are static; only their fills move.
- Captions move on their own track (word pop + cue rise, see brand/style.json `captions.motion`), never slide with a graphic.

## 5. Engagement rhythm for an explainer (30–60 s vertical)
1. **Hook (0–3 s)**: title lands on my first strong word; face full.
2. **Name the thing (3–10 s)**: one card or mockup enters beside me and builds while I describe it.
3. **Show it (10–40 s)**: the diagram / steps / timeline; a change on every beat I name; my face in a corner PiP.
4. **Payoff (last 5 s)**: a single big word or number; everything else gone.
A viewer should see something change roughly every 2–3 s and never wait for a graphic that is already finished.

## 6. Sound ties to motion
Every visible land (card fill, check pop, counter) may carry one soft effect; max ~8 per 30 s; nothing for enters that are fades only. (STYLE.md, brand/sfx README)
