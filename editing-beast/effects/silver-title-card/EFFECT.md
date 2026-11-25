# Silver title card  (`silver-title-card`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Editing Beast style Cinema Lexicon (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** the opening question or the closing line (bookend)

**What it does:** Brand-colour words fly in on silver, sizes jump, one script word, star glyph; the speaker grows out of a rounded card.

**Layer:** full frame · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `color`: Brand colour
- `glyph`: Star glyph (yes / no)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py silver-title-card --piece piece.mp4 --text "your words" --out ./fx_silver-title-card
```
Extra inputs it needs: none.
