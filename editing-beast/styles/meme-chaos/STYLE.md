# Meme Chaos

> One raw, mostly uncut phone take of friends or colleagues doing a challenge in the office. **Every person's turn gets
> its own meme moment**: a fire explosion, disco lights, a Windows XP wallpaper behind them, a clapping meme cat,
> big-nose face warps, a red "crash" line. Each moment has **its own meme sound on the same frame** (Spawn, Vine boom,
> Windows XP, Faa, explosion, applause). Claps get quick zoom pulses. It opens on a **wavy, sparkly, bubbly hook title**.
> Captions are plain white, low on the frame. An upbeat music bed switches to **elevator music for the punchline**.

- Status: **v1 draft, 18 Nov 2026**, waiting for Alina's OK. The working name "Meme Chaos" is Claude's pick, so rename it if you like.
- **Built from:** one production, the final Prosus "dumb scale" contest video, 17 Nov 2026 (Teammate A, Teammate B, Alina).
  - Claude rendered the draft from Alina's brief, then Alina finished it herself.
  - The approved example is her final: `examples/meme-chaos_dumb-scale-contest_team_2026-11-17.mp4` (also in `../../finals/`).
  - Claude's draft before her changes: `references/claude-draft_before-alina-changes.mp4`.
- **Evidence** (`analysis/`):
  - Her final compared with the draft, frame by frame (`cmp_*.jpg`, `pair_*.jpg`) and sample by sample in the audio.
  - Her new disco sound: `her_disco_sound.wav`.
  - Crops of the cat and the face warp: `cat_strip.jpg`, `face_strip.jpg`.
- **Sounds:** every sound from the links in the brief is cut into single files in `sounds/` (62 files, list in `sounds/MANIFEST.tsv`, made by `tools/extract_sounds.py`). The same files are in the Vetto engine's Sound step.
- **Effects:** the 8 effects are in `../../effects/` (group Meme Chaos) and in the Vetto engine (Effects step, group "Meme Chaos").

---

## 0. The main rule: adapt, don't copy (Alina, 18 Nov 2026)
> "The way this style should work is that it doesn't copy the same editing to another video, but adapts and twists
> different other elements so that it's the same level of funny. Use other sound effects or background music.
> Understand the video context and situation."

Meme Chaos is a **level of funny and a rhythm** (a meme beat on every turn, entrance and punchline, the take kept raw), **not a fixed list of sounds and effects**. The dumb-scale example is one instance, not a template.

For every new video:
1. **Read the situation first.** Who is in it, and what is going on (a contest, an unboxing, a team reveal)? What do the shirts, props, words and place say? What is the joke of each moment? Write that down before choosing anything.
2. **Pick each gag from what is in the shot.** A "CEO" shirt walking in → boss-entrance sound. A mic held up → red-carpet camera flashes. A beach wallpaper → vacation music. The sound and picture should "say" the same thing as the moment (rule 7.3).
3. **Rotate the sounds and music.** Don't reuse the previous video's sound set or music beds (Spawn, Vine boom, Windows XP, Island Medium, elevator music) by default. Keep one only when it is clearly the best joke for that moment. A sound used in the last Meme Chaos video needs a reason.
4. **Music follows the story's mood shifts** (tension → swagger → payoff), chosen from `vetto-video-engine/library/music.json` by its vibe tags. It does not always switch to elevator music.
5. **Keep the same intensity:** about one meme beat every 2–4 s, hits louder than the voice, an effect on each person's big moment, the hook question, plain captions and the master level (§6).
6. **Mark every pick as Claude's** in the delivery note with the reason, so Alina can swap it.

## 0b. Meme reaction pictures (Alina, 24 Nov 2026)
> "You can pick up words or facial expressions that would relate to a meme and then insert that meme picture in there from
> the Pinterest FeedMe Emotii folder on desktop."

