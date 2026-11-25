# App buttons drop  (`lexicon-ui-drop`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)

**Use it when:** the product's categories, menu, filters

**What it does:** The take goes soft-blurred; the app's real buttons (same colours, black outline, offset shadow, icons) fall one by one and bounce into a pile.

**Layer:** over video · **Captions during it:** upper

## Fields (`params`)
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
python3 ../make_effect.py lexicon-ui-drop --piece piece.mp4 --text "your words" --brand path/to/brand --out ./fx_lexicon-ui-drop
```
Extra inputs it needs: brand kit with buttons.
