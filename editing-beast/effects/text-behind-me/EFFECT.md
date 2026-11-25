# Word behind me  (`text-behind-me`)

**Group:** Word & notifications · **Status:** from source · **Source:** neurofam PDF p.7

**Use it when:** the one word the clip is about (4–7 letters)

**What it does:** Make a 'word behind me' effect in HyperFrames: vertical 1080x1920, 3 s. Video: [video] from second [start]. Cut me out with `npx hyperframes remove-background`. Layers in order: room, the huge word '[WORD]', me on top. The word spans the full frame width, about 350 px tall, at the top of my head so my head covers the bottom of the letters. Milky colour, light warm glow. In the first 0.45 s the letters rise one by one from under a mask, then the word slowly drifts up 20 px. Darken the room slightly, clean cutout edges with no halo.

**Layer:** behind speaker · **Needs:** cutout · **Captions during it:** stay

## Fields (`params`)
- `word`: Word behind you (4–7 letters reads best)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. This is the browser/HyperFrames version; the Vetto engine draws the final with engine/effects.py `text_behind_me` (ffmpeg + libass over a HyperFrames cutout).
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py text-behind-me --piece piece.mp4 --text "your words" --out ./fx_text-behind-me
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: cutout.
