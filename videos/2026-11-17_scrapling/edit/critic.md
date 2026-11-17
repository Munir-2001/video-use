# critic: 2026-11-17_scrapling, round 3 audit against the 2026-11-17 review rules

File: edit/preview_mixed.mp4 (37.03 s, 30 fps, rendered 02:02 with the round-3 −120 ms leads).
Rules checked: STYLE.md (lines dated 2026-11-17 · review), brand/motion.md §3 / §4c / §5, ROADMAP.md review list, brand/style.json caption presets.

VERDICT: FAIL

The reel was built before these rules and breaks four of them outright:
- **Scenery:** one layout for 34.1 s.
- **Face:** on screen 100 % of the time.
- **Windows:** never move while they hold, are swapped by hard cuts, and no mouse cursor appears.
- **Captions:** every cue still has the 4 px black outline.

The sync rule mostly passes after the round-3 leads, with 6 misses. None of this is a render bug. It is a re-plan: planner first, then motion, then captions.

## TOP 5 FIXES (do these first)

1. **[00.00–34.10] Scenery is frozen and the face never leaves (planner).**
   - Evidence: split_top holds from 0.00 to 34.10 (34.1 s), then face_full for 2.9 s. That is one layout change in 37 s. The face is visible in 1110 of 1110 frames. The hook is not face_full and no informational stretch drops the face.
   - Violates: "The scenery changes every 5–8 s. My face is for the personal lines (hook, an opinion, the CTA), a couple of seconds each; the informational parts drop my video and show the animation alone (graphic_full, up to ~8 s, a change every ≤ 3 s)."
   - Fix: re-plan scenes.json to the layout timeline below. 8 stretches, the longest 6.4 s, hard cuts in speech gaps. The panel slot has to be split into per-stretch slots (graphic_full 1080x1920 and split_top 1080x960).

2. **[03.78–34.10] Windows sit dead still and swap by hard cut; there is no mouse cursor (motion).**
   - Evidence: frame diffing of animations/panel/render.mov (panel area, threshold 20 px changed) finds 9 completely still spans of 1 s or more:

     | Still span (s) | Length (s) |
     |---|---|
     | 0.03–1.57 | 1.57 |
     | 7.87–10.20 | 2.37 |
     | 10.47–12.70 | 2.27 |
     | 12.83–14.20 | 1.40 |
     | 14.47–16.60 | 2.17 |
     | 17.50–20.03 | 2.57 |
     | 20.30–21.53 | 1.27 |
     | 22.83–23.90 | 1.10 |
     | 28.83–31.00 | 2.20 |

     That is 16.9 s of 34.1 s with zero motion. No window drifts.
   - At 21.54 and 24.54 the old window hard-cuts out and the new one rises into an empty panel; nothing slides across.
   - The only "cursor" is window C's text caret blinking at 1 Hz (25.30, 25.80, 26.30, 26.80); no pointer ever moves between targets.
   - Violates: "Windows never sit still: they drift while holding, slide when one replaces another, and the cursor moves between targets." Also the motion.md §3 rows "window hold: drift translateY −8 px + scale 1.00→1.02 over the hold, cursor moves 60–120 px between beats" and "slides out left while the next window slides in".
   - Fix:
     - Give every window hold a continuous drift (−8 px, 1.00→1.02, sine ease, never stopping).
     - Swap B→A and C→B as a 250–350 ms slide (old out left, new in from the right).
     - Draw a pointer in every window that travels 60–120 px to each named target 200 ms before its beat and parks next to it, not on it.

3. **[03.46–36.82] Caption look is the old heavy outline everywhere (captions agent + `helpers/captions_ass.py`).**
   - Evidence: master.ass is unchanged since round 2 (01:52). Style `Cap` is PrimaryColour white, Outline 4, Shadow 2, OutlineColour black, used for all 64 cues: the 56 panel cues on paper (3.46–33.86) and the 8 CTA cues over the wall and face (34.10–36.82).
   - Violates: "Caption look: on the paper panel plain ink, no outline, no shadow; over my face white with a 2 px edge and a soft shadow, never a heavy black outline."
   - Fix:
     - Re-run captions with the presets now in brand/style.json: panel = ink #141418, highlight flame, `\bord0\shad0`; face = white, 2 px edge, soft shadow.
     - Resolve the preset mismatch first: style.json `big` says `outline_px 1.5`, `outline_color ink`, but STYLE.md says 2 px.
     - There is no preset for graphic_full stretches. Add one: ink on paper, no outline, 96 px, band y 0.64–0.72.

