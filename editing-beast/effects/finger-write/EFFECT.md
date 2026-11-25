# Written by my finger  (`finger-write`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** when you point or 'write' in the air

**What it does:** Yellow handwriting appears letter by letter near the raised hand, in two lines.

**Layer:** over video · **Needs:** a raised hand · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `color`: Accent colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py finger-write --piece piece.mp4 --text "your words" --out ./fx_finger-write
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
