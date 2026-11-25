# Green-screen cutout (any background)  (`greenscreen-cutout`)

**Group:** From Alina's brief · **Status:** draft · **Source:** brief

**Use it when:** 'imagine I'm in…', location jokes, swapping the room

**What it does:** Cut me out of [video] from second [start] with `npx hyperframes remove-background` and place me over [background], matching light and adding a soft contact shadow.

**Layer:** replaces background · **Needs:** cutout, background image or video · **Captions during it:** stay

## Fields (`params`)
- `image_index`: Background: photo number in your bank (1 = first)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take (not made: it needs real numbers or photos, never invented).
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py greenscreen-cutout --piece piece.mp4 --text "your words" --out ./fx_greenscreen-cutout
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: cutout, images.
