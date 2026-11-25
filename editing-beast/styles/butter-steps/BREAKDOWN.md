# Reference breakdown: @andreakyton "I built my own AI video editor in Claude"

- Source: https://vt.tiktok.com/ZSpvL1cba/ → `references/andreakyton_7702964649469185287.mp4` (1080×1920, HEVC, 30 fps, 64.7 s, AAC 44.1 kHz)
- Evidence in `analysis/`: 2 fps contact sheets `sheet_01–05.jpg`, 30 fps animation strips `anim_*.jpg`, frames either side of every cut `segments_grid.jpg`, full-res crops `frames/*.png`, word-level transcript `transcript.json`, spectrograms.
- Times are seconds from the start of the file. Frame = 1/30 s = 0.033 s.

---

## 1. Shots and cuts

One locked-off camera for the whole video. A medium shot of the presenter sitting cross-legged on a bed with a pink laptop on her lap, holding a wireless mic transmitter in her right hand. Behind her: a green framed painting, a brown leather headboard, white pillows, a wall lamp on the left. Soft window daylight, natural colour, low contrast, no grade on top.

There are **9 shots and 8 hard jump cuts**. No punch-ins, no zoom alternation, no B-roll shots, no transitions between shots. The framing is the same on both sides of every cut (checked against a grid in `segments_grid.jpg`). The cuts only remove pauses and retakes. Each step of the tutorial is one take.

| # | In → Out | Length | What is said | Cut type out |
|---|---|---|---|---|
| 1 | 0.00 → 9.77 | 9.77 s | Hook: "As a corporate 9-to-5 girly… I made us an AI video editor and it even edited this reel… you're watching right now. Let's" | jump cut |
| 2 | 9.77 → 10.57 | 0.80 s | "…get started." | jump cut |
| 3 | 10.57 → 20.37 | 9.80 s | Step 1: folders, open in Claude Code | jump cut |
| 4 | 20.37 → 29.93 | 9.56 s | Step 2: tools + prompt | jump cut |
| 5 | 29.93 → 40.37 | 10.44 s | Step 3: teach it your style | jump cut |
| 6 | 40.37 → 48.37 | 8.00 s | Step 4: drop the rough cut | jump cut |
| 7 | 48.37 → 49.63 | 1.26 s | "This part is super important." | jump cut |
| 8 | 49.63 → 57.73 | 8.10 s | Step 5: storyboard dashboard, approve / request changes | jump cut |
| 9 | 57.73 → 64.70 | 6.97 s | Payoff + CTA "comment EDITOR" | end on a smile |

- Average shot length: **7.2 s**. Two very short "hinge" shots (0.8 s and 1.3 s) carry a punchy one-liner on its own take.
- Dead air between phrases is trimmed tight. The quietest gaps are 0.1–0.25 s.
- The video has no intro and no outro card. It starts mid-sentence on frame 0 and ends on the last word.

## 2. Visual rhythm (what changes on screen, and when)

The camera hardly changes, so the overlays carry the pace. Something new appears **every 1.5–3 s**:

