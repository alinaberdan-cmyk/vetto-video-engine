# Zoom + proof cards  (`over-the-shoulder-zoom`)

**Group:** Toggles & zoom · **Status:** from source · **Source:** neurofam PDF p.6

**Use it when:** proof, two numbers, before/after facts

**What it does:** Make a 'zoom and proof cards' effect in HyperFrames on [video] from second [start]: 1080x1920, 3 s. The camera pushes in smoothly on my face, scale 1 to 1.14; find the face yourself so the push lands on it. White rounded cards land beside the head: first left '[label]', a large orange '[number]', '[note]'. After half a second it leaves and a second card lands right with other '[label]', '[number]', '[note]'. Cards never cover the face. Word-by-word captions under the chin. Use only real numbers.

**Layer:** over video · **Needs:** face, numbers, transcript · **Captions during it:** stay

## Fields (`params`)
- `card1_label`: Card 1 label
- `card1_number`: Card 1 real number (required)
- `card1_note`: Card 1 note
- `card2_label`: Card 2 label
- `card2_number`: Card 2 real number (required)
- `card2_note`: Card 2 note

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take (not made: it needs real numbers or photos, never invented).
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py over-the-shoulder-zoom --piece piece.mp4 --text "your words" --out ./fx_over-the-shoulder-zoom
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: numbers.
