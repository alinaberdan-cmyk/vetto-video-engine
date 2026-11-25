# Green-screen meme pop  (`greenscreen-meme`)

**Group:** Meme Chaos · **Status:** draft · **Source:** Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)

**Use it when:** claps, cheering, a reaction beat

**What it does:** A keyed green-screen meme clip (e.g. the clapping cat) pops in beside the person, plays, pops out.

**Layer:** over video · **Captions during it:** stay

**Sound that goes with it:** Crowd Applause (Vetto engine Sound step; files in `../../styles/meme-chaos/sounds/`)

## Fields (`params`)
- `clip`: Meme clip (folder in engine/hf/fx/memes; add more with library/add_meme_clip.py) (e.g. explosion)
- `position`: left, right, center or face (e.g. right)
- `size`: Height (share of the frame) (e.g. 0.36)
- `at`: Starts at (s into the 3 s piece) (e.g. 0)
- `hold`: How long it stays (s) (e.g. 1.25)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on the dumb-scale take (18 Nov 2026).
- Shared files in `../_shared/` (`texthook.js` has the `FX` helpers these effects use).

## Use in a project
```bash
python3 ../make_effect.py greenscreen-meme --piece piece.mp4 --text "your words" --out ./fx_greenscreen-meme
```
Extra inputs it needs: a keyed clip in `../_memes/<name>/` (make one with the engine's `library/add_meme_clip.py`).
