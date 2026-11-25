# Light leak  (`light-leak`)

**Group:** Clean White · **Status:** draft · **Source:** Editing Beast style Clean White (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** a cut between two thoughts (max 3 per 15 s)

**What it does:** A cool (mint → lavender) or warm (yellow → red) leak sweeps across, or a white flash; punch-in under it.

**Layer:** full frame · **Captions during it:** stay

## Fields (`params`)
- `tone`: cool, warm or flash

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py light-leak --piece piece.mp4 --text "your words" --out ./fx_light-leak
```
Extra inputs it needs: none.
