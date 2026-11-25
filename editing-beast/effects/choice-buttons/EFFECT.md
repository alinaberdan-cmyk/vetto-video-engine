# Choice buttons  (`choice-buttons`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Editing Beast style Cinema Lexicon (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** 'this or that' moments

**What it does:** Two outlined pills with 'or' between; the chosen one fills with the brand colour.

**Layer:** over video · **Captions during it:** hide

## Fields (`params`)
- `a`: Button 1
- `b`: Button 2
- `chosen`: Chosen button (1 or 2)
- `color`: Brand colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py choice-buttons --piece piece.mp4 --text "your words" --out ./fx_choice-buttons
```
Extra inputs it needs: none.
