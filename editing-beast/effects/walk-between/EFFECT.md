# Me between the words  (`walk-between`)

**Group:** Text hooks · **Status:** draft · **Source:** idea: @ugcwithnyomi TikTok 7679139537196567840

**Use it when:** standing or walking with room on both sides

**What it does:** The text splits into two columns, one on each side of me at chest height; I stand between them in front.

**Layer:** behind speaker · **Needs:** cutout, you in the middle · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py walk-between --piece piece.mp4 --text "your words" --out ./fx_walk-between
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: cutout.
