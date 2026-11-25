# Pixel words  (`screen-push-digital`)

**Group:** Match cut & pixels · **Status:** from source · **Source:** neurofam PDF p.5

**Use it when:** a short punchline of 3–4 words

**What it does:** Make a 'words on a pixel screen' effect in HyperFrames: 1080x1920, 3 s. Almost black background, an RGB sub-pixel grid over everything, as if the camera films a screen up close. Huge white words of the phrase '[PHRASE]' slide right to left, one word in frame at a time. Light glow, red and blue copies of the letters offset 3 px, motion blur. The last word stops in the centre by 1.6 s and flickers slightly until the end. Bold font, the longest word no wider than 890 px.

**Layer:** full screen insert · **Needs:** no video · **Captions during it:** hide

## Fields (`params`)
- `phrase`: Phrase (3–4 short words)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py screen-push-digital --piece piece.mp4 --text "your words" --out ./fx_screen-push-digital
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: no-video.
