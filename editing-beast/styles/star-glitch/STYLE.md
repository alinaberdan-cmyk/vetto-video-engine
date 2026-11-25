# Star Glitch

> A chatty, locked-off talking head whose **captions are the design**. Every caption is one cream colour (`#FBFCDA`), one ultra-tight heavy grotesk, no stroke and no shadow. The words are **sized by importance** (huge punch words, tiny throwaway words), **scattered around the frame**, and use (parentheses), >chevrons< and a typing_ cursor. The hook is dense with words. Then comes a **6–7 s identity sting**: the name glitches with a ★, an episode counter rolls, a script logo writes on, "go!" zooms through the frame into a 0.3-s-per-cut music montage. The middle stays calm: screen recordings as big picture-in-picture cards, key-word captions only, voice with no music. It ends with the finished result as a 90% card and "ok bye !".

- Status: **v1, approved 2026-11-18.** Built from **1 reference** (`references/havnana_7642467868617002254.mp4`, TikTok @havnana "FIVE ST★R FIX ep 06", 94.7 s, CapCut tutorial). 2–4 more refs would set the range.
- Name: **Star Glitch**, chosen by Alina on 2026-11-18. It's named after the most recognisable move: the ★ hopping inside the glitching name. (Working name was "Cream Scatter".)
- Approved example: `examples/star-glitch_feedmeplzthanks-dare-to-try-this-app_alina_2026-11-18.mp4` (project `projects/sg01`: handheld selfie take + app screen recording, 40.2 s). Reusable starting point: `template/` (`build.py` + README).
- Approved adaptations (SG01):
  - **No extra presenter clips → montage from the product:** 14 dish cards from the screen recording, 7 frames each (half-beats at 129 BPM).
  - **Cream type on cream UI vanishes:** in the montage the name sits over the dark food-photo band (y≈25%), not at chest height.
  - **Bright footage:** a faint warm halo behind all cream type (`text-shadow: 0 0 30px rgba(45,28,16,.30)`). It shouldn't read as a shadow.
  - **No "Hi, my name is":** the glitch name is the brand/app name on "this app"; the counter goes on the number she says ("10 minutes"); the script logo lockup goes on "discovered this app".
  - **Payoff card** = the app's "Who's eating?" friends screen on "share it with your friends"; sign-off "lmk (what u think !)".
  - Music: "The Tropics Of Risa" (e s c p, CC BY, Vetto library `tropical-risa` from 87.36 s), ~5 dB under the voice.
- **Timing rule (learned on SG01):** every flip-book state (★ swaps, typed text, counter, font glitch) must be snapped to whole frames: start 0.5 ms early, end 1 ms early (`fr()` in the template). Otherwise two states share a frame (the doubled name in v1) or a frame goes blank. Always check a 30 fps strip of the *rendered* file at each swap.
- Built from scratch. Only the shared celf SFX pack carries over.
- Frame-by-frame breakdown: [`BREAKDOWN.md`](BREAKDOWN.md). Evidence: `analysis/`. Numbers marked *measured* come from beast-measure / ffmpeg on the reference.

## 1. When to use it
**Input that fits:** one person talking to a phone camera in a casual, friendly voice, 45–100 s, as an **episode of a series** or a personal-brand how-to / tip / "my favourite trick". It works best when there is a screen recording or a finished result to show, and **a few extra clips of the presenter** (other outfits, rooms, poses) for the montage.

**Signature (must be present):**
1. Locked-off talking head, **jump cuts only**, no punch-ins, no grade.
2. **All captions cream `#FBFCDA`**: flat, no stroke, no shadow, no box, lowercase, tracking about −0.07 em, hard-cut in on the word onset.
3. **Size hierarchy + scatter** in the hook (XL / L / M / S tiers, stacks, 3-slot Z scatter).
4. **Identity sting** after the hook: glitch name with ★ → counter → script logo → zoom-through → 5–7 s montage at about 0.3 s per cut, with the only music in the video.
5. **Quiet middle:** big PiP screen recordings (74% wide), captions on key words only.
6. **Payoff card** (90%) → "ok bye !" sign-off.

