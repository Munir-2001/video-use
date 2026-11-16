# brand/sfx — sound effect palette

Filled 2026-11-16 from the Pixabay set bundled with the HyperFrames media-use skill (Pixabay Content License, no attribution required; see CREDITS.md). The sound agent only uses what is here; if a slot in the palette is empty it skips that effect and says so.

Name files exactly like this (wav or mp3, 48 kHz preferred):

| file | use |
|---|---|
| `whoosh_short.mp3` | a graphic enters or leaves fast (≤ 300 ms) |
| `whoosh_long.mp3` | a full-frame transition or big reveal |
| `click.mp3` | a cursor click, a toggle, a checkbox |
| `tick.mp3` | list items appearing one by one, counters |
| `pop.mp3` | a word, number or badge pops in |
| `soft_impact.mp3` | a card or title lands |
| `riser.mp3` | the second before a payoff |
| `ding.mp3` | a result, a success, a checkmark |

Extras (use sparingly, same rules): `extra_typing.mp3` (typewriter / typed prompt, loop under the typing only), `extra_key_press.mp3`, `extra_sparkle.mp3` (a highlight ring or a star mark), `extra_chime.mp3` and `extra_notification.mp3` (a result or a message arriving), `extra_glitch_1.mp3` (a hard-cut accent, max once per reel), `extra_impact_bass_1.mp3` (a hero title slam, max once per reel), `extra_whoosh_cinematic.mp3` (a big reveal). `soft_impact.mp3` is a bass hit: mix it at −12 dB or lower.

Rules live in `STYLE.md`: max ~8 effects per 30 s, each tied to a visible event, start before the contact frame by the effect's attack time.

Free sources: freesound.org (check each licence; CC0 preferred), or record your own.
