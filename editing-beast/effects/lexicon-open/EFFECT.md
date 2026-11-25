# Brand open card  (`lexicon-open`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)

**Use it when:** the first call to action or claim (first 4 s)

**What it does:** The brand's cream card: a script word in the accent colour, small words, the object in huge caps fly in one by one; the app's phone rises tilted, its buttons and icon pop; all whip off left with blur.

**Layer:** full frame · **Captions during it:** hide

## Fields (`params`)
- `script`: Script word (accent colour)
- `small`: Small words
- `big`: Huge words (CAPS)
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
python3 ../make_effect.py lexicon-open --piece piece.mp4 --text "your words" --brand path/to/brand --out ./fx_lexicon-open
```
Extra inputs it needs: brand kit (optional).
