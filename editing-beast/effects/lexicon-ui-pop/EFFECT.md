# App button pops  (`lexicon-ui-pop`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)

**Use it when:** a button of the product is named or tapped

**What it does:** That button, in its own colours, springs in tilted high in the frame and leaves before the cut. Click + pop.

**Layer:** over video · **Captions during it:** stay

## Fields (`params`)
- `label`: Button (a button of the brand kit)
- `hold`: How long it stays (s)
- `hold`: how long the graphic stays before the take is back (s)

## Brand kit
Colours, display font, icon, app screens and the product's real buttons come from a brand kit folder
(`brand.json`, see the Vetto engine's `engine/brand.py`). Without one, the cards use cream `#FCF0D4` and magenta `#E028B0`.

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py lexicon-ui-pop --piece piece.mp4 --text "your words" --brand path/to/brand --out ./fx_lexicon-ui-pop
```
Extra inputs it needs: none.
