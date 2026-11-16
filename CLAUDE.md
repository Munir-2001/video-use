# Video studio (fork of browser-use/video-use)

Conversation-driven video editing, everything local and free. No paid APIs, ever.

## Read every session
- `STYLE.md` — my rules, one per line. Non-negotiable.
- `SKILL.md` — the editing process, hard rules, EDL format, and the "Studio additions" orchestration section.
- `brand/style.json` — fonts, colors, handle, caption style, PiP sizes, vocabulary fix-list.

## Read only when needed
- `HOW_IT_WORKS.md` — one video through the system. Read when asked "where are we?" or when lost.
- `DECISIONS.md` — why things are the way they are. Read before changing any tool, helper, agent or folder.
- `cards/` — style/motion/caption/sound cards. Read when planning graphics or matching a style. `cards/_inbox/` is raw drops; never read it except via "process the inbox".
- `examples/` — approved EDLs. Read only when writing a new EDL.
- `studio/` — the local dashboard (HTML/JS/CSS) served by `helpers/studio_ui.py`. Read only when changing the UI.
- `helpers/` — the scripts. Run with `.venv/bin/python helpers/<name>.py` after `source .envrc.studio` (libass ffmpeg on PATH, telemetry off).
- `.agents/skills/hyperframes*` — read inside the motion agent only.

## Never
- Never scan `videos/` or open raw clips unprompted. Inventory only the folder named in the command.
- Never call a paid API (HeyGen, ElevenLabs, any cloud model). Stop and say so if something needs one.
- Never edit upstream files except: `helpers/transcribe.py`, `helpers/render.py` (.ass only), `install.md`, `SKILL.md` (studio section), `.env.example`, `.gitignore`.

## Layout
- `videos/YYYY-MM-DD_slug/` raw clips at top level, `edit/` inside (upstream layout). `videos/index.md` one line per video.
- `videos/<folder>/voice/` separate recordings + `edit/brief.json` (mode voiceover | commentary | clips, offset, notes). Voiceover: cut the voice, clips are footage, `helpers/voiceover.py build`. Commentary: clip keeps its sound, voice rides on top.
- `brand/` style.json, `motion.md` (how things move: build / hold / change / exit; read by planner, motion, designer, critic), `fonts/`, `sfx/` (palette in its README), `music/`.
- `cards/` max 12 cards; `cards/_inbox/` drops + `links.md`.
- `examples/` max 10 approved EDLs, one-line note each in `examples/index.md`.

## Sub-agents (`.claude/agents/`)
| agent | model | does |
|---|---|---|
| writer | opus | writes `videos/<folder>/script.md` before I record: hook, named beats → cards, CTA, recording notes |
| editor | sonnet | picks takes, writes EDL ranges from takes_packed.md |
| planner | opus | decides layout per stretch, writes edit/scenes.json |
| motion | sonnet | builds one animation slot (HyperFrames or PIL+ffmpeg), parallel per slot |
| captions | sonnet | word-synced .ass captions, applied last |
| sound | sonnet | sfx placement + music duck + loudnorm, writes edit/sound.json |
| designer | opus | turns cards/_inbox drops into brand cards |
| critic | opus | final QC, roasts, ranks fixes |
| proofreader | haiku | proposes word-for-word transcript fixes the vocabulary missed |
Sub-agents never ask questions; they pick the obvious option and say so.

## Standing commands
- **"write a script for <topic>"** — writer agent → `videos/<date>_<slug>/script.md` (hook, beats mapped to cards, CTA, recording notes). I record from it, drop the clips, then "edit videos/<folder>".
- **"edit videos/<folder>"** — inventory → pre-scan → converse → strategy → WAIT for my yes → editor → planner → motion (parallel) + captions + sound → render → critic → fix loop (max 3) → preview.
- **"apply my notes"** — read `edit/feedback.json` or my message; update EDL/scenes; re-render only changed scenes; critic again.
- **"process the inbox"** — run the designer agent on `cards/_inbox/`.
- **"learn from my reviews"** — propose dated STYLE.md lines from repeated notes or "make this a rule"; apply only what I approve.
- **"where are we?"** — HOW_IT_WORKS.md in 5 lines, last 3 DECISIONS entries, status of every video from `videos/index.md`.
- **"open the studio"** — `.venv/bin/python helpers/studio_ui.py` → http://127.0.0.1:8765 (library, per-video timeline, cards, rules, decisions; notes saved to `edit/feedback.json`).
- Any change to tools, helpers, agents, folders or workflow: DECISIONS.md entry + HOW_IT_WORKS.md update in the same commit.
- Commit with clear messages. Never push unless told.
