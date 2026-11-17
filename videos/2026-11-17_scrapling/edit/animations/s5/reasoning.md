# s5 reasoning
Engine: HyperFrames 0.9.58, one composition (hf/index.html), `--format mov` (ProRes 4444 alpha), data-duration 4.76, `check` 0 errors. Card: window-mockup-slide-up (drawn paper version; no assets/ folder). Fonts: Inter and JetBrains Mono bundled; both render in the frames (no font file needed).
Clip time = output time - 18.62. Opaque paper + dot grid over y 0-960, transparent below. Windows at [48,192,892,640]; drift transform-origin is the window's right edge so the 1.02 scale never crosses x 940.
Timings (output s, each change starts 120 ms early): '03' pops 18.62-18.79; 'MCP' 20.06; 'server' + plug 20.78 (pop 170 ms); swap 21.66-21.96 (card 03 out left 300 ms power3.in, window B in from right 300 ms power3.out, lines draw top-down from 21.72, band on line 2 fades in 21.66); band to line 3 + tab pops + 'Claude' types 22.38-22.54; 'Code' types 22.86-22.98, dot to flame 22.86; push 1.3x on lines 3-5 lands at 22.98 (starts 22.63), line numbers fade out as it starts, ring 3 px flame 23.13-23.28. Hard cut at 23.38 (no exit).
Drift: card 03 0 -> 21.96, window B 22.08 -> 23.38, sine in-out, y 0->-8, scale 1->1.02.
Pointer (36 px-class arrow, ink, white edge, shadow), 300 ms power3.inOut travels arriving 200 ms before each word: beside '03' 18.54 (on frame 0), beside title 19.98, beside plug 20.70, line 2 21.98, scrapling line 22.30, tab 22.78; 2 px sway between.
Judgment calls:
- Landing: the push is 350 ms, so starting it 120 ms before 22.98 would not be landed on the landing frame (4.36). It starts 350 ms early (22.63, between 'Claude' and 'Code') so it is complete at 4.36; the tab/dot change still starts 120 ms early. The ring follows 150 ms after landing (4.51-4.66) so landing.png shows the push done and last.png the ring.
- Tab: scenes asks for a 'flame tab' and a dot that 'turns flame'; a flame-filled tab would hide a flame dot, so the tab is paper with a 2 px flame outline, the dot goes grey -> flame.
- Tab widened to 224 px (28 px text clipped at 210); ends x 898 at rest.
- Pointer travels exceed the 60-120 px guide on two hops (kicker -> title ~420 px, plug -> line 2 ~270 px, line 3 -> tab ~430 px) because the targets are that far apart in the layout.
- Line numbers stay hidden after the push until the cut.
- Placeholders command/args stay '…'; no real command invented. Kicker/title sized 30/80 px as in scenes.
- Nothing pre-shown: frame 0 is the empty card with the pointer only.
- No audio (sfx belong to the sound agent: whoosh at 21.78).
Frames: first.png (0), f_20.18.png (1.56), f_21.78.png (3.16, mid-swap), f_22.50.png (3.85), mid_zoom.png (4.2), landing.png (4.36), last.png (4.70).
ffprobe: codec_name=prores width=1080 height=1920 pix_fmt=yuva444p12le r_frame_rate=30/1 duration=4.766667
