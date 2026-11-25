# Hanging key word  (`hanging-keyword`)

**Group:** Cinema Lexicon · **Status:** draft · **Source:** Editing Beast style Cinema Lexicon (STYLE.md v1, approved 17 Nov 2026)

**Use it when:** 1 word in 4: the stressed or shouted word

**What it does:** The key word big (italic or CAPS), the small connector words hang off its corners; hard cuts on the words.

**Layer:** over video · **Captions during it:** hide

## Fields (`params`)
- `text`: Text (empty: the words you selected)
- `key`: Key word (empty: the longest)
- `caps`: CAPS instead of italic (yes / no)

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/`.

## Use in a project
```bash
python3 ../make_effect.py hanging-keyword --piece piece.mp4 --text "your words" --out ./fx_hanging-keyword
```
Extra inputs it needs: none.
