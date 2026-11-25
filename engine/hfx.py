"""HyperFrames effects: one HTML template per effect in engine/hf/<effect-id>.html.

For each effect on a word the runner makes a small HyperFrames project:
  assets/piece.mp4   the 3 s of the cut reel (1080x1920) starting at the word
  assets/cut.webm    a person cutout with alpha (only for effects that need it)
  assets/img*.jpg    images from the project's image bank (only for effects that need them)
  assets/*.ttf       the fonts the template uses
  index.html         the template with `const V = {...}` filled in: params (Alina's slots), the words said in
                     these 3 s (relative times), the face / hand boxes found by bin/vision, frame size
then renders it with bin/hyperframes and returns the 3 s mp4 (picture only; the voice stays the reel's).
Numbers on cards are never invented: an effect that needs numbers and has none is refused with a reason.
"""
import json
import shutil
import subprocess
from pathlib import Path

from media import run

ROOT = Path(__file__).resolve().parent.parent
HFDIR = Path(__file__).resolve().parent / "hf"
HF = ROOT / "bin" / "hyperframes"
VISION = ROOT / "bin" / "vision"
FONTS = ROOT / "library" / "fonts"
PIECE = 3.0

# which effects need a cutout / images / real numbers; the rest only need the piece
NEEDS = {
    "pov-carousel-spin": {"cutout", "images"},
    "liquid-glass-graph": {"numbers"},
    "match-cut": {"no-video"},
    "screen-push-digital": {"no-video"},
    "apple-ui-toggles": set(),
    "over-the-shoulder-zoom": {"numbers"},
    "notification-stack": set(),
    "phone-3d-float": set(),
    "sticker-cutout": {"cutout"},
    "zoom-through-text": set(),
    "pencil-outline": set(),
    "handwriting-on-word": set(),
    "greenscreen-cutout": {"cutout", "images"},
    "freeze-frame": {"freeze"},
    "title-mask-rise": set(),
    # text hooks (17 Nov 2026, from the ugcwithnyomi reference video)
    "hook-throw-in": set(),
    "stack-behind-me": {"cutout"},
    "block-behind-me": {"cutout"},
    "finger-write": set(),
    "pull-from-screen": set(),
    "walk-between": {"cutout"},
    "open-hand-reveal": set(),
    "swipe-out": set(),
    # signature pieces of the 3 Editing Beast styles (17 Nov 2026)
    "statement-stack": set(), "white-card": set(), "light-leak": set(),
    "silver-title-card": set(), "hanging-keyword": set(), "choice-buttons": set(),
    "neon-keyword": set(), "neon-pill": set(), "light-burn": set(),
    # Meme Chaos (18 Nov 2026, from Alina's dumb-scale edit, ~/Editing Beast/styles/meme-chaos/STYLE.md)
    "wavy-sparkle-hook": set(), "meme-explosion": {"memes"}, "disco-lights": set(), "xp-background": {"cutout", "background"},
    "greenscreen-meme": {"memes"}, "face-warp": set(), "clap-pulse": {"onsets"}, "crash-line": {"images?"},
    # Cinema Lexicon v6 (18 Nov 2026, Alina's approved CL01 v6): brand cards and the product's UI (projects/<id>/brand/)
    "lexicon-open": {"brand?"}, "lexicon-ui-drop": {"brand", "blur"}, "lexicon-ui-pop": {"brand?"}, "lexicon-swipe": {"brand?"},
    "lexicon-number": {"brand?"}, "lexicon-phone-demo": {"brand"}, "lexicon-close": {"brand?"},
}
TEMPLATES = set(NEEDS)
FONT_FILES = ["Anton-Regular.ttf", "TikTokSans-Bold.ttf", "InstrumentSans-Bold.ttf", "DancingScript-Variable.ttf",
              "BodoniModa-Italic.ttf", "CourierPrime-Bold.ttf", "Gelasio-Bold.ttf", "SourceSerif4-Regular.ttf",
              "SpaceMono-Regular.ttf", "MeowScript-Regular.ttf",
              "InstrumentSerif-Italic-400.ttf", "InstrumentSerif-400.ttf",
              "Unbounded-800.ttf", "GochiHand-400.ttf", "Caveat-700.ttf",
              "InterTight-800.ttf", "EBGaramond-Italic-500.ttf", "Montserrat-ExtraBoldItalic.ttf", "Coiny-Regular.ttf",
              "LilitaOne-Regular.ttf", "GreatVibes-400.ttf"]
