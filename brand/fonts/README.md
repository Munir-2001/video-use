# brand/fonts

| file | use | source | licence |
|---|---|---|---|
| Inter-ExtraBold.ttf | display: titles, captions | github.com/rsms/inter v4.1 (extras/ttf) | OFL 1.1 (LICENSE-Inter.txt) |
| Inter-Bold.ttf, Inter-SemiBold.ttf | body, kickers, pills | same | same |
| JetBrainsMono-Medium.ttf | mono: kickers, URL chips, code lines | github.com/JetBrains/JetBrainsMono v2.304 | OFL 1.1 (LICENSE-JetBrainsMono.txt) |
| InstrumentSerif-Italic.ttf, -Regular.ttf | serif: the one italic accent word in editorial titles / end cards | github.com/google/fonts ofl/instrumentserif | OFL 1.1 (LICENSE-InstrumentSerif.txt) |

`helpers/render.py` passes this folder to libass (`fontsdir`), so burned captions use Inter here even if it is not installed system-wide. HyperFrames bundles Inter and JetBrains Mono; the serif needs `@font-face` from `assets/fonts/` inside a slot (the motion agent copies it).
