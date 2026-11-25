# VHS glitch  (`vhs-glitch`)

**Group:** New (16 Nov) · **Status:** draft · **Source:** idea: lemo-opuscar CRT post (MIT)

**Use it when:** a throwback, 'back in the day', a plot twist, a chaotic beat

**What it does:** Red and blue split, scanlines, moving noise, tracking wobble and a short roll at the start, for 3 s.

**Layer:** full frame · **Needs:** nothing extra · **Captions during it:** stay

## Fields (`params`)
- none (it uses the selected words)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. This is the browser/HyperFrames version; the Vetto engine draws the final with engine/effects.py `vhs_glitch` (ffmpeg).
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py vhs-glitch --piece piece.mp4 --text "your words" --out ./fx_vhs-glitch
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
