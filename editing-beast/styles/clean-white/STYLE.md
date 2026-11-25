# Clean White

> Minimal, premium short-form edit for talking-head / podcast clips: **white glowing captions that build a statement word by word with a blur-in**, a mix of heavy sans and editorial serif, sparse cinematic transitions (light leaks, whips, dark dips), B-roll that carries the voice-over, and a signature **silver-white "card" scene** where the clip shrinks into a rounded frame.

- Status: v0.1, built from 3 references (2 core + 1 twist). Specs are measured from 720-wide frames and scaled to 1080×1920. Fonts are approximations (see §9).
- Evidence: [analysis/timelines.md](analysis/timelines.md) (per-reference cut and caption timelines), `analysis/*sheet*.jpg` (5 fps contact sheets), `analysis/zoom_*.jpg` (full-res key frames).
- References: `references/ref1.mp4` (core), `ref2.mp4` (core, has the white card scene), `ref3.mp4` (twist: serif-led, background blur, film B-roll).

---

## 1. How to recognise when to use this style
Use Clean White when the input is **one person speaking** (podcast, mic in frame, or a creator to camera), 9:16, 10–60 s, with a motivational / insight / "how I do X" message, and the brief asks for something clean, premium or minimal.

**Signature (all of these show up in every reference):**
1. Captions are white (or dark slate on light areas), have **no box or stroke**, have a **soft white glow**, and appear **word by word with a blur-in**.
2. Key phrases become **statement stacks**: 2–5 short lines, tight leading, staggered left/right, with the emphasis word bigger or heavier.
3. Text sits **in the empty space around the head and chest**, never as a bottom-third subtitle bar.
4. Hard cuts by default. At most 1–3 "effect" transitions per 15 s: light leak, whip blur, or a dark/red dip.
5. B-roll inserts of ~1.2–2.5 s keep the voice-over and their own captions.

**Not this style:** coloured caption boxes, emoji or sticker captions, karaoke word highlighting, heavy zoom pulses on every word, meme sound effects.

## 2. What stays fixed and what can vary
| Fixed (do not change) | Allowed range (seen across the references) |
|---|---|
| Blur-in word reveal, no slide or bounce | Sans-led (ref1/ref2) ↔ serif-led (ref3) mix |
| White soft-glow text, no stroke or box | Small caption at the top above the head (ref1) or at chest height (ref2/3) |
| Tight-leading staggered stacks | Text in front of the subject (ref2) or behind it, occluded by mic/hand/necklace (ref1, ref3) |
| Hard cuts as the default | Transition flavour: green-white leak (ref2), warm yellow/orange leak + red dip (ref3) |
| B-roll carries the voice-over | B-roll type: the creator's own shots (ref1), stock (ref2), film/movie clips (ref3) |
| Calm pacing, about one caption event every 0.2–0.4 s | Optional set-pieces: white card scene (ref2), background-blur focus (ref3), drawn line (ref2) |

## 3. Format and edit rhythm
- **Canvas** 1080×1920, 30 fps, 9:16. Total length 12–15 s in the refs (works up to ~60 s).
- **Shot lengths:** TH segments 1.5–3.5 s; B-roll inserts 1.2–2.5 s, alone or 2 back to back; set-pieces 1.0–1.3 s.
- **Cuts land on phrase boundaries,** never mid-word. A new shot usually starts with the first word of a new clause, and its caption appears on the first frame of the shot.
- **Punch-ins:** about 1 per TH segment, a hard scale step from 100% to 112–118% at a phrase change (ref1 at 2.6 s, ref3 at 11.0 s). No slow Ken Burns on TH.
- **Framing changes between TH segments:** when returning from B-roll, use a different crop (wider or tighter) so the jump looks deliberate.
- **Structure template (15 s):** TH hook with a statement stack → TH, then an effect transition → statement → B-roll ×1–2 with VO → transition back → TH, building to a final statement stack that ends the clip on its last word.