- **Library:** `~/Desktop/Pinterest FeedMe - Emotii/` (170 meme pictures from her Pinterest board, sorted by emotion into
  `Amuzament` (fun), `Curiozitate` (curious), `Dezgust` (disgust), `Fericire` (happy), `Furie` (angry), `Incredere`
  (confident), `Indiferenta` (don't care), `Iubire` (love), `Liniste` (calm), `Surpriza` (surprise), `Suspiciune`
  (suspicious), `Tristete` (sad). `index.csv` lists each file with its emotion. The file names describe the picture
  (Romanian), e.g. `barbat_cu_mana_pe_obraz_surprins`. Many come twice: `_original.jpg` and a cut-out `_fara_fundal.png`.
  Skip `_Duplicate/` and the loose hash-named files at the top level unless one clearly fits.
- **When:** a **word** that names or implies an emotion or a meme situation ("wait what", "no way", "I'm done", "love it",
  "suspicious", "money", "cringe"…) or a **facial expression / gesture** in the shot (shock, eye-roll, smug grin, cringe,
  side-eye, crying-laughing, facepalm). Find them from the transcript AND from contact sheets of the faces (4 fps around
  each turn). Write each one in the context sheet with its emotion folder.
- **Which picture: use the catalogue `meme_pictures.json` (in this folder).** Every picture has what it `shows`, the meme's
  `meaning`, the concrete moments it fits (`use_when`), its `quality` and its `cutout` file. Pick by **meaning and situation**,
  not by emotion folder: the emotion folders are only a rough sort.
- **The relevance test (Alina, 24 Nov 2026: "only the last meme was relevant, you need to do a better job at selecting
  memes").** A meme goes in only when ALL of these hold:
  1. **The meme's joke is the moment's joke.** The meme's `meaning` describes what is happening or being said right now
     (the same action, the same situation, or exactly what the viewer is thinking), not just a matching mood. "Someone
     says nice" → "girl snapping fingers" passes; "someone pulls a shirt over his head" → "boy scratching his head
     (confused)" fails, because nobody is confused.
  2. **The 1-second test:** a viewer gets why it is there instantly, without explanation. If it needs a sentence to explain,
     drop it.
  3. **Quality:** `clean` first. `screenshot` only when you crop away the phone frame and it still reads. `caption-baked`
     only when its caption is exactly the moment AND readable on screen. Never `not-a-meme`.
  4. **Write the match** in the context sheet as one line: moment (time + what happens / what is said) → meme (n, meaning)
     → why they are the same joke. If the "why" is only an emotion word ("happy", "confident"), it is not a match: drop it.
- **Fewer, better.** 0–3 meme pictures in a 30–40 s video is normal. Zero is fine when nothing matches. Never fill a quota.
- **Food moments first for FeedMe:** the catalogue marks food memes (delivery horse, cooking cats, tenders, pizza, "full stop").
- **Lesson from IMG_0780 (24 Nov 2026):** of 5 picks only "girl snapping fingers" on "nice" worked. The others failed the test:
  the confused kid on a silly moment (wrong meaning), gold sunglasses on "you should be jealous" (a screenshot, and "cool" is
  not "jealous"), the crossed-paws chihuahua floating in the ceiling (looked random), the raised fist on "rocking the merch"
  (no link).
- **How it looks:** prefer the cut-out `_fara_fundal.png` as a sticker beside the person (never over the face), about
  35–45% of the frame height, a white 10–14 px outline and soft shadow, popping in on the word / expression frame (scale
  0.6 → 1 with a small overshoot in 0.2 s), held 0.8–1.4 s, popping out in 0.12 s. Use the `_original.jpg` as a tilted
  photo card when no cut-out exists. Its own short sound on the same frame (pop, boom, or the sound that matches the meme).
- **How many:** only as many as pass the relevance test (often 0–3 per video), never two on screen at once, never on the same
  beat as a big effect. They add to the funny; they don't replace the per-turn effects.

## 0c. Objects she names → object memes, and never a bare edit (Alina, 24 Nov 2026)
> "The Meme Chaos is not good, there's no music, effects, transitions, photos. Select some memes related to the objects I am
> mentioning from Pinterest, so like an apple funny picture, chocolate and car meme."

- **Every concrete object she names gets a funny meme picture OF THAT OBJECT** (this replaces the plain PNG cut-out other
  stock-free styles use). IMG_1600 "a photo of an apple, a chocolate bar and a car" = an apple meme, a chocolate meme, a car
  meme, each popping on its word's onset, in the §0b sticker look (white outline, soft shadow, pop 0.6 → 1 with overshoot,
  its own sound on the same frame), beside her, never over the face.
- **Funny pictures of the object itself, never text memes** (Alina, 24 Nov 2026: "I just need object funny pictures, not
  text images"): the object doing or being something absurd (an apple with a face sticking its tongue out, a cat stuck in a
  chocolate bar, a car shaped like a banana). No captions, no meme text, no screenshots.
- **IMG_1600 picks (Alina approved the car):** apple → `Obiecte/mar_cu_limba_scoasa_fara_fundal.png`, chocolate bar →
  `Obiecte/pisica_in_baton_de_ciocolata_fara_fundal.png`, car → `Obiecte/masina_banana_fara_fundal.png` (her own pick).
- **Cut-outs:** `"<engine>/bin/lift" in.jpg out.png` (the macOS "lift subject" mask) is
  cleaner than `hyperframes remove-background` on photos; a PNG that is already transparent is used as it is.
- **Where from, in order:** (1) `~/Desktop/Pinterest FeedMe - Emotii/Obiecte/` (funny object pictures from Pinterest, `index.csv`
  lists them); (2) the catalogue `meme_pictures.json`, searching `shows` / `meaning` for the object: apple →
  `Amuzament/barbat_cu_mar_pe_post_de_telefon.jpg` (man using an apple as a phone) or `Amuzament/iphone_muscat_ca_un_mar.jpg`
  (iPhone with a bite out of it); (3) when her library has nothing for an object, a funny photo of exactly that object from
  Pexels (an object doing something absurd, a giant one, a melted chocolate bar, a tiny car…), cut out with
  `bin/hyperframes remove-background`, in the same sticker look. Write in NOTES.md which source each object used.
  The relevance test of §0b still holds: the picture must be that object, instantly readable.
- **The full style kit is mandatory, never a bare talking head:** the music bed (§6), the per-turn effects (§5), the cuts
  and transitions (§3), the wavy sparkle hook (§4.1), the captions (§4.2) and the meme sounds on every gag. Before finishing,
  check the rendered contact sheet and the audio: music audible under the voice the whole video, at least one transition
  and one effect per 5–8 s, every meme picture with its sound. If any is missing, fix it before RESULT.json.

## 0d. Approved benchmark: IMG_0780 test 2 (Alina, 25 Nov 2026)
> "The Meme Chaos test 2 (IMG_0780) was a very good example, also the sound effects that it picked."

- Video: `examples/meme-chaos_team-merch-reveal_team_2026-11-24.mp4`; every choice and why: `examples/meme-chaos_team-merch-reveal_team_2026-11-24_NOTES.md`. Measure new edits against it.
- **The sound rule it proves: every sound names what is happening, literally.**
  - The shirt held up like a holy relic → **Heavenly** choir.
  - Clothes put on wrong → **"And I oop"**.
  - Mic held up → 3× **camera clicks** with the flashes (red carpet).
  - "You should be jealous" → pop, then **"Catch me outside, how 'bout dat"**.
  - Gang pose → **explosion**; the whole group copies it → **Thug Life**.
  - Late arrival → **Undertaker's bell**; group pose held → **Bass Drop**; the spin → a **whoosh**.
  - Payoff on the beach wallpaper → the music **switches to tropical**.
- Memes: only 3, each passing the §0b test; never on the same beat as a big effect; nothing in the last ~1.3 s.
- Music: a confident hip-hop bed for the swagger part (about 2 dB under the voice, then level), and a mood switch at the
  payoff.

## 1. When to use it
Use Meme Chaos when the input is **one continuous take of 2–5 people** doing something silly together, 30–90 s, and the brief says funny, Gen Z, meme or office fun. Typical inputs: a contest, a challenge, "rating" each other, a reveal, team intros.

**Signature (all in the example):**
1. **The take stays raw.** There are no transitions, no B-roll and no grade. Only dead waits are cut.
2. **One meme moment per person's turn.** Each turn gets a different effect, and the effect and its sound start on the same frame.
3. **Meme sounds on every entrance and big beat**, louder than the voice: +2 to +9 dB over the speech.
4. **Zoom pulses on claps** (1.05–1.08×, settling back in 0.2 s, on every clap).
5. **Wavy sparkle hook title** on the opening seconds; **plain white captions** low on the frame the whole way.
6. **Two music moods:** an upbeat bed (Island Medium) under the game, then elevator music after the punchline.

**Not this style:**
- Polished presenter edits, B-roll, branded cards or kinetic type. Those belong to Clean White, Cinema Lexicon and Neon Dimension.
- Transitions between shots.
- Captions in boxes.

## 2. Structure (the example, times in the final video)
| Part | Time | What happens |
|---|---|---|
| **Hook** | 0–4.6 s | "who's the dumbest / in our office?" waves on the chest. Spawn as the 2nd and 3rd person pop into frame (3.2 s, 5.55 s). |
| **Rules** | 5–21 s | The intro and "it's a contest" are left alone: only captions and the music bed. |
| **Turn 1 (Alina)** | 22.1 s | Tongue + rock hands: **meme explosion** (fire ring on the face, flash, shake, punch zoom 1.18) + explosion sound. |
| **Reaction** | 24.9–28 s | Teammate A claps: **clap pulses**. "you can give them applause" gets the applause sound (27.7 s). |
| *cut* | 30.0 s | 2.8 s of Teammate A standing still removed. |
| **Turn 2 (Teammate A)** | 30.35–31.6 s | His move: **disco lights + disco ball**. Alina **replaced all the audio here with a ~130 BPM dance beat** (no voice, no Vine boom). |
| **Reaction** | 33.6–34.8 s | Alina pops in clapping: a **clapping purple cat** (green-screen meme) dances next to her. Applause sound. |
| *cut* | 35.0 s | 2.5 s of empty frame removed. Spawn as Teammate B walks in. |
| **Turn 3 (Teammate B)** | 37.13–38.43 s | His pose: the **Windows XP wallpaper** replaces the room behind him (person cut out). Windows XP sound at 37.32 s, the loudest hit in the video. |
| **Reaction** | 39.0–41.6 s | Everyone claps: **clap pulses** + applause. |
| **Punchline** | 46.6–49 s | "this is called the dumb scale": Vine boom + punch zoom. **Music switches to elevator music** (49.0 s). |
| **Explainer** | 49–56 s | The Moldova explanation: captions only, elevator music. |
| **Brand joke** | 56.6–59 s | "this is how the company Prosus…": **logo badge at the raised hand, red crash line follows the arm down and off screen**, Faa as it leaves. |
| **Ending** | 61.9–63.7 s | "one, two, three!" group pose: **big-face warp** on all three faces. Nothing over the last second (Alina removed the final Faa). |

## 3. Cuts and transitions
- **Hard cuts only, and only on dead air.** There are 2 cuts in 71 s: 2.8 s and 2.5 s of nobody doing anything.
  - The rest of the take plays as shot, including false starts and talking over each other.
  - Alina kept both cuts and added none.
- ~~No transitions.~~ **Transitions on the phrase changes (Alina, 25 Nov 2026: "Add transitions", after an IMG_1600 edit
  with hard cuts only).** One every ~4–6 s, on a sentence/beat change (best in a pause), each a different kind and each with
  its own whoosh landing on the cut frame. The out half is 0.10 s before the cut and the in half 0.16–0.18 s after, all on the
  whole frame:
  - **Zoom blur:** rush into the face (scale 1.7, blur 14 px), then come back out to 1 with the blur clearing.
  - **Whip pan:** blur off to one side (x −230, scale 1.45, blur 20 px), then back in from the other side.
  - **Glitch shake:** 5 frames of jitter (±10–36 px, scale 1.08–1.18) with hue shifts and contrast 1.6, then clean.
    Use it into a mood turn.
  - **Vertical whip:** blur up out of frame (y −300, scale 1.4, blur 20 px), then back in from below.
  - No spins: the HyperFrames video layer ignores rotation, so only the zoom and blur would show.
  - Sounds come from the shared celf whooshes (`Whoosh_05_Fast_Flick`, `Whoosh_02_Wave`, the end of `Whoosh_03_Reverse_Rise`
    rising into the cut, and `Whoosh_04_Deep_Sway`), at about −15 LUFS.
  - Code: `projects/engine-20261124-img-1600-meme-chaos-2-e5a1-meme-chaos-181746/build.py` (`TRANSITIONS`).
  - Never on the same frame as a meme picture's pop-in or a big effect.
- **Camera moves:**
  - A punch zoom on big moments (1.15–1.28×, in over 0.08 s, out over 0.15 s).
  - A push zoom on the XP pose (1.22× over 1 s).
  - Clap pulses (§5).

## 4. Typography
### 4.1 Hook: Wavy sparkle hook (`wavy-sparkle-hook`)
- **Font:** Coiny (rounded, bubbly), 92 px at 1080 w, white fill, dark green outline `#1C5428` (9 px), soft drop shadow.
- **Text:** 2 lines, lowercase, a question to the viewer. Placed on the chest under the face (lines at y ≈ 790 / 900), never on a face.
- **Motion:**
  - Letters pop in one by one (0.04 s apart, overshoot).
  - Then every letter floats on a wave: ±16 px, ±6°, 1.1 Hz, each letter 0.55 rad behind the last.
  - 10 four-point sparkles twinkle around the title. The whole title fades over the last 0.3 s; it is on screen for 4.6 s.
- **Idea from:** the opening of the Emma Chamberlain sound-effects video (`references/h2lJsTaBBU0.mp4`).

### 4.2 Captions
- **Font:** TikTok Sans Bold, 66 px, white, thin dark outline + soft shadow, no box.
- **Placement and timing:**
  - Centred at y = 1440 (75 % of the height).
  - 1–4 words per chunk, swapped hard on the word, lowercase as spoken.
- **Names are spelled as the people spell them** (Teammate A, Teammate B). Ask when unsure.
- **Overlapping or unclear speech gets no caption.** Never guess.

## 5. Effects (all 8 are 3 s Vetto/Editing Beast effects)
| Effect (id) | In the example | How it looks | Sound on the same frame |
|---|---|---|---|
| Wavy sparkle hook (`wavy-sparkle-hook`) | 0–4.6 s | §4.1 | Spawn as people pop in |
| Meme explosion (`meme-explosion`) | 22.1 s | Green-screen fire ring (keyed) 1350 px wide on the face, warm white flash 0.14 s, shake 26 px dying out over 0.7 s, punch zoom 1.18. The example used CapCut's "Explosion for Meme"; the library now uses a clean Pixabay clip of the same burst (`references/pixabay-221022_fire-explosion-green-screen.mp4`) | Explosion (meme blast) |
| Disco lights (`disco-lights`) | 30.35–31.6 s | Disco ball drops on a string and spins; 6 colour beams sweep from it; 7 soft colour spots; room dimmed 45 %; flicker | **Disco beat (Alina's)**, replacing the take's audio |
| Green-screen meme pop (`greenscreen-meme`) | 33.6–34.8 s | Clapping purple cat, right of the person, bottom on the table line, ~35 % of the frame tall, pops in, loops, pops out | Applause |
| Windows XP background (`xp-background`) | 37.13–38.43 s | Room → blue sky + green hill wallpaper behind the cut-out person, 0.1 s fades, starts ~0.2 s before the sound | Windows XP Start |
| Clap zoom pulse (`clap-pulse`) | 24.9–27 s, 39–41.6 s | Jump to 1.05–1.08×, back in 6 frames, on every clap (~every 0.19 s) | Applause |
| Crash line + logo (`crash-line`) | 56.6–59 s | Logo badge (white circle, red rim) at the raised hand; red zigzag "stock crash" with white outline draws down-left off screen along the arm's sweep; badge rides the tip | Faa as it leaves the frame |
| Big-face warp (`face-warp`) | 61.9–63.7 s | Every face swells into a big-nose fisheye face, 4-frame ease in/out | — (Alina used none) |

Rules:
- **One effect per turn, no repeats.**
- An effect lasts as long as the move it marks (0.7–1.9 s) and never covers a face that is talking.

## 6. Sound design (measured on Alina's final)
- **Master:** integrated **−14.5 LUFS**, loudness range 9 LU, true peak −0.4 dBFS.
  - Alina's export peaks higher than our usual −1.5 dBTP. Keep −1.5 dBTP for ours.
- **Voice:**
  - Light compression (threshold −26 dB, 3:1) and high-pass at 80 Hz.
  - Speech sits at about −16 LUFS momentary.
- **Music:**
  - **Intro (0–14 s):** Island Medium about 2 dB under the voice. Alina pulled it down ~6 dB here, and the two Spawns ~3 dB, so the intro words are clear.
  - **Game (14–49 s):** Island Medium about level with the voice. She kept this.
  - **Punchline → end:** elevator music ("Local Forecast – Slower", Kevin MacLeod) about 7 dB under the voice, 0.4 s fade in, 1.2 s fade out.
- **Meme hits:** loudness over the speech.

| Hit | Over the speech |
|---|---|
| Spawn | +1.6 to +4.4 dB |
| Explosion | +3.7 dB |
| Applause | +2.9 to +4.6 dB |
| Disco beat | +5.4 dB |
| Vine boom | +4.6 dB |
| Faa | +8 dB |
| Windows XP | +9 dB (the loudest) |

- **Never a sound on the very last second.**
- **No double hits:** when an effect has its own beat (the disco), the take's audio and any other SFX under it go.

**Sounds** (`sounds/`, also in the Vetto engine's Sound step):
- `meme-top40_QRQEHtIiuDc/`: all 41 sounds of "Top 40 Viral TikTok Meme Sound Effects (2026)" (Spawn, Windows XP Start/Shutdown, Bass Drop, Metal Pipe, Flashbang, Fahh…)
- `meme-top5_DogH-RgansQ/`: Faaa, Vine boom, Get out, Yoooooo, Rizz
- `emma-chamberlain-10_h2lJsTaBBU0/`: Crowd Applause, Golf Hit, Fart, Censor Beep, Camera click, Booing Crowd, Bass Boosted, Bell, Awkward Crickets, Smash Glass (+ her intro talk and the outro jingle)
- `explosion_hryVXjkxs8w/`, `capcut-explosion-for-meme_…/`: the explosion sounds
- `music/`: Island Medium (iMovie), Local Forecast – Slower (Kevin MacLeod, **CC BY 4.0, credit needed**)
- `used-in-dumb-scale/`: the exact cuts used in the example + Alina's disco beat

## 7. What Alina changed on Claude's draft (rules learned)
1. **Disco lights on the second person's move, not on the third.** Their sound is a dance beat that replaces the take's audio for 1.6 s, not a Vine boom.
2. **Added a reaction meme** (clapping cat) on the clapping after a turn → reactions get their own small meme.
3. **Added the XP wallpaper** behind the pose that has the Windows XP sound → the picture should "say" the sound too.
4. **Added zoom pulses on every clap.**
5. **Added the big-face warp on the final group pose** → the ending gets a visual gag, not a sound.
6. **Lower music under the intro** (−6 dB) and quieter Spawns (−3 dB) → the opening words must be easy to hear.
7. **No sound on the last second** (the end Faa was removed). Spelling: Teammate A, Teammate B.

**Learned from productions**
- **IMG_0780 team merch reveal, 18 Nov 2026:**
  - The first render copied the dumb-scale sounds and music (Spawn, Vine boom, Rizz, disco beat, Windows XP, Island Medium, elevator). Alina rejected that as copying (rule §0).
  - She also chose:
    - The fire explosion on the crossed-arms pose instead of the disco lights, with no disco sound.
    - No explosion on the shirt reveal.
    - The site's beach wallpaper for the final pose.
  - A cutout over a wallpaper must be median-smoothed over ~9 frames, or chairs and people at the back flicker.

## 8. Build checklist (per video)
- **Meme reaction pictures** (§0b): list the words and facial expressions that fit an emotion folder, pick one picture per moment.
0. **iPhone HDR takes** (10-bit HLG, e.g. IMG_0780): tone-map to 8-bit SDR first (`zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable,zscale=t=bt709:m=bt709:r=tv,format=yuv420p`). A 10-bit piece makes HyperFrames drop the effects and squash the picture.
1. **Transcribe** with word timestamps; mark each person's turn, every clap, every entrance and the punchline.
2. **Cut** only dead waits over ~1.5 s.
3. **Hook:** a question to the viewer in 2 short lines → `wavy-sparkle-hook` for the first 4–5 s.
1b. **Context sheet** (rule §0): one line per moment with what is happening and what the joke is, then the sound/effect/music that tells that joke. Check it against the last Meme Chaos video's choices and swap repeats.
4. **Turns:** give each person's move a different effect with its sound on the same frame. Choose from the whole effects library, and pick what fits the move (the dumb-scale run was explosion → disco → XP wallpaper).
5. **Reactions:** clap pulses on claps and one reaction meme. Pick the reaction sound to fit (applause, crowd laugh, booing, crickets…).
6. **Entrances and punchlines:** a sound that says who or what enters (Spawn, a boss bell, a game jingle…) and an impact + punch zoom on the punchline. Rotate them between videos.
7. **Brand or "fail" joke:** `crash-line` with the logo from the image bank, plus a fail sound.
8. **Ending:** a visual gag on the group pose (face-warp or another), nothing on the last second.
9. **Mix:** music under the intro ~2 dB below the voice, level after. Switch the music mood where the story turns (not always to elevator music). Master −14.5 LUFS, −1.5 dBTP.
10. **Captions** on everything that is clear, none on overlaps.
11. **Brand merch / products:** product PNGs (transparent) as die-cut stickers with a white edge that pop in on the words that name them (one per word), then a store-name end card over the last beat (first used on IMG_0780, 18 Nov 2026, PNGs from feedmeplzthanks.store in `references/merch-feedmeplzthanks-store/`).

## 9. Open items
- **Explosion clip: solved 18 Nov 2026.**
  - The watermarked CapCut clip was replaced (Alina's choice) by Pixabay video 221022, "Fire, Explosion, Effect, Green Screen" by Sabawaihi.
  - Pixabay Content License: free for commercial use, no credit needed, no watermark.
  - It is keyed as `explosion` (first burst only, 0–1.35 s, 0.3 s fade-out).
- **Clapping cat clip:** not in the library yet. Add it with `vetto-video-engine/library/add_meme_clip.py <clip> cat` once Alina shares the green-screen file or its source.
- **Disco beat:** taken from Alina's final (1.6 s). The original track's name and licence are unknown.
- **Windows XP background:** our version is drawn in code (sky, clouds, green hill). It is not the original photo.
  - Alina's version kept the table edge at the bottom. Ours covers everything behind the person.
- **Island Medium** is iMovie music. **Elevator music** needs the credit line: *Local Forecast – Slower by Kevin MacLeod (incompetech.com), CC BY 4.0*.
- **All meme sounds are from YouTube compilations.** Their licence is unknown, so check before using them in paid content.
- **Built from one video only.** Add "Learned from productions" notes as more Meme Chaos videos are made.
