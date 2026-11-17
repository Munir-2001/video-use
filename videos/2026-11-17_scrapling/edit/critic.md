# critic: 2026-11-17_scrapling, round 4 (the 8-stretch re-plan)

File: edit/preview_mixed.mp4 (37.03 s, 1110 frames, 30 fps).
Checked against STYLE.md (all lines, including the 2026-11-17 review lines), brand/motion.md, ROADMAP.md and brand/style.json.

VERDICT: FIX FIRST

The re-plan works:
- **Scenery and face:** 8 stretches; the face drops out for 17.9 s.
- **Sync:** every named word gets its mark on the onset frame.
- **Motion:** windows drift continuously and swap by slide, and a pointer moves between targets.
- **Captions:** ink with no outline on paper.

Five things still show on screen:
- Two continuity jumps at the seams you asked about (13.46 and 29.74; 7.10 is clean).
- A hard drop shadow on the CTA captions.
- The tagline shows "steps" before it is said.
- Two new windows 1.6 s apart at 21.78 / 23.38.

## TOP 5 FIXES (do these first)

1. **[13.47 → 13.50] Card 01 jumps at the s3 → s4 seam (motion, s4 slot).**
   - Evidence: on the last s3 frame (13.467) the DOM mock shows three rows with "Acme Co" in a small flame tag in row 3, the chip `article.item > h3` + check, and the title at y ≈ 609 (360-px scale). On the first s4 frame (13.500) it is a different drawing: "Acme Co" in a full-width flame box in row 1, rows 2–3 grey bars, a different header bar, and the title 3 px lower.
   - Fix: build s4's opening card 01 from s3's final state (same DOM rows, same Acme Co tag in row 3, same title y), then slide it out as card 02 slides in. Best: render s3's last frame as s4's first frame (one shared component, or s4 reads s3's end state).

2. **[29.73 → 29.77] The session window jumps and its state goes backwards at the s6 → s7 seam (motion, s7 slot).**
   - Evidence: on the last s6 frame (29.733) the window is tall, the prompt "> Scrape this directory" + url chip sit in a flame box at the top, the tool call has a flame dot (done), and the selector is below. On the first s7 frame (29.767) the prompt has vanished, everything jumps up about 60 px, and the tool call shows a loading spinner. The task looks like it restarted.
   - Changing the window size at a layout cut is fine (hard cut, face appears). Losing the prompt and going from "done" back to "loading" is not.
   - Fix: s7 opens with the same three lines (prompt + chip, tool call with the flame dot, css line) at the panel window's scale, or scrolls them up 250 ms after the cut. No spinner: the call already finished in s6.

3. **[33.98–36.82] CTA captions have a hard 4 px drop shadow (captions agent / captions_ass.py).**
   - Evidence: master.ass face cues use `\bord2\shad4\3c&H181414&\4c&H181414&` with no `\blur`. At 36.50, "setup **steps.**" shows a crisp ink offset copy 4 px down-right of every letter, which reads as a sticker or 3D effect.
   - Violates: "over my face white with a 2 px edge and a soft shadow, never a heavy black outline".
   - Fix: `\bord2\shad2\blur3\4a&H90&` (or a second shadow layer with `\blur6\bord0`, 40 % ink, 0 offset). Match style.json `big` (it says 1.5 px; STYLE says 2 px, so pick 2).

4. **[35.70 / 36.18] The tagline shows "steps" before it is said (motion, s8 slot).**
   - Evidence: at 35.70 ("setup") the paper pill appears already reading "setup steps,". "steps" is said at 36.18, 0.48 s later. At 36.18 "sent to you" types in.
   - Violates: "Every named thing gets a visible mark on its own spoken word … nothing on screen changes on a word I did not say." The word lands early.
   - Fix: "setup" on 35.70, "steps," on 36.18, then "sent to you" types after "steps." ends (36.82) or on the same 36.18 beat.
   - It is also a second new element 1.6 s after the pill (34.10), which breaks "Never more than one new graphic element per 3 seconds." Make the tagline a second line that grows inside the pill's paper extension instead of a separate pill, or get the user's yes on ROADMAP #11.

5. **[21.78 / 23.38] Two new windows 1.6 s apart, and the second hard-cuts in (planner + motion, s5/s6).**
   - Evidence: the config window slides in on "Plug" at 21.78. At 23.38 the layout cuts to graphic_full and the session window is simply there at 23.400 (same position on every frame 23.40–23.63, no slide).
   - Violates: "Never more than one new graphic element per 3 seconds." Also "slide when one replaces another". The whoosh at 23.38 accompanies nothing that moves (STYLE: "each tied to a visible event").
   - Fix, one of:
     - (a) The session window slides in from the right over the config window at 23.38 (window replaces window; the layout change can stay a hard cut underneath).
     - (b) Move the s5/s6 boundary so config gets ≥ 3 s. The only silence after 21.78 that keeps the sentence intact is 23.30–23.46, so (a) is the practical fix.
   - Either way, keep the whoosh only if something slides.

## ALL PROBLEMS (ranked, with timecodes)

1. [13.47→13.50] Card 01 continuity jump, s3→s4. (motion)
2. [29.73→29.77] Session continuity jump: prompt disappears, the tool call goes from done back to loading. (motion)
3. [33.98–36.82] CTA caption shadow is hard, not soft. (captions)
4. [35.70] Tagline shows "steps" 0.48 s early; tagline is a second new element 1.6 s after the pill. (motion; ROADMAP #11 still open)
5. [21.78 / 23.38] Two new windows 1.6 s apart. The session window hard-cuts in with a whoosh but no motion. (planner, motion, sound)
6. [7.10–29.74, graphic_full] paper_full captions are 72 px. STYLE says "Captions are big (96 px at 1080x1920 …)" and the exception line covers only split_top (64 px) and hook/CTA. Either set 96 px or add a dated exception for paper_full. (captions or user)
7. [23.40–27.30] The session window in s6 is about 85 % empty white for 4 s: the prompt sits at the top of a 1150 px tall window and nothing else is there until the tool call. In a graphic_full stretch the animation is the whole show. Fix (motion): size the window to its content (grow downward as lines arrive) or start it at a shorter height with the selector area and table placeholders visible.
8. [7.10–18.62, 23.38–29.74] All graphic_full cards occupy y 0.04–0.64 only. The band y 0.76–1.00 is empty paper, and the cards are the same 920 px width as in split_top, so "full frame" is not used. Nitpick (motion): scale the card about 1.15x or centre it at y ≈ 0.38.
9. [18.62–20.06] Card 03 is an empty white window with only "03" for 1.4 s on "Third, it ships an". Within the ≤ 3 s change rule, but the weakest frame in the reel. Pop a dashed placeholder row on "Third," or move the card's title onto "ships". (motion, nitpick)
10. [stretch lengths] s1 3.42, s2 3.68, s5 4.76, s7 4.24, s8 3.02 s are under the 5 s floor of "The scenery changes every 5–8 s". s1 and s8 are the personal "couple of seconds" lines, so they are fine. s2, s5 and s7 are the bridges from my own round-3 table, and each is one sentence. Accept, or merge s1+s2 if the user wants the 5 s floor strict.
11. [34.40–35.30] A motion-blurred hand swings across the left third next to the caption and pill (footage). It covers nothing. Nitpick.
12. [script] Spoken fragments ("First, adaptive selectors.", "The site changes your scrapers. Keep working.", "Second, stealth fetchers.") still break STYLE line 49. There is no assets/ folder, so the windows are drawn mockups (line 50). Needs a re-record. Not fixable in the edit. (writer, user; ROADMAP #1, #2)
13. [rules] style.json `big` preset outline 1.5 px against STYLE 2 px. There is no `paper_full` size in STYLE.md. ROADMAP #11 (pill/tagline spacing, CTA 100 px) is still unanswered. (user)
14. [whole reel] No music (ROADMAP #9, open). The face is soft (ROADMAP #10, the user's call). Not counted.

Verified (clean):
- **Sync:** sampled frames at onset −0.40/−0.27/−0.13/0.
  - Each named word's mark first appears on the frame between −0.13 and its onset, or on the onset frame itself: Claude, Code, scraper, Scrapling (typed from 4.13), GitHub, adaptive, selectors (typed + Acme Co tag), changes, working, stealth, fetchers, walls (wall grid), Cloudflare, MCP, server (plug icon), Plug (config slides in), Claude Code (title-bar tag + ring), scrape / this / directory (typed with speech), picks, CSS, selectors (zoom + ring), table, name, site, email (columns), Scrape (pill fills on 34.58).
  - Nothing is pre-shown except the tagline (problem 4).
  - "Claude" is no longer on frame 0.
- **Window motion:** no slot has a still span ≥ 0.5 s except the CTA (34.65–35.25, face shot). Median 200–400 px change per frame from drift. Windows swap by slide at 7.10–7.5 (README → card 01), about 14.2 (card 01 → 02) and 21.78 (card 03 → config). The pointer moves 60–120 px between targets and parks beside them.
- **Captions:** panel cues are ink #141418, `\bord0\shad0`, 64 px at y 0.465; paper_full cues are ink, no outline, at y 0.72; hook has no captions (the title carries the words); CTA is white at y 0.24 (STYLE line 16). No caption covers the face. 64 events, no overlaps.
- **Seams:** 3.42 (hook → split; panel empty for 1 frame before the README slides in on 3.46, fine), 7.10 (README continuous, clean), 18.62 (hard cut card 02 → split card 03, clean), 33.98 (table → CTA, clean). No flashes, no duplicated frames, no waveform spikes.
- **Never-show** (frames every 0.5 s): clean. Drawn mockups, `.example` data, "…" config placeholders, one face, no private screens.
- **Readability at 360 px:** card titles, labels, prompt, tool call, selector and table cells all read. Only the window title-bar labels ("feature 01", "claude · demo-folder") are under 28 px, and they are decoration.

## MEASURED
- **Duration:** 37.033 s (format) against total_duration_s 37.0. Video 1110 frames at 30/1.
- **Loudness (ebur128 on the mp4):** integrated −14.3 LUFS, LRA 2.8 LU, true peak −1.4 dBTP. Passes.
- **Per stretch, RMS / peak (dBFS):**

  | Stretch | Time (s) | RMS | Peak |
  |---|---|---|---|
  | s1 | 0–3.42 | −16.1 | −1.4 |
  | s2 | 3.42–7.10 | −17.1 | −1.4 |
  | s3 | 7.10–13.46 | −18.2 | −1.5 |
  | s4 | 13.46–18.62 | −18.1 | −1.5 |
  | s5 | 18.62–23.38 | −17.0 | −1.5 |
  | s6 | 23.38–29.74 | −18.4 | −1.5 |
  | s7 | 29.74–33.98 | −16.0 | −1.4 |
  | s8 | 33.98–37.0 | −18.5 | −1.5 |

  The graphic_full stretches run about 1–2 dB quieter (fewer effects, softer lines), which is fine.
- **Effects vs voice:** effect level is the residual after subtracting a rebuilt speech chain (correlation 0.956), measured as the loudest 50 ms RMS. The impact and the 3.46 whoosh sit inside speech, so their figures are upper bounds.

  | Effect | Time (s) | Effect (dBFS) | Voice nearby | Under the voice by |
  |---|---|---|---|---|
  | soft_impact | 2.74 | ≤ −18.0 | −10.3 | ≥ 7.7 dB |
  | whoosh | 3.46 | ≤ −16.3 | −10.4 | ≥ 5.9 dB |
  | whoosh | 21.78 | −21.1 | −9.9 | 11 dB |
  | whoosh | 23.38 | −21.2 | −9.6 | 11.6 dB, nothing moves (problem 5) |
  | ticks | 31.86 / 32.58 / 33.30 | −23.5 (peak −5) | −7.2 to −8.8 | about 15 dB |
  | pop | 34.10 | −22.3 | −8.8 | 13.5 dB |

  Speech gaps sit at −46 to −60 dBFS.
- **Layouts:** 8 stretches, 7 layout changes. Holds 3.42 / 3.68 / 6.36 / 5.16 / 4.76 / 6.36 / 4.24 / 3.02 s (longest 6.36). Face on screen 19.1 s (52 %): face_full 6.4 s, split_top 12.7 s. Face off 17.9 s in three graphic_full stretches of ≤ 6.36 s, each changing at least every 2.3 s.
- **Sync:** 19 named things plus 5 supporting words. All marked on their own word (−120 ms lead, mark complete on the onset frame). 1 early: tagline "steps" (35.70 vs 36.18).
- **Window motion:** still spans ≥ 0.5 s in the window slots: 0. Slides: 3 window swaps. Hard-cut window entries: 1 (23.38). Continuity jumps: 2 (13.48, 29.75). Pointer: present in s2–s7.
- **Graphics per 3 s:** at most 2. Config 21.78 + session 23.38; pill 34.10 + tagline 35.70.
- **SFX per 30 s:** at most 6 (8 total). One whoosh (23.38) has no visible motion.
- **Captions:** 64 events, 0 overlaps. Sizes 64 / 72 / 100 px for panel / paper_full / CTA.
