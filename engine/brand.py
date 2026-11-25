"""Brand kit of a project (18 Nov 2026, Cinema Lexicon v6): projects/<id>/brand/brand.json + its files.

The Cinema Lexicon edit takes its colours, display font, icon, app screens and UI buttons from the product itself
(Editing Beast STYLE.md §10, CL01: "the brand comes from the product"). Claude fills the kit from an App Store / Play
Store page or the files Alina attaches (a "brand kit" request); the engine only reads it.

brand.json:
  name          "feedmeplzthanks"
  kind          "app" | "product" | "person"      (an ad gets the branded close card; see director.cinema_lexicon)
  colors        {"ground": "#FCF0D4", "accent": "#E028B0", "accent2": "#FC5084", "ink": "#111111"}
  font          display face for the cards, a family in library/looks.json ("Lilita One")
  script_font   the script word on the open card ("Great Vibes")
  icon          "icon.png"                       (square app icon; files are relative to the brand folder)
  phone         "phone.jpg"                      (a 9:16-ish app screen for the open card's phone)
  screen_video  "preview.mp4", screen_video_start 3.6   (the official screen recording, shown in a phone frame)
  slogan        "Stop deciding. Dinner's sorted."
  tagline       "Hungry? We can fix that."
  pills         [{"label": "Munchies", "color": "#C2A4FA", "ink": "#111111", "icon": "icons/munchies.png"}, ...]
                (the product's real UI buttons, same colours: they drop onto the take on "categories / options")
  open_pills    3 buttons for the open card (default: the first 3 pills)
  cta_pill      {"label": "Surprise me", "color": "#111111", "ink": "#FBF0D3", "shadow": "#FE2F89"}
  source        where it came from (store link, Alina's files)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = {"name": "", "kind": "", "colors": {"ground": "#FCF0D4", "accent": "#E028B0", "accent2": "#FC5084", "ink": "#111111"},
           "font": "Lilita One", "script_font": "Great Vibes", "pills": [], "cta_pill": None, "slogan": "", "tagline": ""}


def folder(pid):
    return ROOT / "projects" / pid / "brand"


def load(pid):
    """the kit with defaults filled in, or None when the project has no brand kit"""
    f = folder(pid) / "brand.json"
    if not pid or not f.exists():
        return None
    b = json.loads(f.read_text())
    out = dict(DEFAULT, **b)
    out["colors"] = dict(DEFAULT["colors"], **(b.get("colors") or {}))
    # only keep files that exist
    d = folder(pid)
    for k in ("icon", "phone", "screen_video"):
        if out.get(k) and not (d / out[k]).exists():
            out[k] = None
    for k in ("pills", "open_pills"):
        out[k] = [dict(p, icon=p.get("icon") if p.get("icon") and (d / p["icon"]).exists() else None) for p in out.get(k) or []]
    return out


def for_template(b, prefix):
    """the kit as the effect templates see it (V.brand): file names prefixed with where the files are served"""
    if not b:
        return None
    out = json.loads(json.dumps(b))
    for k in ("icon", "phone", "screen_video"):
        if out.get(k):
            out[k] = prefix + out[k]
    for p in out.get("pills") or []:
        if p.get("icon"):
            p["icon"] = prefix + p["icon"]
    return out


# ---------------------------------------------------------------- making a kit (18 Nov 2026)
# Alina: the kit is made only when she gives a link (App Store, Google Play or the product's website) or attaches a brand
# kit. Nothing is invented: the name, icon, screens, colours and slogan come from the page or her files; the product's real
# UI buttons (`pills`) cannot be read off a page, so they stay empty until Claude adds them (the kit says so).
import re
import subprocess
import urllib.parse

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
LINK = re.compile(r"https?://[^\s\"'<>)]+")
KIT_FILE = re.compile(r"(?i)(brand|logo|icon|kit|palette|guideline|colou?rs?)")
IMG = {".png", ".jpg", ".jpeg", ".webp"}


def _get(url, dst=None, timeout=30):
    args = ["curl", "-sSL", "--fail", "-A", UA, "--max-time", str(timeout), url]
    if dst:
        args += ["-o", str(dst)]
    p = subprocess.run(args, capture_output=True, timeout=timeout + 5)
    if p.returncode != 0:
        raise RuntimeError(f"could not fetch {url} ({p.stderr.decode(errors='ignore')[-200:].strip()})")
    return dst if dst else p.stdout.decode("utf-8", errors="ignore")


def _hex(c):
    return "#%02X%02X%02X" % tuple(int(x) for x in c[:3])


def colours(images):
    """ground (a light colour of the icon / screens, else cream), accent (the most vivid colour: saturated and bright,
    skin / wood browns count less), accent2 (a second vivid hue), ink"""
    from PIL import Image
    import colorsys
    px = []
    for f in images:
        try:
            im = Image.open(f).convert("RGB")
            im.thumbnail((128, 128))
            q = im.quantize(16).convert("RGB")
            px += [(n, c) for n, c in q.getcolors(128 * 128)]
        except Exception:
            continue
    out = dict(DEFAULT["colors"])
    if not px:
        return out
    tot = sum(n for n, _ in px)
    hsv = [(n, c, colorsys.rgb_to_hsv(*[x / 255 for x in c])) for n, c in px]
    light = [x for x in hsv if x[2][2] > .85 and x[2][1] < .25 and x[0] / tot > .04]
    vivid = lambda x: x[2][1] ** 2 * x[2][2] * (x[0] / tot) ** .2 * (.4 if .03 < x[2][0] < .14 and x[2][1] < .65 else 1)
    strong = [x for x in hsv if x[2][1] > .45 and x[2][2] > .45 and x[0] / tot > .004]
    if light:
        out["ground"] = _hex(max(light, key=lambda x: x[0])[1])
    if strong:
        acc = max(strong, key=vivid)
        out["accent"] = _hex(acc[1])
        rest = [x for x in strong if min(abs(x[2][0] - acc[2][0]), 1 - abs(x[2][0] - acc[2][0])) > .08]
        out["accent2"] = _hex(max(rest, key=vivid)[1]) if rest else out["accent"]
    return out


def _slogan(text, limit=60):
    for line in re.split(r"[\n\r]+", text or ""):
        line = line.strip()
        if 6 <= len(line) <= limit:
            return line
    first = re.split(r"(?<=[.!?])\s", (text or "").strip())[0]
    return first if len(first) <= limit else ""


def _app_store(url, d):
    m = re.search(r"apps\.apple\.com/(?:(\w\w)/)?app/(?:[^/]+/)?id(\d+)", url)
    country, aid = (m.group(1) or "us"), m.group(2)
    r = __import__("json").loads(_get(f"https://itunes.apple.com/lookup?id={aid}&country={country}"))["results"][0]
    _get(r["artworkUrl512"].replace("512x512bb", "1024x1024bb").replace(".jpg", ".png"), d / "icon.png")
    shots = []
    for k, s in enumerate((r.get("screenshotUrls") or [])[:5]):
        try:
            shots.append(_get(s, d / f"screen_{k + 1}.jpg").name)
        except Exception:
            pass
    kit = {"name": r.get("trackName", ""), "kind": "app", "icon": "icon.png", "phone": shots[0] if shots else None, "screens": shots,
           "slogan": _slogan(r.get("description", "")), "genre": r.get("primaryGenreName", ""), "source": url}
    try:   # the App Store preview video (the page may refuse automated visits: then the kit has no screen video)
        page = _get(url)
        hls = re.findall(r"https://[^\"']+?\.m3u8", page)
        if hls:
            from media import run
            run(["-i", hls[0], "-t", "30", "-c", "copy", d / "preview.mp4"])
            kit["screen_video"], kit["screen_video_start"] = "preview.mp4", 3.0     # past the app's splash screen
    except Exception:
        pass
    return kit


def _play(url, d):
    page = _get(url)
    imgs = list(dict.fromkeys(re.findall(r"https://play-lh\.googleusercontent\.com/[\w\-]+", page)))
    title = re.search(r'<meta property="og:title" content="([^"]+)"', page)
    desc = re.search(r'<meta name="description" content="([^"]+)"', page)
    if imgs:
        _get(imgs[0] + "=s1024", d / "icon.png")
    shots = []
    for k, s in enumerate(imgs[1:6]):
        try:
            shots.append(_get(s + "=h1920", d / f"screen_{k + 1}.jpg").name)
        except Exception:
            pass
    return {"name": re.sub(r"\s*-\s*Apps on Google Play$", "", title.group(1)) if title else "", "kind": "app",
            "icon": "icon.png" if imgs else None, "phone": shots[0] if shots else None, "screens": shots,
            "slogan": _slogan(desc.group(1) if desc else ""), "source": url}


def _website(url, d):
    page = _get(url)
    meta = lambda prop: (re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)' % prop, page, re.I) or
                         re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']' % prop, page, re.I))
    name = meta("og:site_name") or meta("application-name") or re.search(r"<title[^>]*>([^<|–-]+)", page, re.I)
    icons = re.findall(r'<link[^>]+rel=["\'][^"\']*(?:apple-touch-icon|icon)[^"\']*["\'][^>]*href=["\']([^"\']+)', page, re.I)
    icons += re.findall(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\'][^"\']*(?:apple-touch-icon|icon)', page, re.I)
    icons.sort(key=lambda h: ("apple-touch" not in h and "180" not in h and "192" not in h and "512" not in h, h.endswith(".ico")))
    kit = {"name": (name.group(1).strip() if name else urllib.parse.urlparse(url).netloc.replace("www.", "")), "kind": "product", "source": url}
    for h in icons[:3]:
        try:
            ext = Path(urllib.parse.urlparse(h).path).suffix.lower()
            if ext in (".svg", ".ico"):
                continue
            _get(urllib.parse.urljoin(url, h), d / "icon.png")
            kit["icon"] = "icon.png"
            break
        except Exception:
            continue
    og = meta("og:image")
    if og:
        try:
            _get(urllib.parse.urljoin(url, og.group(1)), d / "screen_1.jpg")
            kit["phone"], kit["screens"] = "screen_1.jpg", ["screen_1.jpg"]
        except Exception:
            pass
    desc = meta("og:description") or meta("description")
    kit["slogan"] = _slogan(desc.group(1) if desc else "")
    theme = meta("theme-color")
    if theme and re.match(r"#[0-9a-fA-F]{6}$", theme.group(1)):
        kit["theme"] = theme.group(1).upper()
    return kit


def from_link(pid, url):
    """the kit from the product's App Store / Google Play page or its website"""
    d = folder(pid)
    d.mkdir(parents=True, exist_ok=True)
    if "apps.apple.com" in url:
        kit = _app_store(url, d)
    elif "play.google.com" in url:
        kit = _play(url, d)
    else:
        kit = _website(url, d)
    return _finish(pid, kit)


