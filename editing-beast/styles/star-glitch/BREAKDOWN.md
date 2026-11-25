# Reference breakdown: @havnana "FIVE ST★R FIX ep 06: text glitch effect"

- Source: https://www.tiktok.com/@havnana/video/7642467868617002254 → `references/havnana_7642467868617002254.mp4` (1080×1920, HEVC, 30 fps, 94.7 s, AAC 44.1 kHz stereo). Music credit in the post: "Presentation" by wouldliker. Edited in CapCut.
- Format: a talking-head **editing tutorial** from a recurring series. Hook → series sting with a name montage → how-to with screen recordings → result demo → "ok bye !".
- Evidence in `analysis/`: `study/` (beast-measure: pace, grade, loudness, storyboard), `sheets/` (5 fps contact sheets for 0–23 s, 2 fps for 23–94.7 s), `strips/` (30 fps strips of every transition, and full-res grids `grid_1–7.jpg`), `frames/` (full-res stills), `transcript.json` (392 words, word timestamps, MLX Whisper large-v3-turbo), `spectrogram.png`, `spec_intro.png`.
- Times are seconds from the start of the file. 1 frame = 0.033 s.

---

## 1. Structure (5 acts)

| Act | Time | Length | What happens |
|---|---|---|---|
| 1. Hook | 0.00 → 6.40 | 6.4 s | Talking head with dense word-by-word captions. "So I hear you just started making content… I think I can help with that." |
| 2. Intro / series sting | 6.40 → 15.83 | 9.4 s | "Hi, my name is Hannah" (glitching name) → "welcome back to episode 6" (number counter) → "5 Star Fix" (script logo lockup) → what the series is → "let's go!" zooms through the frame. |
| 3. Name montage | 15.83 → 22.43 | 6.6 s | No speech. 18 fast cuts of her posing in 4 other outfits/rooms; the name "HANN★H" sits over them, then flies huge across the cuts; a photo-booth print stamps on. The only music in the video. |
| 4. Tutorial | 22.43 → 86.63 | 64.2 s | Talking head (the hook room), with sparse key-word captions. CapCut screen recordings show each step as a big picture-in-picture card. The font names are shown in their own fonts, and a sound-library row is stuck on as a sticker. |
| 5. Payoff + outro | 86.63 → 94.73 | 8.1 s | Finished effect plays as a 90% card with its SFX, back to her, "ok bye !" on the last word. |

## 2. Shots and cuts

beast-measure: **55 shots, a change every 1.7 s, median 1.37 s**, but that average hides two very different speeds:

- **Talking head (acts 1, 2, 4, 5):** jump cuts only, every 1–6 s, to remove pauses/retakes. Same locked-off phone framing on both sides (medium close-up, eyes at ~22% from top, head and chest). No punch-ins, no zooms. Dead air trimmed to 0.1–0.2 s.
- **Name montage (act 3):** 18 cuts in 6.6 s, **0.17–0.4 s per shot (5–12 frames), median 0.3 s**. The music is ~140 BPM; cuts land loosely on half-beats (±0.15 s), not strictly on the beat.

