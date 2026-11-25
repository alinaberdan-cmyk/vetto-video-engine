# App screen in a phone  (`lexicon-phone-demo`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)

**Use it when:** 'look how many options', scrolling, browsing the product

**What it does:** The official screen recording in a black phone frame on the brand's cream card, three app buttons popping around it.

**Layer:** full frame · **Captions during it:** dark

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
python3 ../make_effect.py lexicon-phone-demo --piece piece.mp4 --text "your words" --brand path/to/brand --out ./fx_lexicon-phone-demo
```
Extra inputs it needs: brand kit with a screen video or screenshot.
