# Carousel around me  (`pov-carousel-spin`)

**Group:** Carousel & glass · **Status:** from source · **Source:** neurofam PDF p.4

**Use it when:** a list, many examples, 'all my…' moments

**What it does:** Make a 'carousel around me' effect in HyperFrames: vertical 1080x1920, 3 seconds. Video: [video] from second [start]. Cut me out of the background with `npx hyperframes remove-background` and lay the cutout exactly over the source. 8 cards (4:5) from [images] spin in a ring around me. Ring centre at chest height, slight tilt so it reads as a ring. Cards behind me are hidden by me, cards in front pass over me but never cover the face. In the first 0.6 s the cards fly out from behind me into the ring, then the ring rotates about 110 degrees per second. Darken the background slightly.

**Layer:** around speaker · **Needs:** cutout, images:8 (4:5) · **Captions during it:** stay

## Fields (`params`)
- none (it uses the selected words)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take (not made: it needs real numbers or photos, never invented).
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py pov-carousel-spin --piece piece.mp4 --text "your words" --out ./fx_pov-carousel-spin
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: cutout, images.
