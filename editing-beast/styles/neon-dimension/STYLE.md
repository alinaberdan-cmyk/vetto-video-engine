# Neon Dimension

> A talking-head explainer that keeps **cutting out of the room into dark 3D / AI-generated "dimensions"**: neon-lit silhouettes, faceless 3D characters, glowing extruded numbers, tunnels and energy bursts. On the presenter, captions are **one or two words in wide, bold, glowing white caps**. In the 3D worlds, each phrase becomes **kinetic neon type**: a small white lead-in plus a huge, condensed, italic key word in one neon colour. Every scene change gets a light-burn, glitch or energy-burst transition with a sub boom and a swish.

- Status: **v1, approved 2026-11-17**, built from 3 references (same creator, a money/credit/business podcast format). Approved example: `examples/neon-dimension_app-promo_alina_2026-11-17.mp4` (project `projects/s2a`, v2). Reusable starting point: `template/` (the HyperFrames `index.html` with all scenes, captions and transitions, fonts, grain tile, and `mix.py` for the audio).
- Built from scratch. Nothing is carried over from other styles except the shared celf SFX pack.
- Evidence: `analysis/ref*_sheet_*.jpg` (2 fps contact sheets), `analysis/keyA.jpg`, `keyB.jpg` (full-res key frames), `analysis/transitions.jpg` (30 fps strips of 9 transitions), `analysis/ref*_cuts.txt` (scene-cut times), `sfx/ref_snippets/` (1.1 s audio around every reference cut, with voice bleed).

| Ref | Length | Cuts (clusters) | Talking head | 3D / AI worlds |
|---|---|---|---|---|
| ref1 `DAE-KCqiXPv` | 24.0 s | 12 | ~35% | silhouette in a white light; "DISTANCE between your ears" on a figure's back; green neon `$` numbers; red devil emoji |
| ref2 `DAE6ou2CBLV` | 51.7 s | 13 | ~45% | "INVESTMENT" twirl; credit-score phone with flying cards; AI man in a street with a 3D "312 → 784"; red bankruptcy scene; man climbing stairs to light |
| ref3 `DAE-RKfChqe` (**twist**: lighter, more "flat AI" grades) | 41.3 s | 17 | ~50% | white paper + red script titles; green money-rain; red/pink AI office; purple 6-armed 3D businessman; faceless 3D suit character in white/red neon |

---

## 0. Never a bare edit (Alina, 24 Nov 2026)
> "Same for Neon Dimension, you didn't use any effects like in the example video."