def from_files(pid, files):
    """the kit from files Alina attached: a brand.json (used as it is), a logo / icon image, other images as screens"""
    d = folder(pid)
    d.mkdir(parents=True, exist_ok=True)
    files = [Path(f) for f in files]
    kit = {"kind": "product", "source": "files you attached: " + ", ".join(f.name for f in files)}
    for f in files:
        if f.suffix.lower() == ".zip":
            import zipfile
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    if Path(n).suffix.lower() in IMG | {".json"} and not n.startswith("__MACOSX"):
                        (d / "_zip").mkdir(exist_ok=True)
                        out = d / "_zip" / Path(n).name
                        out.write_bytes(z.read(n))
                        files.append(out)
    js = next((f for f in files if f.suffix.lower() == ".json"), None)
    if js:
        kit.update(__import__("json").loads(js.read_text()))
    imgs = [f for f in files if f.suffix.lower() in IMG]
    logo = next((f for f in imgs if re.search(r"(?i)logo|icon", f.name)), imgs[0] if imgs else None)
    import shutil
    if logo and not kit.get("icon"):
        shutil.copy(logo, d / ("icon" + logo.suffix.lower()))
        kit["icon"] = "icon" + logo.suffix.lower()
    screens = []
    for k, f in enumerate([f for f in imgs if f != logo][:5]):
        shutil.copy(f, d / f"screen_{k + 1}{f.suffix.lower()}")
        screens.append(f"screen_{k + 1}{f.suffix.lower()}")
    if screens and not kit.get("phone"):
        kit["phone"], kit["screens"] = screens[0], screens
    if not kit.get("name") and logo:
        kit["name"] = re.sub(r"(?i)[-_ ]*(logo|icon|brand|kit)[-_ ]*", " ", logo.stem).strip()
    return _finish(pid, kit)


