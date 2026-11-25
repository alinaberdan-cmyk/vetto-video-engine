"""Memes on phrases (Alina, 25 Nov 2026): "a Memes section that picks different memes for specific phrases from the transcript.
The engine sees the phrases and matches the words with a category of memes / gifs. Reaction GIFs that fit what you say,
plus a library for any second. The pictures come from Pinterest and the GIFs from giphy.com."

- Moments: the transcript is split into phrases; each phrase's words are matched with reaction categories (CATS: trigger
  words in English and Romanian -> Giphy search terms + her Pinterest emotion folders). Concrete objects she names get
  "<object> funny" (the 24 Nov object-picture rule).
- Pictures: her Pinterest library (~/Desktop/Pinterest FeedMe - Emotii, mirrored into library/memes/pinterest because the
  engine may not read the Desktop), with the Meme Chaos catalogue (what each picture shows / means), plus pin links she
  pastes (the pin's own image is downloaded).
- GIFs: the official GIPHY API with her free key (developers.giphy.com), kept in .secrets.json like the Pexels key.
- Placing one makes an overlay {kind: "meme"} on the phrase: a GIF plays as an animated card, a cut-out PNG pops as a
  sticker, a photo as a white-bordered card; away from the face. Her pick, so status "kept".
"""
import csv
import json
import re
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS = ROOT / ".secrets.json"
DESK = Path.home() / "Desktop" / "Pinterest FeedMe - Emotii"
MIRROR = ROOT / "library" / "memes" / "pinterest"
CATALOGUE = [Path.home() / "Desktop" / "Editing Beast" / "styles" / "meme-chaos" / "meme_pictures.json",
             ROOT / "library" / "memes" / "meme_pictures.json"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
PIC_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# reaction categories: (id, name, giphy search terms, her Pinterest emotion folders, trigger words / phrases EN + RO)
CATS = [
    ("hello", "Hello wave", ["hello wave", "hi there", "waving"], ["Fericire"],
     ["hello", "hi", "hey", "salut", "buna", "bună", "welcome"]),
    ("mindblown", "Mind blown", ["mind blown", "magic", "wow"], ["Surpriza"],
     ["wow", "amazing", "incredible", "magic", "unbelievable", "insane", "crazy", "ai", "engine", "automatically", "genius",
      "uimitor", "incredibil", "magie", "wow"]),
    ("shock", "Shock / no way", ["shocked", "no way", "omg"], ["Surpriza"],
     ["what", "no way", "omg", "seriously", "really", "shocked", "surprise", "ce", "serios", "nu se poate", "șoc", "soc"]),
    ("confused", "No idea / confused", ["no idea", "confused", "shrug"], ["Curiozitate", "Indiferenta"],
     ["don't know", "dont know", "no idea", "confused", "how", "why", "manually", "understand", "nu stiu", "nu știu",
      "habar", "cum", "de ce", "manual"]),
    ("hope", "Fingers crossed", ["fingers crossed", "please please", "praying"], ["Liniste"],
     ["hope", "please", "pray", "wish", "sper", "te rog", "speranta", "speranță"]),
    ("happy", "Happy dance", ["happy dance", "celebrate", "lets go"], ["Fericire"],
     ["yes", "finally", "great", "love", "best", "perfect", "good", "very good", "nice", "won", "da", "super", "minunat",
      "perfect", "bine", "în sfârșit", "in sfarsit"]),
    ("sad", "Sad / for nothing", ["sad crying", "disappointed", "why me"], ["Tristete"],
     ["nothing", "sad", "lost", "wasted", "spent all", "for nothing", "fail", "trist", "degeaba", "pierdut", "nimic"]),
    ("threat", "Watching you / you better", ["i'm watching you", "you better", "threatening"], ["Suspiciune", "Furie"],
     ["better", "otherwise", "or else", "warning", "watch", "altfel", "bine ar fi", "ai grija", "ai grijă"]),
    ("angry", "Angry / rage", ["angry", "rage", "furious"], ["Furie"],
     ["hate", "angry", "mad", "annoying", "stupid", "urăsc", "urasc", "nervos", "enervant"]),
    ("sus", "Suspicious / side eye", ["side eye", "suspicious", "hmm"], ["Suspiciune"],
     ["hmm", "sure", "suspicious", "trust", "sus", "suspect", "sigur"]),
    ("hungry", "Hungry / food", ["hungry", "food", "yummy"], ["Fericire", "Amuzament"],
     ["food", "eat", "eating", "hungry", "delicious", "pizza", "burger", "order", "delivery", "dinner", "lunch", "snack",
      "mâncare", "mancare", "foame", "comand", "livrare", "gustos"]),
    ("confident", "Confident / flex", ["confident", "boss", "too easy"], ["Incredere"],
     ["easy", "pro", "boss", "money", "rich", "confident", "obviously", "of course", "ușor", "usor", "bani", "evident"]),
    ("bored", "Waiting / bored", ["waiting", "bored", "tapping fingers"], ["Indiferenta"],
     ["wait", "waiting", "slow", "time", "bored", "long", "aștept", "astept", "timp", "plictis"]),
    ("work", "Get to work", ["get to work", "typing fast", "working hard"], ["Incredere"],
     ["work", "test", "build", "edit", "editing", "lucrez", "muncă", "munca", "testez"]),
    ("love", "Love", ["love it", "heart eyes", "in love"], ["Iubire"],
     ["love", "cute", "heart", "iubesc", "drăguț", "dragut"]),
    ("cringe", "Cringe / facepalm", ["facepalm", "cringe", "awkward"], ["Dezgust"],
     ["cringe", "awkward", "oops", "mistake", "embarrass", "jenant", "greșeal", "greseal"]),
]
CAT = {c[0]: {"id": c[0], "name": c[1], "giphy": c[2], "folders": c[3], "words": c[4]} for c in CATS}
FOLDERS = ["Amuzament", "Curiozitate", "Dezgust", "Fericire", "Furie", "Incredere", "Indiferenta", "Iubire", "Liniste",
           "Obiecte", "Surpriza", "Suspiciune", "Tristete"]


# ---------------------------------------------------------------- keys
def giphy_key():
    try:
        return json.loads(SECRETS.read_text()).get("giphy") or None
    except Exception:
        return None


def save_giphy_key(key):
    giphy_search("hello", key=key, limit=1)        # raises when the key is wrong
    data = json.loads(SECRETS.read_text()) if SECRETS.exists() else {}
    data["giphy"] = key.strip()
    SECRETS.write_text(json.dumps(data))
    SECRETS.chmod(0o600)


# ---------------------------------------------------------------- GIPHY
def _get(url):
    pr = subprocess.run(["curl", "-sS", "--fail", "--max-time", "20", "-A", "vetto-video-engine/1.0", url],
                        capture_output=True, text=True)
    if pr.returncode != 0:
        raise RuntimeError((pr.stderr or "request failed").strip()[:200])
    return json.loads(pr.stdout)


def giphy_search(q, key=None, limit=12, offset=0):
    key = key or giphy_key()
    if not key:
        return []
    url = "https://api.giphy.com/v1/gifs/search?" + urllib.parse.urlencode(
        {"api_key": key, "q": q, "limit": limit, "offset": offset, "rating": "pg-13", "lang": "en"})
    out = []
    for g in _get(url).get("data", []):
        im = g.get("images", {})
        gif = (im.get("downsized") or im.get("fixed_height") or {}).get("url")
        thumb = (im.get("fixed_height_small") or im.get("fixed_height") or {}).get("url")
        if gif and thumb:
            out.append({"kind": "gif", "id": "g" + g["id"], "thumb": thumb, "src": gif, "title": g.get("title", ""),
                        "by": (g.get("user") or {}).get("display_name") or g.get("username") or "",
                        "url": g.get("url", ""), "source": "GIPHY"})
    return out


# ---------------------------------------------------------------- her Pinterest library
def lib_root():
    """the Desktop folder when the engine may read it (kept in sync into the mirror), else the mirror"""
    try:
        if DESK.exists() and any(DESK.iterdir()):
            sync_mirror()
            return DESK
    except PermissionError:
        pass
    return MIRROR


def sync_mirror():
    MIRROR.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-a", "--exclude", "_Duplicate", f"{DESK}/", f"{MIRROR}/"], capture_output=True)


def _catalogue():
    for c in CATALOGUE:
        try:
            return {e["file"]: e for e in json.loads(c.read_text())}
        except Exception:
            continue
    return {}


def library():
    """every picture in her library: [{kind: picture, id, file (relative), folder, shows, meaning, use_when, cutout}]"""
    root, cat, out = lib_root(), _catalogue(), []
    objs = {}
    try:
        with open(root / "Obiecte" / "index.csv") as f:
            objs = {r["file"]: r for r in csv.DictReader(f)}
    except Exception:
        pass
    for folder in FOLDERS + ["Din engine"]:
        d = root / folder
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix.lower() not in PIC_EXT:
                continue
            rel = f"{folder}/{f.name}"
            if f.stem.endswith("_fara_fundal") and any(d.glob(f.stem[:-12] + "_original.*")):
                continue          # the cut-out is offered with its original
            e = cat.get(rel, {})
            o = objs.get(f.name) or objs.get(f.stem.replace("_original", "_fara_fundal") + ".png") or {}
            cut = e.get("cutout") or (f"{folder}/{f.stem[:-9]}_fara_fundal.png" if f.stem.endswith("_original") else "")
            out.append({"kind": "picture", "id": "p" + re.sub(r"[^a-z0-9]", "", rel.lower())[-40:], "file": rel,
                        "folder": folder, "shows": e.get("shows") or o.get("shows") or f.stem.replace("_", " "),
                        "meaning": e.get("meaning", ""), "use_when": e.get("use_when", "") or o.get("object", ""),
                        "quality": e.get("quality", ""), "cutout": cut if cut and (root / cut).exists() else "",
                        "thumb": "/memelib/" + urllib.parse.quote(rel), "source": "Pinterest (her library)"})
    return out


def library_for(cat_ids, words, items=None, limit=12):
    """her pictures that fit these categories: catalogue text matching the phrase first, then the emotion folders"""
    items = items if items is not None else library()
    folders = {f for c in cat_ids for f in CAT.get(c, {}).get("folders", [])}
    try:
        import stock
        stop = set(getattr(stock, "STOPW", set()))
    except Exception:
        stop = set()
    stop |= {"going", "now", "here", "this", "that", "all", "very", "the", "and", "are", "for", "you", "we", "is", "be", "to"}
    ws = {w for w in words if len(w) > 2 and w not in stop}
    def score(it):
        text = f"{it['shows']} {it['meaning']} {it['use_when']}".lower()
        s = 3 * sum(1 for w in ws if re.search(r"\b" + re.escape(w), text))
        s += 2 if it["folder"] in folders else 0
        s += {"clean": 1, "caption-baked": 0, "screenshot": -1, "not-a-meme": -9}.get(it["quality"], 0)
        return s
    ranked = sorted(((score(it), it) for it in items), key=lambda x: -x[0])
    strong = [it for s, it in ranked if s >= 3]          # the picture's meaning matches the phrase
    loose = [it for s, it in ranked if 2 <= s < 3][:2]   # only the emotion folder matches: at most two
    return (strong + loose)[:limit]


# ---------------------------------------------------------------- moments in the transcript
def _norm(t):
    return re.sub(r"[^\wăâîșțşţ' ]", "", t.lower()).strip()


def phrases(p):
    """sentences / breath groups of the kept words: [{start, end, word_i, text, words}]"""
    ws = [w for w in (p.get("edl") or {}).get("words", []) if not w.get("cut")]
    out, cur = [], []
    for k, w in enumerate(ws):
        cur.append(w)
        gap = ws[k + 1]["start"] - w["end"] if k + 1 < len(ws) else 9
        if re.search(r"[.!?,;:]$", w["text"].strip()) or gap > 0.35 or len(cur) >= 12:
            if re.search(r"[,;:]$", w["text"].strip()) and len(cur) < 4 and gap <= 0.35:
                continue          # a short clause before a comma joins the next one
            out.append({"start": cur[0]["start"], "end": cur[-1]["end"], "word_i": cur[0]["i"],
                        "text": " ".join(x["text"] for x in cur).strip(), "words": [_norm(x["text"]) for x in cur], "wl": list(cur)})
            cur = []
    return out


def categorize(ph):
    text = " " + " ".join(ph["words"]) + " "
    hits, opening = [], " " + " ".join(ph["words"][:2]) + " "
    for c in CATS:
        n = sum(1 for t in c[4] if (" " + t + " ") in text)
        if n:
            n += 2 * any((" " + t + " ") in opening for t in c[4])    # what the phrase opens with leads ("Hello, …")
            hits.append((n, c[0]))
    return [c for n, c in sorted(hits, key=lambda x: -x[0])]


def moments(p, limit=10):
    """the phrases worth a meme, each with its categories, its Giphy query and its candidates"""
    import stock
    items = library()
    out, objects = [], []
    seen = set()
    for ph in phrases(p):
        cats = categorize(ph)
        objs = stock.concrete_words(ph["text"]) if hasattr(stock, "concrete_words") else []
        # every object she names gets its own moment on its own word (24 Nov rule: a funny picture of that object)
        for o in objs:
            if o in seen:
                continue
            w = next((x for x in ph["wl"] if stock._singular(_norm(x["text"])) == o), ph["wl"][0])
            seen.add(o)
            objects.append({"start": w["start"], "end": w["end"], "word_i": w["i"], "text": ph["text"], "words": ph["words"],
                            "cats": [], "objects": [o], "query": f"{o} funny", "terms": [f"{o} funny", f"{o} meme"],
                            "cat_names": [f"{o} (object)"], "focus": w["text"]})
        if cats:
            terms = [t for c in cats[:2] for t in CAT[c]["giphy"][:2]]
            out.append({**ph, "cats": cats, "objects": [], "query": terms[0], "terms": terms[:3],
                        "cat_names": [CAT[c]["name"] for c in cats]})
    # the strongest phrases, at most one every ~2.5 s and never on an object's word
    out.sort(key=lambda m: -len(m["cats"]))
    kept = list(objects)
    for m in out:
        if all(abs(m["start"] - k["start"]) > 2.5 for k in kept):
            kept.append(m)
        if len(kept) >= limit:
            break
    kept = [{k: v for k, v in m.items() if k != "wl"} for m in kept]
    kept.sort(key=lambda m: m["start"])
    def fill(m):
        try:
            gifs = giphy_search(m["query"], limit=6)
        except Exception as e:
            gifs, m["error"] = [], str(e)
        pics = library_for(m["cats"], m["words"] + m["objects"], items, limit=6)
        if m["objects"]:          # her object pictures (Obiecte) first, then anything in her library that shows the object
            o = m["objects"][0]
            pics = [it for it in items if re.search(r"\b" + re.escape(o) + r"s?\b", (it["use_when"] + " " + it["shows"]).lower())]
            pics.sort(key=lambda it: it["folder"] != "Obiecte")
        m["items"] = (pics[:3] + gifs[:6] + pics[3:6]) if gifs else pics[:6]
        m["offset"] = 6
        return m
    with ThreadPoolExecutor(4) as ex:
        return list(ex.map(fill, kept))


def search(q, offset=0, limit=12):
    """the 'library for any second': GIPHY + her pictures for any words"""
    words = [_norm(w) for w in q.split()]
    cats = [c for c in CAT if any(w in CAT[c]["words"] or w in CAT[c]["name"].lower() for w in words)] or \
           [c for c in CAT if c == q]
    if q in CAT:
        q = CAT[q]["giphy"][0]
    try:
        gifs = giphy_search(q, limit=limit, offset=offset)
        err = None
    except Exception as e:
        gifs, err = [], str(e)
    pics = library_for(cats, words, limit=limit) if offset == 0 else []
    return {"items": pics + gifs, "error": err}


def folder_items(folder):
    return [it for it in library() if it["folder"] == folder]


# ---------------------------------------------------------------- Pinterest pin links
def import_pin(url):
    """a pin link she pastes -> the pin's image in her library ('Din engine' folder)"""
    if not re.match(r"^https://([a-z]{2,3}\.)?(www\.)?pinterest\.[a-z.]+/pin/\d+|^https://pin\.it/\w+", url.strip()):
        raise ValueError("That is not a Pinterest pin link (pinterest.com/pin/… or pin.it/…)")
    pr = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "20", "-A", UA, url.strip()], capture_output=True, text=True)
    html = pr.stdout or ""
    # the pin's own picture: its share image (og:image), not the first picture on the page (icons, other pins)
    m = re.search(r'<meta[^>]+(?:property|name)="og:image"[^>]+content="([^"]+)"', html) or \
        re.search(r'<meta[^>]+content="([^"]+)"[^>]+(?:property|name)="og:image"', html)
    if not m or "pinimg.com" not in m.group(1):
        raise RuntimeError("Pinterest did not show the picture for that pin (it may be private)")
    src = m.group(1).replace("&amp;", "&")
    best = re.sub(r"/(\d+x|\d+x\d+)/", "/originals/", src)
    pid = re.search(r"/pin/(\d+)", url) or re.search(r'"pin_id":"?(\d+)', html) or re.search(r"/(\w+)/?$", url)
    name = f"pin_{pid.group(1) if pid else 'x'}{Path(src).suffix or '.jpg'}"
    tmp = MIRROR / "Din engine" / name
    tmp.parent.mkdir(parents=True, exist_ok=True)
    for u in (best, src):
        if subprocess.run(["curl", "-sSL", "--fail", "--max-time", "30", "-A", UA, "-o", str(tmp), u], capture_output=True).returncode == 0:
            break
    else:
        raise RuntimeError("Could not download the pin's picture")
    try:                                   # into her Desktop library too, when the engine may write there
        (DESK / "Din engine").mkdir(exist_ok=True)
        (DESK / "Din engine" / name).write_bytes(tmp.read_bytes())
    except Exception:
        pass
    return {"kind": "picture", "id": "pin" + name, "file": f"Din engine/{name}", "folder": "Din engine", "shows": "pin " + url,
            "meaning": "", "use_when": "", "quality": "", "cutout": "", "thumb": "/memelib/" + urllib.parse.quote(f"Din engine/{name}"),
            "source": f"Pinterest pin {url}"}


