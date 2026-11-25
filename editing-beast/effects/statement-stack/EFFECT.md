# Statement stack  (`statement-stack`)

**Group:** Clean White · **Status:** draft · **Source:** Editing Beast style Clean White (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** the 3–6 key phrases of a clip

**What it does:** 2–4 tight staggered lines, heavy sans + an italic serif last line, white glow; each word blurs in when said.

**Layer:** over video · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `side`: Side: auto, left, right
- `focus`: Blur the background while it builds (yes / no)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py statement-stack --piece piece.mp4 --text "your words" --out ./fx_statement-stack
```
Extra inputs it needs: none.
