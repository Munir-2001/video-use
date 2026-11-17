# s2 reasoning
Engine: HyperFrames 0.9.58, `--format mov` (ProRes 4444 alpha), one composition hf/index.html, data-duration 3.68. Cards: window-mockup-slide-up (paper drawn variant), icon-grid-chapters (panel + dot grid only). Fonts: Inter + JetBrains Mono bundled; document.fonts.check asserted in the page; chrome label/pill/repo at 28 px (type floor, spec said 22/26).
Clip time = output - 3.42. Panel #F3EEE4 + dot grid opaque y 0-960; transparent below (alpha verified).

## Timings (clip s / output s)
- 0.00-0.35 / 3.42-3.77: window + pointer slide in from the right (x 1080 -> 0, power3.out). Starts at clip 0 because "It's" (3.46) minus 120 ms falls before the clip.
- Drift 0.35 -> 3.68: translateY 0 -> -8 px, scale 1 -> 1.02, sine.inOut, origin (494,512) (window centre), applied to a wrapper holding window + pointer, never the frame rect itself.
- Title "Scrapling" types 0.59-0.84 (250 ms, landed on the word at 4.26 / 0.84), flame underline draws 0.84-1.09. Landing frame shows the title complete.
- Pill pops blank 1.92-2.09, "open" types 2.00-2.20, " source" types 2.32-2.56 (words at 2.04 / 2.44). Pill is a fixed 232 px wide so it does not reflow.
- Repo line types 2.80-3.44 (word 2.92; done by 6.90 output = 3.48).
- Pointer tip positions (wrapper coords, drift 0): enter (700,760) -> (446,350) arrives 0.64 (4.06) -> (736,376) arrives 1.84 (5.26) -> (582,442) arrives 2.72 (6.14), parks. 300 ms power3.inOut each. No idle sway (would break the exact park value s3 copies).
- No exit tween: the brief says s3 continues the last frame, so the clip ends in place (deliberate exception to the 250 ms exit).
- Body: 4 grey bars present from landing (spec). Title, pill and repo line absent before their words.

## End state for s3 (copy exactly)
- Window rect at rest [48,192,892,640]; at clip end (7.10) drift = translateY -8 px, scale 1.02 about (494,512) -> rendered rect x 40.0-948.2 (approx), y 178.0-830.0 (approx, incl. 1.02 scale: left=494-446*1.02=39.1, top=512-320*1.02-8=177.6, w=909.8, h=652.8).
- Last rendered frame (3.667) is at 99.6 % of that curve (sine ease), visually identical.
- Pointer tip (arrow, 30x40 svg, hotspot top-left, 36 px nominal): wrapper coords (582,442); screen coords at the end = (494+88*1.02, 512-70*1.02-8) = (583.8, 432.6). Pointer lives inside the drift wrapper so it moves with the window. s3 should place the window with transform scale 1.02 / y -8 about (494,512) and the pointer at wrapper (582,442) (equivalently screen (583.8,432.6) if not wrapped).
- Content at end: title "Scrapling" + flame underline (330 px wide, 6 px, under the title, window coords x 48 y 140 in content area), pill "open source" (window coords x 404, y 80 in content area, 232x48), repo line "github.com/D4Vinci/Scrapling" (x 48, y 164), 4 grey bars at content y 250/290/330/370 (widths 790/730/770/440).

## Checks
`hyperframes check`: 0 errors; warnings accepted (safe-zone notes on in-window text at x 48, first_frame_empty because the window enters from off-canvas as briefed, closing line < 2 s because s3 continues it).
Frames: first.png (empty panel), b1.png (0.2, window sliding), landing.png (0.84), b3 (2.1 pill blank/typing), b4 (2.5), b5 (3.0, repo typing), last.png. All composited on grey for alpha. Nothing within 140 px of the right edge except the window shadow (window ends x 948 at max).
Duration 3.70 s = 111 frames (3.68 rounds up to the next frame, within 1 frame).
ffprobe: codec_name=prores width=1080 height=1920 pix_fmt=yuva444p12le r_frame_rate=30/1 duration=3.700000