- **Build from `template/index.html`** (the approved example's own scenes, captions, transitions, grain) and keep every
  signature move of §1: 50–60% of the runtime in full-screen dark neon **worlds** with kinetic neon key words, presenter
  captions in wide glowing caps, a **loud transition on every boundary** (§7) with its sub boom + swish (§8), the dark
  music bed under everything, grain + dust + vignette, a neon pill per ~10 s and the CTA pill at the end.
  A talking head with captions only is NOT this style.
- **Objects she names** (IMG_1600: apple, chocolate bar, car) each get their own world: a stock clip or photo of exactly
  that object (Pexels), graded dark with the world's neon colour, three.js rings/particles on top and the object's name as
  the neon key word, entered with a transition from §7.
- **Before finishing**, compare the rendered contact sheet with `examples/neon-dimension_app-promo_alina_2026-11-17.mp4` at
  2 fps: worlds, neon type, transitions and grain must read the same; check the audio has the bed and a hit on every cut.
  Fix anything missing before RESULT.json.

## 1. How to recognise when to use this style
Use Neon Dimension when the input is **one person talking to camera** (podcast mic, selfie, desk) explaining a **business, money, tech or product idea**, 20–60 s, and the brief wants it to feel premium, "AI", high-energy or cinematic. Typical: founder explainers, app/product promos, finance tips, "here's how X works".

**Signature (present in every reference):**
1. **Alternation:** presenter shots (35–50% of runtime) cut against **full-screen dark 3D / AI worlds** (50–65%). A world lasts 1.5–5 s and illustrates one idea.
2. **Presenter captions:** 1–2 words, **wide extra-bold white caps with a soft white glow**, centred at chest height, swapped on each word chunk.
3. **World typography:** small white lowercase lead-in (Montserrat-like) + **huge condensed italic caps key word in neon** (green, red, cyan, purple), with a hot near-white core and a coloured glow.
4. **One neon colour per world**, matched to the meaning: green = money, success, "yes"; red = pain, problem, urgency; cyan = calm, solution, tech; purple = AI, magic, "game"; pink = desire.
5. **Every scene change is "loud":** a white light-burn, glitch, energy burst or zoom/whip blur (0.1–0.3 s), each with a **sub boom + swish**.
6. **Film finish over everything:** grain, dust specks, soft vignette, slight chromatic fringe on the 3D shots.

**Not this style:** bright/clean white backgrounds as the default (that is a different style), boxed subtitle bars, karaoke highlighting, long B-roll holds with no type, soft dissolves.

## 2. What stays fixed and what can vary
| Fixed | Range seen |
|---|---|
| Presenter ↔ 3D world alternation, worlds carry kinetic type | Presenter share 35% (ref1) ↔ 50% (ref3) |
| Presenter caption style (wide glow caps, 1–2 words, chest height) | Caption font width: Montserrat ExtraBold (ref1) ↔ extended/wide (ref2–3) |
| Neon key word = condensed italic caps + glow | World look: dark neon (ref1–2) ↔ lighter "paper" and flat 3D AI looks (ref3 twist) |
| Loud transitions with sub + swish | Transition mix: light-burn heavy (ref2) ↔ glitch/energy heavy (ref3) |
| Grain + dust + vignette | Neon pill (outlined caption box) used 0–2 times per video |

## 3. Structure template
| Part | Time | What happens |
|---|---|---|
| **Hook** | 0–3 s | ≤1.2 s of presenter, then straight into a world with the hook's number or key word (ref1 "THE DISTANCE", ref2 "ONE OF THE BEST → INVESTMENT", ref3 "ONE OF THE BEST WAYS"). |
| **Body** | — | Alternate: presenter for "I / you / we" sentences, connective phrases and reactions; a world for every **concrete claim, number, problem or result**. Worlds often run back-to-back (2–3 in a row) on a list or a build. |
| **Proof** | as needed | Real UI / screenshots in a glowing frame (ref2 credit-score cards, YouTube channel page): phone or card in 3D perspective with neon rim. |
| **CTA** | last 3–5 s | Presenter + **neon outlined pill** caption ("DROP A COMMENT"), green, condensed italic white text. |

## 4. Typography
### 4.1 Presenter captions
- Font: wide extra-bold geometric sans, ALL CAPS. Stand-in: **Montserrat 800**, tracking +0.015em (for the wider ref2–3 look, use an extended face such as Unbounded/Monument Extended if licensed).
- Size **76 px at 1080 w** (~7% of width). White, **glow** `0 0 10px rgba(255,255,255,.75), 0 0 30px rgba(255,255,255,.35)` + a soft dark drop `0 4px 18px rgba(0,0,0,.55)`.
- Position: centred; **at chest height**, under the chin. Refs: 50–58% of height. When the subject's face sits low in frame (selfie framing), move it down to keep it off the face (s2a: top 1470 px ≈ 77%).
- Timing: swap on word onsets, 1–2 words per chunk, a tiny 0.09 s pop (scale 1.12→1). Key word now and then: italic condensed in a **neon pill** (§6).

### 4.2 World type
- **Lead-in:** Montserrat 600, lowercase as spoken, 50–64 px, white with a faint glow. Words appear one by one on onsets and accumulate ("dictated" → "dictated upon those"), then blur out on the next chunk.
- **Key word:** **Anton** (stand-in for the condensed italic display face), ALL CAPS, `skewX(-7deg)`, 170–330 px, line-height 0.92. Colour = near-white tint of the neon, glow `0 0 6/22/60/120px <neon>`.
  - Entrance: **slam** from scale 1.6–2.6 with 16 px blur → 1 in 0.2 s (expo.out), then a slow push to 1.07. Exit: 0.1 s blur-out.
  - Optional neon **flicker** (3 blinks to 35% in the first 0.2 s) for red/pink "problem" words.
  - Placement: above or behind the subject, often overlapping it (refs: "$100 MILLION" behind a silhouette, "ESSENTIALLY" behind the 3D man).
- **3D extruded numbers / symbols** ("$100", "784", "40", "€15"): white or neon front face, ~20 darker layers behind it, rotating slowly in perspective.

### 4.3 Palette
| Neon | Hex | Core (text fill) |
|---|---|---|
| Green | `#39FF6A` | `#D9FFE3` |
| Red | `#FF2A2A` | `#FFD6D6` |
| Cyan | `#22D3FF` | `#DDF7FF` |
| Purple | `#B455FF` | `#F0E0FF` |
| Pink | `#FF2E9A` | `#FFE0F0` |
| Gold (rare, money/reward) | `#FFD23F` | `#FFF6D8` |

## 5. Footage: 3D and AI worlds
- **What the refs use:** AI-generated stills/clips (faceless suited figures, silhouettes against light, moody streets, offices) graded dark with one neon colour; 3D-rendered characters and objects (faceless 3D businessman, credit cards, phone); neon line art (outlined `$`, rings, tracers).
- **How we make it now (s2a v1):** procedural **three.js scenes** inside HyperFrames, rendered per frame from the GSAP timeline (deterministic): neon clock, neon tunnel, glowing dice, a QR code assembling from cubes, a neon night skyline. Fake bloom = a blurred half-res copy of the WebGL canvas, screen-blended.
- **AI-generated footage (Figma Weave, connected 2026-11-17):** model **Kling Video, 2.5 Turbo Pro**, text-to-video, `ratio 9:16`, `duration 5`, **35 credits per clip** (model id `wnfmbl8VwUCfX2a1XcdfDlone`). Every run needs the user's explicit OK on the quoted cost. **The free Weave plan allows only 2 model runs**; more clips need a paid plan.
  - Prompt recipe: *"Cinematic vertical shot, [dark location], [subject as a faceless silhouette / stylized faceless 3D character], [action that literally shows the phrase], [one neon colour] rim light, volumetric haze, high contrast, slow push-in camera, film grain, moody, no text"*.
  - Use 1–2 s from the middle of the 5 s clip (`data-media-start` ≈ 1.2–1.6 s), lightly graded (`contrast 1.12, saturate 1.15, brightness .92`).
  - **Hybrid layer (as in the refs):** the AI clip sits full-frame underneath, the three.js neon line art (rings, particles) is screen-blended on top, kinetic type above both.
  - Shot list used in s2a: red fridge silhouette ("40 minutes"), faceless 3D character rolling purple dice ("like a game"). Planned but not run (plan limit): QR scan, friends debating food, friends on a sofa at night.
- **Presenter grade:** pull toward the neon world: contrast +20%, slightly darker, cool shadows/magenta mids (`eq=contrast=1.2:brightness=-0.05:saturation=1.08, colorbalance=rs=-0.10:bs=0.14:rm=-0.04:bm=0.08:bh=0.08`), vignette, plus **coloured rim light overlays** (purple from the left, cyan from the right, screen blend) to imitate the refs' neon studio.
- **Presenter motion:** jump zooms between 1.0 and 1.2 on chunk changes (no easing), as in the refs.
- **Product / proof:** a **3D phone** (CSS 3D: stacked side layers, 86 px corner radius, dynamic island, glass gloss, neon rim glow in the scene colour) that flies in with rotation (expo.out 0.4–0.55 s), then drifts ±15° in Y.

## 6. Graphic elements
| Element | Spec |
|---|---|
| **Neon pill** | Outlined rounded rect, 5 px stroke `#39FF6A`, radius 20–22 px, outer + inner glow; text Anton white, italic skew, 84–92 px. Used for CTA and for one stressed word per ~10 s |
| **Extruded number** | §4.2; slams in from z −900 with rotateY −75° → −22°, then turns to +18° |
| **Neon line art** | Outline `$`, rings, tracer lines behind the subject (ref1, ref2) — three.js rings/tunnels |
| **Particles** | Small additive glowing dots drifting toward camera in every world |
| **Grain / dust** | Animated grain tile (overlay 55%), 4 thin scratch lines + 10 dust specks flashing 1 frame each, vignette 60% at edges |

## 7. Transitions (measured at 30 fps)
| Transition | Look | Where |
|---|---|---|
| **Light burn** | White radial flash with warm edges, 0.08 s up, 0.22 s down, whole frame brightened ×1.6 | World → presenter (most common) |
| **Energy burst** | Neon radial blob grows from the centre to cover the frame in 0.28 s, then reveals the next world | Presenter → world on big moments; world → world |
| **Glitch** | 3–4 frames of offset colour bars, scanlines, horizontal shake ±14 px | Into "problem" or "game" worlds |
| **Zoom blur** | Incoming shot from scale 1.35 + 18 px blur → 1 in 0.22 s | Presenter ↔ world |
| **Whip** | Type enters from the side with 20 px blur in 0.2 s | World → world |
| **Twirl / swirl** (ref2) | Text bends around a vortex | Not built yet |

## 8. Sound design
Measured on the refs: integrated **−14.1 LUFS**, speech p50 −14.5, quiet floor p5 −20…−23 LUFS → **a continuous music bed ~7–8 dB under the voice**. On **every scene change** the highs jump +20–28 dB (swish/whoosh) and the lows +10–17 dB (sub boom).

**Kit** (`sfx/kit/`, synthesized by `tools/synth_sfx.py`, license-free):
| File | Use |
|---|---|
| `ND_sub_boom.wav` | Every presenter↔world cut and every key-word slam (−8…−12 dB) |
| `ND_swish.wav` | Key-word slams, whips (−9…−12 dB) |
| `ND_flash_hit.wav` | Light-burn transitions (−11 dB), placed 60 ms before the cut |
| `ND_energy_burst.wav` | Energy-burst transitions (−9…−11 dB), 80 ms before the cut |
| `ND_glitch.wav` | Glitch transitions and flickering red words (−14…−20 dB) |
| `ND_riser.wav` | 1.2 s into the biggest 2–3 cuts (end-aligned, −14 dB) |
| `ND_dark_bed_70bpm.wav` | Dark cinematic bed, 72 s (−20 dB under the voice before limiting) |

**From the shared celf pack** (`sfx-library/celf-sfx-pack/`, same files as the Drive folder): `Pop_01_Tap` / `Pop_02_Quick` on neon pills, `Mouse_Click_02_Tactile` on a CTA, `Whoosh_05_Fast_Flick` / `Whoosh_02_Wave` as swish variants, `Chime_01_Coin_Pickup` on money/price beats, `Sparkle_04_Scene_Reveal` (quiet) on the end card.

Mix: voice `loudnorm I=−15`, bed −20 dB, SFX as above, `alimiter 0.89` → ≈ −14.5 LUFS integrated.

## 9. Build checklist (per video)
1. Transcribe with word timestamps (`faster-whisper medium`). Remove repeats and false starts; tighten pauses to ~0.1–0.3 s (check the RMS inside long words, since Whisper hides pauses there).
2. Grade the presenter (§5), extend the last frame by ~1.2 s for the CTA.
3. Split the script: presenter windows (I/you/we, connectives) vs **world windows** (claims, numbers, problems, product). Aim for 50–60% worlds, 1.5–5 s each.
4. For each world: pick a neon colour (§4.3), a 3D scene (or AI clip), the lead-in words and one key word or number.
5. Product footage goes on the 3D phone inside a world.
6. Captions on every presenter word chunk; 1 neon pill per ~10 s; CTA pill at the end.
7. Transitions at every boundary (§7), SFX at every transition (§8), bed under everything.
8. `hyperframes check`, then snapshots at every world, then render (`--video-frame-format png` for UI recordings), then mux the mix.

## 10. Open items
- AI footage: Weave is linked, but the free plan stops after 2 model runs. Worlds without an AI clip stay procedural three.js.
- The refs' condensed italic display face and wide caption face are approximated (Anton with skew; Montserrat 800).
- The reference SFX snippets contain voice bleed. The kit is synthesized to match their measured character, not extracted clean.
- Twirl/vortex text transition (ref2) not built yet.
