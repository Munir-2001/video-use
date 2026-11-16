# brand/sfx — sound effect palette

Empty until I add files. The sound agent only uses what is here; if a slot in the palette is empty it skips that effect and says so.

Name files exactly like this (wav or mp3, 48 kHz preferred):

| file | use |
|---|---|
| `whoosh_short.wav` | a graphic enters or leaves fast (≤ 300 ms) |
| `whoosh_long.wav` | a full-frame transition or big reveal |
| `click.wav` | a cursor click, a toggle, a checkbox |
| `tick.wav` | list items appearing one by one, counters |
| `pop.wav` | a word, number or badge pops in |
| `soft_impact.wav` | a card or title lands |
| `riser.wav` | the second before a payoff |
| `ding.wav` | a result, a success, a checkmark |

Rules live in `STYLE.md`: max ~8 effects per 30 s, each tied to a visible event, start before the contact frame by the effect's attack time.

Free sources: freesound.org (check each licence; CC0 preferred), or record your own.
