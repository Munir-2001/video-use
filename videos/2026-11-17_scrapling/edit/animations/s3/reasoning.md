# s3 reasoning
Engine: HyperFrames 0.9.59, one composition (hf/index.html), `--format mov` (ProRes 4444; frames are fully opaque because the paper + dot grid covers 1080x1920). Card: window-mockup-slide-up, drawn paper variant. Layout graphic_full (content band y 0.10-0.66; nothing below y 1231; captions y 0.72 clear; nothing right of x 948).
Fonts: Inter and JetBrains Mono are bundled with HyperFrames; `document.fonts.check` asserted into window.__fontsOk (both true in render). No file needed.
Judgment calls
- s2/reasoning.md did not exist when built, so window A is rebuilt from scenes.json: rect 892x640 at 48,192, drift end state translateY -8 px / scale 1.02 (origin centre), title Scrapling + flame underline, pill "open source", repo line, 4 grey bars, all complete. Pointer assumed parked at tip (600, 432) (beside the repo line end, 16 px right/below). If s2 parks elsewhere, change P0 in hf/index.html and re-render.
- Timeline (clip time = output - 7.10), every change starts 120 ms before its word: swap 0.56-0.86 (A out left 300 ms power3.in, card 01 in from the right power3.out), "01" and "Adaptive" type 0.56-0.81; "selectors" types 1.28-1.40, chip pops blank 1.28, types div.card > h2 1.40-1.70, flame box on Acme Co draws 1.28-1.53; reshuffle 3.12-3.42 (Acme block and the block below swap), box turns grey dashed (stays on the now-empty title spot), chip struck + greyed; working: box slides to Acme 5.60-5.85, chip retypes article.item > h3 5.62-5.86, check pops 5.80-5.97.
- Chrome labels 28 px (type floor used on the other slots) instead of the 22 px in assets_note.
- Title wraps to two lines (Adaptive / selectors) because 88 px does not fit one line in 892 px.
- Non-target listing blocks keep the title zone empty so the dashed box really sits on an empty spot; "Acme Co" is part of the drawn mini page from card arrival (not a spoken-word reveal).
- Drift: card 01 sine in-out translateY 0 -> -8 and scale 1.00 -> 1.02 from 0.98 to 6.36 (8.08-13.46); window A holds its s2 end state while it slides out. Pointer is a page-level element mapped through the drift (targets computed at their arrival time).
- Pointer: leaves (600,432) 0.90, parks beside "selectors" at 1.20 (tip 512,497); moves 2.74, parks beside the box at 3.04 (tip 397,792); moves 5.22, parks under the chip at 5.52 (tip 344,1127). The legs are 100-330 px, longer than the 60-120 px rule because the card is 1000 px tall and the targets are far apart; idles with a 2 px sway between parks (ends at 0 offset).
- check: 0 errors (warnings: line_unread hold floors, canvas_overflow infos from the intended slide-out, accepted).
END STATE at 13.46 (clip 6.36), for s4
- Card 01: wrapper rect 892x1000 at 48,230 (x 0), drift transform translateY -8 px, scale 1.02, origin centre (494, 730). No exit tween; s4 slides it out left.
- Pointer tip (page px): x 344.2, y 1126.9 (36 px ink arrow, sway offset 0), under the chip.
- Chip: article.item > h3 (cobalt on #F3EEE4, rect x 97-469, y 1041-1111 nominal), check pop done (48 px flame circle at x 492-540, y 1003+ nominal, white check) right of it. Mini page: Acme Co block in slot 3 (bottom) with the solid 3 px flame box on it; the other two blocks empty-titled. Title: "01" flame, "Adaptive" ink, "selectors" flame. Paper + dot grid unchanged.
ffprobe: codec_name=prores width=1080 height=1920 r_frame_rate=30/1 pix_fmt=yuva444p12le duration=6.366667 (191 frames, within 1 frame of 6.36)
Frames: first.png (0), landing.png (1.40 = 8.50), f_10.34.png (3.24), f_12.82.png (5.72), last.png (6.33).
