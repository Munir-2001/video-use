# s1 reasoning
- Engine: HyperFrames, overlay_transparent, `--format mov` (ProRes 4444). Card: cards/kinetic-title-accent-word.md (brief's colours/layout override the dark-card defaults).
- Fonts: Inter bundled (800/600); Instrument Serif Italic copied to hf/assets/fonts and @font-faced; document.fonts.check asserted in the page.
- Timings: each of the 6 words starts 120 ms before its beat (0.06, 0.46, 1.10, 1.58, 2.22, 2.62 s), 170 ms pop (scale 0.92->1 + fade, power3.out). Brief says 350 ms for the pops; the caller's 170 ms won. Frame 0 empty. Landing 2.74 s: all words in place. Then whole title drifts y 0 -> -6 px (sine.inOut) until 3.42; no fade (hard cut is the exit).
- Layout: left x 48, ink #141418, kicker #6E6A64 36 px tracked 6 px, lines at y centres ~0.14/0.20/0.28. Lowest ink at y~605 (<0.42), rightmost x~790 (<940). No scrim; contrast was checked only against a #EFE8DA stand-in wall (base footage not available to this slot). If the real wall is darker, add the 40 % paper pill.
- Judgment: "One tool" letter-spacing 6 px instead of 0.18 em (px rule); kicker two words each pop on own beat.
- ffprobe: codec_name=prores width=1080 height=1920 pix_fmt=yuva444p12le r_frame_rate=30/1 duration=3.433333
