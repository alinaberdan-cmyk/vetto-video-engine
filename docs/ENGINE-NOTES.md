# Vetto Video Engine

Raw footage in → reels, stories and carousels out, in a named editing style, with Alina approving every
step and the storyboard before anything is exported. Built 13 Nov 2026 as a local app so footage never
leaves the Mac. The look (since 14 Nov, Alina's pick) follows the studio in the Reels Engine demo video on
flaviapopescu.eu/motorul-de-reels: cream paper, wine red, pill tabs with status dots, preview left with −5 s / Play / +5 s,
scrubber and Undo, a condensed title, italic serif section titles and one wine button in a bottom bar (`ui/app.css`).
Only Vetto's caption fonts are still used (`ui/vetto/fonts.css`)
so it can move into Vetto Studio later.

**Run:** `vetto-video-engine/.venv/bin/python vetto-video-engine/server.py` → http://127.0.0.1:8770
(macOS sharing can take port 8770; then use the `vetto-video-engine-test` launch config, port 8771)
(or the `vetto-video-engine` launch config). Claude's part: `.claude/skills/vetto-video-engine/SKILL.md`.

## The 11 steps (each one: overview of the choice, options, “Approve step”, “Want a change? Type it”)
1. **Footage**: drop a take, a path on the Mac, or pull your own reel (yt-dlp); where the face is in a landscape take; image bank
   (photos named after a word land on that word); link to account + Vetto batch unit (`plan/units.json`).
2. **Brief**: the prompt, polish, pace (Calm / Medium / Very lively = pacing presets), closing word, outputs,
   language; “Transcribe and propose the cut” (MLX Whisper large-v3, word timestamps, on the GPU).
3. **Cut**: every word is a chip; click to cut / restore, Shift for a range; long pauses shortened (dotted),
   click to keep; fillers and retakes (earlier attempt of a repeated phrase) proposed as cuts. Preview skips cuts live.
4. **Style**: pick a style name; the version is edited in it. 6 styles from the neurofam PDF + learned ones.
   “Teach the engine a new style” sends example videos to Claude (StyleLab). “+ Version” = same cut, another style.
5. **Hook & format**: 107 hooks (100+ Viral Hooks doc), 13 formats with beats (Short-Form Formats Breakdown);
   extra openings saved as variants for trial reels.
6. **Effects**: click a word, put an effect on it. 12 PDF effects + 4 from the brief (pencil outline, image on
   the word, handwriting, green-screen cutout). “On screen, in order” list with Keep / Change / Remove.
7. **Text**: 23 Vetto text-look fonts with filters, 8 palettes (Vetto spectrum, the 4 account colours, PDF orange),
   custom colours, 6 text boxes, position, words at a time, case, size.
8. **Sound**: your 28 Drive sound effects by category, play, put on a word; quick-rule proposals.
9. **Outputs**: reel; stories split at sentence ends (≤ 15 s); carousel drafted from the beats (4:5, ≤ 10 slides).
10. **Storyboard**: overview of every choice + one card per beat (thumbnail, words, effects, images, sounds),
    approve or mark Change per beat; approving it needs steps 1–9 approved.
11. **Check & export**: checks (length, % removed, words/min, hook ≤ 8 words, stories ≤ 15 s, HyperFrames
    effects pending, storyboard approved); quick preview any time, final export only after approval.

## Added 16 Nov 2026 (repo review, see `research/REPOS.md`)
- **Better cuts** (`engine/edit.py`, mirrored in `ui/app.js` keepRanges): word edges snapped to where the voice really
  starts/stops (10 ms energy, `start_r`/`end_r`, set at transcription); a little air before/after a kept word at a cut
  (lead/tail per pace); pauses keep a beat by type (mid-sentence, sentence end, topic change); only silence is merged
  back — a word you cut never returns (fixes a bug where cuts under 0.25 s came back on export).
- **Render** (`engine/render.py`): punch-ins on jump cuts (1.10 Medium / 1.15 Very lively) centred on the face (Apple
  Vision); the hook is on the very first frame (the cover) and steps aside for title effects; colour grade (10, in
  `looks.json` `grades`); loudness from the pace (−14/−16 LUFS, true peak −1.5); 10 caption motions (`caption_anims`):
  pop, bounce, karaoke fill, word by word, fade up, box on the word, glow, one big word, still, slam + keyword block.
- **Library**: 67 fonts (44 Google Fonts via `library/fetch_fonts.py`, `ro: false` = no ș/ț), 24 colour sets,
  "Colours from my video" (picks the frame's colours), 19 styles (13 new drafts in `library/styles_more.json`, each with
  fonts, colours, caption motion, text box, grade, pace and effects that fit), 19 effects (new: freeze-frame + punch,
  masked title rise, VHS glitch). All effect templates share `engine/hf/motion.js` (easing rules).
- **iPhone rotation fix** (16 Nov): footage stored sideways with a rotate flag came out sideways and squashed; the cut now
  strips the flag (`sidedata=mode=delete:type=DISPLAYMATRIX` in `engine/render.py`) after ffmpeg turns frames upright.
- **Move and resize text on the preview** (16 Nov): drag the dashed Captions / Title box anywhere, pull its corner to
  resize, double-click to reset. Saved as `text.cap_pos` / `title_pos` {x, y, w} and `size` / `title_size`; the export
  uses the same place (`\an5\pos` + side margins for the wrap width in `engine/render.py`).
- **Change a word's text** (16 Nov): Cut step switch "Click a word to: ✂ Cut it | ✎ Change its text" (or ⌥-click). The
  timing stays; captions, SRT and effects use the new text; `orig` keeps what Whisper heard.
- **No overwrites between tabs** (16 Nov): every page save bumps `rev`; a page with an older copy gets 409 and reloads
  the newest version (background jobs don't bump; their fields are merged).
- **Export**: "Open the cut in another editor": Premiere/Resolve XML, EDL and SRT (`engine/export_nle.py`).
- **Checks**: hook reading time, sound spacing, cover frame.

## Added 17 Nov 2026: text hooks + live effect previews
- **8 text hooks** (group "Text hooks", drafts) rebuilt in our own code from the text effects in @ugcwithnyomi's TikTok
  7679139537196567840 (local copy in `research/refs/ugcwithnyomi/`, never published): Thrown-in title, Stacked words behind
  me, Text I move under, Written by my finger, Pulled out of the screen, Me between the words, Open-hand reveal, Swipe out.
  Wide heavy sans (Unbounded 800) in white with the reference's yellow #FAFD6C, Gochi Hand for handwriting (Caveat for ș/ț).
  HyperFrames templates `engine/hf/<id>.html` + shared helpers `engine/hf/texthook.js`; the 3 "behind me" ones use the person cutout.
- **Effects step**: pick a word, Shift-click a second word for a phrase, or "⤢ whole line"; every effect box shows the
  name with a live preview under it (the effect's own template, looping, with your words, on a still of your take at that
  moment), then **Apply**. Server: `/prev/<project>/<effect>` (`engine/preview.py`): per moment it makes the frame, the
  face/hand boxes and, only when needed, a still cutout (about 6 s the first time). The 4 ffmpeg effects have browser
  versions in `engine/hf/preview/` for the boxes; their export is unchanged. An effect now stores the whole selection
  (`word`, `word_i` … `word_end_i`).
- All 27 effects are also in `~/Editing Beast/effects/` (template, EFFECT.md, example.mp4, `make_effect.py`).

## Added 17 Nov 2026 (later): the 3 Editing Beast styles + live style examples
- **Styles** (drafts here; approved in Editing Beast): **Clean White**, **Cinema Lexicon**, **Neon Dimension**, read from
  `~/Editing Beast/styles/<id>/STYLE.md` into `library/styles_more.json` (fonts, colours, caption motion, grade, pace,
  effects that fit, and the style's rules).
- **Their signature pieces as effects** (9, HyperFrames, live previews): Statement stack, Clean-white card, Light leak ·
  Silver title card, Hanging key word, Choice buttons · Neon key word, Neon pill, Light burn.
- **Captions**: 2 new motions, Blur-in (Clean White) and Glow pop (Neon Dimension); new text settings `glow` (soft
  light border), `outline_w` (stroke width, 0 = none) and `shadow`, in the editor preview and the export (`engine/render.py`).
- **Grades**: Clean contrast, Neon presenter (with vignette + grain).
- **Style cards** now show a live example instead of a drawing: your frame in the style's grade, your words captioned in
  its font, colours and motion, the hook in its title font (`engine/hf/preview/_style.html`, `/prev/<project>/_style`).
- **Font fix**: 12 downloaded Google Fonts (Inter Tight, Unbounded, Syne, Rubik, Manrope, EB Garamond…) fell back to
  Helvetica on export because libass looks a face up by its legacy family name (nameID 1, e.g. "Inter Tight ExtraBold").
  `looks.json` and `library/fetch_fonts.py` now use that name.

## Added 18 Nov 2026
- **Delete a video** from the start screen: hover a card, ✕ Delete, confirm. The whole project folder moves to the macOS
  Trash as `vetto-video-<id>` (recoverable there); refused while it is still transcribing or rendering.

- **Meme Chaos** (18 Nov, from Alina's final dumb-scale edit; style `~/Editing Beast/styles/meme-chaos/STYLE.md`, draft):
  - **8 effects** (group "Meme Chaos", HyperFrames, live previews):
    - Wavy sparkle hook (Coiny, added to base.css)
    - Meme explosion (keyed Pixabay fire ring 221022, no watermark, + flash + shake + punch)
    - Disco lights (ball, beams, spots)
    - Windows XP background (cutout over a drawn sky/hill)
    - Green-screen meme pop
    - Big-face warp (SVG displacement from every face box)
    - Clap zoom pulse (claps found in the piece's sound: `hfx.onsets`)
    - Crash line + logo (image-bank logo rides a red zigzag)
  - **Keyed meme clips:** `engine/hf/fx/memes/<name>/` (webp frames with alpha + meta.json), made by
    `library/add_meme_clip.py <clip> <name> [--mode fire] [--vertical] [--fade-out 0.3] [--source "credit"]`. They are copied into the render and served to previews at `/prev/a/fx/…`.
    `hfx._boxes` now keeps every face (`faces`), not only the largest.
  - **62 sounds** added to `library/sfx` + `sfx.json` (90 in all), with new categories:
    - meme voice, meme jingle, impact, crowd, funny, music
    - Sources: the Top 40 and Top 5 meme compilations, the Emma Chamberlain pack, the explosion sounds, Island Medium,
      Local Forecast – Slower (CC BY, credit), and Alina's disco beat.
    - Each entry has `source_url` and `license`.
  - **Style:** Meme Chaos in `library/styles_more.json`.

- **Hook step** (was "Hook & format"): formats removed at Alina's request; hooks only.
- **Export now in the style**: the Style step (and Check & export) has "Export in <style> now": a full-size reel of the
  cut in that style without approving the other steps; the render is labelled "quick export (steps not approved)".
- **Captions match the export**: libass sizes by line height, the preview by the em, so exports were 57–74 % of the
  preview size; `engine/render.py` `_em()` now scales by each font's (winAscent + winDescent) / unitsPerEm. The preview
  glow was about twice the export's and is now the same; the spoken word only grows in the preview for the Pop motion.
- The word picker in Effects / Sound scrolls in its own box (it spilled over the titles below).

## Added 18 Nov 2026 (later): a style makes the whole edit (`engine/director.py`)
- Picking **Clean White**, **Cinema Lexicon** or **Neon Dimension** (or "Make the style edit again") places, on your words, what the
  Editing Beast guide does: the caption tier and its place (above the head / chest, from the face), the signature effects
  (statement stacks + background-blur focus, the card, bookends, key words, neon worlds, CTA pill), transitions (light
  leaks, flashes, light burns), punch-ins at phrase changes (`punches`, a hard 1.0 ↔ 1.15/1.12/1.2 step), the sound map at
  the guide's volumes, a music bed and the loudness (−15 / −14 LUFS). Everything is `"by": "style:<id>"`, status proposed;
  running it again replaces only what the style added.
- **Same look, different sound**: the visuals stay the style's; sounds follow what is said (swipe, tap, typing, photo,
  money, done, surprise, appears, fun, time: once on the word, spaced) and the music follows the mood of the words, or the
  **Music vibe** typed in the Style step. No track fits → a request to Claude ("Find a song… vibe: …").
- Music library `library/music.json` + `library/music/` (from Editing Beast): Hip-Hop 2 (CC BY 3.0, credit when posting),
  Jazzy Funk (CC BY-SA 3.0 placeholder), Neon dark bed (licence-free); Neon kit sounds ND_* in `library/sfx/`.
- **18 Nov: 15 more tracks** (18 in all, 82 MB), all CC BY from Openverse / Jamendo, downloaded with Alina's OK: upbeat lounge,
  corporate/motivational, acoustic, lo-fi, chill lounge, emotional piano, two quirky/funny, epic cinematic, dark cinematic,
  smooth jazz, tropical, happy hip-hop, suspense, inspirational. Each entry has its measured loudness (the bed's level is
  set from it), where the music really starts (`start`), vibe tags and the credit line to post. Short tracks loop.
  The automatic pick weighs the moods of the words; a typed vibe wins; the CC BY-SA placeholder only wins when it clearly fits best.

- **iPhone HDR footage** (18 Nov): 10-bit HLG / PQ takes are now detected (`media.probe` → `hdr`, `media.hdr_kind`) and
  tone-mapped to 8-bit BT.709 SDR (Hable) wherever the original is decoded: the proxy, thumbnails, the export's cut (stage 1),
  stills and the style director's face frames (`media.sdr_vf`).
  - Before this, HDR came out washed out.
  - A 10-bit piece also made HyperFrames drop every effect layer and squash the picture.
  - Projects imported before 18 Nov keep their old proxy until the footage is added again.

## Added 18 Nov 2026: rea-video review (see `research/REPOS.md`)
- **Punch-ins on the beat** (`engine/director.py` + `engine/rhythm.py`): when a style makes the edit, each punch-in moves
  onto the music bed's beat if one is up to 0.12 s before / 0.08 s after it. The edit summary says how many
  (`punches_on_beat`). Every track's tempo and beats are measured once into `library/music_beats.json` (tracks with no
  clear beat, like lo-fi and the acoustic one, are left alone).
- **Key words from the voice**: the take's words are measured for emphasis (louder, higher, held longer than the words
  around them; `stress` per word, cached in the project's `media/stress.json`). When a style picks the key word of a phrase
  (hanging key word, neon world, card), a stressed word wins a close call; the effect's note then says
  "“word” said with emphasis". Filler words like "something" are no longer picked.
- **Study a reference video** before teaching a style: `.venv/bin/python engine/study.py <video> [...]` →
  `research/studies/<name>/` with STUDY.md (pace and the nearest engine pace, punch-ins and their size, flashes, grade in
  words, main colours, loudness, beat and cuts on the beat, possible sound hits), study.json and storyboard.jpg.
  Local only; it does not read captions or fonts.
- **Command line** for the two measures: `.venv/bin/python engine/rhythm.py beats <song> [--start s]` and
  `engine/rhythm.py stress <take> [transcript.json]`. Also in `~/Editing Beast` as the skill `beast-measure`
  (`~/Editing Beast/.claude/skills/`), next to a link to the `vetto-video-engine` skill (its paths are absolute now).
- **rea-video skill** installed unchanged in `.claude/skills/rea-video/` (Apache-2.0). Its CLI is not installed (needs
  Python 3.10+, pip packages and ~216 MB of models): ask Alina first.

## Added 18 Nov 2026 (evening)
- **Chat bar attachments**: "Want a change?" has 📎 Attach a file (photos, videos) → `projects/<id>/attachments/`, sent to Claude
  with the next message (`requests[].files`).
- **Green-screen background** (id `xp-background`, was "Windows XP background"): the person (cutout) in front of the last attached
  photo/video, or the one named in its `file` field; videos loop, `bg_start` picks the part. No file → left out of the
  export with the reason; the preview shows a plain green screen.
- **Explosion** (was "Meme explosion"); **Green-screen meme pop** has no default clip any more (its preview shows a green screen;
  a clip comes from an attached green-screen video that Claude adds with `library/add_meme_clip.py`); **Silver title card** has no star.
- Fixed: the Sound list crashed on sounds without a length; a deleted video's address now goes back to the start screen.

## Added 18 Nov 2026 (night): Edit now = Claude edits it, like in a chat
- Bottom bar: **Edit now** next to Approve (once a style is picked). The engine runs Claude Code headless (`engine/claude_edit.py`,
  the copy bundled with the Claude app) in `~/Editing Beast` with the style's STYLE.md (or the engine's style entry), this project's
  transcript, her cut, hook, placed effects, photos and chat-bar attachments. Claude makes the whole edit (captions, text effects,
  transitions, B-roll/stock, sounds, music, set-pieces), renders and checks it, writes NOTES.md + RESULT.json; the reel joins
  the version's renders as "Claude edit · <style>" with its summary and credits. Progress shows in the bar; Stop kills it.
- Allowed downloads without asking (Alina, 18 Nov): Apple emoji icons, transition / sound / text-effect assets, free stock
  clips and photos (no watermark), CC music. Never: paid AI generation, uploading footage, signing in, posting.
- One-time: the background Claude must be signed in (`claude auth login`); `/api/claude` says whether it is.
- Styles **Butter Steps** and **Star Glitch** (renamed from Cream Scatter by Alina, 18 Nov; videos with the old id were moved)
  added (25 styles): all 6 Editing Beast styles (Clean White, Cinema Lexicon, Neon Dimension, Meme Chaos, Butter Steps, Star Glitch) can be picked.

## Added 24 Nov 2026: Final reel | Live edit
- Above the preview, once a version has an exported reel: **Final reel** plays that file exactly as exported (no cut skipping, no
  overlays; opens by default after a Claude edit) and **Live edit** is the engine's step-by-step draft. A Claude edit is built in
  Editing Beast, so changes in the steps don't alter it: they show in Live edit and in the next export.

## Added 24 Nov 2026: Trim & view (was the Storyboard step)
- A CapCut-style timeline in reel time instead of the beat cards: Video (what stays after the cut, with thumbnails), Text
  (hook + caption lines), Effects (+ images), Sounds, Music, and a red playhead that follows the preview.
- Drag on the video track to select a part → ✂ Cut (cuts the words in it); click a caption word to change its text; drag
  effects/images (snap to a word) and sounds (exact time, `clock: "output"`) to move them; click a clip to change, keep or
  remove it; + Sound / + Effect at the playhead; + Music, music track, volume, on/off; Undo; zoom.
- Every change edits the same data as the other steps and marks those steps "changed" if they were approved; "Approve the
  storyboard" stays the last approval before export.

- **Image bank** (Footage step): each photo has a box for the word or phrase it belongs to + "Put it there" (finds the phrase in
  the kept words, or a word starting with it; shows the photo from that word for the phrase's length, at least 1.6 s); "Take off".

## Added 24 Nov 2026: Stock on your words (Pexels, all styles)
- Effects step → **Stock on your words**: the engine finds the kept words that name something showable (food, ordering /
  delivery — searched as "food delivery <word>" —, phone/app, friends, places, objects…; `engine/stock.py` `SHOWABLE`), searches
  Pexels photos + portrait videos for each (official API: her free key, pasted in the engine, kept in `.secrets.json`), and
  places the one she clicks: a photo pop-up on the word (placed away from the face, Apple Vision) or an embedded clip (a
  full-frame cutaway of up to 2.4 s, the voice goes on). A typed search goes on the selected word.
- Edit now uses Pexels only for stock (`stock.py search videos|photos "<query>"`, downloads by id) and adds supporting
  pictures on showable words in the style's own way. Pexels' website search blocks automated fetches; downloads by id work.

## What renders where
Export runs in three stages: (1) the cut, cropped to 9:16 around the face (`focus_x`, set in Footage for
landscape takes); (2) effects on words; (3) images on words, captions + hook title (libass, Vetto fonts),
voice denoise + loudness to −14 LUFS, sound effects.
- **All 44 effects render on export**, each as a 3 s piece starting at its word, then cut back into the reel
  (the voice is never touched):
  - ffmpeg (`engine/effects.py`): word behind me (HyperFrames person cutout), three offset clones; images on words in stage 3.
  - HyperFrames templates (`engine/hf/<effect>.html`, run by `engine/hfx.py`): carousel around me, glass card with
    graph, match cut, pixel words, iOS toggles, zoom + proof cards, notifications, 3D phone, sticker, fly through a
    letter, pencil outline, handwriting on the word, green-screen background. Each gets `V` = its fields, the words
    said in its 3 s, the face and hand boxes (`bin/vision`, Apple Vision, on device), the image bank.
  - Fields per effect (`fields` in effects.json) are filled on the effect's card in the Effects step. Effects that
    need real numbers (glass graph, proof cards) or photos (carousel, green screen) are left out of a render with
    the reason shown, never filled with invented values.
  - While an effect is on screen, captions move out of its way or hide (`caption_zone`).
- Templates build after `document.fonts.ready` and then register the timeline (HyperFrames' block pattern;
  hfx.py wraps them). GSAP 3.14.2 is vendored in `engine/hf/` (from HyperFrames' registry).

## Tools installed 13 Nov 2026 (Alina's OK)
- `tools/`: npm `hyperframes@0.8.186` (Apache-2.0, the version edit-my-video pins) and
  `@ffprobe-installer/ffprobe@2.1.2` (ffprobe 4.4.1, LGPL). Run HyperFrames only through `bin/hyperframes`
  (sets ffmpeg/ffprobe paths, no telemetry). It uses the installed Google Chrome. The cutout model
  (onnxruntime-node, CoreML) downloaded on first use: about 7.5 s per 3 s piece.
- `bin/yt-dlp`: yt-dlp_macos 2026.10.26, SHA-256 checked against the release. TikTok links work logged out;
  TikTok photo posts have no video and are refused with a clear message.
- `bin/ffmpeg`, `bin/ffprobe`: links to the binaries above.

## Files
- `engine/` media.py (ffmpeg, probe, proxy), transcribe.py (MLX Whisper), edit.py (cuts, pauses, retakes), render.py
- `library/` styles.json, effects.json (built by build_pdf_library.py from the PDF), hooks.json, formats.json,
  sfx.json + sfx/, looks.json, outputs.json, pacing.json (build_extras.py), fonts/ (Vetto faces, OFL), sources/
- `projects/<id>/` project.json, media/ (proxy, thumbs), images/, renders/
- `plan/units.json` Vetto batch units (empty until synced)

## Sources and what was used from the repos (13 Nov 2026 review)
- neurofam PDF “12 effects + 6 styles” → effects.json / styles.json (prompts translated, numbers kept).
- learnaiwithhugo/video-editor-skills: **stylelab** and **edit-my-video** installed unchanged in `.claude/skills/`
  (MIT). edit-my-video expects Python 3.10+, ffprobe and English-only Whisper: the engine's own pipeline covers
  those parts on this Mac; its storyboard-first flow and feedback-to-rules loop are the model for steps 10–11.
- social-media-skills/video-editing-skill (MIT): pacing presets, 45 % / 190 wpm warnings.
- MarioRodrigues10/shorts (MIT): cut-by-word and pause UI model; its energy-snapped cut edges are a next step.
- heygen-com/hyperframes (Apache-2.0): renderer for the PDF effects and person cutouts.
- ffmpeg: all cutting and audio. ggml-org/whisper.cpp: skipped (needs cmake), MLX Whisper used instead.
- yt-dlp: standalone macOS binary in bin/. remotion: skipped (company licence). jub0t/concat: skipped
  (AGPL, beta). openpocket capcut-edit: phone UI automation, only its order of operations kept.

## Added 18 Nov 2026 (night): Cinema Lexicon makes a CL01 v6 edit
Alina: "the Cinema Lexicon style in the engine has to reproduce other content the way v6 does" (her approved
`~/Editing Beast/projects/cl01/out/CL01_cinema-lexicon_v6.mp4`, measured in `research/studies/CL01_cinema-lexicon_v6/`).
Picking Cinema Lexicon (`engine/director.py` `cinema_lexicon`) now places, on the words:
- **Example clips** (`overlays[]` with `"kind": "clip"`, full frame, the voice goes on): one literal clip per phrase that names a
  thing, an action or a feeling; never 3 in a row; never on the creator's own demo moments ("this app", "look how…", "show it to you").
  About one per 5 s (v6: 7–8 in 40 s). The slots start empty (`"status": "needs clip"`, a `query` to start from) and a request
  `kind: "example-clips"` goes to Claude, who picks a Pexels clip for the human meaning of each phrase and fills it with
  `engine/stock.py <project> <slot> <pexels id | file> [start s]` (downloads from pexels.com/download/video/<id>/, conforms to
  1080x1920 30 fps in `projects/<id>/clips/`). Each slot has `media_start` and `focus` (0–1, where the 9:16 crop sits).
- **The brand kit** (`projects/<id>/brand/brand.json`, `engine/brand.py`): colours, display font, icon, an app screen, the screen
  recording and the product's real buttons. Claude makes it from a store page or files Alina attaches.
- **7 graphics** (group "Cinema Lexicon", HyperFrames, in the brand kit): Brand open card (first call to action), App buttons drop
  (categories / menu, over the blurred take), App button pops (a button is named), Swipe chip (swipe left / right), Giant number
  (a number + unit gets its own phrase), App screen in a phone (options / scrolling), Brand close card (ads only; the last frame is
  held 1.3 s: `tail` in the version, a new render option).
- **Captions**: new motion "Cut on the word (Cinema Lexicon)" (`anim: "lexicon"`): 1–3 small lowercase words cut on the word; a key
  word alone and big (`text.keys`, punchy or stressed words, CAPS ≤ 5 letters else italic); low on the take, mid on clips, high
  while buttons drop, dark on cream cards, hidden on cards that carry the words.
- **Sound** as in v6: swish on every clip cut, pops on buttons, click + pop on a named button, reverse rise into cards and the
  number, sway + bubbles + sparkle on the close; v6 volumes × 4 (v6 mixed against the raw −27 LUFS voice, the engine against −15).
  Bed 9 dB under the voice, no punch-ins (v6 has none). Interviews / opinion pieces (no brand kit, or no ad words) get no close card.
- **"No pictures" in the brief** (CL02): no clips; punch-ins on the key words and captions on the chest.
- Fonts added: Great Vibes (script word), Lilita One now in the effect templates.
- **Automatic since the same night** (Alina: "when I pick this style these steps must happen too"): right after the Cinema Lexicon
  edit the server runs `lexicon_prep` (job "lexicon-prep"):
  1. **Brand kit, only when she gave a link or attached a kit**: the Style step's "Product link" field or a link in the brief
     (App Store → iTunes lookup API + the page's preview video; Google Play page; any website: name, icon, og:image, description,
     theme colour), or attached files named logo / icon / brand / kit / palette, a brand.json or a zip (`brand.from_link`,
     `brand.from_files`). Colours are read off the icon and screens. Hand-made parts of an existing kit (buttons, colours,
     slogan, font) are kept. The product's real buttons cannot be read off a page: the kit notes it and Claude adds them.
     A new kit → the Cinema Lexicon edit is made again so the cards use it.
  2. **Example clips** found by the engine on Pexels' official API (`stock.auto`): each slot's searches start from the phrase's
     *meaning* (`director.MEANING`: "showed it to me" → "two friends looking at a phone", "decide" → "person thinking
     indecisive"…), then its own words; the first portrait clip long enough and not used yet fills the slot (credit in `source`).
     Needs a free Pexels key, saved once in the Style step (`.secrets.json`, never served). Without a key, or when nothing fits,
     the slots stay for Claude (request `example-clips`).
  - **No Pexels key needed** (Alina has no access to one): without a key the engine searches **Mixkit** (mixkit.co, free licence
    for commercial use, no watermark, no credit required). Pexels pages sit behind a bot check, so they are not scraped. Mixkit's
    search takes short tags, so each slot also has `tags` (`director._tags`: the meaning's tags, then the phrase's words); results are
    ranked by how many words of the clip's title match the phrase's meaning, then probed remotely (length ≥ the phrase + 0.4 s) and the
    1080 file is downloaded. CL01 test: 7 of 7 slots filled in about a minute. A Pexels key still works if one is saved later.
