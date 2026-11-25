# Video in a 3D phone  (`phone-3d-float`)

**Group:** Phone & copies · **Status:** from source · **Source:** neurofam PDF p.8

**Use it when:** showing an app, a screen recording, 'look at this'

**What it does:** Make a 'video in a 3D phone' effect in HyperFrames: 1080x1920, 3 s. Dark warm background with soft orange side light. In the centre a logo-free smartphone drawn in code: rounded body, metal edge, camera cutout. On its screen [video] from second [start]. The phone starts rotated 38 degrees on the vertical axis and 12 on the horizontal; over 0.9 s it turns to face the camera and a glare sweeps the glass. Then it floats up and down 10 px and slowly approaches. A soft shadow under it moves with it.

**Layer:** full frame · **Needs:** video or screen recording · **Captions during it:** hide

## Fields (`params`)
- none (it uses the selected words)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py phone-3d-float --piece piece.mp4 --text "your words" --out ./fx_phone-3d-float
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
