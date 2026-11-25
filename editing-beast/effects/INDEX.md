# Effects: index

Every effect from the Vetto Video Engine (`Content Matrix FeedMe/vetto-video-engine`), copied here on 2026-11-17 so any
Editing Beast style can use them. Each one is a 3 s HyperFrames composition (1080x1920) that plays over the 3 s of the
reel starting at its word; the voice is never touched. Same files as the engine: when an effect changes there, copy it again.

51 effects in 13 groups: Carousel & glass, Match cut & pixels, Toggles & zoom, Word & notifications, Phone & copies, Sticker & fly-through, From Alina's brief, New (16 Nov), Text hooks, Clean White, Cinema Lexicon, Neon Dimension, Meme Chaos.
The 8 **Text hooks** come from the text effects in @ugcwithnyomi's TikTok 7679139537196567840 (ideas only, our own
code; frames of the reference in `_reference/`). They are drafts until Alina approves them.

The groups **Clean White**, **Cinema Lexicon** and **Neon Dimension** are the signature pieces of the 3 styles in `../styles/`,
rebuilt as 3 s effects for the Vetto engine (17 Nov 2026).

The group **Meme Chaos** (18 Nov 2026) is every effect of Alina's final dumb-scale edit, the 4th style in `../styles/meme-chaos/`.
Keyed green-screen meme clips for them are in `_memes/` (the engine's `engine/hf/fx/memes/`).

7 more **Cinema Lexicon** effects (18 Nov 2026, `lexicon-*`) are the graphics of Alina's approved CL01 v6, drawn in the
product's own brand kit (`--brand <folder>` in make_effect.py): open card, app buttons drop, app button pops, swipe chip,
giant number, app screen in a phone, close card.

| Effect | id | Group | Use it when | Extra inputs | Status |
|---|---|---|---|---|---|
| [Carousel around me](pov-carousel-spin/EFFECT.md) | `pov-carousel-spin` | Carousel & glass | a list, many examples, 'all my…' moments | cutout, images | from source |
| [Glass card with graph](liquid-glass-graph/EFFECT.md) | `liquid-glass-graph` | Carousel & glass | a number, progress, growth, result | numbers | from source |
| [Match cut on one word](match-cut/EFFECT.md) | `match-cut` | Match cut & pixels | the key word / brand name; a transition between your clips | no-video | from source |
| [Pixel words](screen-push-digital/EFFECT.md) | `screen-push-digital` | Match cut & pixels | a short punchline of 3–4 words | no-video | from source |
| [iOS toggles](apple-ui-toggles/EFFECT.md) | `apple-ui-toggles` | Toggles & zoom | steps, pros, a 3-item list | — | from source |
| [Zoom + proof cards](over-the-shoulder-zoom/EFFECT.md) | `over-the-shoulder-zoom` | Toggles & zoom | proof, two numbers, before/after facts | numbers | from source |
| [Word behind me](text-behind-me/EFFECT.md) | `text-behind-me` | Word & notifications | the one word the clip is about (4–7 letters) | cutout | from source |
| [Notifications over my head](notification-stack/EFFECT.md) | `notification-stack` | Word & notifications | 'my phone blew up', orders, messages, reactions | — | from source |
| [Video in a 3D phone](phone-3d-float/EFFECT.md) | `phone-3d-float` | Phone & copies | showing an app, a screen recording, 'look at this' | — | from source |
| [Three offset copies (clones)](split-clones/EFFECT.md) | `split-clones` | Phone & copies | lots of gesturing, 'me, me and me', emphasis | — | from source |
| [You as a sticker](sticker-cutout/EFFECT.md) | `sticker-cutout` | Sticker & fly-through | a reaction, a fun beat, 'made with…' tag | cutout | from source |
| [Fly through a letter](zoom-through-text/EFFECT.md) | `zoom-through-text` | Sticker & fly-through | opening transition, the title of the clip | — | from source |
| [Pencil outline on an object](pencil-outline/EFFECT.md) | `pencil-outline` | From Alina's brief | the word that names an object you hold or point at | — | draft |
| [Image on the word that names it](word-image-pop/EFFECT.md) | `word-image-pop` | From Alina's brief | every noun that has a matching photo | — | draft |
| [Handwriting on the word](handwriting-on-word/EFFECT.md) | `handwriting-on-word` | From Alina's brief | a key word to underline, circle or annotate | — | draft |
| [Green-screen cutout (any background)](greenscreen-cutout/EFFECT.md) | `greenscreen-cutout` | From Alina's brief | 'imagine I'm in…', location jokes, swapping the room | cutout, images | draft |
| [Freeze-frame + punch](freeze-frame/EFFECT.md) | `freeze-frame` | New (16 Nov) | the punchline, a reaction, 'wait for it', the moment to remember | freeze | draft |
| [Masked title rise](title-mask-rise/EFFECT.md) | `title-mask-rise` | New (16 Nov) | the hook, a chapter title, the payoff word | — | draft |
| [VHS glitch](vhs-glitch/EFFECT.md) | `vhs-glitch` | New (16 Nov) | a throwback, 'back in the day', a plot twist, a chaotic beat | — | draft |
| [Thrown-in title](hook-throw-in/EFFECT.md) | `hook-throw-in` | Text hooks | the opening line, the topic of the video | — | draft |
| [Stacked words behind me](stack-behind-me/EFFECT.md) | `stack-behind-me` | Text hooks | a 2–6 word statement you want to land word by word | cutout | draft |
| [Text I move under](block-behind-me/EFFECT.md) | `block-behind-me` | Text hooks | when you duck, walk or lean into the frame | cutout | draft |
| [Written by my finger](finger-write/EFFECT.md) | `finger-write` | Text hooks | when you point or 'write' in the air | — | draft |
| [Pulled out of the screen](pull-from-screen/EFFECT.md) | `pull-from-screen` | Text hooks | when you hold a laptop or phone and 'pull' something out | — | draft |
| [Me between the words](walk-between/EFFECT.md) | `walk-between` | Text hooks | standing or walking with room on both sides | cutout | draft |
| [Open-hand reveal](open-hand-reveal/EFFECT.md) | `open-hand-reveal` | Text hooks | when your hands open apart, one up and one down | — | draft |
| [Swipe out](swipe-out/EFFECT.md) | `swipe-out` | Text hooks | a closing line you swipe away | — | draft |
| [Statement stack](statement-stack/EFFECT.md) | `statement-stack` | Clean White | the 3–6 key phrases of a clip | — | draft |
| [Clean-white card](white-card/EFFECT.md) | `white-card` | Clean White | an intro or name card, a shaky part of the take | — | draft |
| [Light leak](light-leak/EFFECT.md) | `light-leak` | Clean White | a cut between two thoughts (max 3 per 15 s) | — | draft |
| [Silver title card](silver-title-card/EFFECT.md) | `silver-title-card` | Cinema Lexicon | the opening question or the closing line (bookend) | — | draft |
| [Hanging key word](hanging-keyword/EFFECT.md) | `hanging-keyword` | Cinema Lexicon | 1 word in 4: the stressed or shouted word | — | draft |
| [Choice buttons](choice-buttons/EFFECT.md) | `choice-buttons` | Cinema Lexicon | 'this or that' moments | — | draft |
| [Neon key word](neon-keyword/EFFECT.md) | `neon-keyword` | Neon Dimension | a claim, number, problem or result | — | draft |
| [Neon pill](neon-pill/EFFECT.md) | `neon-pill` | Neon Dimension | the CTA or one stressed word per ~10 s | — | draft |
| [Light burn](light-burn/EFFECT.md) | `light-burn` | Neon Dimension | every presenter ↔ world change | — | draft |
| [Wavy sparkle hook](wavy-sparkle-hook/EFFECT.md) | `wavy-sparkle-hook` | Meme Chaos | the opening question (first 3–5 s) | — | draft |
| [Meme explosion](meme-explosion/EFFECT.md) | `meme-explosion` | Meme Chaos | the first big move or reveal (one per video) | — | draft |
| [Disco lights](disco-lights/EFFECT.md) | `disco-lights` | Meme Chaos | a dance move, a pose, a 'party' moment | — | draft |
| [Windows XP background](xp-background/EFFECT.md) | `xp-background` | Meme Chaos | a pose with the Windows XP sound; anything 'old internet' | cutout | draft |
| [Green-screen meme pop](greenscreen-meme/EFFECT.md) | `greenscreen-meme` | Meme Chaos | claps, cheering, a reaction beat | — | draft |
| [Big-face warp](face-warp/EFFECT.md) | `face-warp` | Meme Chaos | a group pose, a silly face, the ending | — | draft |
| [Clap zoom pulse](clap-pulse/EFFECT.md) | `clap-pulse` | Meme Chaos | people clapping, a beat drop, any rhythm | — | draft |
| [Crash line + logo](crash-line/EFFECT.md) | `crash-line` | Meme Chaos | 'it's going down', a fall, a loss, a fail | — | draft |

## How an effect is filled in
Every template reads one object `V` (the engine's `engine/hfx.py` writes it; `make_effect.py` here does the same):
`word` (the selected words), `words` ([{text, t, e}] said in the 3 s, times relative), `params` (the fields in each
EFFECT.md), `face` [x, y, w, h] and `track` (face/hand boxes every 0.5 s, 1080x1920 pixels), `images` (photo paths).
Inputs some effects need: `cutout` = `assets/cut.webm` (person with alpha: `hyperframes remove-background piece.mp4 -o
assets/cut.webm`), `freeze` = `assets/freeze.jpg`, `images` = photos, `numbers` = real numbers only (never invented).

## Make and render one
```bash
python3 effects/make_effect.py stack-behind-me --piece piece.mp4 --text "placing text behind you" --out work/fx1 --face 330,640,300,300
```
```bash
cd work/fx1 && source "../../projects/img5978/hf-env.sh" && "$HF" render -o fx1.mp4 -q standard --fps 30
```
Then overlay `fx1.mp4` on the reel from the word's time for 3 s (picture only).
| [Brand open card](lexicon-open/EFFECT.md) | `lexicon-open` | Cinema Lexicon | the first call to action or claim (first 4 s) | brand kit (optional) | draft |
| [App buttons drop](lexicon-ui-drop/EFFECT.md) | `lexicon-ui-drop` | Cinema Lexicon | the product's categories, menu, filters | brand kit with buttons | draft |
| [App button pops](lexicon-ui-pop/EFFECT.md) | `lexicon-ui-pop` | Cinema Lexicon | a button of the product is named or tapped | none | draft |
| [Swipe chip](lexicon-swipe/EFFECT.md) | `lexicon-swipe` | Cinema Lexicon | 'swipe left / right' | none | draft |
| [Giant number](lexicon-number/EFFECT.md) | `lexicon-number` | Cinema Lexicon | a number with its unit ('10 minutes', '3 steps', '50%') | none | draft |
| [App screen in a phone](lexicon-phone-demo/EFFECT.md) | `lexicon-phone-demo` | Cinema Lexicon | 'look how many options', scrolling, browsing the product | brand kit with a screen video or screenshot | draft |
| [Brand close card](lexicon-close/EFFECT.md) | `lexicon-close` | Cinema Lexicon | the last line of an ad (not for interviews or opinion pieces) | brand kit (optional) | draft |
