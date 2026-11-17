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
