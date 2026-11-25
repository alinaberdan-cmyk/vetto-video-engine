"""Builds library/effects.json and library/styles.json.

Source: sources/neurofam-12-effects-6-styles.pdf (neurofam, "12 effects + 6 styles", 13 pages, Russian).
Prompts are translated to English, keeping every number from the PDF. [brackets] are the slots the
engine fills from the project (video, start second, words, image folders).
Entries tagged source "brief" come from Alina's request of 13 Nov 2026, not from the PDF; values
tagged "draft" are Claude's proposals that wait for her approval.
Run: python3 library/build_pdf_library.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
PDF = "neurofam PDF"

effects = [
    # ---- PDF p.4
    dict(id="pov-carousel-spin", name="Carousel around me", ru="Карусель вокруг тебя", page=4, group="Carousel & glass",
         needs=["cutout", "images:8 (4:5)"], trigger="a list, many examples, 'all my…' moments",
         layer="around speaker",
         prompt="Make a 'carousel around me' effect in HyperFrames: vertical 1080x1920, 3 seconds. Video: [video] from second [start]. "
                "Cut me out of the background with `npx hyperframes remove-background` and lay the cutout exactly over the source. "
                "8 cards (4:5) from [images] spin in a ring around me. Ring centre at chest height, slight tilt so it reads as a ring. "
                "Cards behind me are hidden by me, cards in front pass over me but never cover the face. In the first 0.6 s the cards fly out "
                "from behind me into the ring, then the ring rotates about 110 degrees per second. Darken the background slightly.",
         slots=["video", "start", "images"]),
    dict(id="liquid-glass-graph", name="Glass card with graph", ru="Стеклянная карточка", page=4, group="Carousel & glass",
         needs=["numbers", "transcript"], trigger="a number, progress, growth, result",
         layer="over video",
         prompt="Make a 'liquid glass with graph' effect in HyperFrames over [video] from second [start]: 1080x1920, 3 s. "
                "In the lower half a glass card 840x470, radius 44: blurred background under it, light edge on top, dark at the bottom, soft shadow. "
                "Top-left small label '[LABEL]', right a large percentage counting 23, 48, 76, 92 over 2.2 s in whole numbers. "
                "A green graph line with fill climbs with the number, glowing dot at its tip. Above the card, word-by-word captions of my speech "
                "timed exactly (transcript).",
         slots=["video", "start", "label", "numbers"]),
    # ---- PDF p.5
    dict(id="match-cut", name="Match cut on one word", ru="Нарезка на одном слове", page=5, group="Match cut & pixels",
         needs=["no video"], trigger="the key word / brand name; a transition between your clips",
         layer="full screen insert",
         prompt="Make a match-cut effect in HyperFrames: 1080x1920, 3 s, no video. 16 article pages change with hard cuts every 0.12–0.2 s. "
                "On every page the word '[WORD]' sits exactly in the centre on a red-orange highlight; only the text around it changes. "
                "Pages differ: typewriter, serif newspaper, grotesque, different paper shades and text sizes. Very close up: lines cropped "
                "by the frame edges, more blur further from the centre, light vignette and paper grain. On every cut the camera jolts 6 px and "
                "slowly pushes in the whole time. Invent the article texts about [topic], no publication names or figures.",
         slots=["word", "topic"]),
    dict(id="screen-push-digital", name="Pixel words", ru="Пиксельные слова", page=5, group="Match cut & pixels",
         needs=["no video"], trigger="a short punchline of 3–4 words",
         layer="full screen insert",
         prompt="Make a 'words on a pixel screen' effect in HyperFrames: 1080x1920, 3 s. Almost black background, an RGB sub-pixel grid over "
                "everything, as if the camera films a screen up close. Huge white words of the phrase '[PHRASE]' slide right to left, one word "
                "in frame at a time. Light glow, red and blue copies of the letters offset 3 px, motion blur. The last word stops in the centre "
                "by 1.6 s and flickers slightly until the end. Bold font, the longest word no wider than 890 px.",
         slots=["phrase"]),
    # ---- PDF p.6
    dict(id="apple-ui-toggles", name="iOS toggles", ru="Переключатели iOS", page=6, group="Toggles & zoom",
         needs=["3 short lines"], trigger="steps, pros, a 3-item list",
         layer="over video",
         prompt="Make an 'iOS toggles' effect in HyperFrames over [video] from second [start]: 1080x1920, 3 s. A white card like iPhone "
                "Settings, centred in the lower half. Three rows: '[LINE 1]', '[LINE 2]', '[LINE 3]', thin dividers. A real iOS switch on the "
                "right of each row: track 102x62, white knob with shadow. The card appears in 0.25 s. Switches turn on in turn at 0.3, 0.8 and "
                "1.3 s: the knob overshoots slightly, the track turns green #34C759. Darken the video under the card slightly.",
         slots=["video", "start", "line1", "line2", "line3"]),
    dict(id="over-the-shoulder-zoom", name="Zoom + proof cards", ru="Зум и карточки у головы", page=6, group="Toggles & zoom",
         needs=["face", "numbers", "transcript"], trigger="proof, two numbers, before/after facts",
         layer="over video",
         prompt="Make a 'zoom and proof cards' effect in HyperFrames on [video] from second [start]: 1080x1920, 3 s. The camera pushes in "
                "smoothly on my face, scale 1 to 1.14; find the face yourself so the push lands on it. White rounded cards land beside the head: "
                "first left '[label]', a large orange '[number]', '[note]'. After half a second it leaves and a second card lands right with "
                "other '[label]', '[number]', '[note]'. Cards never cover the face. Word-by-word captions under the chin. Use only real numbers.",
         slots=["video", "start", "card1", "card2"]),
    # ---- PDF p.7
    dict(id="text-behind-me", name="Word behind me", ru="Слово за спиной", page=7, group="Word & notifications",
         needs=["cutout"], trigger="the one word the clip is about (4–7 letters)",
         layer="behind speaker",
         prompt="Make a 'word behind me' effect in HyperFrames: vertical 1080x1920, 3 s. Video: [video] from second [start]. Cut me out with "
                "`npx hyperframes remove-background`. Layers in order: room, the huge word '[WORD]', me on top. The word spans the full frame "
                "width, about 350 px tall, at the top of my head so my head covers the bottom of the letters. Milky colour, light warm glow. "
                "In the first 0.45 s the letters rise one by one from under a mask, then the word slowly drifts up 20 px. Darken the room "
                "slightly, clean cutout edges with no halo.",
         slots=["video", "start", "word"]),
    dict(id="notification-stack", name="Notifications over my head", ru="Уведомления над головой", page=7, group="Word & notifications",
         needs=["4 notification texts"], trigger="'my phone blew up', orders, messages, reactions",
         layer="over video",
         prompt="Make a 'notification stack' effect in HyperFrames over [video] from second [start]: 1080x1920, 3 s. iPhone-like "
                "notifications drop from the top: dark frosted glass, radius 34, app icon on the left, app name and 'now' on top, bold title "
                "and one line below. Four notifications at 0.05, 0.4, 0.75 and 1.1 s with texts [app, title, line for each]. Each new one lands "
                "on top and springs the older ones down; older ones shrink and darken slightly. The stack sits above the head, never on the "
                "face. Draw the icons yourself, no real company logos.",
         slots=["video", "start", "notifications"]),
    # ---- PDF p.8
    dict(id="phone-3d-float", name="Video in a 3D phone", ru="Видео в 3D-телефоне", page=8, group="Phone & copies",
         needs=["video or screen recording"], trigger="showing an app, a screen recording, 'look at this'",
         layer="full frame",
         prompt="Make a 'video in a 3D phone' effect in HyperFrames: 1080x1920, 3 s. Dark warm background with soft orange side light. "
                "In the centre a logo-free smartphone drawn in code: rounded body, metal edge, camera cutout. On its screen [video] from second "
                "[start]. The phone starts rotated 38 degrees on the vertical axis and 12 on the horizontal; over 0.9 s it turns to face the "
                "camera and a glare sweeps the glass. Then it floats up and down 10 px and slowly approaches. A soft shadow under it moves with it.",
         slots=["video", "start"]),
    dict(id="split-clones", name="Three offset copies (clones)", ru="Три копии со сдвигом", page=8, group="Phone & copies",
         needs=["gestures"], trigger="lots of gesturing, 'me, me and me', emphasis",
         layer="full frame",
         prompt="Make a 'three copies of me' effect in HyperFrames: 1080x1920, 3 s. Three vertical strips of 352 px with dark 12 px gaps. "
                "Each holds [video], face centred and slightly larger. Strips are offset in time: left from second [start], middle 0.25 s later, "
                "right 0.5 s later. In the first 0.5 s the left strip slides in from the top, the right from the bottom, the middle is already "
                "there. Then the strips slowly drift in different directions. At 0.6 s a thin orange line slides under the middle strip.",
         slots=["video", "start"]),
    # ---- PDF p.9
    dict(id="sticker-cutout", name="You as a sticker", ru="Ты стикер", page=9, group="Sticker & fly-through",
         needs=["cutout"], trigger="a reaction, a fun beat, 'made with…' tag",
         layer="replaces background",
         prompt="Make a 'me as a sticker' effect in HyperFrames on [video] from second [start]: 1080x1920, 3 s. Cut me out with "
                "`npx hyperframes remove-background`. At 0.05 s the room goes away, replaced by an orange background [#E8572A] with small dots "
                "and a vignette. I become a sticker: white outline about 14 px tight to the silhouette and a soft shadow. I 'peel off': shrink "
                "to 0.86 and rotate 4 degrees with a bounce, then sway slightly. At 0.5 s a white label with '[TEXT]' appears beside the head.",
         slots=["video", "start", "bg_color", "label"]),
    dict(id="zoom-through-text", name="Fly through a letter", ru="Пролёт сквозь букву", page=9, group="Sticker & fly-through",
         needs=["word with a thick letter"], trigger="opening transition, the title of the clip",
         layer="transition",
         prompt="Make a 'fly through a letter' effect in HyperFrames: 1080x1920, 3 s. Black frame, a huge word '[WORD]' full width in the "
                "centre. The letters are windows: through them you see [video] from second [start]; around the letters is black. Thin light "
                "outline on the letters. The camera accelerates into the thick part of the letter 'A'. In 0.95 s the letter fills the screen "
                "and only my video remains. Then the scale settles softly from 1.06 to 1. Smooth letter edges.",
         slots=["video", "start", "word"]),
    # ---- Alina's brief, 13 Nov 2026 (not in the PDF)
    dict(id="pencil-outline", name="Pencil outline on an object", ru=None, page=None, group="From Alina's brief",
         needs=["object mask"], trigger="the word that names an object you hold or point at",
         layer="over object", source="brief", status="draft",
         prompt="On [video] from second [start], when I say '[WORD]', draw a hand-drawn pencil outline around [object] in the frame: "
                "graphite texture, slightly wobbly line drawn on over 0.5 s, small arrow and handwritten label '[WORD]'. Track the object "
                "if it moves. Keep it 1.5 s, then erase.",
         slots=["video", "start", "word", "object"]),
    dict(id="word-image-pop", name="Image on the word that names it", ru=None, page=None, group="From Alina's brief",
         needs=["images"], trigger="every noun that has a matching photo",
         layer="over video", source="brief", status="draft",
         prompt="When I say '[WORD]', pop the matching image from [images] next to my head (never on the face) with a white 6 px frame, "
                "slight tilt and a spring. Hold it while the word and the next 2–3 words are spoken, then slide it out.",
         slots=["video", "start", "word", "images"]),
    dict(id="handwriting-on-word", name="Handwriting on the word", ru=None, page=None, group="From Alina's brief",
         needs=["handwriting font"], trigger="a key word to underline, circle or annotate",
         layer="over video", source="brief", status="draft",
         prompt="When I say '[WORD]', write it by hand on screen in [handwriting font] stroke by stroke over 0.4 s, with a scribbled "
                "underline or circle, in [ink colour]. Place it in empty space, never on the face.",
         slots=["video", "start", "word", "font", "color"]),
    dict(id="greenscreen-cutout", name="Green-screen cutout (any background)", ru=None, page=None, group="From Alina's brief",
         needs=["cutout", "background image or video"], trigger="'imagine I'm in…', location jokes, swapping the room",
         layer="replaces background", source="brief", status="draft",
         prompt="Cut me out of [video] from second [start] with `npx hyperframes remove-background` and place me over [background], "
                "matching light and adding a soft contact shadow.",
         slots=["video", "start", "background"]),
]

FIELDS = {
    "pov-carousel-spin": [{"key": "_images", "label": "Uses the photos in your image bank (8 cards, repeated if fewer)", "type": "note"}],
    "liquid-glass-graph": [{"key": "label", "label": "Small label", "placeholder": "PROGRESS"},
                           {"key": "numbers", "label": "Your real numbers, in order", "placeholder": "23, 48, 76, 92", "required": True}],
    "match-cut": [{"key": "word", "label": "Word in the highlight", "placeholder": "the word"},
                  {"key": "topic_text", "label": "Article text (empty: your own words from the video)", "placeholder": ""}],
    "screen-push-digital": [{"key": "phrase", "label": "Phrase (3–4 short words)", "placeholder": "Every effect one prompt"}],
    "apple-ui-toggles": [{"key": "line1", "label": "Row 1"}, {"key": "line2", "label": "Row 2"}, {"key": "line3", "label": "Row 3"}],
    "over-the-shoulder-zoom": [{"key": "card1_label", "label": "Card 1 label"}, {"key": "card1_number", "label": "Card 1 real number", "required": True},
                               {"key": "card1_note", "label": "Card 1 note"}, {"key": "card2_label", "label": "Card 2 label"},
                               {"key": "card2_number", "label": "Card 2 real number", "required": True}, {"key": "card2_note", "label": "Card 2 note"}],
    "notification-stack": [{"key": f"n{i}_{k}", "label": f"Notification {i} {k}"} for i in range(1, 5) for k in ("app", "title", "line")],
    "sticker-cutout": [{"key": "label", "label": "Label beside the head", "placeholder": "made with FeedMe"},
                       {"key": "bg_color", "label": "Background colour", "type": "color", "placeholder": "#E8572A"}],
    "zoom-through-text": [{"key": "word", "label": "Word to fly through", "placeholder": "the word"}],
    "text-behind-me": [{"key": "word", "label": "Word behind you (4–7 letters reads best)", "placeholder": "the word"}],
    "pencil-outline": [{"key": "label", "label": "Handwritten label", "placeholder": "the word"}],
    "handwriting-on-word": [{"key": "text", "label": "Written word", "placeholder": "the word"},
                            {"key": "color", "label": "Ink colour", "type": "color", "placeholder": "#FFFFFF"}],
    "freeze-frame": [{"key": "label", "label": "Label on the freeze", "placeholder": "the word"}],
    "title-mask-rise": [{"key": "setup", "label": "Setup line (small, italic, optional)", "placeholder": "the one thing I"},
                        {"key": "word", "label": "Payoff word (huge)", "placeholder": "the word"},
                        {"key": "color", "label": "Accent dot colour", "type": "color", "placeholder": "#EFB36C"}],
    "vhs-glitch": [],
    "greenscreen-cutout": [{"key": "image_index", "label": "Background: photo number in your bank (1 = first)", "placeholder": "1"}],
}

# more effects (16 Nov 2026) from the repo review: ideas and numbers, our own code
effects += [
    dict(id="freeze-frame", name="Freeze-frame + punch", ru=None, page=None, group="New (16 Nov)",
         needs=["the word"], trigger="the punchline, a reaction, 'wait for it', the moment to remember",
         layer="full frame", source="idea: lemo-opuscar freeze grammar", status="draft",
         prompt="White flash 0.14 s, the frame freezes and pushes in 1.0 → 1.12, colour drops to 45 %, corner brackets and a label chip; lets go at 2.4 s.",
         slots=["word"]),
    dict(id="title-mask-rise", name="Masked title rise", ru=None, page=None, group="New (16 Nov)",
         needs=["a short title"], trigger="the hook, a chapter title, the payoff word",
         layer="over video", source="values: mengto/skills html-reel (MIT)", status="draft",
         prompt="Italic serif setup line, then a huge condensed payoff word; each word rises from 135 % inside its own mask in 0.32 s, shrinking stagger.",
         slots=["setup", "word"]),
    dict(id="vhs-glitch", name="VHS glitch", ru=None, page=None, group="New (16 Nov)",
         needs=[], trigger="a throwback, 'back in the day', a plot twist, a chaotic beat",
         layer="full frame", source="idea: lemo-opuscar CRT post (MIT)", status="draft",
         prompt="Red and blue split, scanlines, moving noise, tracking wobble and a short roll at the start, for 3 s.",
         slots=[]),
]


# text hooks (17 Nov 2026): the 8 text effects in @ugcwithnyomi's TikTok 7679139537196567840, rebuilt in our own code
REF = "idea: @ugcwithnyomi TikTok 7679139537196567840"
TXT = {"key": "text", "label": "Text (empty: the words you selected)", "placeholder": "the words you selected"}
YEL = {"key": "color", "label": "Accent colour", "type": "color", "placeholder": "#FAFD6C"}
FIELDS.update({
    "hook-throw-in": [TXT, {"key": "subline", "label": "Small yellow line under it (empty: words 3+ of the text)", "placeholder": "in your next video"}, YEL],
    "stack-behind-me": [TXT, {"key": "highlight", "label": "Word in yellow (empty: the 2nd word)", "placeholder": "text"}, YEL],
    "block-behind-me": [TXT, {"key": "lines", "label": "Lines (2–4)", "placeholder": "3"}],
    "finger-write": [TXT, YEL],
    "pull-from-screen": [TXT, {"key": "screen", "label": "Where the screen is: left, middle or right", "placeholder": "middle"}, YEL],
    "walk-between": [TXT],
    "open-hand-reveal": [TXT, YEL],
    "swipe-out": [TXT],
})
G = "Text hooks"
effects += [
    dict(id="hook-throw-in", name="Thrown-in title", group=G, needs=["a short title"], layer="over video",
         trigger="the opening line, the topic of the video",
         prompt="Title thrown in from the top-right corner, lands at chest height; a small yellow line wipes in under it; three spark strokes pop at its corner.",
         slots=["text", "subline"]),
    dict(id="stack-behind-me", name="Stacked words behind me", group=G, needs=["cutout", "2–6 words"], layer="behind speaker",
         trigger="a 2–6 word statement you want to land word by word",
         prompt="One huge word per line, stacked around the head, each popping in when said, one word yellow; I stay in front.",
         slots=["text", "highlight"]),
    dict(id="block-behind-me", name="Text I move under", group=G, needs=["cutout", "moving in the frame"], layer="behind speaker",
         trigger="when you duck, walk or lean into the frame",
         prompt="A tight three-line block hangs at head height; I move under and through it, my body covers the letters.",
         slots=["text"]),
    dict(id="finger-write", name="Written by my finger", group=G, needs=["a raised hand"], layer="over video",
         trigger="when you point or 'write' in the air",
         prompt="Yellow handwriting appears letter by letter near the raised hand, in two lines.",
         slots=["text"]),
    dict(id="pull-from-screen", name="Pulled out of the screen", group=G, needs=["a laptop or phone in shot"], layer="over video",
         trigger="when you hold a laptop or phone and 'pull' something out",
         prompt="The text sits small on the screen (black tilted label, yellow), then flies up and grows into a big yellow title.",
         slots=["text", "screen"]),
    dict(id="walk-between", name="Me between the words", group=G, needs=["cutout", "you in the middle"], layer="behind speaker",
         trigger="standing or walking with room on both sides",
         prompt="The text splits into two columns, one on each side of me at chest height; I stand between them in front.",
         slots=["text"]),
    dict(id="open-hand-reveal", name="Open-hand reveal", group=G, needs=["hands opening apart"], layer="over video",
         trigger="when your hands open apart, one up and one down",
         prompt="Yellow text revealed between the hands, growing from the middle line outward.",
         slots=["text"]),
    dict(id="swipe-out", name="Swipe out", group=G, needs=["a swipe at the end"], layer="over video",
         trigger="a closing line you swipe away",
         prompt="The text pops out of the hand, jumps to the top-left, holds, then slides out of frame with a skew and blur.",
         slots=["text"]),
]
for e in effects[-8:]:
    e.update(ru=None, page=None, source=REF, status="draft")


# signature pieces of the 3 Editing Beast styles (17 Nov 2026): ~/Editing Beast/styles/<id>/STYLE.md, approved there
EB = "Editing Beast style {} (STYLE.md v1, approved 17 Nov 2026)"
BRAND = {"key": "color", "label": "Brand colour", "type": "color", "placeholder": "#007A4E"}
FIELDS.update({
    "statement-stack": [TXT, {"key": "side", "label": "Side: auto, left, right", "placeholder": "auto"},
                        {"key": "focus", "label": "Blur the background while it builds (yes / no)", "placeholder": "no"}],
    "white-card": [TXT, {"key": "italic", "label": "Italic serif word under it (empty: the last word)", "placeholder": "thumbnail"}],
    "light-leak": [{"key": "tone", "label": "cool, warm or flash", "placeholder": "cool"}],
    "silver-title-card": [TXT, BRAND],
    "hanging-keyword": [TXT, {"key": "key", "label": "Key word (empty: the longest)", "placeholder": "experience"},
                        {"key": "caps", "label": "CAPS instead of italic (yes / no)", "placeholder": "no"}],
    "choice-buttons": [{"key": "a", "label": "Button 1", "placeholder": "read a book"}, {"key": "b", "label": "Button 2", "placeholder": "look at tiktok"},
                       {"key": "chosen", "label": "Chosen button (1 or 2)", "placeholder": "2"}, BRAND],
    "neon-keyword": [TXT, {"key": "key", "label": "Key word (empty: the last word)", "placeholder": "investment"},
                     {"key": "neon", "label": "Neon: green (money, yes), red (problem), cyan (calm, tech), purple (AI, game), pink, gold", "placeholder": "green"}],
    "neon-pill": [TXT, {"key": "color", "label": "Neon colour", "type": "color", "placeholder": "#39FF6A"}],
    "light-burn": [{"key": "kind", "label": "burn or glitch", "placeholder": "burn"}],
})
def _sig(id, name, style, trigger, prompt, layer="over video", needs=()):
    return dict(id=id, name=name, group=style, needs=list(needs), layer=layer, trigger=trigger, prompt=prompt, slots=["text"],
                ru=None, page=None, source=EB.format(style), status="draft")
effects += [
    _sig("statement-stack", "Statement stack", "Clean White", "the 3–6 key phrases of a clip",
         "2–4 tight staggered lines, heavy sans + an italic serif last line, white glow; each word blurs in when said."),
    _sig("white-card", "Clean-white card", "Clean White", "an intro or name card, a shaky part of the take",
         "The clip shrinks into a rounded card on brushed silver with a magenta glow; a small statement inside.", "full frame"),
    _sig("light-leak", "Light leak", "Clean White", "a cut between two thoughts (max 3 per 15 s)",
         "A cool (mint → lavender) or warm (yellow → red) leak sweeps across, or a white flash; punch-in under it.", "full frame"),
    _sig("silver-title-card", "Silver title card", "Cinema Lexicon", "the opening question or the closing line (bookend)",
         "Brand-colour words fly in on silver, sizes jump, one script word; the speaker grows out of a rounded card.", "full frame"),
    _sig("hanging-keyword", "Hanging key word", "Cinema Lexicon", "1 word in 4: the stressed or shouted word",
         "The key word big (italic or CAPS), the small connector words hang off its corners; hard cuts on the words."),
    _sig("choice-buttons", "Choice buttons", "Cinema Lexicon", "'this or that' moments",
         "Two outlined pills with 'or' between; the chosen one fills with the brand colour."),
    _sig("neon-keyword", "Neon key word", "Neon Dimension", "a claim, number, problem or result",
         "The room goes dark in one neon colour, a small lead-in builds, the key word slams in (Anton, skewed, glowing).", "full frame"),
    _sig("neon-pill", "Neon pill", "Neon Dimension", "the CTA or one stressed word per ~10 s",
         "An outlined neon pill with skewed white caps at chest height, glow breathing."),
    _sig("light-burn", "Light burn", "Neon Dimension", "every presenter ↔ world change",
         "White light burn with warm edges, then the shot zoom-blurs in; or a 4-frame glitch.", "full frame"),
]


# Meme Chaos (18 Nov 2026): the effects of Alina's dumb-scale edit (her final cut, 17 Nov), ~/Editing Beast/styles/meme-chaos/STYLE.md
MC = "Meme Chaos (Alina's dumb-scale edit, 17 Nov 2026; STYLE.md draft 18 Nov 2026)"
AT = {"key": "at", "label": "Starts at (s into the 3 s piece)", "placeholder": "0"}
HOLD = lambda d: {"key": "hold", "label": "How long it stays (s)", "placeholder": str(d)}
FIELDS.update({
    "wavy-sparkle-hook": [{"key": "text", "label": "Hook text (\"/\" = line break; empty: the words you selected)", "placeholder": "who's the dumbest / in our office?"},
                          {"key": "color", "label": "Outline colour", "type": "color", "placeholder": "#1C5428"}, HOLD(2.9)],
    "meme-explosion": [AT, {"key": "size", "label": "Fire size (1.25 = as in the dumb-scale edit)", "placeholder": "1.25"},
                       {"key": "zoom", "label": "Punch zoom", "placeholder": "1.18"}],
    "disco-lights": [AT, HOLD(1.35), {"key": "ball_x", "label": "Disco ball x (px, 540 = middle)", "placeholder": "540"}],
    "xp-background": [{"key": "file", "label": "Background file (empty: the last photo or video you attached in the chat bar)", "placeholder": "the last file you attached"},
                      {"key": "bg_start", "label": "Video background starts at (s into it)", "placeholder": "0"}, AT, HOLD(3)],
    "greenscreen-meme": [{"key": "clip", "label": "Green-screen clip (attach a green-screen video in the chat bar and ask Claude to add it; then type its name here)", "placeholder": "clip name"},
                         {"key": "position", "label": "left, right, center or face", "placeholder": "right"},
                         {"key": "size", "label": "Height (share of the frame)", "placeholder": "0.36"}, AT, HOLD(1.25)],
    "face-warp": [AT, HOLD(1.85), {"key": "amount", "label": "Strength (1 = as in Alina's edit)", "placeholder": "1"}],
    "clap-pulse": [{"key": "strength", "label": "Zoom on each clap", "placeholder": "1.07"},
                   {"key": "times", "label": "Clap times (s, empty: found in the sound)", "placeholder": "0.5, 0.7, 0.9"}],
    "crash-line": [{"key": "text", "label": "Badge text if the image bank has no logo", "placeholder": "brand"},
                   {"key": "direction", "label": "Falls to the left or right", "placeholder": "left"},
                   {"key": "draw_at", "label": "Line starts at (s)", "placeholder": "0.95"},
                   {"key": "x", "label": "Start x (px; empty: the raised hand)", "placeholder": ""},
                   {"key": "y", "label": "Start y (px)", "placeholder": ""}, AT],
})
def _mc(id, name, trigger, prompt, layer="over video", needs=()):
    return dict(id=id, name=name, group="Meme Chaos", needs=list(needs), layer=layer, trigger=trigger, prompt=prompt, slots=["text"],
                ru=None, page=None, source=MC, status="draft")
effects += [
    _mc("wavy-sparkle-hook", "Wavy sparkle hook", "the opening question (first 3–5 s)",
        "Bubbly rounded title (Coiny, white, thick dark-green outline) on the chest; letters pop in one by one, then float on a wave; 10 sparkles twinkle."),
    _mc("meme-explosion", "Explosion", "the first big move or reveal (one per video)",
        "A green-screen fire ring (Pixabay, no watermark) bursts around the face + white flash + shake + punch zoom. Add the explosion sound.", "full frame"),
    _mc("disco-lights", "Disco lights", "a dance move, a pose, a 'party' moment",
        "A disco ball drops in, six colour beams sweep, colour spots wander, the room dims and flickers. Add the disco beat.", "full frame"),
    _mc("xp-background", "Green-screen background", "any moment you want somewhere else behind you",
        "The room behind the person is replaced by the photo or video attached in the chat bar (the last one, or the one named in the field); the person stays in front (cutout).", "behind speaker", ["cutout", "a file attached in the chat bar"]),
    _mc("greenscreen-meme", "Green-screen meme pop", "claps, cheering, a reaction beat",
        "A keyed green-screen meme clip (e.g. the clapping cat) pops in beside the person, plays, pops out."),
    _mc("face-warp", "Big-face warp", "a group pose, a silly face, the ending",
        "Every face swells into a big-nose fisheye face for ~1.9 s.", "full frame"),
    _mc("clap-pulse", "Clap zoom pulse", "people clapping, a beat drop, any rhythm",
        "On every clap the picture jumps in to 1.07 and settles back in 0.2 s; claps found in the sound.", "full frame"),
    _mc("crash-line", "Crash line + logo", "'it's going down', a fall, a loss, a fail",
        "A logo badge pops at the raised hand, then a red stock-crash zigzag draws down and off screen, the badge riding its tip."),
]

# Cinema Lexicon v6 (18 Nov 2026): the graphics of Alina's approved CL01 v6, in the product's own brand kit (projects/<id>/brand/)
LX = "Cinema Lexicon v6 (Alina's approved CL01 edit, 17 Nov 2026; Editing Beast STYLE.md §10)"
HOLDF = lambda d: {"key": "hold", "label": "How long it stays (s)", "placeholder": str(d)}
FIELDS.update({
    "lexicon-open": [{"key": "script", "label": "Script word (accent colour)", "placeholder": "dare"},
                     {"key": "small", "label": "Small words", "placeholder": "you to try"},
                     {"key": "big", "label": "Huge words (CAPS)", "placeholder": "this app."}, HOLDF(1.12)],
    "lexicon-ui-drop": [HOLDF(1.1)],
    "lexicon-ui-pop": [{"key": "label", "label": "Button (a button of the brand kit)", "placeholder": "Surprise me"}, HOLDF(1.76)],
    "lexicon-swipe": [{"key": "dir", "label": "left (✕) or right (♥)", "placeholder": "left"}],
    "lexicon-number": [{"key": "lead", "label": "Small line above", "placeholder": "in less than"},
                       {"key": "number", "label": "The number", "placeholder": "<10"},
                       {"key": "unit", "label": "Unit under it", "placeholder": "minutes."},
                       {"key": "t_number", "label": "Number slides in at (s)", "placeholder": "0.7"}, HOLDF(1.28)],
    "lexicon-phone-demo": [HOLDF(1.58)],
    "lexicon-close": [{"key": "name", "label": "Name next to the icon (empty: the brand's)", "placeholder": "feedmeplzthanks"},
                      {"key": "slogan", "label": "Slogan (empty: the brand's)", "placeholder": "Stop deciding. Dinner's sorted."},
                      {"key": "bubbles", "label": "Chat bubbles (yes / no)", "placeholder": "yes"}],
})
def _lx(id, name, trigger, prompt, layer="over video", needs=()):
    return dict(id=id, name=name, group="Cinema Lexicon", needs=list(needs), layer=layer, trigger=trigger, prompt=prompt, slots=["text"],
                ru=None, page=None, source=LX, status="draft")
effects += [
    _lx("lexicon-open", "Brand open card", "the first call to action or claim (first 4 s)",
        "The brand's cream card: a script word in the accent colour, small words, the object in huge caps fly in one by one; the app's phone rises tilted, its buttons and icon pop; all whip off left with blur.", "full frame", ["brand kit (optional)"]),
    _lx("lexicon-ui-drop", "App buttons drop", "the product's categories, menu, filters",
        "The take goes soft-blurred; the app's real buttons (same colours, black outline, offset shadow, icons) fall one by one and bounce into a pile.", "over video", ["brand kit with buttons"]),
    _lx("lexicon-ui-pop", "App button pops", "a button of the product is named or tapped",
        "That button, in its own colours, springs in tilted high in the frame and leaves before the cut. Click + pop."),
    _lx("lexicon-swipe", "Swipe chip", "'swipe left / right'",
        "A round chip (✕ red or ♥ brand colour) flies off the frame in the swipe direction."),
    _lx("lexicon-number", "Giant number", "a number with its unit ('10 minutes', '3 steps', '50%')",
        "Cream card: a small lead-in, the number huge in the accent colour sliding in from the right with motion blur, the unit under it.", "full frame"),
    _lx("lexicon-phone-demo", "App screen in a phone", "'look how many options', scrolling, browsing the product",
        "The official screen recording in a black phone frame on the brand's cream card, three app buttons popping around it.", "full frame", ["brand kit with a screen video or screenshot"]),
    _lx("lexicon-close", "Brand close card", "the last line of an ad (not for interviews or opinion pieces)",
        "The take shrinks into a rounded card on cream; app icon + name on top, chat bubbles pop around it, the slogan fades in; the last frame is held.", "full frame", ["brand kit (optional)"]),
]

for e in effects:
    e.setdefault("source", PDF)
    e.setdefault("status", "from source")
    e["duration_s"] = 3 if e["source"] == PDF else None
    # what this engine renders itself (engine/effects.py, render.py); the rest Claude builds in HyperFrames
    # all 16 render in the engine now: ffmpeg (word-image-pop), engine/effects.py (text-behind-me, split-clones),
    # HyperFrames templates in engine/hf/<id>.html (the other 13)
    e["engine"] = "engine"
    e["renderer"] = "ffmpeg" if e["id"] in ("text-behind-me", "split-clones", "word-image-pop", "vhs-glitch") else "hyperframes template"
    e["caption_zone"] = {"liquid-glass-graph": "above-card", "apple-ui-toggles": "upper", "match-cut": "hide",
                         "screen-push-digital": "hide", "phone-3d-float": "hide", "zoom-through-text": None,
                         "title-mask-rise": "lower-only", "freeze-frame": None,
                         "lexicon-open": "hide", "lexicon-number": "hide", "lexicon-ui-drop": "upper", "lexicon-phone-demo": "dark",
                         "lexicon-close": "dark", "lexicon-ui-pop": None, "lexicon-swipe": None}.get(e["id"], "hide" if e.get("group") == "Text hooks" or e["id"] in ("statement-stack", "white-card", "silver-title-card", "hanging-keyword", "choice-buttons", "neon-keyword", "neon-pill") else None)
    # what Alina fills in on the effect's card (the rest comes from the footage)
    e["fields"] = FIELDS.get(e["id"], [])

styles = [
    dict(id="glass-explainer-reel", name="Glass explainer", ru="Объяснялка на стекле", page=10,
         look="Almost-black background with fine dot texture and a warm orange glow in the centre. Glass plates: a top plate with '01', the "
              "topic in the centre and a thin orange bar on the left; two glass number cards (before → after, counting up by 1.2 s); "
              "me in a rounded card at the bottom with word-by-word captions above it.",
         palette={"bg": "#0E0D0C", "accent": "#E8572A", "text": "#FFFFFF", "glass": "rgba(255,255,255,.10)"},
         fonts={"title": "Inter Tight 600", "caption": "Inter 600"},
         caption={"mode": "word-by-word", "position": "above speaker card", "case": "sentence", "box": "none"},
         textbox="glass plate, radius 28, light top edge",
         slots=["topic", "before", "after"]),
    dict(id="cinematic-type-reel", name="Cinematic typography", ru="Кинотипографика", page=10,
         look="Scene 1 (to 0.95 s): warm orange fill with light grain, a large white italic serif phrase in the centre and a small line "
              "under it typing word by word. Hard cut to scene 2: light-grey background, white card with a cutaway frame on the topic; "
              "under it a big black word that changes with my speech.",
         palette={"bg": "#E8572A", "bg2": "#E9E9E7", "text": "#FFFFFF", "ink": "#111111"},
         fonts={"title": "Instrument Serif Italic", "caption": "Inter 800"},
         caption={"mode": "one big word", "position": "under card", "case": "lower", "box": "none"},
         textbox="white card, no border",
         slots=["phrase", "cutaway"]),
    dict(id="image-cluster-reel", name="Images over my head", ru="Картинки над головой", page=11,
         look="Images from a folder appear over the head at 0, 0.35, 0.7 and 1.05 s: white 6 px frame, shadow, slight tilt, spring in, "
              "stacking but never covering the face. A small 3-line caption block on the left at chest height, words appear as spoken. "
              "Wall darkened slightly.",
         palette={"frame": "#FFFFFF", "text": "#FFFFFF", "dim": "rgba(0,0,0,.25)"},
         fonts={"caption": "Inter 700"},
         caption={"mode": "3-line block, word reveal", "position": "left, chest height", "case": "sentence", "box": "none"},
         textbox="white photo frame 6 px",
         slots=["images"]),
    dict(id="cutout-grid-reel", name="Me over a grid", ru="Ты поверх сетки", page=11,
         look="Cutout of me. Background: 4 images in a 2x2 grid with no gaps, each slowly zooming; at 1 s all four swap to a second set. "
              "Me centred, scaled to about 0.6, cropped under the chest. A dark translucent plate on the chest with captions.",
         palette={"plate": "rgba(0,0,0,.55)", "text": "#FFFFFF"},
         fonts={"caption": "Inter 700"},
         caption={"mode": "phrase", "position": "chest plate", "case": "sentence", "box": "dark translucent plate"},
         textbox="dark translucent plate",
         slots=["images_1", "images_2"]),
    dict(id="depth-ui-reel", name="Interface behind me", ru="Интерфейс за спиной", page=12,
         look="Cutout of me. Layers: room, a light UI card (radius 28, code-drawn, no real logos) with an orange circle '1' on the left, "
              "me on top so my head covers the bottom of the card. Card flies in in 0.4 s. On the chest a large orange italic serif word "
              "that changes with my speech.",
         palette={"card": "#FFFFFF", "accent": "#E8572A", "text": "#E8572A"},
         fonts={"title": "Instrument Serif Italic", "caption": "Instrument Serif Italic"},
         caption={"mode": "one big word", "position": "chest", "case": "lower", "box": "none"},
         textbox="light UI card, radius 28",
         slots=["ui_content"]),
    dict(id="split-reel", name="Split screen", ru="Разделённый экран", page=12,
         look="Top half: me, face centred. Bottom: almost-black panel with warm glow, a small orange italic label '[step]', a large glowing "
              "orange word '[MAIN]', a small line under it. Below, two glass cards with a 'VS' circle: left '[before]', right fills with "
              "'[after]' at 1 s. At the bottom a strip of 5 images slowly moving left.",
         palette={"bg": "#0E0D0C", "accent": "#E8572A", "text": "#FFFFFF", "glass": "rgba(255,255,255,.10)"},
         fonts={"title": "Inter Tight 800", "label": "Instrument Serif Italic"},
         caption={"mode": "panel word", "position": "bottom panel", "case": "upper", "box": "glass"},
         textbox="glass cards with VS",
         slots=["step", "main", "before", "after", "images"]),
]
for s in styles:
    s["source"] = PDF
    s["status"] = "from source"
    # The PDF gives looks and timings per 3 s piece, not overall pacing or fonts by name: those are drafts.
    s["pacing"] = {"value": "3 s pieces, hard cuts between pieces", "status": "from source"}
    s["fonts_status"] = "draft (PDF names no font families; it says bold / italic serif)"
    s["sfx"] = {"value": [], "status": "open"}
    s["engine"] = "hyperframes"

(HERE / "effects.json").write_text(json.dumps(effects, ensure_ascii=False, indent=1))
# more named styles (16 Nov 2026), drafts by Claude for Alina to approve: library/styles_more.json
for st in json.loads((HERE / "styles_more.json").read_text()):
    st.setdefault("source", "draft (Claude, 16 Nov 2026)")
    st.setdefault("status", "draft")
    st.setdefault("pacing", {"value": f"{st.get('pace', 'Medium')} pace", "status": "draft"})
    st["engine"] = "engine"
    styles.append(st)
(HERE / "styles.json").write_text(json.dumps(styles, ensure_ascii=False, indent=1))
print(len(effects), "effects,", len(styles), "styles")