SHARED = ["gsap.min.js", "base.css", "motion.js", "texthook.js"]
REG = 'window.__timelines = window.__timelines || {}; window.__timelines["root"] = tl;'


MEMES = HFDIR / "fx" / "memes"


def meme_names(effect, params):
    """The keyed meme clips (engine/hf/fx/memes/<name>/, made by library/add_meme_clip.py) an effect plays."""
    if effect == "meme-explosion":
        return ["explosion"]
    if effect == "greenscreen-meme":
        name = str((params or {}).get("clip") or "").strip().lower()   # no default: Explosion is its own effect (18 Nov)
        return [name] if name and (MEMES / name / "meta.json").exists() else []
    return []


def meme_meta(effect, params):
    return {n: json.loads((MEMES / n / "meta.json").read_text()) for n in meme_names(effect, params)}


def onsets(piece):
    """Times (relative, s) of sharp sound hits in the piece's audio: claps, slaps, beats. Spectral flux on 10 ms hops,
    peaks above an adaptive threshold, at least 0.12 s apart."""
    import numpy as np
    raw = subprocess.run([str(ROOT / "bin" / "ffmpeg"), "-v", "error", "-i", str(piece), "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) < 1600:
        return []
    hop, win = 160, 512
    n = (len(x) - win) // hop
    spec = np.abs(np.fft.rfft(np.stack([x[i * hop:i * hop + win] * np.hanning(win) for i in range(n)]), axis=1))
    flux = np.maximum(np.diff(np.log1p(spec[:, 20:]), axis=0), 0).sum(1)
    thr = np.convolve(flux, np.ones(25) / 25, "same") * 1.6 + np.percentile(flux, 60)
    out, last = [], -1.0
    for i in range(1, len(flux) - 1):
        t = (i + 1) * hop / 16000
        if flux[i] > thr[i] and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1] and t - last >= 0.12:
            out.append(round(t, 3)); last = t
    return out


def template_path(effect):
    """The effect's template: engine/hf/<id>.html, or a preview-only one in engine/hf/preview/ (ffmpeg effects)."""
    for f in (HFDIR / f"{effect}.html", HFDIR / "preview" / f"{effect}.html"):
        if f.exists():
            return f
    return None


def build_html(effect, V, assets="assets/", preview=False):
    """The template with `const V` filled in. Builds after every declared font has loaded (fonts on hidden elements
    are not fetched by themselves, and glyph metrics must be final), then registers the timeline: the pattern of
    HyperFrames' own registry blocks. preview=True: still frame + still cutout instead of the videos, and the
    timeline loops (the editor's effect boxes)."""
    import re
    html = template_path(effect).read_text()
    if REG not in html:
        raise RuntimeError(f"template {effect} does not register its timeline the expected way")
    play = ""
    if preview:
        play = (' tl.repeat(-1).repeatDelay(.6); tl.play(0);'
                ' window.addEventListener("message", function (e) { if (e.data === "pause") tl.pause(); if (e.data === "play") tl.play(); });')
        html = re.sub(r'<video([^>]*?)src="assets/piece\.mp4"([^>]*)></video>', r'<img\1src="__FRAME__"\2>', html)
        html = re.sub(r'<video([^>]*?)src="assets/cut\.webm"([^>]*)></video>', r'<img\1src="__CUT__"\2>', html)
        html = html.replace("assets/freeze.jpg", "__FRAME__")
        html = re.sub(r'<video([^>]*?)src="assets/bg\.mp4"([^>]*)></video>', r'<img\1src="__BG__"\2>', html)
        html = re.sub(r'<video([^>]*?)src="assets/blur\.mp4"([^>]*)></video>', r'<img\1src="__FRAME__" style="filter:blur(26px) brightness(.92)"\2>', html)
        html = html.replace("__BG__", V.get("bg_preview") or GREEN)
        html = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + re.sub(r"\bvideo\b", ".clip", m.group(1)) + "</style>", html, flags=re.S)
        html = html.replace("__FRAME__", V.get("frame", "")).replace("__CUT__", V.get("cut", ""))
        html = html.replace("</head>", "<style>html,body{overflow:hidden} img.clip{object-fit:cover}</style></head>", 1)
    html = html.replace("/*VARS*/", "const V = " + json.dumps(V, ensure_ascii=False) + ";\n"
                        "Promise.all([...document.fonts].map(f => f.load().catch(() => null))).then(() => document.fonts.ready).then(function () {")
    html = html.replace(REG, REG + play + ' if (typeof window.__hfForceTimelineRebind === "function") window.__hfForceTimelineRebind(); });')
    html = html.replace("<!--BASE-->", f'<link rel="stylesheet" href="{assets}base.css"><script src="{assets}gsap.min.js"></script>'
                        f'<script src="{assets}motion.js"></script><script src="{assets}texthook.js"></script>')
    return html


