# Match cut on one word  (`match-cut`)

**Group:** Match cut & pixels · **Status:** from source · **Source:** neurofam PDF p.5

**Use it when:** the key word / brand name; a transition between your clips

**What it does:** Make a match-cut effect in HyperFrames: 1080x1920, 3 s, no video. 16 article pages change with hard cuts every 0.12–0.2 s. On every page the word '[WORD]' sits exactly in the centre on a red-orange highlight; only the text around it changes. Pages differ: typewriter, serif newspaper, grotesque, different paper shades and text sizes. Very close up: lines cropped by the frame edges, more blur further from the centre, light vignette and paper grain. On every cut the camera jolts 6 px and slowly pushes in the whole time. Invent the article texts about [topic], no publication names or figures.

**Layer:** full screen insert · **Needs:** no video · **Captions during it:** hide

## Fields (`params`)
- `word`: Word in the highlight
- `topic_text`: Article text (empty: your own words from the video)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py match-cut --piece piece.mp4 --text "your words" --out ./fx_match-cut
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: no-video.
