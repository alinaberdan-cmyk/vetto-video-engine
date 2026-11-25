# Windows XP background  (`xp-background`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** a pose with the Windows XP sound; anything 'old internet'

**What it does:** The room behind the person turns into a blue-sky, green-hill desktop wallpaper (drawn in code) while they pose.

**Layer:** behind speaker · **Captions during it:** stay

**Sound that goes with it:** Windows XP Start (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `at`: Starts at (s into the 3 s piece) (e.g. 0)
- `hold`: How long it stays (s) (e.g. 1.3)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py xp-background --piece piece.mp4 --text "your words" --out ./fx_xp-background
```
Extra inputs it needs: cutout (`assets/cut.webm`).
