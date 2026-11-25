# Clean-white card  (`white-card`)

**Group:** Clean White · **Status:** draft · **Source:** Editing Beast style Clean White (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** an intro or name card, a shaky part of the take

**What it does:** The clip shrinks into a rounded card on brushed silver with a magenta glow; a small statement inside.

**Layer:** full frame · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `italic`: Italic serif word under it (empty: the last word)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py white-card --piece piece.mp4 --text "your words" --out ./fx_white-card
```
Extra inputs it needs: none.
