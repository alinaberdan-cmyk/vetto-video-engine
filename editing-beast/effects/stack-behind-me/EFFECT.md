# Stacked words behind me  (`stack-behind-me`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** a 2–6 word statement you want to land word by word

**What it does:** One huge word per line, stacked around the head, each popping in when said, one word yellow; I stay in front.

**Layer:** behind speaker · **Needs:** cutout, 2–6 words · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `highlight`: Word in yellow (empty: the 2nd word)
- `color`: Accent colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py stack-behind-me --piece piece.mp4 --text "your words" --out ./fx_stack-behind-me
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: cutout.