def _finish(pid, kit):
    """colours from the icon and screens (unless given), keep what Claude or Alina already set by hand, write brand.json"""
    import json
    d = folder(pid)
    old = json.loads((d / "brand.json").read_text()) if (d / "brand.json").exists() else {}
    if not kit.get("colors"):
        imgs = [d / x for x in [kit.get("icon")] + (kit.get("screens") or [])[:2] if x and (d / x).exists()]
        kit["colors"] = colours(imgs)
        if kit.get("theme"):      # the site's own theme colour, when it is a real colour (not near black / white)
            import colorsys
            h, sat, val = colorsys.rgb_to_hsv(*[int(kit["theme"][i:i + 2], 16) / 255 for i in (1, 3, 5)])
            if sat > .35 and val > .3:
                kit["colors"]["accent"] = kit["theme"]
    kit.setdefault("font", "Lilita One")
    kit.setdefault("script_font", "Great Vibes")
    for k in ("pills", "open_pills", "cta_pill", "slogan", "tagline", "font", "colors", "screen_video_start"):   # hand-made parts win
        if old.get(k) and old.get("by") != "engine":
            kit[k] = old[k]
    kit.setdefault("pills", [])
    kit["by"] = "engine" if not old or old.get("by") == "engine" else old.get("by")
    kit["note"] = ("the product's real buttons (pills) are not on the page: ask Claude to add them from the screenshots"
                   if not kit.get("pills") else "")
    (d / "brand.json").write_text(json.dumps({k: v for k, v in kit.items() if v not in (None, "")}, ensure_ascii=False, indent=1))
    return load(pid)


def link_in(text):
    """the first link in a text (the brief), if any"""
    m = LINK.search(text or "")
    return m.group(0).rstrip(".,") if m else None


def kit_files(files):
    """attached files that look like a brand kit (a brand.json, a zip, or names like logo / brand / icon / palette)"""
    return [Path(f) for f in files if Path(f).suffix.lower() in (".json", ".zip") or KIT_FILE.search(Path(f).name)]