| Time | Event | Synced to |
|---|---|---|
| 0.00 | Hook title already on screen on frame 0 (no entrance) | start |
| 0.40 → ~1.30 | 9 reel thumbnails pop in one after another **behind** the presenter | "to" / "have" |
| 9.63 | Hook title and collage hard-cut off; yellow pill pops in | "let's" |
| 10.50 → 10.60 | Collage fades and shrinks out | "started" |
| 10.87 → 10.97 | Pill fades out | — |
| 11.00 | "STEP 1 SET UP YOUR FOLDERS" header cuts in; Finder panel glass-fades in over 4 frames | "first" |
| 16.0 / 16.5 / 17.0 | Folder icons highlight one at a time: Raw footage → References → Exports | each folder name |
| 19.4 | "THEN · Open the 📁 AI Video Editor folder in Claude Code" card slides in under the panel | "open" |
| 20.40 | Step 2 header + tools table | "next is the tools" |
| 23.0 | Header text swaps to "STEP 2 SCREENSHOT THIS 📸" | "screenshot" |
| 24.3 | "PROMPT · COPY THIS" card appears under the table | "tell Claude" |
| 30.20 | Step 3 header; frosted empty panel → solid white, 5 empty reel slots | "teach it your style" |
| 31.5 → 32.5 | 5 reel thumbnails fill the slots one by one | "3 to 5 of your own reels" |
| 35.5 | Prompt card: "Study these and pull the fonts, colors, captions and pacing into one brand sheet." | "study" |
| 37.0 → 38.5 | fonts, colors, captions, pacing each get a yellow highlighter swipe | each word |
| 39.43 | Green "✓ BRAND SHEET SAVED" badge pops on the panel corner | "sheet" |
| 40.00 | Step 4 header; Finder "Raw footage" with a dashed drop zone | "now" |
| 41.0 → 42.0 | `rough-cut.mp4` thumbnail is dragged in from the right and dropped | "drop … rough" |
| 44.0 | Prompt card: "Add titles, captions and animations, and show me a storyboard before you export." | "add" |
| 48.00 | Step 5 header; storyboard dashboard (screen recording) | "this part" |
| 50.0 → 51.5 | Dashboard scrolls down to a beat card | "builds this storyboard" |
| 52.0 → 52.5 | "Approve beat" is clicked and turns green "Approved ✓" | "approve each beat" |
| 53.5 → 55.0 | "make this look like an iMessage" is typed into the change request field | "notes" |
| 55.5 | "Request changes" is clicked → "Sent ✓" | "send it back" |
| 56.0 | Toast "✕ Notes sent · Claude is making Draft 2" | "next draft" |
| 57.5 | Header swaps to "STEP 5 THE PART EVERYONE ASKS ABOUT 👀" | "dashboard part" |
| 60.40 | "THE FULL STEP-BY-STEP GUIDE 📘" card: guide cover + 4 ✓ bullets | "step by step guide" |
| 62.37 | Header swaps to "COMMENT "EDITOR" 💬"; Instagram comment bar fades in | "comment" |
| 62.5 → 62.9 | "EDITOR" types itself letter by letter (~1 letter / 2–3 frames), "Post" | "editor" |
| 63.5 | Bubble "andreakyton sent you the guide 📎" pops on the card | "send it right to you" |

Rules that come out of this:
- **Every visual change lands on the spoken word it illustrates** (folder names, "screenshot", "fonts/colors/captions/pacing", "approve", "send", "comment").
- **The overlays do not follow the jump cuts.** A new step panel can land 0.3 s before or after the cut (30.20 vs 29.93, 40.00 vs 40.37, 48.00 vs 48.37). The panel is timed to the word, not to the edit.
- **The header stays on screen and changes its text in place** inside a step ("INSTALL THE TOOLS" → "SCREENSHOT THIS", "APPROVE YOUR STORYBOARD" → "THE PART EVERYONE ASKS ABOUT").
- Stacking: panels build downward. Main card first, then a "THEN" or "PROMPT" card under it, then a badge or toast on top.

## 3. Subtitles

- **One word at a time**, lowercase exactly as spoken (no punctuation), hard swap on each word onset. No entrance animation, no karaoke fill, no box.
- 249 words in 64.7 s: about **3.9 words/s**, so each word holds for about 0.25 s.
- Font: heavy neo-grotesk sans, bold to extra-bold (looks like **Inter Bold / SF Pro Display Bold**). About **62–66 px at 1080 w**, tight tracking.
- Colour: white `#FFFFFF` with a soft dark shadow (about `0 2px 10px rgba(0,0,0,.35)`), no stroke.
- **Key words in butter yellow `#F5EEA8`**: video / AI editor, Claude, screenshot, editor, storyboard, dashboard, guide. These are the product, the hero feature and the CTA word. That is roughly 1 word in 20.
- Position: centred horizontally, **centre at about 68% of the height (y ≈ 1300 px)**, over the presenter's chest, under her chin and above the laptop. The position never moves.

## 4. On-screen text, stickers, picture-in-picture

### 4.1 Hook title (0–9.63 s, top third)
Three lines, centred, over the painting:
1. `I BUILT MY OWN`: geometric sans caps, extra-bold (**Montserrat ExtraBold**), white, about 34 px, y ≈ 295.
2. `AI video editor`: **high-contrast serif italic** (closest: **Playfair Display Italic**; alternatives Instrument Serif Italic or Libre Caslon Italic), butter yellow `#F5EEA8`, about 100 px, y ≈ 410, soft shadow.
3. `IN ✳ Claude`: "IN" in the Montserrat caps, then the tool's logo mark (orange `#D37859`) and wordmark in white serif, y ≈ 506.

It is on screen from frame 0 (no entrance), held for 9.6 s, and hard-cut off when the pill comes in.

### 4.2 Reel collage "proof wall" (0.40–10.6 s)
- **9 portrait thumbnails of her own past reels** (each with its own hook text visible) scattered in an arc around her head, from y ≈ 600 to y ≈ 1180.
- Cards about 160×280 px, rounded corners about 14 px, a soft drop shadow, small random offsets, almost no rotation.
- **They sit behind the presenter.** She is cut out (a person matte), so her head and hair cover the cards. This is the one "depth" trick in the video.
- Entrance: staggered pops starting at 0.40 s, about 0.1 s apart, each scaling up from about 0.6 → 1 in 3–4 frames. Exit: fade + slight shrink over 3 frames at 10.5 s.

