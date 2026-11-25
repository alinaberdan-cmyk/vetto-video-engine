# iOS toggles  (`apple-ui-toggles`)

**Group:** Toggles & zoom · **Status:** from source · **Source:** neurofam PDF p.6

**Use it when:** steps, pros, a 3-item list

**What it does:** Make an 'iOS toggles' effect in HyperFrames over [video] from second [start]: 1080x1920, 3 s. A white card like iPhone Settings, centred in the lower half. Three rows: '[LINE 1]', '[LINE 2]', '[LINE 3]', thin dividers. A real iOS switch on the right of each row: track 102x62, white knob with shadow. The card appears in 0.25 s. Switches turn on in turn at 0.3, 0.8 and 1.3 s: the knob overshoots slightly, the track turns green #34C759. Darken the video under the card slightly.

**Layer:** over video · **Needs:** 3 short lines · **Captions during it:** upper

## Fields (`params`)
- `line1`: Row 1
- `line2`: Row 2
- `line3`: Row 3

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py apple-ui-toggles --piece piece.mp4 --text "your words" --out ./fx_apple-ui-toggles
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
