# Clap zoom pulse  (`clap-pulse`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** people clapping, a beat drop, any rhythm

**What it does:** On every clap the picture jumps in to 1.07 and settles back in 0.2 s; claps found in the sound.

**Layer:** full frame · **Captions during it:** stay

**Sound that goes with it:** Crowd Applause (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `strength`: Zoom on each clap (e.g. 1.07)
- `times`: Clap times (s, empty: found in the sound) (e.g. 0.5, 0.7, 0.9)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py clap-pulse --piece piece.mp4 --text "your words" --out ./fx_clap-pulse
```
Extra inputs it needs: clap times with `--param times=0.5,0.7,…` (the engine finds them in the sound).
