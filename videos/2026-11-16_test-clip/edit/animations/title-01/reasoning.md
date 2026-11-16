# title-01 · kinetic title (smoke test, built by the main session, not the motion agent)

- **engine:** HyperFrames 0.9.58, `npx hyperframes render --format mov --quality looks` → ProRes 4444 with alpha.
- **card:** cards/kinetic-title-accent-word.md. Kicker "video studio · smoke test", headline "first **real** render" (accent #FFD166).
- **font:** Inter 900 from the HyperFrames bundle (brand/fonts/ is still empty; the burned captions fall back to Helvetica Neue).
- **timings:** overlay starts at 0.3 s in the output; words land at +0.0 / +0.25 / +0.5 s (350 ms cubic, scale 0.92→1), fully in place before the payoff word "Munir" at 1.1 s; exit 250 ms at 3.45 s; duration 3.7 s.
- **size:** 1920x1280 to match `render.py`'s base (landscape sources scale to 1920 wide). Top third, nothing in the caption band or the bottom 20 %.
- **gotchas found:** `gap: 0.28em` collapsed to 4 px because em resolves against the container's 16 px — use px. Lint warns `nested_structure_needs_subcomposition` for a single-file overlay; harmless for a one-element overlay, but real slots should use `compositions/<id>.html`. Render from inside `hf/` with an absolute `-o`.
- **ffprobe:** codec_name=prores width=1920 height=1280 pix_fmt=yuva444p12le r_frame_rate=30/1 duration=3.700000
