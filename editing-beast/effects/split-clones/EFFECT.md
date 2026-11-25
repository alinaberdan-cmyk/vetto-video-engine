# Three offset copies (clones)  (`split-clones`)

**Group:** Phone & copies · **Status:** from source · **Source:** neurofam PDF p.8

**Use it when:** lots of gesturing, 'me, me and me', emphasis

**What it does:** Make a 'three copies of me' effect in HyperFrames: 1080x1920, 3 s. Three vertical strips of 352 px with dark 12 px gaps. Each holds [video], face centred and slightly larger. Strips are offset in time: left from second [start], middle 0.25 s later, right 0.5 s later. In the first 0.5 s the left strip slides in from the top, the right from the bottom, the middle is already there. Then the strips slowly drift in different directions. At 0.6 s a thin orange line slides under the middle strip.

**Layer:** full frame · **Needs:** gestures · **Captions during it:** stay

## Fields (`params`)
- none (it uses the selected words)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. This is the browser/HyperFrames version; the Vetto engine draws the final with engine/effects.py `split_clones` (ffmpeg).
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py split-clones --piece piece.mp4 --text "your words" --out ./fx_split-clones
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
