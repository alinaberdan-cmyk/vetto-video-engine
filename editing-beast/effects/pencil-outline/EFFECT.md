# Pencil outline on an object  (`pencil-outline`)

**Group:** From Alina's brief · **Status:** draft · **Source:** brief

**Use it when:** the word that names an object you hold or point at

**What it does:** On [video] from second [start], when I say '[WORD]', draw a hand-drawn pencil outline around [object] in the frame: graphite texture, slightly wobbly line drawn on over 0.5 s, small arrow and handwritten label '[WORD]'. Track the object if it moves. Keep it 1.5 s, then erase.

**Layer:** over object · **Needs:** object mask · **Captions during it:** stay

## Fields (`params`)
- `label`: Handwritten label

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py pencil-outline --piece piece.mp4 --text "your words" --out ./fx_pencil-outline
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
