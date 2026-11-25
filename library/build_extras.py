"""Builds library/looks.json (fonts, palettes, text boxes), library/outputs.json and library/pacing.json.

Fonts: the 24 faces of Vetto Studio's text looks (staging.vetto.world/static/fonts.css, OFL), copied into
library/fonts so ffmpeg/libass can burn captions in the same type the Vetto look picker shows.
The grouping (bold / serif / simple / handwritten / retro) follows the font filter of the Reels Engine
reference (flaviapopescu.eu); it is a Claude draft.
Pacing: numbers from social-media-skills/video-editing-skill (MIT), styles podcast / youtube / tight,
mapped to the Calm / Medium / Very lively question of the Reels Engine reference.
Palettes: Vetto spectrum (theme.css) and the account colours of the 4 FeedMe accounts (content system page,
14 Oct 2026). The neurofam PDF orange #E8572A is its own palette.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

fonts = [
    ("TikTok Sans", "TikTokSans-Bold.ttf", 700, "normal", "bold"),
    ("Lilita One", "LilitaOne-Regular.ttf", 400, "normal", "bold"),
    ("Onest", "Onest-Bold.ttf", 700, "normal", "bold"),
    ("Anton", "Anton-Regular.ttf", 400, "normal", "bold"),
    ("Barlow Condensed", "BarlowCondensed-Bold.ttf", 700, "normal", "bold"),
    ("Montserrat", "Montserrat-ExtraBoldItalic.ttf", 800, "italic", "bold"),
    ("Instrument Sans", "InstrumentSans-Bold.ttf", 700, "normal", "simple"),
    ("Instrument Sans Condensed", "InstrumentSans-CondensedMedium.ttf", 500, "normal", "simple"),
    ("Nunito Sans Condensed", "NunitoSans-CondensedMedium.ttf", 500, "normal", "simple"),
    ("Didact Gothic", "DidactGothic-Regular.ttf", 400, "normal", "simple"),
    ("Barlow Condensed SemiBold", "BarlowCondensed-SemiBold.ttf", 600, "normal", "simple"),
    ("Gelasio", "Gelasio-Bold.ttf", 700, "normal", "serif"),
    ("Bodoni Moda", "BodoniModa-Italic.ttf", 400, "italic", "serif"),
    ("Source Serif 4", "SourceSerif4-Regular.ttf", 400, "normal", "serif"),
    ("Source Serif 4 Light", "SourceSerif4-Light.ttf", 300, "normal", "serif"),
    ("Calistoga", "Calistoga-Regular.ttf", 400, "normal", "retro"),
    ("Coiny", "Coiny-Regular.ttf", 400, "normal", "retro"),
    ("Sansita", "Sansita-BlackItalic.ttf", 900, "italic", "retro"),
    ("Courier Prime", "CourierPrime-Bold.ttf", 700, "normal", "retro"),
    ("Space Mono", "SpaceMono-Regular.ttf", 400, "normal", "retro"),
    ("Comic Neue", "ComicNeue-Bold.ttf", 700, "normal", "handwritten"),
    ("Dancing Script", "DancingScript-Variable.ttf", 700, "normal", "handwritten"),
    ("Meow Script", "MeowScript-Regular.ttf", 400, "normal", "handwritten"),
]

palettes = [
    {"id": "classic", "name": "Classic white", "source": "draft", "text": "#FFFFFF", "highlight": "#FCDB1D", "outline": "#111111", "box_color": "#111111"},
    {"id": "vetto", "name": "Vetto spectrum", "source": "Vetto theme.css", "text": "#FFFFFF", "highlight": "#FE48B7", "outline": "#1E1E1E", "box_color": "#1E1E1E",
     "swatches": ["#FC1D1D", "#FEA048", "#FCDB1D", "#1DFC72", "#3CE2FF", "#421DFC", "#FE48B7"]},
    {"id": "fred", "name": "Fred Mey · indigo", "source": "account colour", "text": "#FFFFFF", "highlight": "#421DFC", "outline": "#0B0530", "box_color": "#421DFC"},
    {"id": "frank", "name": "Frank Mey · cyan", "source": "account colour", "text": "#FFFFFF", "highlight": "#3CE2FF", "outline": "#06303A", "box_color": "#06303A"},
    {"id": "fmpt2", "name": "feedmeplzthanks 2 · pink", "source": "account colour", "text": "#FFFFFF", "highlight": "#FE48B7", "outline": "#3A0626", "box_color": "#FE48B7"},
    {"id": "hr", "name": "Hongry Royalty · orange", "source": "account colour", "text": "#FFFFFF", "highlight": "#FEA048", "outline": "#3A1E06", "box_color": "#FEA048"},
    {"id": "neurofam", "name": "Warm orange (PDF)", "source": "neurofam PDF", "text": "#FFFFFF", "highlight": "#E8572A", "outline": "#0E0D0C", "box_color": "#0E0D0C"},
    {"id": "ink", "name": "Ink on paper", "source": "draft", "text": "#1E1E1E", "highlight": "#421DFC", "outline": "#F3F3F3", "box_color": "#FFFFFF"},
]

# more colour sets (16 Nov 2026, Alina: "more diverse fonts, colours, effects, styles"): Claude drafts, she picks
palettes += [
    {"id": "studio", "name": "Cream & wine", "source": "draft", "text": "#FFFFFF", "highlight": "#E8B4BC", "outline": "#5A0F22", "box_color": "#9C1131", "swatches": ["#F5F0E8", "#9C1131", "#3A1219"]},
    {"id": "butter", "name": "Butter box", "source": "draft", "text": "#111111", "highlight": "#111111", "outline": "#FFE45C", "box_color": "#FFE45C", "swatches": ["#FFE45C", "#111111"]},
    {"id": "neon", "name": "Neon night", "source": "draft", "text": "#FFFFFF", "highlight": "#39FF14", "outline": "#0A0A0A", "box_color": "#0A0A0A", "swatches": ["#0A0A0A", "#39FF14", "#FF2BD6"]},
    {"id": "pastel", "name": "Pastel pop", "source": "draft", "text": "#FFFFFF", "highlight": "#FFB3E6", "outline": "#7A4FA3", "box_color": "#C9B6FF", "swatches": ["#FFB3E6", "#C9B6FF", "#B5F2E3"]},
    {"id": "sunset", "name": "Sunset", "source": "draft", "text": "#FFF6EC", "highlight": "#FF7A3D", "outline": "#4A1530", "box_color": "#D9367A", "swatches": ["#FFB347", "#FF7A3D", "#D9367A"]},
    {"id": "ocean", "name": "Ocean", "source": "draft", "text": "#FFFFFF", "highlight": "#5CE1E6", "outline": "#06233F", "box_color": "#0B3D6B", "swatches": ["#06233F", "#0B3D6B", "#5CE1E6"]},
    {"id": "mono", "name": "Black & white", "source": "draft", "text": "#FFFFFF", "highlight": "#FFFFFF", "outline": "#000000", "box_color": "#000000", "swatches": ["#000000", "#FFFFFF"]},
    {"id": "paper", "name": "White box, black words", "source": "draft", "text": "#111111", "highlight": "#E8452A", "outline": "#FFFFFF", "box_color": "#FFFFFF", "swatches": ["#FFFFFF", "#111111", "#E8452A"]},
    {"id": "retro70", "name": "Retro 70s", "source": "draft", "text": "#FFF1D6", "highlight": "#F2A541", "outline": "#5B3A1E", "box_color": "#B5532A", "swatches": ["#F2A541", "#B5532A", "#5B3A1E"]},
    {"id": "teal-orange", "name": "Cinema teal & orange", "source": "draft", "text": "#FFFFFF", "highlight": "#FF9F43", "outline": "#0C3B40", "box_color": "#0C3B40", "swatches": ["#0C3B40", "#1B8A8F", "#FF9F43"]},
    {"id": "candy", "name": "Candy red", "source": "draft", "text": "#FFFFFF", "highlight": "#FFD1DC", "outline": "#B0001E", "box_color": "#E10032", "swatches": ["#E10032", "#FFFFFF", "#FFD1DC"]},
    {"id": "matcha", "name": "Matcha", "source": "draft", "text": "#F4F7E8", "highlight": "#B6E36A", "outline": "#2F4A1E", "box_color": "#5C7A3A", "swatches": ["#2F4A1E", "#5C7A3A", "#B6E36A"]},
    {"id": "lilac", "name": "Lilac", "source": "draft", "text": "#FFFFFF", "highlight": "#D9C2FF", "outline": "#3B2266", "box_color": "#7C5CC4", "swatches": ["#3B2266", "#7C5CC4", "#D9C2FF"]},
    {"id": "cobalt", "name": "Cobalt", "source": "draft", "text": "#FFFFFF", "highlight": "#FFE45C", "outline": "#0A1F8F", "box_color": "#1F3BD1", "swatches": ["#0A1F8F", "#1F3BD1", "#FFE45C"]},
    {"id": "earth", "name": "Earth", "source": "draft", "text": "#F7EFE3", "highlight": "#D9A066", "outline": "#3D2B1F", "box_color": "#7A5236", "swatches": ["#3D2B1F", "#7A5236", "#D9A066"]},
    {"id": "gold-lux", "name": "Black & gold", "source": "draft", "text": "#F6E7C1", "highlight": "#D4AF37", "outline": "#0B0B0B", "box_color": "#0B0B0B", "swatches": ["#0B0B0B", "#D4AF37", "#F6E7C1"]},
]

# colour grades for the footage itself (export: ffmpeg filter; preview: CSS filter on the video). Claude drafts.
grades = [
    {"id": "natural", "name": "Natural", "ffmpeg": "", "css": "none"},
    {"id": "warm", "name": "Warm", "ffmpeg": "colorbalance=rs=.06:gs=.02:bs=-.06:rm=.05:bm=-.05,eq=saturation=1.08", "css": "sepia(.18) saturate(1.12)"},
    {"id": "cool", "name": "Cool", "ffmpeg": "colorbalance=rs=-.05:bs=.07:rm=-.03:bm=.05", "css": "hue-rotate(-8deg) saturate(.95) brightness(1.02)"},
    {"id": "cinematic", "name": "Cinematic", "ffmpeg": "colorbalance=rs=-.08:bs=.10:rh=.08:bh=-.08,eq=contrast=1.12:saturation=.92,vignette=PI/5", "css": "contrast(1.12) saturate(.9) hue-rotate(-6deg)"},
    {"id": "editorial", "name": "Editorial", "ffmpeg": "eq=contrast=1.15:saturation=.72:brightness=.01", "css": "contrast(1.15) saturate(.72)"},
    {"id": "film", "name": "Vintage film", "ffmpeg": "curves=preset=vintage,noise=alls=10:allf=t,vignette=PI/4", "css": "sepia(.32) contrast(.92) saturate(.85)"},
    {"id": "bw", "name": "Black & white", "ffmpeg": "hue=s=0,eq=contrast=1.12", "css": "grayscale(1) contrast(1.12)"},
    {"id": "punchy", "name": "Punchy", "ffmpeg": "eq=contrast=1.18:saturation=1.3", "css": "contrast(1.18) saturate(1.3)"},
    {"id": "soft", "name": "Soft pastel", "ffmpeg": "eq=contrast=.9:saturation=.85:brightness=.04,colorbalance=rh=.04:bh=.04", "css": "contrast(.9) saturate(.85) brightness(1.06)"},
    # from the Editing Beast styles (17 Nov 2026)
    {"id": "clean-contrast", "name": "Clean contrast (Clean White)", "ffmpeg": "eq=contrast=1.14:brightness=-.01:saturation=1.02,colorbalance=bs=.05:bm=.02", "css": "contrast(1.14) brightness(.99) hue-rotate(-4deg)"},
    {"id": "neon-presenter", "name": "Neon presenter (Neon Dimension)", "ffmpeg": "eq=contrast=1.2:brightness=-.05:saturation=1.08,colorbalance=rs=-.10:bs=.14:rm=-.04:bm=.08:bh=.08,vignette=PI/4.5,noise=alls=9:allf=t", "css": "contrast(1.2) brightness(.92) saturate(1.08) hue-rotate(12deg)"},
    {"id": "night", "name": "Night neon", "ffmpeg": "eq=contrast=1.2:saturation=1.25:brightness=-.04,colorbalance=bs=.12:rh=.06", "css": "contrast(1.2) saturate(1.25) brightness(.95) hue-rotate(10deg)"},
]

# how the captions move (libass tags in engine/render.py, CSS in the preview). Claude drafts.
caption_anims = [
    {"id": "pop", "name": "Pop", "note": "the spoken word grows a little and takes the highlight colour"},
    {"id": "bounce", "name": "Bounce", "note": "each word springs in (70% → 115% → 100%)"},
    {"id": "karaoke", "name": "Karaoke fill", "note": "the highlight fills each word as it is said"},
    {"id": "reveal", "name": "Word by word", "note": "words appear only when they are said"},
    {"id": "rise", "name": "Fade up", "note": "each line fades in and slides up"},
    {"id": "box", "name": "Box on the word", "note": "a coloured box sits behind the spoken word"},
    {"id": "glow", "name": "Glow", "note": "the spoken word glows in the highlight colour"},
    {"id": "punch", "name": "One big word", "note": "one word at a time, large, with a small punch-in"},
    {"id": "still", "name": "Still", "note": "no motion, the spoken word only changes colour"},
    {"id": "blurin", "name": "Blur-in (Clean White)", "note": "words appear as they are said, blurring in (14 px → 0 in 0.2 s), soft white glow, no box or stroke"},
    {"id": "lexicon", "name": "Cut on the word (Cinema Lexicon)", "note": "1–3 small words cut hard on the spoken word, no motion; the key word alone and big (caps or italic); low on your take, mid-frame on example clips, dark on cream cards"},
    {"id": "glowpop", "name": "Glow pop (Neon Dimension)", "note": "1–2 words in glowing caps, each chunk pops 112 % → 100 % in 0.09 s"},
    {"id": "slam", "name": "Slam + keyword block", "note": "each line slams in (130% → 100%), its longest word gets a colour block (idea: lemo-opuscar caption-news, our own numbers)"},
]

textboxes = [
    {"id": "none", "name": "No box", "note": "outline only"},
    {"id": "box", "name": "Solid box", "note": "a filled box behind each line"},
    {"id": "plate", "name": "Dark plate", "note": "translucent plate (PDF: Me over a grid)"},
    {"id": "glass", "name": "Glass plate", "note": "blurred glass, light top edge (PDF: Glass explainer)"},
    {"id": "sticker", "name": "Sticker", "note": "white label, slight tilt (PDF: You as a sticker)"},
    {"id": "note", "name": "Handwritten note", "note": "handwriting with a scribble underline (Alina's brief)"},
]

ASS = {'TikTok Sans': ('TikTok Sans 36pt', 1, 0), 'Lilita One': ('Lilita One', 0, 0), 'Onest': ('Onest', 1, 0), 'Anton': ('Anton', 0, 0), 'Barlow Condensed': ('Barlow Condensed', 1, 0), 'Montserrat': ('Montserrat ExtraBold', 0, 1), 'Instrument Sans': ('Instrument Sans', 1, 0), 'Instrument Sans Condensed': ('Instrument Sans Condensed Medium', 0, 0), 'Nunito Sans Condensed': ('Nunito Sans Normal Condensed Medium', 0, 0), 'Didact Gothic': ('Didact Gothic', 0, 0), 'Barlow Condensed SemiBold': ('Barlow Condensed SemiBold', 0, 0), 'Gelasio': ('Gelasio', 1, 0), 'Bodoni Moda': ('Bodoni Moda', 0, 1), 'Source Serif 4': ('Source Serif 4', 0, 0), 'Source Serif 4 Light': ('Source Serif 4 24pt Light', 0, 0), 'Calistoga': ('Calistoga', 0, 0), 'Coiny': ('Coiny', 0, 0), 'Sansita': ('Sansita', 1, 1), 'Courier Prime': ('Courier Prime', 1, 0), 'Space Mono': ('Space Mono', 0, 0), 'Comic Neue': ('Comic Neue', 1, 0), 'Dancing Script': ('Dancing Script', 0, 0), 'Meow Script': ('Meow Script', 0, 0)}
# libass finds a face by its internal family name (read with fontTools), not by the CSS name
looks = {"fonts": [dict(family=f, file=file, weight=w, style=s, group=g, ro=True, ass=dict(zip(("name", "bold", "italic"), ASS[f]))) for f, file, w, s, g in fonts],
         "font_groups": ["all", "bold", "simple", "serif", "retro", "handwritten"],
         "palettes": palettes, "textboxes": textboxes, "grades": grades, "caption_anims": caption_anims}
# keep the Google Fonts faces added by fetch_fonts.py
try:
    old_looks = json.loads((HERE / "looks.json").read_text())
    looks["fonts"] += [f for f in old_looks.get("fonts", []) if str(f.get("source", "")).startswith("Google")]
except FileNotFoundError:
    pass

outputs = [
    {"id": "reel", "name": "Reel", "size": [1080, 1920], "note": "TikTok and Instagram Reels, 9:16, the main cut"},
    {"id": "story", "name": "Stories", "size": [1080, 1920], "note": "the reel split at sentence ends, each part 15 s or less"},
    {"id": "carousel", "name": "Carousel", "size": [1080, 1350], "note": "4:5 slides from the reel's beats, up to 10"},
    {"id": "cover", "name": "Cover", "size": [1080, 1920], "note": "one frame with the hook as title"},
]

pacing = [
    {"id": "calm", "name": "Calm", "preset": "podcast", "shorten_pauses_over": 0.8, "beat_mid": 0.40, "beat_sentence": 0.60, "beat_topic": 1.0,
     "min_cut": 0.6, "punch_in": None, "lufs": -16, "lead": 0.10, "tail": 0.20},
    {"id": "medium", "name": "Medium", "preset": "youtube", "shorten_pauses_over": 0.5, "beat_mid": 0.30, "beat_sentence": 0.45, "beat_topic": 0.9,
     "min_cut": 0.4, "punch_in": 1.10, "lufs": -14, "lead": 0.06, "tail": 0.10},
    {"id": "lively", "name": "Very lively", "preset": "tight", "shorten_pauses_over": 0.3, "beat_mid": 0.22, "beat_sentence": 0.25, "beat_topic": 0.5,
     "min_cut": 0.25, "punch_in": 1.15, "lufs": -14, "lead": 0.04, "tail": 0.06},
]

(HERE / "looks.json").write_text(json.dumps(looks, ensure_ascii=False, indent=1))
(HERE / "outputs.json").write_text(json.dumps(outputs, ensure_ascii=False, indent=1))
(HERE / "pacing.json").write_text(json.dumps(pacing, ensure_ascii=False, indent=1))
print("ok", len(looks["fonts"]), "fonts", len(palettes), "palettes", len(grades), "grades", len(caption_anims), "caption animations")
