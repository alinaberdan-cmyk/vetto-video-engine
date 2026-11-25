# Pulled out of the screen  (`pull-from-screen`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** when you hold a laptop or phone and 'pull' something out

**What it does:** The text sits small on the screen (black tilted label, yellow), then flies up and grows into a big yellow title.

**Layer:** over video · **Needs:** a laptop or phone in shot · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `screen`: Where the screen is: left, middle or right
- `color`: Accent colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py pull-from-screen --piece piece.mp4 --text "your words" --out ./fx_pull-from-screen
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
