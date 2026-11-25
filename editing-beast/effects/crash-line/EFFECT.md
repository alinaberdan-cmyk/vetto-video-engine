# Crash line + logo  (`crash-line`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** 'it's going down', a fall, a loss, a fail

**What it does:** A logo badge pops at the raised hand, then a red stock-crash zigzag draws down and off screen, the badge riding its tip.

**Layer:** over video · **Captions during it:** stay

**Sound that goes with it:** Fahh / Faaa (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `text`: Badge text if the image bank has no logo (e.g. brand)
- `direction`: Falls to the left or right (e.g. left)
- `draw_at`: Line starts at (s) (e.g. 0.95)
- `x`: Start x (px; empty: the raised hand)
- `y`: Start y (px)
- `at`: Starts at (s into the 3 s piece) (e.g. 0)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py crash-line --piece piece.mp4 --text "your words" --out ./fx_crash-line
```
Extra inputs it needs: optional: a logo PNG with `--image logo.png`.
