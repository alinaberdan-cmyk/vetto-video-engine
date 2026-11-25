# Vetto Video Engine

A local video editor for short-form social videos (Reels, TikTok, Shorts). You drop in a raw talking-head take; the engine
transcribes it, proposes the cut, and edits it in a named **editing style**, with captions, text effects, transitions,
sound effects, music, B-roll, memes and GIFs. Every choice is a proposal you approve, change or remove, step by step,
before anything is exported. One button, **Edit now**, hands the whole edit to Claude, which builds it the way it would if
you pasted the video into a chat.

It runs entirely on your Mac (Apple Silicon). Your footage never leaves the machine; the only network calls are searches
for stock clips (Pexels), GIFs (GIPHY), Pinterest pin links you paste, and the Claude run when you press Edit now.

---

## How the whole system works

```
raw take ──► transcription ──► cut by word ──► style ──► hook ──► effects ──► memes ──► text ──► sound ──► outputs
 (Footage)    (MLX Whisper,      (fillers,      (Editing   (text    (on words,  (GIFs +   (fonts,   (sfx +    (reel,
              word timestamps)    retakes,       Beast      hook     previews   pictures  colours,  music     stories,
                                  pauses)        styles)    styles)  on your    on your   boxes)    by vibe)  carousel)
                                                                     frame)     phrases)
                     ──► Trim & view (timeline, CapCut-like) ──► Check & export (ffmpeg + HyperFrames render)
```

