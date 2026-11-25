# Neon key word  (`neon-keyword`)

**Group:** Neon Dimension · **Status:** draft · **Source:** Editing Beast style Neon Dimension (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** a claim, number, problem or result

**What it does:** The room goes dark in one neon colour, a small lead-in builds, the key word slams in (Anton, skewed, glowing).

**Layer:** full frame · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `key`: Key word (empty: the last word)
- `neon`: Neon: green (money, yes), red (problem), cyan (calm, tech), purple (AI, game), pink, gold

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py neon-keyword --piece piece.mp4 --text "your words" --out ./fx_neon-keyword
```
Extra inputs it needs: none.