# ---------------------------------------------------------------- placing one
def spot(fs, W=1080, H=1920):
    """where a meme card goes so it never covers her head while it is on screen. fs = her face boxes (x, y, w, h, Vision,
    starting at the eyebrows) at the start, middle and end of the card's time. Above the head when there is room, else
    beside the face on the freer side, else a small card in the top corner of the freer side."""
    if fs and isinstance(fs[0], (int, float)):
        fs = [fs]
    head_top = min(f[1] - 0.45 * f[3] for f in fs) / H  # hair and forehead above the face box
    above = head_top - 0.12                              # the card starts at 10 % of the height
    left, right = min(f[0] for f in fs) / W, max(f[0] + f[2] for f in fs) / W
    gap_l, gap_r = left, 1 - right
    x = "right" if gap_r >= gap_l else "left"
    if above >= 0.12:
        return x, "top", round(min(0.34, above), 3), 0.4
    if max(gap_l, gap_r) >= 0.2:                         # beside the face, as wide as the free side allows
        return x, "middle", 0.34, round(min(0.4, max(gap_l, gap_r) - 0.08), 3)
    return x, "top", 0.12, 0.3


def place(pid, version_id, item, at, word_i=None, phrase="", hold=1.6, by="memes", status="kept", why="picked by you in Memes"):
    pdir = ROOT / "projects" / pid
    pj = pdir / "project.json"
    p = json.loads(pj.read_text())
    (pdir / "images").mkdir(exist_ok=True)
    cutout = False
    if item["kind"] == "gif":
        dst = pdir / "images" / f"meme_{item['id']}.gif"
        if not dst.exists():
            r = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "60", "-A", UA, "-o", str(dst), item["src"]], capture_output=True)
            if r.returncode != 0:
                raise RuntimeError("Could not download that GIF from GIPHY")
        src_txt = f"GIPHY: {item.get('title') or ''}{' by ' + item['by'] if item.get('by') else ''} ({item.get('url', '')})"
    else:
        root = lib_root()
        rel = item.get("cutout") or item["file"]
        cutout = bool(item.get("cutout")) or rel.lower().endswith(".png")
        srcf = root / rel
        if not srcf.exists():
            srcf = MIRROR / rel
        dst = pdir / "images" / f"meme_{Path(rel).name}"
        dst.write_bytes(srcf.read_bytes())
        src_txt = f"Pinterest library: {item['file']} ({item.get('shows', '')})"
    try:
        from PIL import Image
        ow, oh = Image.open(dst).size
    except Exception:
        ow, oh = 0, 0
    ws = (p.get("edl") or {}).get("words", [])
    if word_i is None and ws:
        word_i = min(ws, key=lambda w: abs(w["start"] - at))["i"]
    x, y, max_h, scale = "right", "top", 0.24, 0.4
    try:
        import preview
        fs = [b.get("face") for b in (preview.frame(pdir, p, t)[1] for t in (at, at + hold / 2, at + hold - 0.1))]
        fs = [f for f in fs if f]
        if fs:
            x, y, max_h, scale = spot(fs)
    except Exception:
        pass
    v = next(x_ for x_ in p["versions"] if x_["id"] == version_id)
    ov = {"id": "m" + item["id"][-6:] + f"{int(at * 10):04d}", "kind": "meme", "image": str(dst), "cutout": cutout,
          "word_i": word_i, "at": at, "hold": hold, "x": x, "y": y, "max_h": max_h, "ow": ow, "oh": oh, "tilt": -4 if x == "right" else 4, "scale": scale,
          "status": status, "by": by, "phrase": phrase, "source": src_txt, "why": why}
    v["overlays"] = [o for o in v.get("overlays", []) if not (str(o.get("by", "")).startswith("memes") and abs(o["at"] - at) < 0.05)] + [ov]
    p["rev"] = int(p.get("rev") or 0) + 1
    pj.write_text(json.dumps(p, ensure_ascii=False, indent=1))
    return {"overlay": ov, "project": p}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    pj = json.loads((ROOT / "projects" / sys.argv[1] / "project.json").read_text())
    for m in moments(pj):
        print(f"{m['start']:5.1f} {m['text'][:50]:50s} {m['cat_names']} {m['objects']} -> {m['terms']} ({len(m['items'])} items)")


