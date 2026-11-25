# Disco lights  (`disco-lights`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** a dance move, a pose, a 'party' moment

**What it does:** A disco ball drops in, six colour beams sweep, colour spots wander, the room dims and flickers. Add the disco beat.

**Layer:** full frame · **Captions during it:** stay

**Sound that goes with it:** Disco beat (Alina) (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `at`: Starts at (s into the 3 s piece) (e.g. 0)
- `hold`: How long it stays (s) (e.g. 1.35)
- `ball_x`: Disco ball x (px, 540 = middle) (e.g. 540)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py disco-lights --piece piece.mp4 --text "your words" --out ./fx_disco-lights
```
Extra inputs it needs: none.
