# STYLE.md — my rules

One rule per line. Each line ends with `(date · origin)`. Origins: `seed` = initial setup, `review` = from my notes on a video, `rule` = I said "make this a rule". Newest at the bottom of each section. Agents read this every session and the critic checks every line.

## Captions
- Sentence case, never ALL CAPS. (2026-11-16 · seed)
- 2–3 words per cue. (2026-11-16 · seed)
- Word-synced highlight: the word being spoken is brighter and slightly larger than the rest of the cue. (2026-11-16 · seed)
- Vertical (9:16): captions sit in the lower band, centre ≈ 68 % down, just under the chin: never over my face, never in the bottom 20 %. (2026-11-16 · rule)
- Catchy text is its own layer: a new idea opens with a 2–4 word title, heavy sans, exactly one accent word in flame. Captions never repeat the title's words while it is on screen. (2026-11-16 · seed)
- Text beside my face goes in a card in the empty side of the frame, never across the face. (2026-11-16 · seed)
- Captions are applied last, after every overlay, so nothing hides them. (2026-11-16 · seed)
- Captions are big (96 px at 1080x1920, 80 px at 1080p) and they move: the spoken word pops in and each cue rises into place. Static subtitles are wrong. (2026-11-16 · rule)
- Caption look: on the paper panel plain ink, no outline, no shadow; over my face white with a 2 px edge and a soft shadow, never a heavy black outline. (2026-11-17 · review)
- Two layout exceptions to the size and band lines above: in a `split_top` stretch the captions are a smaller line (64 px) at the panel's bottom edge (y ≈ 0.465); a hook or call-to-action stretch may use the `big` preset, still 2–3 words per cue, at 120 px, y 0.64, with the CTA pill under it. One word per cue is never used. (2026-11-16 · rule)
- When my face fills the lower half of a face_full shot (head top below y 0.45), the hook/CTA captions and the CTA pill go above my head (captions y ≈ 0.24, pill ≈ 0.34), never across the face. (2026-11-17 · review)

## Framing and safe areas
- Vertical: the bottom 20% and the right edge stay clear of captions and graphics (platform UI lives there). (2026-11-16 · seed)
- Graphics never cover my mouth or eyes when I am on screen. (2026-11-16 · seed)
- The scenery changes every 5–8 s. My face is for the personal lines (hook, an opinion, the CTA), a couple of seconds each; the informational parts drop my video and show the animation alone (graphic_full, up to ~8 s, a change every ≤ 3 s). (2026-11-17 · review)

## Cuts and pacing
- Hard cuts only. No crossfades, no dissolves, no wipes. (2026-11-16 · seed)
- Cut on word boundaries, pad 30–200 ms, prefer silences ≥ 400 ms. (2026-11-16 · seed)
- When I repeat a sentence, the last complete attempt wins. (2026-11-16 · seed)
- Never more than one new graphic element per 3 seconds. (2026-11-16 · seed)
- Every named thing gets a visible mark on its own spoken word (box, flash, band, fill); nothing on screen changes on a word I did not say. (2026-11-17 · review)
- Windows never sit still: they drift while holding, slide when one replaces another, and the cursor moves between targets. (2026-11-17 · review)

## Sound
- Music sits about −12 dB under speech. (2026-11-16 · seed)
- At most ~8 sound effects per 30 s, each tied to a visible event on screen. (2026-11-16 · seed)
- Final mix: −14 LUFS integrated, true peak ≤ −1 dBTP. (2026-11-16 · seed)
- No audio pops at cuts: 30 ms fades at every boundary. (2026-11-16 · seed)

## Palette
- One palette, always: paper #F3EEE4 panels with ink #141418 text, flame #F4502A as the only accent (cobalt #1F5BFF for a second emphasis), near-black #0B0B0F only for full-frame cards. Never another accent colour. (2026-11-16 · rule)

## Never show
- Cigarettes. (2026-11-16 · seed)
- Private screens (notifications, chats, passwords, unblurred desktops). (2026-11-16 · seed)
- Confidential client data or Innova data. (2026-11-16 · seed)
- Other people's faces without their consent. (2026-11-16 · seed)

## Process
- No paid APIs. Everything renders locally. (2026-11-16 · seed)
- Nothing is shown to me before the critic has passed it. (2026-11-16 · seed)
- Scripts are complete, natural spoken sentences; no telegraphic fragments, no dropped words; every named thing sits inside a sentence. (2026-11-17 · review)
- Every script ends with the list of assets (screenshots, recordings) to capture into videos/<folder>/assets/ before I record. (2026-11-17 · review)