**Not this style:** caption strips/karaoke, coloured key words, strokes/shadows on text, slide/pop/bounce animations on overlays, music under the talking, whooshes on every cut, B-roll stock, colour grades, zoom punch-ins.

## 2. Structure template
| Part | Ref timing | Length | Do this |
|---|---|---|---|
| Hook | 0 → 6.4 s | 4–7 s | Relatable "so I hear you…" line → "I think I can help". **Dense scatter captions**, one per word, XL on the punch words. Open with a typed-on S-tier word ("sooo_"). Leave the last sentence of the hook uncaptioned while she gestures (shot 3). |
| Intro / sting | 6.4 → 15.8 s | 8–10 s | "Hi, my name is X" → **glitch name** (M2). "Welcome back to episode N" → **counter** (M3). Series name → **script logo lockup** (M4). One line about the series with a **3-slot scatter** (M5). End on "let's go!" → **zoom-through** (M7). |
| Montage | 15.8 → 22.4 s | 5–7 s | 15–20 cuts of 0.17–0.4 s (median 0.3 s) of the presenter's extra clips, 3–4 looks, on ~140 BPM music. The name stays on over the cuts (M8), 1–2 **glitch flash** frames (M9), name **fly-through** (M10). Music stops dead on the cut back. No extra presenter clips? Cut the montage from the product itself (screen-recording frames, dish/product cards). |
| Body | 22.4 → 86.6 s | 40–65 s | Talking head with jump cuts every 2–6 s. Captions only on ~1 word in 25: the key nouns, an "(aside) (stack)", and a **teaser** of the payoff (M12). **PiP card** for each step, cut in on the verb that names it (§5). Optional: font parade (M13), **sound sticker** (M14). |
| Payoff | 86.6 → 88.0 s | 1–2 s | The finished result as a **90% card**, with its own SFX. |
| Sign-off | 88 → end | 4–7 s | "Super easy… let me know what you want next" → **"ok bye !"** on the last word, held to the last frame. No end card. |

If the take is not a tutorial, keep **hook → sting → body → sign-off** and drop PiP/payoff. The sting is the part that makes the style recognisable.

## 3. Caption system
```css
--cream: #FBFCDA;            /* measured, identical on 5 frames */
font-family: "Inter Tight";  /* 800; closest local match to her CapCut grotesk */
font-weight: 800;
letter-spacing: -0.07em;     /* letters touch / overlap */
line-height: 0.85;
text-transform: none;        /* lowercase as spoken; caps only for the name */
color: var(--cream); text-shadow: none; -webkit-text-stroke: 0;
```
Fonts on disk: `InterTight-800.ttf`, `GreatVibes-400.ttf` (script logo), `Anton-Regular.ttf` (condensed caps for glitch bursts). For pixel / gothic glitch fonts, add Silkscreen + UnifrakturMaguntia (Google Fonts, OFL) when building the template.

| Tier | Font size @1080w | Use |
|---|---|---|
| XL | 340–380 px | punch word: 1–3 per hook ("hear", "just", "go!") |
| L | 180–220 px | normal content words, the name, "text", "ok bye !" |
| M | 100–130 px | scatter phrases, (asides), "welcome" |
| S | 55–70 px | fast filler, typed >quotes<, "my name is" |

- **Timing:** each caption is on from its word's onset to the next caption's onset (hold ~0.2–0.35 s in the hook). Hard in and hard out. Within one sentence, the words **stay stacked** until the sentence ends (e.g. "(making)" stays while "(content)" appears).
- **Slots:** default centre at y 50%. Stack top (y 6–9%) + chest (y 50–64%). Z scatter: TL (x 30%, y 9%) → R (x 80%, y 25%) → low C (x 45%, y 39%), and new words replace the oldest slot.
- **Rewrite, don't transcribe:** "let's get into it" → "let's / go!"; "5 out of 5" → "five (out of) ★"; "okay bye" → "ok bye !". Write it the way a friend texts.
- **Punctuation:** (aside), >quoted thought<, trailing `_` cursor while typing, "!" with a space before it at the end.

