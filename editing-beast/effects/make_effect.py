"""Fill one effect template into a HyperFrames project folder (same as the Vetto engine's hfx.build_html).

python3 make_effect.py <effect-id> --piece piece.mp4 --text "the words" --out work/fx1
  [--face x,y,w,h] [--hands x,y,w,h;x,y,w,h] [--words '[{"text":"hi","t":0,"e":0.3}]'] [--param key=value ...] [--image a.jpg ...]
The piece must be the 3 s of the reel (1080x1920) starting at the word. Effects that need a cutout get it from
`hyperframes remove-background` when $HF points at the hyperframes binary (source projects/img5978/hf-env.sh first).
"""
import argparse, json, os, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SH = HERE / "_shared"
REG = 'window.__timelines = window.__timelines || {}; window.__timelines["root"] = tl;'
CUTOUT = {"xp-background", "pov-carousel-spin", "sticker-cutout", "greenscreen-cutout", "text-behind-me", "stack-behind-me", "block-behind-me", "walk-between"}

a = argparse.ArgumentParser()
a.add_argument("effect"); a.add_argument("--piece", required=True); a.add_argument("--text", default=""); a.add_argument("--out", required=True)
a.add_argument("--face", default="324,346,432,422"); a.add_argument("--faces", default=""); a.add_argument("--hands", default=""); a.add_argument("--words", default="[]")
a.add_argument("--param", action="append", default=[]); a.add_argument("--image", action="append", default=[])
a.add_argument("--brand", default="", help="a brand kit folder with brand.json (Cinema Lexicon lexicon-* effects; see the engine's engine/brand.py)")
o = a.parse_args()
tpl = HERE / o.effect / "template.html"
if not tpl.exists(): raise SystemExit(f"no effect called {o.effect}: see INDEX.md")
out = Path(o.out); (out / "assets").mkdir(parents=True, exist_ok=True)
for f in SH.iterdir(): shutil.copy(f, out / "assets" / f.name)
# Meme Chaos (18 Nov 2026): keyed green-screen clips from _memes/ (meme-explosion: explosion; greenscreen-meme: --param clip=<name>)
memes = {}
_pp = dict(p.split("=", 1) for p in o.param)
for name in (["explosion"] if o.effect == "meme-explosion" else [_pp.get("clip", "explosion")] if o.effect == "greenscreen-meme" else []):
    src = HERE / "_memes" / name
    if src.exists():
        shutil.copytree(src, out / "assets" / "fx" / "memes" / name, dirs_exist_ok=True)
        memes[name] = json.loads((src / "meta.json").read_text())
shutil.copy(o.piece, out / "assets" / "piece.mp4")
imgs = []
for k, src in enumerate(o.image):
    dst = out / "assets" / f"img{k}{Path(src).suffix.lower()}"; shutil.copy(src, dst); imgs.append("assets/" + dst.name)
face = [int(x) for x in o.face.split(",")]
hands = [[int(x) for x in h.split(",")] for h in o.hands.split(";") if h.strip()]
html = tpl.read_text()
if 'src="assets/freeze.jpg"' in html or "assets/freeze.jpg" in html:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.3", "-i", o.piece, "-frames:v", "1", str(out / "assets" / "freeze.jpg")])
if o.effect in CUTOUT and not (out / "assets" / "cut.webm").exists():
    hf = os.environ.get("HF")
    if not hf: print("needs a cutout: set $HF (source projects/img5978/hf-env.sh) or put assets/cut.webm there yourself")
    else: subprocess.run([hf, "remove-background", str(out / "assets" / "piece.mp4"), "-o", str(out / "assets" / "cut.webm"), "--quality", "best"], check=True)
V = {"W": 1080, "H": 1920, "D": 3.0, "word": o.text, "params": dict(p.split("=", 1) for p in o.param), "words": json.loads(o.words),
     "images": imgs, "face": face, "track": [{"t": k * .5, "face": face, "hands": hands,
     "faces": [[int(x) for x in b.split(",")] for b in o.faces.split(";") if b.strip()] or [face]} for k in range(6)],
     "cutout": o.effect in CUTOUT, "memes": memes, "onsets": []}
# Cinema Lexicon v6 (18 Nov 2026): the product's brand kit (colours, font, icon, screens, its real buttons)
if o.brand:
    bd = Path(o.brand).expanduser()
    shutil.copytree(bd, out / "assets" / "brand", dirs_exist_ok=True)
    B = json.loads((bd / "brand.json").read_text())
    for k in ("icon", "phone", "screen_video"):
        if B.get(k): B[k] = "assets/brand/" + B[k]
    for p in B.get("pills") or []:
        if p.get("icon"): p["icon"] = "assets/brand/" + p["icon"]
    V["brand"] = B
    if o.effect == "lexicon-phone-demo" and B.get("screen_video"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(B.get("screen_video_start", 0)), "-stream_loop", "-1", "-i", str(bd / Path(B["screen_video"]).name),
                        "-t", "3", "-an", "-vf", "scale=560:-2,fps=30,format=yuv420p", str(out / "assets" / "brand_screen.mp4")])
if 'src="assets/blur.mp4"' in html:   # the take, soft-blurred (lexicon-ui-drop)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", o.piece, "-an", "-vf", "boxblur=28:3,eq=brightness=-0.03", str(out / "assets" / "blur.mp4")])
html = html.replace("/*VARS*/", "const V = " + json.dumps(V, ensure_ascii=False) + ";\n"
                    "Promise.all([...document.fonts].map(f => f.load().catch(() => null))).then(() => document.fonts.ready).then(function () {")
html = html.replace(REG, REG + ' if (typeof window.__hfForceTimelineRebind === "function") window.__hfForceTimelineRebind(); });')
html = html.replace("<!--BASE-->", '<link rel="stylesheet" href="assets/base.css"><script src="assets/gsap.min.js"></script>'
                    '<script src="assets/motion.js"></script><script src="assets/texthook.js"></script>')
(out / "index.html").write_text(html, encoding="utf-8")
print("ready:", out / "index.html")
