# cta slot
- Engine: HyperFrames 0.9.58, overlay_transparent, `--format mov` (ProRes 4444). Card: big-words-cta-caption. 1080x1920 @ 30 fps, 2.90 s.
- Fonts: Inter 600 and JetBrains Mono 500, bundled with HyperFrames (no file needed).
- Beats: pill (centre y 653 = 0.34, x 328-752) slides up 20 px + fades over 125 ms, power3.out, at 0.00 s. Tagline hard-appears at 1.20 s (tl.set), centred y 0.40, JetBrains Mono 34 px #141418 on a paper #F3EEE4 pill (999 px radius, 12/24 px padding, 1 px #DCD6CA stroke, shadow 0 6 16 rgba(20,20,24,.18)). Round 2 critic fix: replaces the grey 30 px text on a dark scrim (low contrast, off palette).
- Judgment calls: Landing frame 0.48 s: pill complete (it lands at 0.125 s); tagline is not yet in (it is on "send" at 1.20 s). No exit, holds to 2.90 s. Nothing below y 800 or right of x 782. Nothing static >3 s (clip is 2.9 s).
- check --json: 0 errors.
- ffprobe: codec_name=prores width=1080 height=1920 r_frame_rate=30/1 pix_fmt=yuva444p12le duration=2.900000