### 4.3 Transition pill (9.63–10.97 s)
- `5 steps → let's get started 👇` in **dark brown `#2D2216`, Inter ExtraBold, about 40 px**, on a **butter-yellow `#F5EEA6` rounded pill** (fully rounded ends), rotated about −3°, y ≈ 440.
- Pop in: scale 0.5 → 1.05 → 1 over about 6 frames (9.63 → 9.83). Fade out over 3 frames.

### 4.4 Step header (11.0 s to the end, always the same spot)
- `STEP n` in **butter yellow `#F4EFAB`** + the step name in **white**, all caps, **Montserrat ExtraBold, about 36 px**, centred, y ≈ 190, soft shadow. Often ends in an emoji (📸 👀 📘 💬).
- It cuts in 1 frame before its panel. Its text swaps in place, with no animation.

### 4.5 UI panels (the "picture-in-picture")
These are rebuilt, simplified mock-ups of real UI, not screen recordings. The exception is Step 5, which looks like a real recording of the dashboard.
- Area: **x 65 → 1015 (950 px wide), from y ≈ 220 down to about 620–720**. Always in the top third, above her head. Her face is never covered.
- Card: white `#FCFCFC` (the guide card is cream `#F9F6ED`), **corner radius about 22 px**, large soft shadow, macOS traffic-light dots + window title for Finder and dashboard cards.
- Content type: system UI font (Inter / SF Pro), dark grey text; the repo column is in a **monospace** (SF Mono / JetBrains Mono). Labels are small grey caps with wide tracking (`TOOL`, `WHAT IT DOES`, `PROMPT · COPY THIS`), colour `#6A6967`.
- Sub-cards stack 12–16 px under the main card: a **"PROMPT · COPY THIS" card with a yellow left accent bar**; a pale yellow warning strip (`⚠️ Needs Claude Code on a paid Claude plan · I'm on a Mac`); a "THEN" card.
- **Entrance ("glass in")**: a frosted, blurred, semi-transparent white rectangle appears and sharpens to the solid card over **4 frames (0.13 s)**. No slide, no bounce.
- **Exit**: hard cut, replaced by the next step's card.
- Micro-interactions inside the cards, each on its word: folder highlight (blue selected state), slots filling, yellow highlighter on words, drag-and-drop file, button press → green "Approved ✓", typing in a field, toast, comment typing, DM bubble.

### 4.6 Badges, toasts and bubbles
- `✓ BRAND SHEET SAVED`: small green pill, white caps, pops on the panel's bottom-right corner (scale-in over 3 frames).
- `✕ Notes sent · Claude is making Draft 2`: dark rounded toast on the dashboard.
- Instagram-style comment bar (avatar + typed text + blue "Post") and a DM bubble with an avatar: the CTA is shown as the action itself.

### 4.7 Emoji use
Emoji appear only at the end of pills and headers (👇 📸 👀 📘 💬 📎). Never in the subtitles.

## 5. Audio

- **Voice only. No music bed** (the gaps fall to −53 dBFS room tone; there is no tonal content in the pauses on the spectrogram).
- Mic: wireless lav transmitter held in the hand (visible). Clean, close, dry.
- **Loudness: −14.1 LUFS integrated, loudness range only 2.8 LU.** The voice is heavily compressed or levelled so every word hits the same level.
- Pauses are trimmed to about 0.1–0.25 s, so the speech feels breathless and fast (about 230 words per minute).
- **SFX: almost none.** There are short shimmering high-frequency tones only at 0.20–0.65 s (collage pops) and 9.50–9.70 s (pill pop). These are likely soft "pop/sparkle" sounds mixed well under the voice. The panels, typing and clicks have **no** SFX. Confidence: medium (inferred from the spectrogram, not heard).

## 6. Copy and structure

| Beat | Time | Content |
|---|---|---|
| Relatable hook | 0–4.8 | "As a corporate 9-to-5 girly, I do not have time to edit my reels…" + proof wall of her reels |
| Promise + meta proof | 4.8–9.6 | "…so I made us an AI video editor, and it even edited this reel you're watching right now." |
| Route map | 9.6–11 | "5 steps → let's get started" |
| 5 numbered steps | 11–57.5 | Each step = header + UI card + copyable prompt. ~8–10 s per step |
| Curiosity peak | 57.5–60.4 | "The dashboard part is the one everybody asks me about" |
| Lead-magnet CTA | 60.4–64.7 | Guide card → "comment EDITOR" typed live → "sent you the guide" bubble |