| # | In → Out | Len | Picture | Said / shown |
|---|---|---|---|---|
| 1 | 0.00 → 1.90 | 1.9 | head (room A: white wall, paper lamp, wooden dresser) | "So I hear you just started making content and" |
| 2 | 1.90 → 4.83 | 2.9 | head | "you don't know how to make that content just a little bit more interesting." |
| 3 | 4.83 → 6.40 | 1.6 | head (no captions, big hand gestures) | "Well, I think I can help with that." |
| 4 | 6.40 → 10.27 | 3.9 | head | "Hi, my name is Hannah and welcome back to episode 6 of the 5 Star Fix" |
| 5 | 10.27 → 11.10 | 0.8 | head (no captions) | "a little series I started to" |
| 6 | 11.10 → 15.67 | 4.6 | head | "basically show you step by step how to make your edits 5 out of 5 stars. Let's get into it." |
| 7 | 15.67 → 15.83 | 0.17 | "go!" fills the frame cream (zoom-through) | — |
| 8–25 | 15.83 → 22.43 | 0.17–1.13 each | montage: room B (blue curtain, red drapes, fluffy earmuffs), room C (black/white spiral backdrop), room D (polka-dot backdrop, orange curtain, bow tights) | music only |
| 26–31 | 22.43 → 42.74 | 1.9–5.9 | head (room A) | "Welcome to episode 6…" through "the first thing you're going to do, obviously, is import" |
| 32–35 | 42.74 → 50.44 | 1.0–3.2 | **screen-recording PiP** over head; the cuts inside it skip ahead in the recording | import video → add text box → fonts → colour |
| 36 | 50.44 → 53.84 | 3.4 | head | "…zoom in a little bit" |
| 37 | 53.84 → 60.17 | 6.3 | **PiP**: timeline zoomed, text split into 0.1 s pieces | "splice it up… 0.1 seconds, 0.2 max" |
| 38–39 | 60.17 → 65.74 | 1.8–3.0 | head | "I really don't like them to be super long…" |
| 40 | 65.74 → 68.91 | 3.2 | **PiP**: tapping each piece, font panel | "click into each… edit that font" |
| 41 | 68.91 → 71.31 | 2.4 | head + **font-name parade** (§4) | "my absolute favorite fonts" |
| 42–43 | 71.31 → 76.24 | 1.6–3.3 | **PiP**: fonts being swapped, playback | "repeat that for all of them… this is what it'll look like" |
| 44–47 | 76.24 → 86.63 | 1.5–2.3 | head; SFX stickers 82.9–85.0 | "add sound effects… glitch sound… camera shutter" |
| 48 | 86.63 → 88.00 | 1.4 | **result demo card** (90%) over head | finished effect with SFX |
| 49–51 | 88.00 → 94.73 | 0.2–4.7 | head | "Super easy… let me know… Okay, bye." |

## 3. Captions (subtitles)

**One look for every caption:** flat cream **`#FBFCDA`** (sampled on 5 frames, identical), **no stroke, no shadow, no box**. A heavy rounded neo-grotesk, lowercase, with **very tight tracking (letters touch or overlap, about −0.07 em)**. Inter Tight 800 at −0.07 em is the closest local match. Every caption **hard-cuts in on the word onset and hard-cuts out**, with no fade, pop or scale. (The only animated captions are the special moves in §4.)

**Not karaoke and not a strip.** The captions are typography laid out over the frame. In the hook almost every word gets one; in the tutorial only about 1 word in 25 does.

### 3a. Size hierarchy (the main signature)
Each word is sized by how much it matters:

| Tier | Cap height @1080w | Font size ≈ | Used for | Examples |
|---|---|---|---|---|
| XL | ~260 px | 340–380 px | the punch word | "hear", "just", "started", "go!" (before it zooms) |
| L | ~150 px | 180–220 px | normal content words | "you", "don't", "know", "more", "text", "right", "hi!", "back" |
| M | ~80 px | 100–130 px | build-up words, scattered phrases | "welcome", "step / by / step", "how / to / make", "(so)", "(fun)", "(easy)" |
| S | ~35 px | 55–70 px | throwaway/fast talk, typed lines | "sooooo_", ">how to make that content<", "my / name / is", "your edits" |

### 3b. Punctuation tricks
- **(parentheses)** = an aside or a word said under the breath: "(making)", "(content)", "(little)", "(interesting)", "(out of)", "(so) (fun) (easy)". Shown at tier L/M.
- **>chevrons<** around a small, typed phrase = she's quoting a thought: ">how to make that content<".
- **Trailing underscore = typing cursor:** "sooooo_" grows a letter per frame with the "_" at the end (0.20 → 0.45 s), then "…!" is added.
- Captions are **not word-for-word**. She rewrites them: "Let's get into it" → "let's / go!", "5 out of 5 stars" → "five (out of) ★", "Okay, bye" → "ok bye !" (space before the "!").

