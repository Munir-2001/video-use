# cta slot
- Engine: HyperFrames 0.9.58, overlay_transparent, `--format mov` (ProRes 4444). Card: big-words-cta-caption. 1080x1920 @ 30 fps, 2.90 s.
- Fonts: Inter 600 and JetBrains Mono 500, bundled with HyperFrames (no file needed).
- Beats: pill (centre y 653 = 0.34, 424 px wide, x 328-752) slides up 20 px + fades over 125 ms, power3.out, at 0.00 s. Tagline hard-appears at 1.20 s (tl.set, no fade), centre y 768 = 0.40, 30 px mono, #F5F5F7 at 80 %, 40 % #0B0B0F scrim pill plus 2 px black text shadow.
- Judgment calls: tagline 30 px (card says 26) for phone legibility; kept the 40 % scrim as briefed. Landing frame 0.48 s: pill complete (it lands at 0.125 s); tagline is not yet in (it is on "send" at 1.20 s). No exit, holds to 2.90 s. Nothing below y 800 or right of x 782. Nothing static >3 s (clip is 2.9 s).
- check --json: 0 errors.
- ffprobe: codec_name=prores width=1080 height=1920 r_frame_rate=30/1 pix_fmt=yuva444p12le duration=2.900000
