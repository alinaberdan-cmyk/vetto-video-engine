# Wavy sparkle hook  (`wavy-sparkle-hook`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** the opening question (first 3–5 s)

**What it does:** Bubbly rounded title (Coiny, white, thick dark-green outline) on the chest; letters pop in one by one, then float on a wave; 10 sparkles twinkle.

**Layer:** over video · **Captions during it:** stay

**Sound that goes with it:** Spawn (on the first face) (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `text`: Hook text ("/" = line break; empty: the words you selected) (e.g. who's the dumbest / in our office?)
- `color`: Outline colour (e.g. #1C5428)
- `hold`: How long it stays (s) (e.g. 2.9)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py wavy-sparkle-hook --piece piece.mp4 --text "your words" --out ./fx_wavy-sparkle-hook
```
Extra inputs it needs: none.