# ---------------------------------------------------------------- Meme Chaos: memes applied by themselves
def auto(pid, version_id, log=print, gap=3.0):
    """Alina, 25 Nov 2026: "for the Meme Chaos style, when I select this style the memes and gifs need to be automatically
    applied from the api key and pinterest data base to the video, without me having to select them manually."
    Every object she names gets its funny picture (her Pinterest library first, else a GIF); the strongest reaction phrases
    get the top GIPHY GIF, at most one every `gap` seconds and never on top of another meme. Picks are 'proposed' (she swaps
    or removes them in Memes); her own picks are kept and never replaced."""
    pdir = ROOT / "projects" / pid
    p = json.loads((pdir / "project.json").read_text())
    v = next(x for x in p["versions"] if x["id"] == version_id)
    mine = [o for o in v.get("overlays", []) if o.get("by") == "memes" and o.get("status") != "removed"]
    # a meme she removed means "no meme here": the automatic picks leave that moment alone
    said_no = [o["at"] for o in v.get("overlays", []) if str(o.get("by", "")).startswith("memes") and o.get("status") == "removed"]
    # earlier automatic picks go (she gets a fresh set); hers stay
    v["overlays"] = [o for o in v.get("overlays", []) if o.get("by") != "memes-auto" or o.get("status") == "removed"]
    p["rev"] = int(p.get("rev") or 0) + 1
    (pdir / "project.json").write_text(json.dumps(p, ensure_ascii=False, indent=1))
    ms = moments(p)
    taken = [o["at"] for o in mine]
    placed = []
    def free(t):
        return all(abs(t - x) >= gap for x in taken)
    objs = [m for m in ms if m["objects"]]
    phr = sorted([m for m in ms if not m["objects"]], key=lambda m: -len(m["cats"]))
    for m in objs + phr:
        if any(abs(m["start"] - x) < 0.3 for x in said_no):
            continue
        if m["objects"]:
            if any(abs(m["start"] - x) < 0.3 for x in taken):
                continue                                   # she already put something on this word
            pics = [it for it in m["items"] if it["kind"] == "picture"]
            gifs = [it for it in m["items"] if it["kind"] == "gif"]
            it = (pics or gifs or [None])[0]
            hold = 1.3
        else:
            if not free(m["start"]):
                continue
            gifs = [it for it in m["items"] if it["kind"] == "gif"]
            it = (gifs or [None])[0]                       # reactions: the top GIPHY GIF (pictures only if no key)
            if it is None:
                strong = [x for x in m["items"] if x["kind"] == "picture" and x["folder"] != "Obiecte"]
                it = strong[0] if strong else None
            hold = max(1.2, min(2.5, m["end"] - m["start"]))
        if not it:
            continue
        try:
            what = ", ".join(m["objects"]) if m["objects"] else " / ".join(m["cat_names"][:2])
            place(pid, version_id, it, m["start"], m["word_i"], m["text"], hold, by="memes-auto", status="proposed",
                  why=f"Meme Chaos picked it for “{what}”")
            taken.append(m["start"]); placed.append({"at": m["start"], "what": what, "kind": it["kind"]})
            log(f"{m['start']:.1f}s {what}: {it['kind']}")
        except Exception as e:
            log(f"{m['start']:.1f}s: {e}")
    return {"placed": placed, "kept_yours": len(mine)}