## 4. Caption system
Three tiers. All of them use the same reveal (§4.4).

### 4.1 Tier S — running caption (small)
- Shows filler words between statements, 1–2 words at a time, **replacing** the previous chunk (not accumulating).
- **Font:** sans bold. **Size** ≈ 4.2% of width → **46 px** at 1080w. Tracking −0.02em.
- **Colour** `#FFFFFF`. Variant A (ref1) adds a strong glow; variant B (ref2/3) adds only a subtle shadow.
- **Position:** centred horizontally. Either **above the head**, centre-y ≈ 7% (ref1), or **at chest / collar height**, centre-y ≈ 37–50% (ref2/3). Keep one position per video.
- **Timing:** each chunk appears **on the spoken word onset** and stays until the next chunk. Reveal is a hard cut or a very short blur-in (≤3 frames).

### 4.2 Tier L — statement stack (the hero)
- Use for the 3–6 key phrases per 15 s, usually the clause that carries the meaning ("cleanest editing style", "wins every single time", "self realization.").
- **Size:** 9–11% of width per line → **96–120 px** at 1080w. Emphasis words go up to 13% (**~140 px**).
- **Leading 0.82–0.90.** Lines almost touch.
- **Stagger:** each new line is offset horizontally by 0.5–1.5 em, alternating or stepping diagonally ("wins / every / single / time": right, left, right). Alignment is ragged, centred or left; never justified.
- **Mixing:** heavy sans for the punch words; serif (regular or italic) for connectors and the last word of a thought ("to be", "to the", *habits.*, *world.*). Ref3 flips this and uses bold serif as the hero.
- **Build:** words reveal **one at a time, synced to speech** (one word every ~0.15–0.3 s). The stack **holds** 0.6–1.2 s after the last word, then blurs out over 4–6 frames, or disappears on the next cut.
- **Placement:** in negative space. Left or right of the head, or on the dark chest area. Avoid the face. Two stacks can coexist (left block, then right block: ref2 4.4 s, ref3 4.6 s).
- **Depth (optional, about 1 in 3 stacks):** place the stack **behind the subject**. The subject matte (mic, hand, necklace, shoulder) occludes the text.

### 4.3 Tier B — B-roll caption
- 1–2 words at a time, replacing each other, centred.
- Either a **serif** word at centre-y ≈ 50% at about 5% width (~56 px), white (ref3 film B-roll), or a **gold** sans bold `#F5D97F` with glow at centre-y ≈ 83% (ref2 stock B-roll).

### 4.4 Reveal and exit (the core motion)
| Phase | Spec |
|---|---|
| In | Gaussian blur **14 px → 0** and opacity **0 → 1** over **6 frames (0.2 s)**, ease-out. No translate, no scale (≤2% scale-down allowed). |
| Hold | Static. No wiggle or pulse. |
| Out | Blur **0 → 12 px** and opacity **1 → 0** over **4–6 frames**, or a hard cut with the shot. |
| Whole-stack fade (ref2 "Quality/Quantity") | Opacity 1 → 0.5 → 0 over 0.3 s. |

### 4.5 Glow and shadow
- **White glow:** `text-shadow: 0 0 6px rgba(255,255,255,.55), 0 0 18px rgba(255,255,255,.35), 0 0 36px rgba(255,255,255,.15)`.
- **Legibility shadow:** add `0 2px 8px rgba(0,0,0,.35)` under the glow on busy B-roll.
- **Dark variant** (text over a white shirt or a white scene): colour **`#2B2F38`**, with no glow and a soft `0 0 10px rgba(255,255,255,.25)` halo.
- **Maroon accent** for the last word in the white scene: `#5A1F2B`, used rarely.

