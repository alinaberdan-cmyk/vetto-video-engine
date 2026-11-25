# Freeze-frame + punch  (`freeze-frame`)

**Group:** New (16 Nov) · **Status:** draft · **Source:** idea: lemo-opuscar freeze grammar

**Use it when:** the punchline, a reaction, 'wait for it', the moment to remember

**What it does:** White flash 0.14 s, the frame freezes and pushes in 1.0 → 1.12, colour drops to 45 %, corner brackets and a label chip; lets go at 2.4 s.

**Layer:** full frame · **Needs:** the word · **Captions during it:** stay

## Fields (`params`)
- `label`: Label on the freeze

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py freeze-frame --piece piece.mp4 --text "your words" --out ./fx_freeze-frame
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: freeze.