## 4. Moves library (timings measured at 30 fps on the ref)
| ID | Move | Spec |
|---|---|---|
| M1 | Typed-on word | +1 letter per frame, `_` cursor at the end, S tier, centre-left |
| M2 | Glitch name | caps, L tier, centre; **★ replaces one letter** and hops between two positions every 4–6 frames; "my / name / is" scattered S tier above it |
| M3 | Counter | XL numbers: "01" holds 4 frames, then +1 per frame up to N, hold 0.5 s |
| M4 | Script logo | series word in Great Vibes **writes on** (left → right mask, ~0.15 s) around the number; second word below-right with a swash; hard out on the next cut |
| M5 | 3-slot scatter | §3 slots, M tier |
| M6 | Word + ★ | solid cream star glyph beside the word, same height |
| M7 | Zoom-through | word scales ×1.6 per frame for 5–6 frames (ease-in), 2 frames of ~solid cream, hard cut. **Whoosh_05_Fast_Flick** under it |
| M8 | Name over cuts | the caption layer ignores the cuts |
| M9 | Glitch flash | 1 frame: the shot pushed to white (+80% exposure) with a pink/cyan RGB split; **Camera_01_Snapshot** or nothing |
| M10 | Fly-through | name scales ×1.15 per frame and slides left until only 2 letters fill the frame (~0.8 s, crosses 2–3 cuts) |
| M11 | ~~Photo stamp~~ | **Not used (Alina, 2026-11-18).** The ref stamps a B&W photo-booth print on for 0.3 s; leave it out of our edits |
| M12 | Teaser glitch | key word in L tier; for 6 frames it cycles condensed caps → thin → pixel → script, then settles |
| M13 | Font parade | each name in its own font, 0.33–0.4 s each, centre |
| M14 | Sound sticker | dark bar `#1E1E1E`, radius 12 px, x 2–95%, y 66%, ♪ + name + "00:01" + icons; cut in on the word; real sounds from the celf pack |
| M15 | Sign-off | "ok bye !" L tier, centre, to the last frame |

## 5. Picture-in-picture and payoff
- Screen recording at **74% frame width**, centred, top y 2.5% (full phone aspect). **Square corners, no border, no shadow**, presenter visible behind. Hard in/out on the step's verb. Inside, cut down to the taps that matter (jump cuts inside the card are fine).
- Payoff: the finished clip at **90% width**, centred, static, hard in/out, 1–2 s, with its SFX.

## 6. Audio
- **Voice dry, no music under speech** (gaps fall to room tone).
- **Music only under the montage:** upbeat ~140 BPM. It starts on the zoom-through frame and stops hard on the cut back. In the ref it sits ~5 dB under the speech level. **Take it from the Vetto Video Engine library** (`vetto-video-engine/library/music.json`, beat grids in `music_beats.json`; upbeat/playful tags, 120–140 BPM, strong beat) or suggest a CC track (Alina's call).
- SFX are sparse and only where the picture glitches: whoosh on M7, an optional snapshot on M9, and the demo sounds in the payoff (Camera_03_Rapid_Burst for a shutter burst).
- Ref is −21.6 LUFS (*measured*). Our house rule wins: **master to −15 LUFS, true peak −1.5 dBTP**.

## 7. Picture
- Phone footage as shot, no grade, no grain or vignette. Keep the camera locked; if the take is handheld, stabilise lightly and accept it.
- Render iPhone HDR footage with `hyperframes render --sdr` and check a 1 fps contact sheet of the rendered MP4.

## 8. Checklist before delivering
- [ ] Every caption is cream #FBFCDA, no shadow/stroke, tight tracking, hard cuts
- [ ] Hook has all 4 tiers, ≥1 stack, ≥1 (aside); body is quiet
- [ ] Sting has the glitch name, counter or logo, zoom-through, montage with music (no photo stamp)
- [ ] PiP 74% / payoff 90%, hard in/out on the word
- [ ] No music under speech; −15 LUFS
- [ ] Final named `star-glitch_<topic>_<people>_<date>.mp4` → `finals/` + `examples/`