## 5. Transitions
| Name | Frames | Recipe | Seen |
|---|---|---|---|
| Hard cut | 0 | Default for ~80% of cuts | all |
| Light leak (cool) | 6 | Additive radial blob: mint `#BFF5D0` → white → lavender `#C9B8FF`, sweeping left→right, peak at frame 3, then cut under it | ref2 3.4 s, 7.9 s |
| Light leak (warm) | 4–6 | Same, but yellow `#FFE58A` → orange `#FF8A3D` → red `#E2402C` | ref3 1.4 s, 8.4 s, 12.6 s |
| Dark-red dip | 6 | Multiply the outgoing shot toward `#3A0A0E` while the text dims, then a leak or cut | ref3 5.6 s, 12.4 s |
| Whip blur | 3–4 | Horizontal motion blur 60–90 px across the cut, with a 1.15× punch-in on the incoming shot | ref2 9.4 s, ref3 11.0 s |
| White flash | 2–3 | Full-frame white, then fade | ref2 7.8 s |
| Card push | 4 | The full-frame clip scales down into the card (§6.1) | ref2 5.5 s |

Budget: at most 3 non-cut transitions per 15 s, never two of the same kind back to back.

## 6. Set-pieces (use 0–2 per video)
### 6.1 Clean-white card (the name-giver)
- **Background:** brushed-silver gradient, cool white top-left to grey bottom-left: `linear-gradient(160deg, #EAF4FB 0%, #E2E8EB 35%, #D6D8DA 60%, #B8BBBD 100%)`, plus a soft white radial highlight at the top-right.
- **Card:** the talking-head clip, **88% of width**, centred, aspect ≈ 0.89 (633×712 at 720w → **950×1068 at 1080w**), centre-y ≈ 51%, **corner radius ≈ 3.6% of width (39 px)**, soft shadow `0 20px 60px rgba(0,0,0,.18)`. There is a magenta `#C026D3` glow peeking out at the bottom-right corner.
- **Content inside the card:** small Tier-L stacks (≈ 45% of normal size), white, plus an italic serif word ("*thumbnail*").
- **Duration** 1.0–1.3 s. Can drift down by about 4% during the hold.

### 6.2 White kinetic scene
- The same silver background with no video. Bold-italic sans in black `#111` builds a stack left-aligned at x ≈ 10%. A **grey UI skeleton** (avatar circles plus rounded bars in `#9A9A9A`, 30–40% blurred) blurs in on the right. The final word is in maroon `#5A1F2B` and fades.
- Exit with a white flash into B-roll.

### 6.3 Background-blur focus (twist)
- While a long statement builds, blur the TH plate with a 24–30 px gaussian over 6 frames. The subject is no longer readable and the text owns the frame. Unblur on the next cut.

### 6.4 Drawn line
- A thin white line (2–3 px at 1080w, with glow) draws diagonally from bottom-left to top-right between two contrasting words ("Quality" ↗ "Quantity") over 0.4 s.

## 7. Picture and grade
- Contrasty, deep blacks, slightly cool shadows (navy studio background). Skin stays natural. No heavy LUTs, no grain, no vignette.
- B-roll may have its own look (film, neon stock). Don't force-match it.
- Momentary grade shift (teal / desaturated) is allowed right after a light leak (ref2 3.6 s).

## 8. Sound
- Low trending instrumental or hip-hop bed under clear speech. Voice is always dominant.
- No SFX were detected on transitions; they are optional subtle whooshes on the whip/leak only. *(Not measured precisely yet — verify in the next pass.)*
- **House SFX map** (team pack: `sfx-library/celf-sfx-pack/`). Each peak lands one frame after its picture event. Effects go only on transitions, never on text.
  | Event | Effect | Volume |
  |---|---|---|
  | Light leak | `Whoosh_02_Wave` | 0.28 |
  | Into blur focus | `Whoosh_03_Reverse_Rise` (peak 0.69 s after its start) | 0.30 |
  | Card push | `Whoosh_01_Sway` | 0.28 |
  | White flash | `Camera_01_Snapshot` | 0.25 |
  | B-roll blur swap | `Whoosh_04_Deep_Sway` | 0.20 |
  | Whip | `Whoosh_05_Fast_Flick` | 0.30 |