### 1. Footage and transcription
`server.py` is a small Python HTTP server (port from `VETTO_PORT`, default 8770) that serves the editor (`ui/`) and runs
jobs in the background. A take is copied into `projects/<id>/media/`, probed with ffprobe, and transcribed with
**MLX Whisper** (large-v3, on the Mac's GPU) into word-level timestamps (`engine/transcribe.py`). Word edges are snapped
to where the voice really starts and stops.

### 2. The cut (`engine/edit.py`)
Every word is a chip. Fillers, retakes (the earlier attempt of a repeated phrase) and long pauses are proposed as cuts;
pauses keep a beat by type (mid-sentence, sentence end, topic change) and by the chosen pace. The preview skips cuts live.

### 3. Styles: the Editing Beast
A style is a written guide plus code, kept in [`editing-beast/`](editing-beast/): `styles/<id>/STYLE.md` (what stays the
same, what adapts, structure, typography, effects, sound design, the rules learned from feedback, a build checklist) and
a `template/` with the approved build. Six styles:

| Style | In one line |
|---|---|
| **Clean White** | white glowing captions that build a statement word by word, a sharp card over a blurred copy, B-roll with voice-over |
| **Cinema Lexicon** | one phrase = one literal example clip (Pexels), small centred captions, branded bookends |
| **Neon Dimension** | cuts out of the room into dark neon 3D "worlds" with huge neon key words; loud transitions with a sub boom + swish |
| **Meme Chaos** | a raw take with meme reactions: punch zooms, face warps, explosions, meme sounds that name the moment, reaction GIFs and pictures, a mood-switching music bed |
| **Butter Steps** | step headers, butter-yellow key words, white rounded UI cards that glass in on the spoken word, cut-out pop-ups |
| **Star Glitch** | cream ultra-tight captions as the design, ★ glitch name moves, a fast montage on the beat |

Approved example edits (the author's own videos): [Butter Steps](editing-beast/styles/butter-steps/examples/), [Neon Dimension](editing-beast/styles/neon-dimension/examples/), [Star Glitch](editing-beast/styles/star-glitch/examples/).

**The rule for every style:** what stays exactly the same is the editing style, the fonts, the colours, the transitions
and the text templates. Everything about the content adapts to each new video: which words get effects, which sounds,
which music, which B-roll, which memes. Nothing from another style is ever mixed in.

In the editor, `engine/director.py` makes a style's whole edit as proposals: effects on the right words, punch-ins snapped
to the beat (`engine/rhythm.py`), sound effects chosen for what happens, and a music bed chosen by vibe from
`library/music.json` (all tracks Creative Commons, see [CREDITS.md](CREDITS.md)).

### 4. Hooks and effects
Effects are HyperFrames compositions (HTML + GSAP, 1080×1920, 3 s) in `engine/hf/*.html`, mirrored with docs in
`editing-beast/effects/<id>/` (`EFFECT.md` + `template.html`). You select a word or a phrase and **every effect box plays
that effect live with your own words on your own frame** (`engine/preview.py`) before you apply it. The text-hook effects
(wavy sparkle, hook throw-in, swipe-out, title mask rise…) work the same way. `editing-beast/effects/make_effect.py`
renders any effect as a piece from a clip.

### 5. Memes on phrases (`engine/memes.py`)
The engine reads your phrases and matches their words (English and Romanian) with a reaction category: mind blown, no
idea, fingers crossed, for nothing, you better, hungry… For each moment it offers **GIFs from GIPHY** (official API, your
own key) and **pictures from your Pinterest library** (a folder of pins sorted by emotion, with a catalogue of what each
picture shows and means). Every concrete object you name gets its own moment and a funny picture of that object. Click
one to put it on the phrase; there is also a reaction library for any second and an "Add pin" box for Pinterest pin links.
Placement checks your face at the start, middle and end of the meme's time on screen (Apple Vision) and keeps the card
clear of it. **Meme Chaos applies memes and GIFs by itself** when you pick the style; you swap or remove them.

### 6. Stock, cut-outs, sound
- Stock photos and clips: **Pexels** (official API, your own key), pop-ups on showable words or cutaway clips
  (`engine/stock.py`).
- Cut-outs: the macOS "lift subject" mask (`bin/lift.swift`) or HyperFrames `remove-background`.
- Sound effects by category, placed on words; music beds with loudness matching (`library/sfx.json`, `library/music.json`).

### 7. Edit now: Claude makes the whole edit (`engine/claude_edit.py`)
Edit now runs Claude Code headless in the Editing Beast folder with a prompt built from the style's guide: analyse the
video first (who, setting, actions, what is said, mood beat by beat), then build from the style's approved template,
compare contact sheets with the approved example, and write every choice and its reason into `NOTES.md`. The finished
reel lands in the project's renders.

### 8. Trim & view and export
A CapCut-like timeline shows the whole edit (cuts, text, effects, sounds, music) with a draggable playhead. Export
(`engine/render.py`) runs in three stages: the cut with punch-ins; the effects as HyperFrames pieces; then pictures, GIFs,
captions (libass), voice clean-up, sound effects and the music bed, mastered for social. Stories (≤ 15 s) and a carousel
are drafted from the same edit.

---

## Setup (macOS, Apple Silicon)

1. Python 3.9+ and Node 18+.
2. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
3. `cd tools && npm install` (HyperFrames renderer and ffprobe).
4. ffmpeg: put one on your PATH, or set `VETTO_FFMPEG=/path/to/ffmpeg`.
5. Build the two small Apple Vision tools:
   `swiftc -O engine/vision.swift -o bin/vision` and `swiftc -O bin/lift.swift -o bin/lift`.
6. Run: `.venv/bin/python server.py` → http://127.0.0.1:8770 (set `VETTO_PORT` for another port).
7. Keys, pasted in the editor (they are saved in `.secrets.json`, which is never committed):
   a free **Pexels** key (pexels.com/api) for stock, a free **GIPHY** key (developers.giphy.com) for GIFs.
8. Optional: Claude Code signed in (`claude auth login`) for **Edit now**; your own Pinterest picture library in
   `~/Desktop/Pinterest FeedMe - Emotii/` (or `library/memes/pinterest/`), sorted into emotion folders.

## What is in this repository, and what is not

Included: all the code, the Editing Beast style guides, templates and tools, three approved example edits, the effect library (templates and docs),
the open-licence fonts (Google Fonts, SIL OFL), the Creative Commons music with credits, and the sounds made in code.

Not included, on purpose (see [NOT-INCLUDED.md](NOT-INCLUDED.md)): footage or finished edits showing anyone other than the author, API keys,
other creators' reference videos, meme sounds and pictures whose licence is unknown, third-party documents and repos.

Older build notes, step by step: [docs/ENGINE-NOTES.md](docs/ENGINE-NOTES.md).
