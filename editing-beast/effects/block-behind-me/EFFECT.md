# Text I move under  (`block-behind-me`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** when you duck, walk or lean into the frame

**What it does:** A tight three-line block hangs at head height; I move under and through it, my body covers the letters.

**Layer:** behind speaker · **Needs:** cutout, moving in the frame · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `lines`: Lines (2–4)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py block-behind-me --piece piece.mp4 --text "your words" --out ./fx_block-behind-me
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: cutout.
