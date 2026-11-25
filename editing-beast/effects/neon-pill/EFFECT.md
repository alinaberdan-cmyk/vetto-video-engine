# Neon pill  (`neon-pill`)

**Group:** Neon Dimension · **Status:** draft · **Source:** Editing Beast style Neon Dimension (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** the CTA or one stressed word per ~10 s

**What it does:** An outlined neon pill with skewed white caps at chest height, glow breathing.

**Layer:** over video · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `color`: Neon colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py neon-pill --piece piece.mp4 --text "your words" --out ./fx_neon-pill
```
Extra inputs it needs: none.
