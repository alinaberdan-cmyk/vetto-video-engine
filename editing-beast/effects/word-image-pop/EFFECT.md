# Image on the word that names it  (`word-image-pop`)

**Group:** From Alina's brief · **Status:** draft · **Source:** brief

**Use it when:** every noun that has a matching photo

**What it does:** When I say '[WORD]', pop the matching image from [images] next to my head (never on the face) with a white 6 px frame, slight tilt and a spring. Hold it while the word and the next 2–3 words are spoken, then slide it out.

**Layer:** over video · **Needs:** images · **Captions during it:** stay

## Fields (`params`)
- none (it uses the selected words)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. This is the browser/HyperFrames version; the Vetto engine draws the final with engine/render.py stage 3 image overlay (ffmpeg).
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py word-image-pop --piece piece.mp4 --text "your words" --out ./fx_word-image-pop
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
