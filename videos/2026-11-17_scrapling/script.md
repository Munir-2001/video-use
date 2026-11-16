# Scrape leads with Claude Code (Scrapling)  ·  target 30 s · vertical · 2026-11-17

## Say this (read to camera)
One tool turns Claude Code into a lead (scraper).
It's called (Scrapling), open source on GitHub. [pause]
First, (adaptive) selectors. [pause]
The site changes, your scraper keeps (working).
Second, (stealth) fetchers. [pause]
They get past walls like (Cloudflare).
Third, it ships an (MCP) server. [pause]
Plug it into (Claude Code).
Then I ask: scrape this (directory). [pause]
It picks the CSS (selectors). [pause]
Back comes a (table). [pause] Name, site, email.
Comment "Scrape" and I'll send you the setup (steps).

74 words · about 30 s at 2.5 words/s with short pauses (31 s if the pauses run long; the editor trims the pauses, not the words).

## Beats → graphics (pre-plan for the planner)
Estimated times at 2.5 words/s; the planner replaces them with word times from the transcript. Layout is `split_top` from 0.0 to the CTA, then a hard cut to `face_full`. Each window is one element; the zoom beats are its internal changes (one change every 1.5–3 s, a new window never sooner than 3 s after the last).

| # | ~t (s) | words I say | what appears | card | layout | caption preset |
|---|---|---|---|---|---|---|
| 1 | 0.0–3.0 | "One tool turns Claude Code into a lead scraper." | Title on the paper panel, words land on their onsets: "Claude Code," then "lead *scraper*" (scraper in flame). Small kicker "Open source" above. | kinetic-title-accent-word | split_top | none (the title carries the words; no double text) |
| 2 | 3.0–6.0 | "It's called Scrapling, open source on GitHub." | Title cuts out; Window A (README recording) slides up 350 ms into the panel, already playing. Zoom beat 1 on the repo name `D4Vinci/Scrapling` on "Scrapling". | window-mockup-slide-up (live screen) | split_top | panel |
| 3 | 6.0–7.6 | "First, adaptive selectors." | Window A zoom beat 2: moves to the README line about adaptive selectors, flame ring. | window-mockup-slide-up (live screen) | split_top | panel |
| 4 | 7.6–10.4 | "The site changes, your scraper keeps working." | Hold on beat 2 (ring stays); the recording keeps playing inside (slow scroll is enough as the internal change). | window-mockup-slide-up (live screen) | split_top | panel |
| 5 | 10.4–12.0 | "Second, stealth fetchers." | Window A zoom beat 3: the README line on the stealth fetcher. | window-mockup-slide-up (live screen) | split_top | panel |
| 6 | 12.0–14.4 | "They get past walls like Cloudflare." | Hold on beat 3; if the word "Cloudflare" sits in a separate line, a small move (250 ms) to it counts as beat 4 of 4 for this window. | window-mockup-slide-up (live screen) | split_top | panel |
| 7 | 14.4–17.0 | "Third, it ships an MCP server." | Hard cut to Window B (the `mcpServers` block in `~/.claude.json`). Zoom beat 1 on the `"mcpServers"` key on "MCP". | window-mockup-slide-up (live screen) | split_top | panel |
| 8 | 17.0–19.0 | "Plug it into Claude Code." | Window B zoom beat 2: the `"scrapling"` entry inside the block. | window-mockup-slide-up (live screen) | split_top | panel |
| 9 | 19.0–22.2 | "Then I ask: scrape this directory." | Hard cut to Window C (Claude Code session); the prompt is visible being sent. Zoom beat 1 on the prompt line on "directory". | window-mockup-slide-up (live screen) | split_top | panel |
| 10 | 22.2–24.4 | "It picks the CSS selectors." | Window C zoom beat 2: the selector argument in the Scrapling tool call. | window-mockup-slide-up (live screen) | split_top | panel |
| 11 | 24.4–27.4 | "Back comes a table. Name, site, email." | Window C zoom beat 3: the result table on "table"; beat 4 (250 ms) onto the header row "name / site / email" on "Name". Eases back to 1.0 or hard-cuts at the end. | window-mockup-slide-up (live screen) | split_top | panel |
| 12 | 27.4–31.0 | "Comment "Scrape" and I'll send you the setup steps." | Hard cut to my face full. Big 2–3 word cues; "Scrape" in flame with quotes. Pill `Comment "Scrape"` slides up with the first cue; mono tagline "setup steps, sent to you" hard-appears on "send". Last frame may hard-cut back to beat 1's empty panel for the loop. | big-words-cta-caption | face_full | big (+ CTA pill, tagline) |

Zoom boxes for the planner (fractions of the screen recording, filled in from the clips): A1 repo name, A2 adaptive line, A3 stealth line, (A4 Cloudflare word), B1 `"mcpServers"`, B2 `"scrapling"` entry, C1 prompt, C2 selector argument, C3 table, C4 header row. Max 4 whooshes per window.

