# critic: 2026-11-17_scrapling, round 5

File: edit/preview_mixed.mp4 (37.03 s, 1110 frames, 30 fps).
Checked against STYLE.md (every line), brand/motion.md and ROADMAP.md.

VERDICT: FIX FIRST

Every round-4 fix is confirmed:
- The 13.46 seam is clean.
- 23.38 now slides the session window in over the config window.
- 29.74 keeps the finished session.
- The tagline lands "setup" and "steps," on their words.
- The CTA edge is soft and reads at 360 px.

One new visible bug came with the 96 px paper_full captions: three cues re-wrap every time the highlighted word changes, so the text jumps between one and two lines and changes its break. That is the only thing that changes what the viewer sees. The rest are nitpicks and open user decisions.

## TOP 5 FIXES (do these first)

1. **[13.54–15.62, 16.74–18.50, 24.82–26.66] paper_full captions reflow as the highlight moves (captions agent / captions_ass.py).**
   - Evidence (caption band, 360 px):
     - "Second, stealth fetchers." is "Second, stealth / fetchers." at 13.57, "Second, / stealth fetchers." at 13.83–14.17, back to "Second, stealth / fetchers." at 14.50–15.17.
     - "scrape this directory." is two lines at 25.17, one line at 25.50–25.73, two lines again at 26.17–26.67.
     - "walls like Cloudflare." is one line at 17.00–17.50 and two lines at 18.00.
   - Cause: at 96 px a 3-word cue is about as wide as the 832 px line. WrapStyle 0 (smart wrap) re-balances every event, and the 112 % pop on the spoken word tips it over the edge, so each new event breaks differently. The cue's centre also moves up and down by half a line.
   - Fix, one of:
     - (a) Split cues longer than about 18 characters into 2 words in the paper_full stretches: [Second, stealth] [fetchers.], [walls like] [Cloudflare.], [scrape this] [directory.].
     - (b) Keep the 3 words but choose the break once per cue: `WrapStyle: 2` plus an explicit `\N` written identically into every event of that cue, so the break never moves.
   - "First, adaptive / selectors." (7.22–9.30) is also two lines but stable. Fine, though (a) would make it one line.

2. **[29.73 → 29.77] Small jump at the s6 → s7 layout cut (motion, s7 slot).**
   - Evidence: the content is all there now (prompt + chip, tool call with flame dot, css line), but it sits about 10 px higher at 360 px (about 27 px at 1080). The window loses about 40 % of its height on the same frame as the face appears.
   - The hard cut hides most of it. It reads as a nudge, not a bug.
   - Fix (optional): place s7's opening lines at s6's last y, then do the scroll-up on "table" (31.02) that already exists. Only worth doing if s7 is re-rendered for another reason.

