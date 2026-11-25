# Open-hand reveal  (`open-hand-reveal`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** when your hands open apart, one up and one down

**What it does:** Yellow text revealed between the hands, growing from the middle line outward.

**Layer:** over video · **Needs:** hands opening apart · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `color`: Accent colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py open-hand-reveal --piece piece.mp4 --text "your words" --out ./fx_open-hand-reveal
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
