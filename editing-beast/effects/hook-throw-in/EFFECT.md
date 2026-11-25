# Thrown-in title  (`hook-throw-in`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** the opening line, the topic of the video

**What it does:** Title thrown in from the top-right corner, lands at chest height; a small yellow line wipes in under it; three spark strokes pop at its corner.

**Layer:** over video · **Needs:** a short title · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `subline`: Small yellow line under it (empty: words 3+ of the text)
- `color`: Accent colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py hook-throw-in --piece piece.mp4 --text "your words" --out ./fx_hook-throw-in
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
