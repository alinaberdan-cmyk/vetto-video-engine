# You as a sticker  (`sticker-cutout`)

**Group:** Sticker & fly-through · **Status:** from source · **Source:** neurofam PDF p.9

**Use it when:** a reaction, a fun beat, 'made with…' tag

**What it does:** Make a 'me as a sticker' effect in HyperFrames on [video] from second [start]: 1080x1920, 3 s. Cut me out with `npx hyperframes remove-background`. At 0.05 s the room goes away, replaced by an orange background [#E8572A] with small dots and a vignette. I become a sticker: white outline about 14 px tight to the silhouette and a soft shadow. I 'peel off': shrink to 0.86 and rotate 4 degrees with a bounce, then sway slightly. At 0.5 s a white label with '[TEXT]' appears beside the head.

**Layer:** replaces background · **Needs:** cutout · **Captions during it:** stay

## Fields (`params`)
- `label`: Label beside the head
- `bg_color`: Background colour

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py sticker-cutout --piece piece.mp4 --text "your words" --out ./fx_sticker-cutout
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: cutout.
