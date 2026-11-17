# s8 slot
- Engine: HyperFrames 0.9.59, overlay_transparent, `--format mov` (ProRes 4444). Card: big-words-cta-caption (variant above the head, per STYLE line 2026-11-17). 1080x1920 @ 30 fps, data-duration 3.02 s (clip 0 = output 33.98).
- Fonts: Inter 600/800 and JetBrains Mono 500 bundled with HyperFrames; `document.fonts.check` asserted in the page.
- Timings (revised): pill pops empty at clip 0.00, text fills 0.48, glyph swap 1.20; tagline per spoken word: pill pops with "setup" at 1.72 (35.70), grows to "setup steps," at 2.20 (36.18, 300 ms), then " sent to you" grows at 2.45 (300 ms, unspoken promise); drift -4 px from 2.20.
- Judgment calls: pill centre y 653 (0.34), tagline centre y 768 (0.40); both centred on x 470 so nothing is right of x 940 (max ~740); nothing below y 820. Pill is 72 px high, padding 20 px, flame #F4502A, ink #0B0B0F text per slide data. Straight quotes. Tagline text ink #141418 on paper with 1 px #DCD6CA stroke and shadow (per task, overrides the card's light text). Clip carries nothing before 0.00 beyond transparent; first.png is the first frame (pill already starting its pop).
- check: 0 errors.
- ffprobe: codec_name=prores width=1080 height=1920 pix_fmt=yuva444p12le r_frame_rate=30/1 duration=3.033333