3. **[34.10 / 35.70] The pill and the tagline are still two new elements 1.6 s apart (user decision, ROADMAP #11).**
   - The flame pill pops at 34.10 and the paper tagline pill appears at 35.70. STYLE.md still says "Never more than one new graphic element per 3 seconds." The tagline is now a separate pill under the flame one; the coordinator's "inside the same pill" means the tagline's own pill grows. Each word is in sync now.
   - Fix: the user says yes to a dated exception for CTA taglines, or the motion agent attaches the tagline as an extension of the flame pill (one shape that grows a paper second row on "setup").

4. **[18.62–20.06] Card 03 is an empty window with only "03" for 1.4 s (motion, s5 slot).**
   - "Third, it ships an" has no named thing, so there is no sync breach. But it is the weakest frame in the reel, and it arrives right after a hard cut from the full-frame card 02.
   - Fix (optional): show card 03's dashed placeholder row and a plug-outline ghost on "Third," (18.74), then fill "MCP" on 20.18 as now.

5. **[7.10–29.74 graphic_full] The cards use only the top 60 % of a full-frame stretch (motion, nitpick).**
   - The cards sit at y 0.04–0.64 at the split_top width (920 px). The band y 0.76–0.80 is empty paper above the 20 % safe zone.
   - Fix (optional): scale cards 1.1–1.15x and centre them at y ≈ 0.36, so graphic_full reads bigger than split_top. Captions stay at 0.72.

## ALL PROBLEMS (ranked, with timecodes)

1. [13.54–15.62, 16.74–18.50, 24.82–26.66] paper_full captions re-wrap on each highlighted word; text jumps between one and two lines. (captions)
2. [29.73→29.77] Content about 27 px higher, window shorter on the s6→s7 cut. Minor. (motion)
3. [34.10 / 35.70] Pill and tagline are two new elements 1.6 s apart. Open user decision. (ROADMAP #11)
4. [34.10–36.82] CTA captions are 100 px against "at 120 px" in STYLE line 15. Open user decision. (ROADMAP #11)
5. [18.62–20.06] Card 03 empty for 1.4 s. (motion, nitpick)
6. [7.10–29.74] graphic_full cards do not use the full frame. (motion, nitpick)
7. [0.00–0.17] The first frame has no text (kicker "One" lands at 0.18). This is correct under the sync rule; thumb.jpg covers the cover frame. Nitpick.
8. [34.43–35.30] A blurred hand swings across the left third and points down toward the pill. It covers neither the caption nor the pill. Nitpick (footage).
9. [stretch lengths] s2 3.68, s5 4.76 and s7 4.24 s are under the 5 s floor of "The scenery changes every 5–8 s". These are the one-sentence bridges from the round-3 plan. Accept.
10. [script] Fragments ("First, adaptive selectors.", "The site changes your scrapers. Keep working.", "Second, stealth fetchers.") still break STYLE line 49. There is no assets/ folder (line 50). Fix with a re-record. (writer, user)
11. [rules] style.json `big` outline 1.5 px against STYLE 2 px. master.ass uses 2 px, so style.json is the stale one. (designer)
12. No music (ROADMAP #9). Soft face (ROADMAP #10). Not counted.

Verified (clean):
- **Seams (one frame before / after):**
  - 3.42: hook → split, panel empty for one frame, README slides in on 3.46.
  - 7.10: README continuous.
  - 13.46: card 01 identical across the cut; card 02 slides over it at about 14.2.
  - 18.62: hard cut card 02 → card 03.
  - 23.38: the config window carries across the cut into paper_full, and the session window slides in over it 23.43–23.73.
  - 29.74: minor, see 2.
  - 33.98: table → CTA.
  - No flashes, no duplicate frames, no waveform spikes.
- **s6 growth:** the window grows 260 → 600 → 1000 px with the content (prompt 24.0, tool call 27.3, selector 27.9). Its bottom edge stays at y ≤ 0.66, so it never touches the caption at 0.72. The 28.50 zoom dims the other lines to 15 % and rings the selector, with no clipped words in focus. Nothing new is broken.
- **Sync:** every named word is marked between −0.13 s and its onset frame. Scrapling, GitHub, adaptive, selectors, changes, working, stealth, fetchers, walls, Cloudflare, MCP, server, Plug, Claude Code, scrape / this / directory, picks, CSS, selectors, table, name / site / email, Scrape (pill text types "Comment…" from 34.46, complete at 34.567 for the 34.58 onset), setup (35.70), steps (36.18). Nothing is pre-shown.
- **Window motion:** no still span ≥ 0.5 s in any window slot (s2–s7). The pointer moves between targets. Swaps slide at 7.1, about 14.2, 21.78 and 23.43.
- **Captions:** panel 64 px ink, no outline; paper_full 96 px ink, no outline, at y 0.72; CTA 100 px white with 2 px soft ink edge and 2 px shadow blurred 3 px at 55 %. At 360 px the CTA edge is soft, legible on the cream wall, and no longer sticker-like. 64 events, 0 overlaps.
- **Never-show** (frames every 0.5 s): clean.
- **Readability at 360 px:** all content text reads; only the decorative title-bar labels are small.

## MEASURED
- Duration: 37.033 s (format) against total_duration_s 37.0. 1110 frames at 30/1.
- Loudness (ebur128 on the mp4): integrated −14.3 LUFS, LRA 2.8 LU, true peak −1.4 dBTP.
- Per stretch RMS / peak (dBFS, unchanged mix from round 4): s1 −16.1 / −1.4 · s2 −17.1 / −1.4 · s3 −18.2 / −1.5 · s4 −18.1 / −1.5 · s5 −17.0 / −1.5 · s6 −18.4 / −1.5 · s7 −16.0 / −1.4 · s8 −18.5 / −1.5.
- Effects vs voice (loudest 50 ms, residual method, round-4 audio unchanged): impact ≥ 7.7 dB under, whoosh 3.46 ≥ 5.9 dB, whooshes 21.78 / 23.38 11–11.6 dB (23.38 now has the session slide on screen), ticks about 15 dB, pop 13.5 dB. Speech gaps sit at −46 to −60 dBFS.
- Layouts: 8 stretches, 7 changes. Holds 3.42 / 3.68 / 6.36 / 5.16 / 4.76 / 6.36 / 4.24 / 3.02 s. Face on screen 19.1 s (52 %), off 17.9 s.
- Sync: 19 / 19 named things marked on their own word; 0 early.
- Window motion: still spans ≥ 0.5 s in s2–s7: 0. Slides 4, hard-cut window entries 0, continuity jumps 1 minor (29.75).
- Graphics per 3 s: at most 2 (pill 34.10 + tagline 35.70).
- SFX per 30 s: at most 6 (8 total). Each effect lands on a visible event.
- Captions: 64 events, 0 overlaps, 3 cues re-wrap while on screen.
