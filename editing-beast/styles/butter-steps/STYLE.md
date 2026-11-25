# Butter Steps

> A calm, locked-off talking head with a **numbered how-to built in the top third of the screen**: a step header in butter-yellow and white caps, then clean white UI cards (Finder windows, tables, prompts, dashboards) that "glass in" and react to the exact word being said. Captions are **one lowercase word at a time** at chest height, with key words in butter yellow. The hook pairs extra-bold caps with a **yellow serif italic** title and a wall of past reels behind the presenter. Voice only, no music.

- Status: **v1, approved 2026-11-18**. Built from **1 reference** (`references/andreakyton_7702964649469185287.mp4`, TikTok @andreakyton, 64.7 s). 2–4 more refs would set the range.
- Approved example: `examples/butter-steps_feedmeplzthanks-dare-to-try-this-app_alina_2026-11-18.mp4` (project `projects/bs01`: handheld selfie take + clean app screen recording). Reusable starting point: `template/` (`build.py` = cut list from detected pauses, card clips cut from a screen recording, the HyperFrames page; `extract_icons.py` = cut UI icons out of a screen recording as transparent PNGs; fonts + pop SFX).
- Approved adaptations for handheld / bright footage: a soft dark gradient on the top 900 px so the yellow and white type reads; a stronger caption shadow when white phone screens sit behind the words; app cards cut from the clean screen recording, timed so the app's own actions (SKIP / GET IT swipes) land on the spoken word; proof wall of content cards beside the face when there is no person cut-out.
- Built from scratch. Only the shared celf SFX pack carries over (and it is used very sparingly here).
- Full frame-by-frame breakdown: [`BREAKDOWN.md`](BREAKDOWN.md). Evidence: `analysis/`.

## 1. When to use it
Use it for **one person on camera teaching a process**: a tool setup, a workflow, "how I do X in N steps", a product walkthrough with real UI, 30–75 s, ending in a lead-magnet CTA ("comment WORD and I'll send you the guide").

**Signature (must be present):**
1. One locked-off shot of the presenter. Jump cuts only, no zooms, no B-roll cutaways.
2. **Top third = "the screen"**: a step header (`STEP n` in yellow + name in white, Montserrat ExtraBold caps) with white rounded UI cards under it. The face stays clear.
3. **One-word lowercase captions** at about 68% height, white, with key words in `#F5EEA8`.
4. One accent colour, **butter yellow**, everywhere: hook serif, `STEP n`, pill, highlighter, prompt bar, key words.
5. Every on-screen change hits the word it illustrates.
6. Voice only, about −14 LUFS, tight pauses.

**Not this style:** music beds, whooshes on every change, full-screen screen recordings, captions in boxes, multi-word caption lines, punch-in zooms, colour grades.

## 2. Structure template
| Part | Length | Do this |
|---|---|---|
| Hook | 0–5 s | Relatable pain line + **title block** (caps line / yellow serif italic line / "IN + logo") + **proof wall** of 6–9 of the creator's own thumbnails popping in behind them |
| Promise | 5–10 s | "So I made… and it even edited this video" (a meta-proof line) |
| Route map | 0.8–1.5 s | Yellow pill: `N steps → let's get started 👇`, on its own short take |
| Steps | 8–10 s each | Header + UI card + optional "THEN"/"PROMPT · COPY THIS" card + 1–3 micro-interactions |
| Curiosity peak | 2–3 s | Header swaps to "THE PART EVERYONE ASKS ABOUT 👀" |
| CTA | 4–5 s | Guide card (cover + ✓ list) → header `COMMENT "WORD" 💬` → comment bar types the word → "sent you the guide" bubble |

## 3. Edit
- Remove every pause longer than about 0.25 s and all retakes with **hard jump cuts at the same framing**. Expect about 1 cut per step plus 1–2 short "hinge" takes (0.8–1.3 s) for punchy lines.
- Never use a transition between shots.
- Overlays are timed to **words**, not to cuts. It is fine for a panel to land 0.3 s before or after the cut.