## Recording notes
- **Framing (face take):** vertical 9:16, phone at eye height, face in the lower half with eyes at ~0.62 of frame height, top half plain wall (it is covered by the paper panel). Record the CTA line ("Comment Scrape...") as a **separate take** with your eyes at ~0.38 so the big captions at y 0.64 sit on your chest, not your mouth. Hands below the chest during the CTA. Read the whole script in one go, then the CTA twice; the last complete attempt wins.
- **Pace / pauses / pointing:** brisk, ~2.5 words per second; a short beat (about half a second) at every [pause], never longer. Lean on the word in (parentheses). On "Scrapling", "MCP" and "table" glance or point up-left to the panel above your head (never toward the right edge, the platform UI lives there). Say "Scrape" in the CTA clearly and alone, it becomes the pill.
- **Screen recording (capture separately, three clips, nothing private in any frame):** close every other tab and app, notifications off (Do Not Disturb), no bookmarks bar, no desktop visible. Browser and terminal windows at about 1440x1100, browser zoom 150 %, terminal font 20 pt or larger, so each target is readable at 2.2x inside a 920x700 window. For each target: move the cursor next to it (not over it), **select/highlight the exact text**, hold perfectly still for 3 s, then move on. That highlighted span is the zoom box.
  1. **Clip A, GitHub README** (`github.com/D4Vinci/Scrapling`, logged out or in a private window so no avatar/notifications show): start at the top, hold 3 s on the repo name `D4Vinci/Scrapling` (target A1). Scroll slowly to the line that says the selectors are adaptive (survive site changes) and highlight it (A2). Scroll to the stealth fetcher line and highlight it, and the word "Cloudflare" if it is on a separate line (A3, A4). Scroll to the MCP server section and highlight its heading (spare shot for "MCP"). Do not hold on star counts; do not highlight any numbers.
  2. **Clip B, MCP registration:** open `~/.claude.json` in your editor, but show **only** the `"mcpServers"` block: fold or scroll so no other key is in view (that file holds your projects, history and account info; nothing else may appear). If that is hard, paste just the block into a new untitled file and record that. Highlight `"mcpServers"` (B1), hold 3 s; then highlight the `"scrapling"` entry with its command (B2), hold 3 s. Optional 3 s: in Claude Code, type `/mcp` and show scrapling listed as connected.
  3. **Clip C, Claude Code session:** fresh session in an empty demo folder (`/clear`, no history above), terminal scrolled to the top. Type and send: `Use the scrapling tool to fetch <public directory URL> and extract every company's name, website and email with CSS selectors. Return a table and save it as leads.csv.` Highlight the prompt (C1) after sending. When the Scrapling tool call appears, make sure the selector argument is visible (expand the tool call / transcript if it is collapsed) and highlight the selector string (C2), hold 3 s. When the table renders, hold 3 s on the whole table (C3), then highlight the header row `name | site | email` (C4), hold 3 s. Use a public directory of companies that shows generic company contact emails (info@, hello@) and allows scraping; if any personal email appears, it gets blurred in the edit. Nothing from clients or Innova.

## CTA
Comment "Scrape" and I'll send you the setup steps. · keyword "Scrape" · promise: the setup steps (install, the `mcpServers` block, the prompt) sent to you

## Assumptions
- Hook card: `kinetic-title-accent-word` on the split_top paper panel (ink text, "scraper" in flame), not `icon-grid-chapters`: there are only three named features, far under the ~12 items that card needs. The hook stays split_top (no reframe) so Window A can slide into the same panel on "Scrapling".
- Captions are off while the hook title is on screen, because the title repeats the spoken words (STYLE.md: no double text); panel captions resume on "It's called".
- Keyword "Scrape": one word, a verb, matches the angle, sentence case in the captions and pill.
- Claims are limited to the brief's verified facts: open source Python library, adaptive selectors, stealth fetchers past anti-bot walls like Cloudflare, bundled MCP server registered in `~/.claude.json`, Claude Code extracting with CSS selectors into a table. No star counts, no speed or success numbers, no "free" claim, and the crawl/scale fact is left out to keep one idea.
- "Lead scraper" in the hook is the angle's claim and is shown by beats 9-11; the demo directory must be a public one whose terms allow scraping (I name no specific site).
- The exact `mcpServers` entry is whatever the Scrapling README gives; this script does not invent the command line.
- Three separate windows (README, config, session) are hard cuts between each other; each stays ≥ 3 s, so the one-new-element-per-3-s rule holds, and each has at most 4 zoom beats.
- No `videos/*/edit/project.md` exists yet and `examples/` is empty, so pacing follows `brand/motion.md` section 5 and the cards only.
