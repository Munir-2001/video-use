# critic: 2026-11-17_scrapling, round 2 (preview_mixed.mp4, 37.03 s, 30 fps)

VERDICT: PASS

Every round-1 fix is verified in the new file. I found no clipped text, no ghosted or wrong-sized captions, no late hook, and no unreadable tagline. Effects now sit 11–20 dB under the voice and true peak is under the limit. Nothing on the never-show list appears. Everything left is a nitpick or a STYLE.md decision the user has to make. The pill and tagline (problem 1) is a literal STYLE.md line that needs either the user's exception or a one-element change. It is the only thing I would raise with the user before publishing.

## TOP 5 FIXES (do these first, all small)

1. [34.10 / 35.30] **The pill and the tagline are two new graphic elements 1.2 s apart.** This is unchanged from round 1. STYLE.md still says "Never more than one new graphic element per 3 seconds." The new dated exception (line 15) covers the position of the captions and pill, not this. The CTA card allows it, but STYLE.md outranks cards. Fix: either the user approves a dated exception ("the CTA tagline may land on the reward word ≥ 1 s after the pill"), or the motion agent (cta slot) makes the pill and tagline one element. For example, the tagline is pre-drawn inside the pill's paper box at 0 % and fades in on "send", so it is a change inside the element rather than a new one.

2. [04.26, 05.46, 07.78, 14.34, 20.18, 27.30, …] **Panel beats after the hook still start on their onset, so they are fully in about 170 ms late.** On the payoff frame 4.26 "Scrapling" is absent; it is in at 4.41. The same holds for the pill at 5.46/5.61, row 01 at 7.78/7.93, row 03 at 20.18/20.33 and the tool call at 27.30/27.45. The hook got the 120 ms lead; the windows did not. This is just over the 150 ms "late" line. Fix (motion agent, panel slot): apply the same −120 ms lead to every pop and fill in windows A/B/C.

3. [34.10–36.82] **CTA captions are 100 px. STYLE line 14 says the big preset is "at 120 px".** The new exception line 15 changes the position, not the size. 100 px is the right call (one line, fits within 832 px), but it needs the rule updated. Fix: the user adds "(100 px when above the head)" to line 15, or the captions agent goes back to 120 px with a deliberate two-line `\N` cue. A rules decision, not a render fix.

4. [00.00–02.22] **The hook panel does not change for 2.2 s.** With "Claude Code," on frame 0, the 1.22 "Claude" and 1.70 "Code" beats no longer do anything. The first motion is "lead" at about 2.22. That is under the 3 s static limit, so it passes, but the most important 2 s of the reel are a still slide. Optional fix (motion agent): land "turns" as a small flame arrow or underline on 0.66, or pop "Code," on 1.70 while "Claude" is on frame 0.

5. [31.86 / 32.58 / 33.30] **The ticks are quieter than needed.** Estimated tick level about −27.6 dBFS (max 50 ms RMS) against speech at −7 to −9: about 20 dB under. On a phone speaker they may disappear under "name, site, email". Optional (sound agent): ticks −10 → −6 dB. The whooshes (11–14 dB under) and the pop (13 dB under) are now right.

## ALL PROBLEMS (ranked, with timecodes)

1. [34.10 / 35.30] Pill and tagline are two new elements 1.2 s apart, against "Never more than one new graphic element per 3 seconds." STYLE.md needs a decision (see fix 1).
2. [4.26–27.45] Window beats land fully about 170 ms after their onset (payoff frame 4.26 shows no "Scrapling"). Motion agent: −120 ms lead.
3. [34.10–36.82] CTA caption size is 100 px against "at 120 px" in STYLE line 14. Rule wording needed.
4. [00.00–02.22] Static hook panel, 2.2 s. Under the limit.
5. [31.86–33.30] Ticks about 20 dB under speech, possibly inaudible on phones.
6. [21.54 → 24.54] Windows B and C are exactly 3.00 s apart: on the line, not over it. Deliberate.
7. [34.40–35.40] A motion-blurred hand swings up on the left beside "Comment" and "and I'll". It covers no caption, pill or face feature. Nitpick (footage).
8. [00.00–34.10] The panel edge at y 960 slices flat across the top of the hair. It is consistent with split_top. Nitpick.
9. [all] Integrated −14.3 LUFS against the −14 target (0.3 LU under). Nitpick.
10. [36.82–37.03] No loop seam back to the hook frame. Optional, deliberate.

