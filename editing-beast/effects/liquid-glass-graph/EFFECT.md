# Glass card with graph  (`liquid-glass-graph`)

**Group:** Carousel & glass · **Status:** from source · **Source:** neurofam PDF p.4

**Use it when:** a number, progress, growth, result

**What it does:** Make a 'liquid glass with graph' effect in HyperFrames over [video] from second [start]: 1080x1920, 3 s. In the lower half a glass card 840x470, radius 44: blurred background under it, light edge on top, dark at the bottom, soft shadow. Top-left small label '[LABEL]', right a large percentage counting 23, 48, 76, 92 over 2.2 s in whole numbers. A green graph line with fill climbs with the number, glowing dot at its tip. Above the card, word-by-word captions of my speech timed exactly (transcript).

**Layer:** over video · **Needs:** numbers, transcript · **Captions during it:** above-card

## Fields (`params`)
- `label`: Small label
- `numbers`: Your real numbers, in order (required)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take (not made: it needs real numbers or photos, never invented).
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py liquid-glass-graph --piece piece.mp4 --text "your words" --out ./fx_liquid-glass-graph
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: numbers.
