# Swipe chip  (`lexicon-swipe`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)

**Use it when:** 'swipe left / right'

**What it does:** A round chip (✕ red or ♥ brand colour) flies off the frame in the swipe direction.

**Layer:** over video · **Captions during it:** stay

## Fields (`params`)
- `dir`: left (✕) or right (♥)
- `hold`: how long the graphic stays before the take is back (s)

## Brand kit
Colours, display font, icon, app screens and the product's real buttons come from a brand kit folder
(`brand.json`, see the Vetto engine's `engine/brand.py`). Without one, the cards use cream `#FCF0D4` and magenta `#E028B0`.

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py lexicon-swipe --piece piece.mp4 --text "your words" --brand path/to/brand --out ./fx_lexicon-swipe
```
Extra inputs it needs: none.