- **Mix recipe:** speech median around −20 dBFS (boost quiet phone audio with `data-volume` up to ~2.8). Music bed ~13 dB under the speech. Then a two-pass `loudnorm` on the render to **−15 LUFS, true peak −1.5 dBTP**.

## 9. Fonts
| Role | Likely original | OpenMotion / free stand-in |
|---|---|---|
| Sans (captions, punch words) | Helvetica Neue Bold / SF Pro Display Bold | **Inter** 700–800, tracking −0.03em |
| Bold display serif (ref3 hero) | Tiempos / Gloock-like heavy serif | **Bodoni Moda** 700 (or Fraunces 700) |
| Light serif (connectors, *habits.*) | Times / Instrument Serif | **EB Garamond** 400 / italic |
| Bold italic (white scene) | Helvetica Neue Bold Italic | **Inter** 800 italic |

## 10. Build checklist (per new video)
1. Transcribe with **word-level timestamps**. Captions must hit the word onsets.
2. Mark 3–6 statement phrases per 15 s and choose a stack layout for each (side, stagger, emphasis word).
3. Pick cut points on clause boundaries. Plan 1–2 B-roll inserts and at most 3 effect transitions.
4. Choose at most 2 set-pieces (white card is the default one).
5. If text goes behind the subject, generate the subject matte.
6. Render, then compare side by side with a reference at matching beats. Check reveal timing, glow strength, sizes and stagger.

## 11. Learned from productions
- **IMG_5978 (selfie, face fills ~400–1500 px of 1920), 2026-11-17** — `projects/img5978/`
  - With a close selfie there is no side space. Put Tier S **above the head** (centre-y ≈ 300 px) and Tier L stacks on the **dark hoodie** (y 1480–1830). Keep stacks off the white T-shirt V and the neck.
  - Anchor punch-ins on the **chin line** (`transform-origin` at y ≈ 1450). The face then grows upward, away from the chest captions.
  - A camera pan or other shaky part of the raw take works well **inside the clean-white card** (§6.1). The card turns the pan into a feature.
  - Still B-roll photos (low-res stock, 960 px) work as a **sharp rounded card over a heavily blurred copy of the same photo**. This replaces moving B-roll and hides the low resolution.
  - ~~Where speech is uncertain, cover it with B-roll and no captions.~~ **Corrected by review:** the "uncertain" window was a **second person introducing herself** ("and I am Alina"), which ASR missed. Rule: when another person comes on camera, re-transcribe that window on its own. If the words are still unclear, ask what is said. **Every self-introduction gets its own transition and name card**, matching the first speaker's (e.g. a second card push, or a slide of the card to the new name).
  - **Two-speaker intro recipe (v3):**
    1. Card 1 holds a **still of speaker 1**, taken just before the camera moves, under "My name is / **Name**". This way the raw pan never puts the wrong face over the wrong name.
    2. On the first word of speaker 2 ("and"), do a **card swap**: the card whips out left in 0.12 s (power3.in, blur 14 px) and back in from the right in 0.24 s (expo.out). Play `Whoosh_04_Deep_Sway` on the swap.
    3. Card 2 shows the live take of speaker 2 under "and I'm / **Name**". The name blurs in on its spoken onset.
  - B-roll photos: use the ones the client supplies. Use stock only as a fallback.
  - Approved music default: "Hip-Hop 2" by Deff Syndicate (CC BY 3.0, 95 BPM), ~13 dB under speech.
  - Stack reading order must stay top→bottom, then left→right. A small connector ("so you") placed to the right of the next line reads out of order.
  - The refs use up to 5 effect transitions in 13 s when a set-piece is present (leak, card push, white flash, blur swap, whip). The 3-per-15 s budget applies only to clips without set-pieces.

## 12. Open items
- Word-onset offsets (caption vs speech) still need an ASR pass. Visually the captions land on the word.
- Exact font identification is pending. Sizes are ±10%.
- Music level and SFX have not been measured yet.
