# Brand close card  (`lexicon-close`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)

**Use it when:** the last line of an ad (not for interviews or opinion pieces)

**What it does:** The take shrinks into a rounded card on cream; app icon + name on top, chat bubbles pop around it, the slogan fades in; the last frame is held.

**Layer:** full frame · **Captions during it:** dark

## Fields (`params`)
- `name`: Name next to the icon (empty: the brand's)
- `slogan`: Slogan (empty: the brand's)
- `bubbles`: Chat bubbles (yes / no)
- `hold`: how long the graphic stays before the take is back (s)

## Brand kit
Colours, display font, icon, app screens and the product's real buttons come from a brand kit folder
(`brand.json`, see the Vetto engine's `engine/brand.py`). Without one, the cards use cream `#FCF0D4` and magenta `#E028B0`.

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py lexicon-close --piece piece.mp4 --text "your words" --brand path/to/brand --out ./fx_lexicon-close
```
Extra inputs it needs: brand kit (optional).
