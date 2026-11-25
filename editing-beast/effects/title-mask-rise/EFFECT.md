# Masked title rise  (`title-mask-rise`)

**Group:** New (16 Nov) · **Status:** draft · **Source:** values: mengto/skills html-reel (MIT)

**Use it when:** the hook, a chapter title, the payoff word

**What it does:** Italic serif setup line, then a huge condensed payoff word; each word rises from 135 % inside its own mask in 0.32 s, shrinking stagger.

**Layer:** over video · **Needs:** a short title · **Captions during it:** lower-only

## Fields (`params`)
- `setup`: Setup line (small, italic, optional)
- `word`: Payoff word (huge)
- `color`: Accent dot colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py title-mask-rise --piece piece.mp4 --text "your words" --out ./fx_title-mask-rise
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