## 4. Typography
| Element | Font (stand-in) | Size @1080 w | Colour | Notes |
|---|---|---|---|---|
| Captions | Inter 700–800 | 64 px | `#FFFFFF`, key words `#F5EEA8` | 1 word, lowercase, no punctuation, shadow `0 2px 10px rgba(0,0,0,.35)`, centre y ≈ 1300 |
| Hook line 1 | Montserrat 800, caps | 34 px | white | tracking +0.03em, y ≈ 295 |
| Hook line 2 | Playfair Display Italic 400 | 100 px | `#F5EEA8` | soft shadow `0 3px 14px rgba(0,0,0,.3)`, y ≈ 410 |
| Hook line 3 | Montserrat 800 "IN" + logo + serif wordmark | 40 px | white + logo colour | y ≈ 506 |
| Step header | Montserrat 800, caps | 36 px | `STEP n` `#F4EFAB`, rest white | y ≈ 190, emoji at the end |
| Pill | Inter 800 | 40 px | `#2D2216` on `#F5EEA6` | radius 999, rotate −3°, y ≈ 440 |
| Card UI | Inter 500–700 | 22–30 px | `#1D1D1F` / grey `#6A6967` | labels: 14 px caps, tracking +0.12em |
| Code / repos | JetBrains Mono 500 | 24 px | `#1D1D1F` | |

## 5. Layout tokens
```css
:root{
  --butter:#F5EEA8; --butter-pill:#F5EEA6; --ink:#2D2216;
  --card:#FCFCFC; --card-cream:#F9F6ED; --label:#6A6967; --ok:#2FA35B;
  --card-x:65px; --card-w:950px; --card-top:220px; --radius:22px;
  --card-shadow:0 18px 50px rgba(0,0,0,.18), 0 2px 6px rgba(0,0,0,.08);
  --cap-y:1300px;   /* caption centre */
  --header-y:190px; /* step header baseline area */
}
```
- Safe zone: the cards live between y 150 and y 720. The face sits at about y 700–1000, captions at y 1300, and TikTok/IG UI below y 1500.
- Sub-cards stack 14 px below the card above them. A prompt card has a 6 px `--butter` bar on the left.

## 6. Motion
| Thing | In | Out |
|---|---|---|
| Caption word | hard cut on the word onset | hard cut |
| Hook title | already on at frame 0 | hard cut |
| Proof-wall thumbnails | staggered 0.1 s, scale 0.6→1 in 3–4 frames, **behind the person matte** | fade + scale 0.95 over 3 frames |
| Pill | scale 0.5→1.05→1 over 6 frames (back.out) | fade over 3 frames |
| Step header | hard cut, 1 frame before its card; text swaps in place | hard cut |
| UI card | "glass in": blur 20→0 px, opacity 0.4→1, white veil, 4 frames | hard cut to the next card |
| Badge / toast / bubble | scale 0.8→1 over 3 frames | stays until the card changes |
| Typing | 1 character every 2–3 frames, with a caret | — |
| Highlighter | yellow marker swipe left→right behind the word, 4–6 frames | stays |

## 7. Audio
- Voice only. **No music.** Level to **−14 LUFS integrated, LRA ≤ 3 LU** (compressor + limiter, true peak −1 dBTP).
- SFX: at most a soft pop or sparkle on the proof-wall pops and the pill, mixed about −20 dB under the voice (pick from `sfx-library/celf-sfx-pack/`). No SFX on cards, clicks or typing.

## 8. Recipe (HyperFrames / OpenMotion)
1. Transcribe with word timestamps (faster-whisper). Cut pauses longer than 0.25 s and retakes → `rough.mp4`.
2. Run a person matte on the presenter (needed only for the hook proof wall). Layer order: background plate → thumbnails → matted presenter → text.
3. Script the beats: for each step, list its header text, card type, sub-cards and the **trigger word** for each micro-interaction.
4. Build cards as HTML at 950 px wide using the tokens above. Rebuild the UI as clean mock-ups rather than raw screenshots (crisper, on-brand). Use a real screen recording only for the one "hero" feature.
5. Captions: 1 word per chunk from the word timestamps. Highlight the product name, the hero feature and the CTA word.
6. Render (`--sdr` for iPhone footage) and check a 1 fps contact sheet of the rendered MP4.

## 9. Open questions for the next references
- Do the hook title fonts change from video to video? The yellow serif italic and caps pairing looks like the creator's brand.
- Are the proof-wall and person-matte tricks a regular part of the hook or a one-off?
- SFX: confirm by ear that the two hook pops are sound effects.
