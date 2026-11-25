# Big-face warp  (`face-warp`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** a group pose, a silly face, the ending

**What it does:** Every face swells into a big-nose fisheye face for ~1.9 s.

**Layer:** full frame · **Captions during it:** stay

**Sound that goes with it:** Vine boom (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `at`: Starts at (s into the 3 s piece) (e.g. 0)
- `hold`: How long it stays (s) (e.g. 1.85)
- `amount`: Strength (1 = as in Alina's edit) (e.g. 1)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py face-warp --piece piece.mp4 --text "your words" --out ./fx_face-warp
```
Extra inputs it needs: face boxes: pass every face with `--faces x,y,w,h;x,y,w,h`.