4. **[08.50, 14.98, 16.74, 22.50, 34.58, 36.18, 00.00] Sync misses: named things with no mark, and text that appears before the word (planner beats + motion).**
   - Evidence: the change log, matched to transcript word times (output timeline). See the sync table under ALL PROBLEMS.
   - No mark on its own word:
     - "selectors" 8.50: the row label "Adaptive selectors" filled on "adaptive" 7.78.
     - "fetchers" 14.98: filled on "stealth".
     - "Claude Code" 22.50: the push lands on the `"scrapling"` entry, and nothing on screen says Claude Code.
     - "Scrape" 34.58: the pill showing "Scrape" already landed on "Comment" 34.10.
     - "steps" 36.18: the tagline "setup steps…" already landed on "send" 35.30.
   - Text before the spoken word:
     - The "Cloudflare" chip appears on "walls" 16.74, 0.72 s before "Cloudflare" (17.46).
     - "Claude" is on frame 0, 1.22 s before it is said. This was my own round-2 suggestion and it is wrong under the new rule; the planner should drop it.
     - The tagline shows "setup steps" 0.40 s before "setup" (35.70).
   - Violates: "Every named thing gets a visible mark on its own spoken word (box, flash, band, fill); nothing on screen changes on a word I did not say."
   - Fix:
     - Split the row fills: label first word on "adaptive" / "stealth", second word (or a band/flash on it) on "selectors" / "fetchers".
     - Chip pops blank on "walls" and its text types on "Cloudflare".
     - Add a "Claude Code" mark on 22.50 (a flame label tab "→ Claude Code" on the config window, or the window's title bar swapping to "Claude Code · mcp").
     - In the CTA: the pill pops empty on "Comment" with only the bubble glyph, its text "Scrape" lands on 34.58, and the tagline lands on "setup" 35.70. That also answers the open 1.2 s pill/tagline question: it becomes a fill of one element.
     - Hook: frame 0 = kicker only, or the hook goes face_full (fix 1).

5. **[script / recording] The spoken script still breaks the new script rules; this cannot be fixed in the edit (writer, then the user re-records).**
   - Evidence:
     - "First, adaptive selectors." (7.22), "Second, stealth fetchers." (13.54) and "Third, it ships an MCP server." are list fragments.
     - "The site changes your scrapers. Keep working." (9.54–13.38) is a broken sentence; the script meant "your scraper keeps working". Captions must print it word for word, so the viewer reads the broken grammar too.
     - There is no `videos/2026-11-17_scrapling/assets/`, so every window is a drawn mockup, not a real screen.
   - Violates: "Scripts are complete, natural spoken sentences; no telegraphic fragments, no dropped words; every named thing sits inside a sentence." Also "Every script ends with the list of assets … to capture into videos/<folder>/assets/ before I record."
   - Fix: the writer rewrites the script in full sentences with an assets list (ROADMAP #1, #2). The user records the take and captures the README, `.claude.json` mcpServers block and Claude Code session screenshots into `assets/`. There is no edit-side fix: captions must stay word for word, so this take should not become the reference reel.

## ALL PROBLEMS (ranked, with timecodes)

1. [00.00–34.10] One layout for 34.1 s; face on screen 100 %; hook not face_full; no graphic_full stretch. Scenery rule broken. (planner)
2. [03.78–34.10] No window drift: 16.9 s of motionless holds. (motion)
3. [21.54, 24.54] Window replacements are hard cut out + rise in, not slides. [03.46–03.78] The hook title fades and window A rises separately with an empty panel between (3.73–3.80). (motion)
4. [03.78–34.10] No pointer cursor at all. Window C has only a text caret. (motion)
5. [03.46–33.86] 56 panel cues are white with a 4 px black outline and 2 px shadow on paper, against "plain ink, no outline, no shadow". (captions)
6. [34.10–36.82] 8 CTA cues have a 4 px black outline over the wall and face, against "white with a 2 px edge and a soft shadow, never a heavy black outline". (captions)
7. [08.50] "selectors" has no mark. [14.98] "fetchers" has no mark. (planner, motion)
8. [22.50] "Claude Code" has no mark of its own; the zoom marks `"scrapling"`. (planner)
9. [16.74] The "Cloudflare" chip text shows 0.72 s before the word. (motion)
10. [00.00] "Claude" is on screen 1.22 s before it is said. (motion/planner)
11. [34.10 / 34.58] The pill shows "Scrape" on "Comment"; nothing lands on "Scrape". [35.30 / 35.70 / 36.18] The tagline shows "setup steps" on "send"; nothing lands on "steps". (motion)
12. [21.54, 24.54] Windows B and C enter in silences (21.54–21.78, 24.50–24.82), not on a word. Minor: the content does land on "Plug" / "scrape". (motion)
13. [07.22, 13.54, 18.74, 09.54–13.38] Script fragments and a broken sentence (STYLE line 49). Needs a re-record. (writer, user)
14. [whole reel] No `assets/` folder, so drawn mockups stand in for real screens (STYLE line 50, ROADMAP #2). (writer, user)
15. [rules] brand/style.json `captions.presets.big` = 1.5 px ink outline against the STYLE line's "2 px edge". There is no caption preset for graphic_full. The `layouts.graphic_full` entry has only a description: no panel colour, no dot grid, no caption band. The planner cannot plan graphic_full stretches consistently until this is filled in. (designer/user)
16. [rules] "Hard cuts only. No crossfades, no dissolves, no wipes" against "slide when one replaces another". motion.md §3 treats slides as element moves inside a shot, which is how I read it. Worth one clarifying clause in STYLE.md so a later critic does not flag window slides as wipes.
17. [34.10 / 35.30] Pill and tagline are two new elements 1.2 s apart. Still open (ROADMAP #11). Fix 4's empty-pill-then-fill design removes it.
18. [34.10–36.82] CTA captions are 100 px against the 120 px in STYLE line 15. Still open (ROADMAP #11).
19. [whole reel] No music (ROADMAP #9, open). The face is soft from the 1.78x upscale (ROADMAP #10, the user's call). Not counted against the verdict.

Sync table (named thing → mark on its own word?). Times are word onsets on the output timeline; "change" is the detected start of the panel change.

| word | onset | change | verdict |
|---|---|---|---|
| Claude (hook) | 1.22 | on frame 0 | early, text before word |
| Code (hook) | 1.70 | 1.60 | ok |
| lead / scraper | 2.34 / 2.74 | 2.23 / 2.63 | ok |
| Scrapling | 4.26 | 4.17 | ok |
| GitHub | 6.34 | 6.27–6.77 (repo line types) | ok |
| adaptive | 7.78 | 7.67 | ok |
| selectors | 8.50 | none | MISS |
| (changes) | 10.34 | 10.23 chip swap | ok |
| working | 12.82 | 12.73 check | ok |
| stealth | 14.34 | 14.23 | ok |
| fetchers | 14.98 | none | MISS |
| (walls) | 16.74 | 16.63, chip with "Cloudflare" text | early text |
| Cloudflare | 17.46 | 17.37 lock → check | ok |
| MCP | 20.18 | 20.07 | ok |
| (Plug) | 21.78 | 21.57–22.00 window B in + lines | ok-ish (enters in a silence) |
| Claude Code | 22.50 | 22.40, push on "scrapling" | wrong thing marked |
| (ask) | 24.02 | 23.93 placeholder blink | ok |
| scrape / this / directory | 24.82 / 25.46 / 25.70 | typed, 25.37 / 25.60 | ok |
| (picks) | 27.30 | 27.20 tool call | ok |
| CSS | 27.86 | 27.77 selector types | ok |
| selectors | 28.50 | 28.40 zoom | ok |
| table | 31.14 | 31.03 header + ease back | ok |
| name / site / email | 31.86 / 32.58 / 33.30 | 31.77 / 32.47 / 33.20 | ok |
| Scrape (CTA) | 34.58 | none (pill already says it at 34.10) | MISS + early text |
| steps | 36.18 | none (tagline already says it at 35.30) | MISS + early text |

Score: 19 named things, 13 marked on their word, 6 misses or early text.

## Proposed layout timeline (planner starting point)

All cuts are hard cuts, placed inside the transcript's silences (word times = source − 0.30).

| # | start | end | dur | layout | words | why |
|---|---|---|---|---|---|---|
| 1 | 0.00 | 3.42 | 3.4 | face_full | "One tool turns Claude Code into a lead scraper." | Hook is a personal line. Title words land on their onsets above the head (STYLE line 16: face is low, captions y ≈ 0.24). Cut in the 3.38–3.46 gap. |
| 2 | 3.42 | 7.10 | 3.7 | split_top | "It's called Scrapling. Open source on GitHub." | Name the thing beside me. README window slides in, title on "Scrapling", pill on "Open", repo on "GitHub". Cut in the 6.98–7.22 gap. |
| 3 | 7.10 | 13.46 | 6.4 | graphic_full | "First, adaptive selectors. The site changes your scrapers. Keep working." | Informational. Feature card 01 full frame: "Adaptive" on adaptive, "selectors" on selectors, DOM chip swap on "changes", check on "working". Drift throughout. Cut in the 13.38–13.54 gap. |
| 4 | 13.46 | 18.62 | 5.2 | graphic_full | "Second, stealth fetchers. They get past walls like Cloudflare." | Informational. Card 02 slides in over card 01 (window swap by slide): "stealth" / "fetchers" marks, a wall graphic on "walls", Cloudflare chip text on "Cloudflare". Cut in the 18.50–18.74 gap. |
| 5 | 18.62 | 23.38 | 4.8 | split_top | "Third, it ships an MCP server. Plug it into Claude Code." | Bridge back to me. Card 03 on "MCP", config window slides in on "Plug", a "Claude Code" mark on 22.50. Cut in the 23.30–23.46 gap. |
| 6 | 23.38 | 29.74 | 6.4 | graphic_full | "Then I ask, scrape this directory. It picks the CSS selectors." | Informational demo. Claude Code session full frame: prompt types with speech, tool call on "picks", selector on "CSS", push + ring on "selectors". Pointer moves prompt → tool call → selector. Cut in the 29.54–29.94 gap. |
| 7 | 29.74 | 33.98 | 4.2 | split_top | "Back comes a table, name, site, email," | Result reveal with my face reacting. Table builds on "table", rows on name/site/email. Cut in the 33.86–34.10 gap. |
| 8 | 33.98 | 37.03 | 3.0 | face_full | "Comment "Scrape" and I'll send you the setup steps." | CTA is a personal line. Pill pops empty on "Comment", "Scrape" fills on 34.58, tagline on "setup" 35.70 (one element, two fills). |

Result:
- Layout changes every 3.0–6.4 s (7 changes against 1 now).
- The face is on screen 21.9 s of 37.0 (59 %) against 100 %: full 6.4 s, split 12.7 s.
- The face is off for 18.0 s in three graphic_full stretches of ≤ 6.4 s.
- Stretches 2 and 8 are under 5 s by necessity (one sentence each). If the user wants a strict 5 s minimum, merge 1+2 (face_full 0–7.10, with the README card beside the face from 3.42).

## MEASURED
- Duration: 37.033 s (format) against 37.0. Video 37.000 s, 1110 frames, 30/1.
- Loudness (ebur128 on the mp4): integrated −14.3 LUFS, LRA 2.8 LU, true peak −1.4 dBTP.
- Per section RMS / peak (dBFS): hook −16.2 / −1.4 · readme −17.7 / −1.4 · config −17.8 / −1.5 · terminal −17.2 / −1.4 · cta −18.3 / −1.5.
- Ticks (now −6 dB in sound.json): peak −5.0, max 50 ms RMS −23.6 against speech −7.2 to −8.8. About 15–16 dB under the voice, audible. Whooshes, pop and impact unchanged from round 2 (≥ 7, 11–14.6 and 13.5 dB under).
- Layouts: 2 (split_top 34.1 s, face_full 2.9 s). Longest layout hold 34.1 s (rule 5–8 s). Face on screen 100 % (rule: personal lines only).
- Window motion: 9 completely still spans ≥ 1 s, 16.9 s total, longest 2.57 s (17.50–20.07). Drift 0 px. Pointer cursor: none. Window swaps: 2 hard cut + rise, 0 slides.
- Sync: 19 named things, 13 marked on their own word (−120 ms leads verified, changes start 90–110 ms before onset), 4 with no mark, 4 cases of text before its word (Claude 0.00, Cloudflare 16.74, Scrape 34.10, setup steps 35.30).
- Captions: 64 cues, all style `Cap` with a 4 px black outline and 2 px shadow (56 on paper, 8 over the wall and face). 0 cues match the new look.
- Graphics per 3 s: at most 2 (pill + tagline). SFX per 30 s: at most 6 (8 total).
- Never-show: clean (unchanged footage and mockups).
