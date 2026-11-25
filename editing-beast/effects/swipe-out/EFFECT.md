# Swipe out  (`swipe-out`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** a closing line you swipe away

**What it does:** The text pops out of the hand, jumps to the top-left, holds, then slides out of frame with a skew and blur.

**Layer:** over video · **Needs:** a swipe at the end · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py swipe-out --piece piece.mp4 --text "your words" --out ./fx_swipe-out
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
