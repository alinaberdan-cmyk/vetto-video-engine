# Handwriting on the word  (`handwriting-on-word`)

**Group:** From Alina's brief · **Status:** draft · **Source:** brief

**Use it when:** a key word to underline, circle or annotate

**What it does:** When I say '[WORD]', write it by hand on screen in [handwriting font] stroke by stroke over 0.4 s, with a scribbled underline or circle, in [ink colour]. Place it in empty space, never on the face.

**Layer:** over video · **Needs:** handwriting font · **Captions during it:** stay

## Fields (`params`)
- `text`: Written word
- `color`: Ink colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py handwriting-on-word --piece piece.mp4 --text "your words" --out ./fx_handwriting-on-word
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