### 3c. Placement
- Default slot: **centre, at chest height (y ≈ 49–52%)**, over the presenter.
- **Stacks:** two words share the frame, one above the other: "more" over "(interesting)" (one block), "(making)" at the top (y ≈ 9%) over "(content)" at chest (y ≈ 64%), "welcome" at the top (y ≈ 6%) over "back" at chest.
- **3-slot scatter for a phrase:** top-left (x≈30%, y≈9%) → right (x≈80%, y≈25%) → low centre (x≈45%, y≈39%) in a Z, building "step by step". The next words then **replace the oldest slot one at a time**: "how" replaces the first "step", "to" replaces "by", "make" replaces the second "step". There are always 3 words on screen.
- Captions may sit over the face. The text is cream on skin and nobody avoids it.

### 3d. Rhythm
- Hook (0–15.8 s): 63 words, **~4 words/s, a new caption every 0.2–0.35 s**.
- Tutorial (22.4–94 s): only ~12 caption moments in 72 s ("(so)(fun)(easy)", "text", "right", the font parade, "ok bye !"). The PiP cards carry the information there.

## 4. Signature moves (titles, stickers, effects), frame by frame

| # | Time | Move | Exact behaviour (30 fps) |
|---|---|---|---|
| M1 | 0.20 → 0.48 | **Typed-on word** | "sooo_" grows by one letter per frame, cursor "_" kept, then "…!" at 0.42. Tier S. Cut to "i" at 0.48. |
| M2 | 6.90 → 7.57 | **Glitch name** | "my / name / is" sit scattered small (S) at top-left, top-centre and right. On "Hannah" the name appears big (L), in caps with **a ★ standing in for one letter A**. The star swaps between the two A's: `H★NNAH` (7.13–7.30) → `HANN★H` (7.33–). Hard swaps, no motion. |
| M3 | 8.45 → 9.40 | **Number counter** | On "episode 6": "01" holds 4 frames, then **02, 03, 04, 05, 06 one frame each** (an odometer). "06" holds 0.5 s; on "5 Star" it hard-swaps to "05". Huge (XL) numbers with very tight tracking at chest. |
| M4 | 9.40 → 10.23 | **Series logo lockup** | Around "05" the word "Star" **writes itself on** in a copperplate script (Great Vibes / Pinyon Script look), above-left of the numbers. "Fix" sits below-right with a long swash. Cream. Hard cut out at 10.23 (on the jump cut). |
| M5 | 12.20 → 13.60 | **3-slot scatter** | See §3c. |
| M6 | 14.40 → 15.30 | **Word + star glyph** | "five" with "(out of)" under it and a **big solid ★** to the right, same cream. |
| M7 | 15.45 → 15.83 | **Zoom-through into the next scene** | "go!" holds at L size, then scales up fast over 6 frames (15.62 → 15.78, ≈ ×1.6 per frame, ease-in) until the letters cover the frame. Two frames are almost solid cream (15.78–15.83), then hard cut to the first montage shot. Doubles as a cream flash transition. |
| M8 | 15.83 → 19.27 | **Name over the montage** | "H★NNAH"/"HANN★H" (L, centred at y≈50%) stays on screen **across the cuts**, while the star keeps jumping between the A's. |
| M9 | 18.68 | **1-frame glitch flash** | One overexposed frame: white, with pink/RGB ghosting of the shot. Also at 19.90 (a blue-white bleed frame). Use 1–2 per montage. |
| M10 | 19.27 → 20.13 | **Name fly-through** | The name **grows (≈ ×1.15 per frame) and slides left** until only "NN" is visible, filling the frame (19.80–20.10). It crosses 3 cuts. Hard cut to room D at 20.13. |
| M11 | 20.40 → 20.70 | **Photo stamp** | A **black-and-white photo-booth print** of her (sepia, cream border, 4:5, ~57% of the frame width) **cuts in over her face** and holds 0.3 s. It sits slightly off-centre, top at y≈2%. No animation. |
| M12 | 34.77 → 36.25 | **Effect teaser** | The "text" caption (L) appears when she first says "text glitch", then **glitches through 6 fonts in 0.2 s** (35.27–35.45: condensed caps "TEXT" → thin sans → bitmap/pixel → script, 1–2 frames each), then settles back. It previews the payoff. |
| M13 | 69.00 → 71.07 | **Font parade** | Each favourite font name is shown **in its own font**, centred at chest, held **0.33–0.4 s each**: flourish (pixel-blackletter) → bootzyTM (heavy grotesk) → ghostech (gothic) → Elen (copperplate script) → cc-softedge (thin sans) → CC-TRANSISTOR (condensed caps). Hard swaps. |
| M14 | 82.93 → 85.0 | **Sound sticker** | A **CapCut sound-library row** (dark rounded bar #1E1E1E, ♪ icon, "Glitch sound that matc…", "00:01", bookmark and download icons) is stuck across the frame at y≈66%, x 2–95%. It cuts in on the word "glitch" (82.98) and swaps to "Camera burst mode s…" with a cyan "+" just before "shutter" (84.72). |
| M15 | 93.57 → end | **Sign-off** | "ok bye !" (L), centred at y≈50%, on "Okay". Cut in hard and held to the last frame. |

## 5. Picture-in-picture (screen recordings)

- **What:** raw CapCut phone screen recordings (dark UI #121212, cyan "Export" button, orange text track).
- **Size and place:** **74% of the frame width, centred, top at y≈2.5%, bottom at y≈95%.** It's a full 9:19.5 phone screen, square corners, **no border, no shadow, no rounding**. The presenter stays visible behind it on both sides (her hands and hair show at the edges).
- **In/out: hard cuts**, on the word that names the step ("your video" 42.74; "splice it up" 53.84; "click into each" 65.74; "repeat" 71.31).
- **Inside the card:** the recording is cut to only the taps that matter. The cuts skip ahead in the recording (43.70, 45.10, 48.27, 49.37), with no zoom on taps and no cursor highlight.
- **Result demo (86.63 → 88.00):** the finished clip plays as a **90% card** (x 4.8–94.8%), centred, static, hard in/out. It's the effect with its own SFX, 1.4 s, and then straight back to her face.

## 6. Picture and grade

- Phone front camera, natural window daylight, **no grade on top** (beast-measure: warm, contrast 69.6, saturation 0.27, black point 4.6). The hook room is bright and soft; the montage rooms are warmer and darker (lamp light).
- Main colours: near-black clothes #151314, grey-white wall #B1B0A8, hair auburn #63382D / #8E7B6F, caption cream #FBFCDA.
- No vignette, no grain, no letterbox.

## 7. Audio

- **Voice-only for 88 of 94.7 s.** The talking-head parts have **no music bed**: the gaps between phrases fall to −45 dB (room tone). The voice is dry phone audio.
- **Music only under the montage (15.8 → 22.4 s):** "Presentation", wouldliker, about **140 BPM**, beat strength 0.12 (soft). Level ≈ −28 dB RMS, about 5 dB under the speech average. It starts on the "go!" zoom-through and stops hard on the cut back to room A (22.43).
- **SFX:** heard on the result demo (glitch + camera shutter, 86.63–87.66, ~−35 dB) and when she names them (82.9–85). *Guess:* beast-measure hits at 7.81, 8.4 and 15.6 may be small ticks/whooshes under the name glitch, the counter and the zoom-through. Listen before copying.
- Loudness: **−21.6 LUFS integrated** (quiet for TikTok), LRA 3.9 LU, true peak −2.8 dBFS.

## 8. Rules that come out of this

1. **Two speeds.** A calm, locked-off talking head with jump cuts, plus one **6–7 s burst** of 0.3 s cuts with music: the identity sting. Nothing in between.
2. **Typography is the effect.** One cream colour and one tightly tracked heavy grotesk, varied only by **size, position and punctuation**. Script and novelty fonts appear only as accents (logo, font demos, glitch bursts).
3. **Busy hook, quiet middle.** Words on almost every syllable for the first 15 s, then captions only on key words while screen recordings carry the tutorial.
4. **Every overlay cuts hard.** No easing and no slide-ins. The only motion is the zoom-through and the name fly-through, which both act as transitions.
5. **Visual change on the spoken word** (PiP on the step's verb, sticker on "glitch", "text" on "text", "ok bye !" on "okay").
6. **Show the finished effect** at the end, then close fast (6.7 s from demo to the last frame).
