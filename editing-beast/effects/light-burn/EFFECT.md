# Light burn  (`light-burn`)

**Group:** Neon Dimension · **Status:** draft · **Source:** Editing Beast style Neon Dimension (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** every presenter ↔ world change

**What it does:** White light burn with warm edges, then the shot zoom-blurs in; or a 4-frame glitch.

**Layer:** full frame · **Captions during it:** stay

## Fields (`params`)
- `kind`: burn or glitch

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py light-burn --piece piece.mp4 --text "your words" --out ./fx_light-burn
```
Extra inputs it needs: none.