# a green screen, for previews that have no background / clip yet
GREEN = ("data:image/svg+xml;utf8," + __import__("urllib.parse").parse.quote(
    '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920"><rect width="1080" height="1920" fill="#00B140"/>'
    '<g stroke="#ffffff" stroke-opacity=".55" stroke-width="10" fill="none"><path d="M80 260v-120h120M1000 260v-120H880M80 1660v120h120M1000 1660v120H880"/></g>'
    '<text x="540" y="1000" font-family="Helvetica, Arial" font-size="64" font-weight="700" fill="#ffffff" fill-opacity=".8" text-anchor="middle">green screen</text></svg>'))


class NeedsInput(Exception):
    """The effect cannot be made without something only Alina can give (real numbers, images)."""


def vision(frames):
    p = subprocess.run([str(VISION)] + [str(f) for f in frames], capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return [{"faces": [], "objects": [], "hands": []} for _ in frames]


def _boxes(piece, work):
    """Face and hand boxes every 0.5 s (the largest face; hands as found), in 1080x1920 pixels."""
    fr = work / "vf"
    fr.mkdir(exist_ok=True)
    run(["-i", piece, "-vf", "fps=2,scale=540:-2", "-q:v", "4", fr / "f_%02d.jpg"])
    frames = sorted(fr.glob("f_*.jpg"))
    found = vision(frames)
    W, H = 1080, 1920
    px = lambda b: [round(b[0] * W), round(b[1] * H), round(b[2] * W), round(b[3] * H)]
    track = []
    for k, f in enumerate(found):
        faces = sorted(f.get("faces", []), key=lambda b: -b[2] * b[3])
        track.append({"t": k * 0.5, "face": px(faces[0]) if faces else None, "faces": [px(b) for b in faces],
                      "hands": [px(h) for h in f.get("hands", [])]})
    face = next((t["face"] for t in track if t["face"]), [int(W * .3), int(H * .18), int(W * .4), int(H * .22)])
    return {"track": track, "face": face}


def _cutout(piece, out_webm):
    p = subprocess.run([str(HF), "remove-background", str(piece), "-o", str(out_webm), "--quality", "best"],
                       capture_output=True, text=True)
    if p.returncode != 0 or not Path(out_webm).exists():
        raise RuntimeError("cutout failed: " + p.stderr[-600:])


VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def pick_attachment(params, attachments):
    """the background file: the one named in the effect's `file` field, else the last file Alina attached in the chat bar"""
    attachments = [Path(a) for a in (attachments or [])]
    want = str((params or {}).get("file") or "").strip().lower()
    if want:
        hit = [a for a in attachments if a.name.lower() == want or a.stem.lower() == want]
        if hit:
            return hit[-1]
    return attachments[-1] if attachments else None


def _background(src, dst, start=0.0):
    """any photo or video → a 3 s 1080x1920 clip (cover-fitted; a short video loops)"""
    src = Path(src)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
    if src.suffix.lower() in VIDEO_EXT:
        run(["-stream_loop", "-1", "-ss", f"{float(start):.2f}", "-i", src, "-t", PIECE, "-an", "-vf", vf, "-c:v", "libx264", "-crf", "18", dst])
    else:
        run(["-loop", "1", "-i", src, "-t", PIECE, "-vf", vf, "-c:v", "libx264", "-crf", "18", dst])


def _check(effect, params, images, attachments=None, preview=False, brand=None):
    need = NEEDS[effect]
    if "background" in need and not preview and not pick_attachment(params, attachments):
        raise NeedsInput("Green-screen background needs a background: attach a photo or video in the chat bar (Want a change?) first.")
    if "numbers" in need:
        if effect == "liquid-glass-graph" and not str(params.get("numbers", "")).strip():
            raise NeedsInput("Glass card with graph needs your real numbers (e.g. 23, 48, 76, 92). The PDF says: only real numbers.")
        if effect == "over-the-shoulder-zoom" and not (params.get("card1_number") and params.get("card2_number")):
            raise NeedsInput("Zoom + proof cards needs two real numbers, one per card.")
    if "memes" in need and not meme_names(effect, params) and not preview:
        raise NeedsInput("No green-screen clip called '" + str(params.get("clip", "")) + "' yet: add one with library/add_meme_clip.py.")
    if "images" in need and not images:
        raise NeedsInput("This effect needs photos in the image bank (Footage step).")
    if "brand" in need and not brand:
        raise NeedsInput("This effect shows the product's own UI: it needs the brand kit (ask Claude: \"make the brand kit from <store link>\").")


def render(effect, piece, params, words, images, work, word="", attachments=None, brand=None):
    """piece: 3 s 1080x1920 mp4. params: Alina's slots. words: [{text, t, e}] said in these 3 s (relative).
    images: paths from the project's bank. Returns the path of the rendered 3 s mp4."""
    if effect not in TEMPLATES:
        raise KeyError(effect)
    params = dict(params or {})
    import brand as brandmod
    bdir = Path(brand) if brand else None
    bkit = brandmod.load(bdir.parent.name) if bdir and (bdir / "brand.json").exists() else None
    _check(effect, params, images, attachments, brand=bkit)
    work = Path(work)
    proj = work / f"hf_{effect}"
    if proj.exists():
        shutil.rmtree(proj)
    (proj / "assets").mkdir(parents=True)
    shutil.copy(piece, proj / "assets" / "piece.mp4")
    for f in SHARED:
        shutil.copy(HFDIR / f, proj / "assets" / f)
    for f in FONT_FILES:
        shutil.copy(FONTS / f, proj / "assets" / Path(f).name)
    if bkit and ("brand" in NEEDS[effect] or "brand?" in NEEDS[effect]):
        shutil.copytree(bdir, proj / "assets" / "brand")
    if effect == "lexicon-phone-demo" and bkit and bkit.get("screen_video"):   # the official screen recording, from its start point
        run(["-ss", f"{float(bkit.get('screen_video_start') or 0):.2f}", "-stream_loop", "-1", "-i", bdir / bkit["screen_video"], "-t", PIECE, "-an",
             "-vf", "scale=560:-2,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18", proj / "assets" / "brand_screen.mp4"])
    if "blur" in NEEDS[effect]:    # the take, blurred (CSS blur on video is not seek-safe in HyperFrames)
        run(["-i", proj / "assets" / "piece.mp4", "-an", "-vf", "boxblur=28:3,eq=brightness=-0.03", "-c:v", "libx264", "-crf", "20",
             proj / "assets" / "blur.mp4"])
    need = NEEDS[effect]
    if "cutout" in need:
        _cutout(proj / "assets" / "piece.mp4", proj / "assets" / "cut.webm")
    imgs = []
    for n in meme_names(effect, params):
        shutil.copytree(MEMES / n, proj / "assets" / "fx" / "memes" / n)
    if "images" in need or ("images?" in need and images):
        for k, src in enumerate(images[:8]):
            dst = proj / "assets" / f"img{k}{Path(src).suffix.lower()}"
            shutil.copy(src, dst)
            imgs.append("assets/" + dst.name)
    if "background" in need:   # the attached photo / video behind the person (Green-screen background)
        _background(pick_attachment(params, attachments), proj / "assets" / "bg.mp4", (params or {}).get("bg_start") or 0)
    if "freeze" in need:   # the frame the freeze holds (0.3 s into the piece)
        run(["-ss", "0.3", "-i", proj / "assets" / "piece.mp4", "-frames:v", "1", "-q:v", "2", proj / "assets" / "freeze.jpg"])
    boxes = _boxes(piece, work) if "no-video" not in need else {"track": [], "face": None}
    V = {"W": 1080, "H": 1920, "D": PIECE, "word": word, "params": params, "words": words, "images": imgs,
         "face": boxes["face"], "track": boxes["track"], "cutout": "cutout" in need,
         "memes": meme_meta(effect, params), "onsets": onsets(piece) if "onsets" in need else [],
         "brand": brandmod.for_template(bkit, "assets/brand/") if bkit else None}
    html = build_html(effect, V)
    (proj / "index.html").write_text(html, encoding="utf-8")
    out = work / f"{effect}.mp4"
    p = subprocess.run([str(HF), "render", "-o", str(out), "-q", "standard", "--fps", "30"], cwd=proj,
                       capture_output=True, text=True)
    if p.returncode != 0 or not out.exists():
        raise RuntimeError(f"HyperFrames render of {effect} failed: " + (p.stderr or p.stdout)[-1500:])
    return out
