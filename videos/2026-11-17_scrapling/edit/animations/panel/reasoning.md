# panel (s1) reasoning
Engine: HyperFrames 0.9.58, one composition (hf/index.html), `--format mov` (ProRes 4444, alpha). Cards: kinetic-title-accent-word, window-mockup-slide-up (drawn variants), icon-grid-chapters (panel+dots only).
Fonts: Inter and JetBrains Mono bundled; Instrument Serif Italic copied to hf/assets/fonts and declared via @font-face (renders as the serif italic in frames).
Timing: every beat from scenes.json is a GSAP tween/set starting at exactly its t (absolute times). Clips: hook 0-3.71 (fade 250 ms from 3.46), A 3.78-21.54, B 21.54-24.54, C 24.54-34.10; hard cuts between windows and at 34.10 (brief says hard cut out, so no 250 ms exit).
Judgment calls:
- 'open source' pill moved to x 400 (window coords) to stop it overlapping the 72 px title.
- Row chip sits in the lower half of the row (right side) so it never collides with the 44 px label; check on row 01 at far right.
- B zoom ring: scenes box y fractions would cut line 2; ring/zoom centre box set to lines 3-5 exactly (y 210-418 of the 632 px content area, x/w as specified), scale 1.35. Push starts 22.50 (350 ms power3.out), ring fades 22.85-23.00.
- C selector line font 26 px (not 28) and zoom 1.6x measured on the selector string itself, so the 34-char string fits the 892 px window when zoomed; ring fades 28.85-29.00, held to 31.14, ease back 250 ms, table header draws 31.14.
- C prompt URL chip is on a second line under the prompt (does not fit beside the 40 px text in the window).
- Cursor blinks 1 Hz from 24.89 to 27.3. Band/bar positions animated with transforms (check rule).
- Typewriter (repo line, selector) is per-character set tweens inside the stated windows (6.34-6.88, 27.86-28.42).
- Landing: title word 'scraper' starts popping at 2.74 (beat time), fully in place by 3.09; landing.png is the 2.74 frame, title_full.png (3.2 s) shows it complete.
Checks: `hyperframes check` 0 errors (warnings: sub-composition structure, type floor for spec'd small mono text, no sound, closing line held <2 s; all accepted). Alpha verified: y>=960 fully transparent, nothing right of x 940 besides the panel itself.
Frames in this folder (gray backdrop for alpha): first, landing, title_full, beat_A_row1(.78), beat_A_row1_settled, beat_B_zoom_start/zoom, beat_C_zoom_start/zoom, beat_C_table(33.3), beat_C_table_row3.
ffprobe: codec_name=prores width=1080 height=1920 r_frame_rate=30/1 pix_fmt=yuva444p12le duration=34.100000

## Round 2 (critic fixes)
- Hook: kicker and "Claude Code," are on frame 0 (no tween). "lead" and "scraper" start 120 ms before onsets (2.22, 2.62), 170 ms pop (scale 0.8->1 + fade), fully in place on 2.34 / 2.74.
- C zoom: scale 1.25 (not 1.6) centred on the whole 28 px selector line (css: + string = 655 px, 1.25x is the largest scale that keeps it whole with >= 16 px inset); ring inset ~27 px from window edge; prompt, send, url chip and tool-call line fade to 15 % on 28.5 and return to 100 % at 31.14 with the ease back.
- B zoom: line numbers fade to 0 (120 ms) as the push starts at 22.5.
- Type floor: all text >= 28 px (repo line, grey lines, chips, pill, chrome labels, line numbers, url chip, tool/selector lines, table header). Chips reflowed: chip bottom-right (right 24 px), row-01 check moved to the label line top-right; url chip stays on its own line. Chip text unchanged. 
- check: 0 errors. Render: codec_name=prores width=1080 height=1920 r_frame_rate=30/1 pix_fmt=yuva444p12le duration=34.100000

## Round 3
- All in-window pops, fills, band moves, chip swaps, checks, typing, zooms, rings and table rows now start 120 ms before their scenes.json beat time (landed on the word). Window enter times (3.78, 21.54, 24.54) and hard cuts unchanged. Window B lines draw from 21.77; B push/band/line-number fade start 22.38; C zoom starts 28.38; table rows 31.74 / 32.46 / 33.18; header draw and ease-back 31.02.
- Hook: "Code," pops 1.58-1.75 (onset 1.70); "Claude" alone on frame 0 with the kicker.
- Final render: codec_name=prores width=1080 height=1920 r_frame_rate=30/1 pix_fmt=yuva444p12le duration=34.100000; check 0 errors.
