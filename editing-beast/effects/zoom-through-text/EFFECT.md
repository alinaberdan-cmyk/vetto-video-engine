# Fly through a letter  (`zoom-through-text`)

**Group:** Sticker & fly-through · **Status:** from source · **Source:** neurofam PDF p.9

**Use it when:** opening transition, the title of the clip

**What it does:** Make a 'fly through a letter' effect in HyperFrames: 1080x1920, 3 s. Black frame, a huge word '[WORD]' full width in the centre. The letters are windows: through them you see [video] from second [start]; around the letters is black. Thin light outline on the letters. The camera accelerates into the thick part of the letter 'A'. In 0.95 s the letter fills the screen and only my video remains. Then the scale settles softly from 1.06 to 1. Smooth letter edges.

**Layer:** transition · **Needs:** word with a thick letter · **Captions during it:** stay

## Fields (`params`)
- `word`: Word to fly through

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py zoom-through-text --piece piece.mp4 --text "your words" --out ./fx_zoom-through-text
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
