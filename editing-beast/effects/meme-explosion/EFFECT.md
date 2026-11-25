# Meme explosion  (`meme-explosion`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** the first big move or reveal (one per video)

**What it does:** A green-screen fire ring (Pixabay video 221022, no watermark) bursts around the face + white flash + shake + punch zoom. Add the explosion sound.

**Layer:** full frame · **Captions during it:** stay

**Sound that goes with it:** Explosion · meme blast (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `at`: Starts at (s into the 3 s piece) (e.g. 0)
- `size`: Fire size (1.25 = as in the dumb-scale edit) (e.g. 1.25)
- `zoom`: Punch zoom (e.g. 1.18)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py meme-explosion --piece piece.mp4 --text "your words" --out ./fx_meme-explosion
```
Extra inputs it needs: the keyed clip `../_memes/explosion/` (copied by make_effect.py).