Verified fixed from round 1:
- **Caption sizes:** 0 `{\r}` in master.ass. Panel cues are 64 px throughout; at 14.34 "Second, stealth fetchers." is one line; at 22.70 "Claude Code." is all one size.
- **Caption overlaps:** none among the 64 events. 22.28 shows a single clean "Plug it into".
- **Hook:** "lead" is fully in at 2.34 and "scraper" fully in at 2.74; the impact sound and the visual coincide. Frame 0 reads "ONE TOOL / Claude Code,".
- **Window C zoom (28.50–31.14):** 1.25x, other lines at 15 % ink, ring inset about 26 px from the window edges. It reads as a focus, not a bug. It eases back at 31.14 and the table builds at full view.
- **Window B zoom (22.50):** line numbers hidden during the push; no fragments at 22.70.
- **CTA:** 'Comment "Scrape"' is one line at 34.30; the tagline is 34 px ink on a paper pill, legible at 360 px (36.20).
- **Phone readability (360 px):** window A descriptors and chips, window C tool-call and selector lines, and the table header all read; nothing under 28 px except the decorative title-bar labels.
- **Frame rate:** constant 30 fps, 1110 frames.

Checked and clean:
- **Cuts:** the window hard cuts at 3.46/3.78, 21.54, 24.54 and 34.10 show no flash and no duplicated frame. Each element is absent one frame before its entry.
- **Seams and audio:** no waveform spikes at the seams. The largest sample jumps (3.777, 14.553) are consonants. Gaps sit at −45 to −60 dBFS.
- **Captions vs face and safe areas:** panel captions at y 893 stay on paper above the hairline (5.0, 12.9, 22.7, 26.2, 33.4). CTA captions and pill sit on the wall above the head, now covered by STYLE line 15. Nothing is in the bottom 20 % or right of x 940.
- **Static spans:** no graphic is static for more than 3 s. The longest are 2.72 s (17.46→20.18) and 2.64 s (28.50→31.14, ring at 28.85).
- **Never-show list** (frames every 2 s): clean. Drawn mockups with `.example` data and "…" config placeholders, one face, no cigarettes, no private screens.
- **STYLE.md walk:** sentence case; 2–3 words per cue; spoken word brighter and larger; title has exactly one flame accent word ("yellow" → "flame" fixed); captions are burned last and never repeat the title; hard cuts only; palette is paper/ink/flame/cobalt with no near-black on footage; no paid APIs. Exceptions: problems 1 and 3 above.

## MEASURED
- **Duration:** 37.033 s (format) against total_duration_s 37.0 (within ±0.1). Video 37.000 s, 1110 frames, 30/1 constant.
- **Loudness (ebur128 on the mp4):** integrated **−14.3 LUFS**, LRA 2.7 LU, true peak **−1.4 dBTP**. That passes ≤ −1. sound_report.json says −1.5 on the wav; the AAC encode adds 0.1.
- **Per section, RMS / peak (dBFS):**

  | Section | Time (s) | RMS | Peak |
  |---|---|---|---|
  | hook | 0–3.5 | −16.2 | −1.4 |
  | readme | 3.5–21.5 | −17.7 | −1.4 |
  | config | 21.5–24.5 | −17.8 | −1.5 |
  | terminal | 24.5–34.1 | −17.2 | −1.5 |
  | cta | 34.1–37.0 | −18.3 | −1.5 |

  The CTA is about 1 dB quieter than the body, which is fine.
- **Effects vs voice:** I rebuilt the speech chain (high-pass 70, compressor, +17 dB, limiter), fitted it to the mix (corr 0.957) and took the residual as the effects. The residual floor is about −25, so the impact and whoosh A figures are upper bounds.

  | Effect | Time (s) | Effect, max 50 ms RMS (dBFS) | Voice nearby | Under the voice by |
  |---|---|---|---|---|
  | impact | 2.74 | ≤ −18.1 | −10.3 | ≥ 8 dB |
  | whoosh A | 3.78 | ≤ −17.3 | −10.1 | ≥ 7 dB |
  | whoosh B | 21.54 | −21.1 | −10.0 | 11 dB |
  | whoosh C | 24.54 | −21.4 | −6.8 | 14.6 dB |
  | ticks | 31.86–33.30 | −27.6 (peak −9) | −7.2 to −8.8 | about 20 dB |
  | pop | 34.10 | −22.3 (peak −10.8) | −8.8 | 13.5 dB |

- **Music:** none (brand/music is empty).
- **Graphics per 3 s:** at most 2 new elements (pill 34.10 + tagline 35.30); everything else is 1. Internal changes peak in window A (pill 5.46, repo line 6.34, row 7.78).
- **Effects per 30 s:** at most 6 (8 total). Every effect lands on a visible event.
