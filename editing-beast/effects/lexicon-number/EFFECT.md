# Giant number  (`lexicon-number`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)

**Use it when:** a number with its unit ('10 minutes', '3 steps', '50%')

**What it does:** Cream card: a small lead-in, the number huge in the accent colour sliding in from the right with motion blur, the unit under it.

**Layer:** full frame · **Captions during it:** hide

## Fields (`params`)
- `lead`: Small line above
- `number`: The number
- `unit`: Unit under it
- `t_number`: Number slides in at (s)
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
python3 ../make_effect.py lexicon-number --piece piece.mp4 --text "your words" --brand path/to/brand --out ./fx_lexicon-number
```
Extra inputs it needs: none.
