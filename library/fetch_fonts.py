"""Adds more caption/title fonts from Google Fonts (all OFL / Apache) to library/fonts/gf/ and library/looks.json.

Each face: downloaded as a static TTF (the css2 API returns TTF for a plain user agent), its internal family name read with
fontTools (libass finds fonts by that name), and whether it has the Romanian letters ă â î ș ț (`ro`).
Run: vetto-video-engine/.venv/bin/python vetto-video-engine/library/fetch_fonts.py
"""
import json
import re
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
OUT = HERE / "fonts" / "gf"
OUT.mkdir(parents=True, exist_ok=True)

# (CSS family, weight, italic, group)
FACES = [
    # bold / display
    ("Bebas Neue", 400, False, "bold"), ("Archivo Black", 400, False, "bold"), ("Oswald", 700, False, "bold"),
    ("Poppins", 800, False, "bold"), ("Inter Tight", 800, False, "bold"), ("Unbounded", 800, False, "bold"),
    ("Syne", 800, False, "bold"), ("Rubik", 900, False, "bold"), ("Bricolage Grotesque", 800, False, "bold"),
    ("Big Shoulders Display", 900, False, "bold"), ("Anybody", 900, False, "bold"),
    # serif
    ("Playfair Display", 700, True, "serif"), ("Playfair Display", 900, False, "serif"), ("Instrument Serif", 400, False, "serif"),
    ("Instrument Serif", 400, True, "serif"), ("DM Serif Display", 400, False, "serif"), ("DM Serif Display", 400, True, "serif"),
    ("Fraunces", 700, True, "serif"), ("Cormorant Garamond", 700, True, "serif"), ("EB Garamond", 500, True, "serif"),
    ("Abril Fatface", 400, False, "serif"), ("Young Serif", 400, False, "serif"),
    # handwritten
    ("Caveat", 700, False, "handwritten"), ("Permanent Marker", 400, False, "handwritten"), ("Kalam", 700, False, "handwritten"),
    ("Shadows Into Light", 400, False, "handwritten"), ("Gochi Hand", 400, False, "handwritten"), ("Rock Salt", 400, False, "handwritten"),
    ("Reenie Beanie", 400, False, "handwritten"), ("Pacifico", 400, False, "handwritten"),
    ("Great Vibes", 400, False, "handwritten"),   # Cinema Lexicon open card script word (CL01 v6, 18 Nov 2026)
    # retro / fun
    ("Bungee", 400, False, "retro"), ("Righteous", 400, False, "retro"), ("Rubik Mono One", 400, False, "retro"),
    ("Press Start 2P", 400, False, "retro"), ("Monoton", 400, False, "retro"), ("Shrikhand", 400, False, "retro"),
    ("Bagel Fat One", 400, False, "retro"), ("Chango", 400, False, "retro"),
    # simple
    ("DM Sans", 700, False, "simple"), ("Manrope", 800, False, "simple"), ("Plus Jakarta Sans", 800, False, "simple"),
    ("Figtree", 800, False, "simple"), ("Space Grotesk", 700, False, "simple"), ("IBM Plex Mono", 600, False, "simple"),
]
RO = "ăâîșțĂÂÎȘȚ"


def css_url(fam, w, it):
    axis = f"ital,wght@1,{w}" if it else f"wght@{w}"
    return f"https://fonts.googleapis.com/css2?family={fam.replace(' ', '+')}:{axis}"


def fetch(url, ua="Wget/1.21"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


looks = json.loads((HERE / "looks.json").read_text())
have = {(f["family"], f.get("weight"), f.get("style")) for f in looks["fonts"]}
added, failed = [], []
for fam, w, it, group in FACES:
    label = fam + (" Italic" if it else "") + ("" if w in (400,) else f" {w}")
    if (label, w, "italic" if it else "normal") in have:
        continue
    try:
        css = fetch(css_url(fam, w, it)).decode()
        url = re.search(r"url\((https://[^)]+\.ttf)\)", css).group(1)
        fname = re.sub(r"[^A-Za-z0-9]+", "", fam) + ("-Italic" if it else "") + f"-{w}.ttf"
        dst = OUT / fname
        if not dst.exists():
            dst.write_bytes(fetch(url))
        tt = TTFont(str(dst))
        name = tt["name"]
        fam_int = name.getDebugName(1) or name.getDebugName(16)   # libass matches the legacy family (nameID 1), not the typographic one (16)
        sub = name.getDebugName(17) or name.getDebugName(2) or ""
        cmap = tt.getBestCmap()
        ro = all(ord(c) in cmap for c in RO)
        looks["fonts"].append({
            "family": label, "css_family": fam, "file": "gf/" + fname, "weight": w, "style": "italic" if it else "normal",
            "group": group, "ro": ro, "source": "Google Fonts (OFL)",
            # libass: family + bold/italic flags select the face inside fontsdir
            "ass": {"name": fam_int, "bold": w >= 600 and "Bold" in sub or w >= 700, "italic": it, "subfamily": sub},
        })
        added.append(f"{label}{'' if ro else ' (no ș/ț)'}")
    except Exception as e:  # keep going; report at the end
        failed.append(f"{label}: {e}")

for f in looks["fonts"]:
    f.setdefault("ro", True if f.get("source") is None else f.get("ro"))
(HERE / "looks.json").write_text(json.dumps(looks, ensure_ascii=False, indent=1))
print(len(added), "added:", ", ".join(added))
print("failed:", failed)
