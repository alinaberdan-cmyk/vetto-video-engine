"""Example clips for Cinema Lexicon (18 Nov 2026): one literal clip per phrase, from Pexels (free licence, no watermark).

The style's director leaves a slot on each phrase that needs a picture (`overlays[]` with `"kind": "clip"`, a `query`
and no file yet) and a request to Claude. Claude picks a clip that acts out the *human meaning* of the phrase (Editing
Beast STYLE.md §4 and §10: "showed it to me" → two people scrolling one phone), then fills the slot:

  .venv/bin/python engine/stock.py <project id> <overlay id> <pexels id | video file> [media start s]

The clip is downloaded from pexels.com/download/video/<id>/ (no sign-in), conformed to 1080x1920 30 fps without
sound in projects/<id>/clips/, and the slot gets its file. Never a watermarked clip, never a removed watermark.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from media import run, sdr_vf  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"


def download_pexels(pexels_id, dst):
    url = f"https://www.pexels.com/download/video/{int(pexels_id)}/"
    p = subprocess.run(["curl", "-sSL", "-A", UA, "--fail", "-o", str(dst), url], capture_output=True, text=True)
    if p.returncode != 0 or not Path(dst).exists() or Path(dst).stat().st_size < 50_000:
        raise RuntimeError(f"Pexels download of {pexels_id} failed: {p.stderr[-300:]}")
    return dst


def conform(src, dst):
    """any clip → 1080x1920 30 fps h264, no sound (cover crop; the slot's `focus` moves the crop at render time,
    so keep a little extra width: scale to 1920 tall and crop to at most 1920 wide)"""
    run(["-i", src, "-an", "-vf", f"{sdr_vf(src)}scale=-2:1920,crop='min(iw,1920)':1920,setsar=1,fps=30,format=yuv420p",
         "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-movflags", "+faststart", dst])
    return dst


def fill(pid, oid, what, media_start=None):
    pdir = ROOT / "projects" / pid
    pj = pdir / "project.json"
    p = json.loads(pj.read_text())
    slot = next((o for v in p["versions"] for o in v.get("overlays", []) if o["id"] == oid), None)
    if not slot:
        raise SystemExit(f"no overlay {oid} in {pid}")
    out_dir = pdir / "clips"
    out_dir.mkdir(exist_ok=True)
    if str(what).isdigit():
        raw = out_dir / f"pexels_{what}_raw.mp4"
        if not raw.exists():
            download_pexels(what, raw)
        source = f"Pexels {what} (https://www.pexels.com/video/{what}/), Pexels licence"
    else:
        raw = Path(what).expanduser()
        source = f"file {raw.name}"
    dst = out_dir / f"{oid}_{Path(str(what)).stem if not str(what).isdigit() else what}.mp4"
    conform(raw, dst)
    # write back on the newest copy of the project (the editor may have saved meanwhile)
    p = json.loads(pj.read_text())
    for v in p["versions"]:
        for o in v.get("overlays", []):
            if o["id"] == oid:
                o["image"] = str(dst)
                o["source"] = source
                if media_start is not None:
                    o["media_start"] = float(media_start)
                if o.get("status") == "needs clip":
                    o["status"] = "proposed"
    pj.write_text(json.dumps(p, ensure_ascii=False, indent=1))
    return dst


def _main():
    # python engine/stock.py search videos|photos "<query>"   → JSON results (Pexels API key needed)
    if len(sys.argv) >= 4 and sys.argv[1] == "search":
        key = pexels_key()
        if not key:
            raise SystemExit("No Pexels key saved (Effects step → Stock on your words). Find Pexels ids with a web search instead.")
        res = search(sys.argv[3], key) if sys.argv[2].startswith("vid") else search_photos(sys.argv[3], key)
        print(json.dumps([_video_item(v) for v in res] if sys.argv[2].startswith("vid") else [_photo_item(x) for x in res], indent=1))
        return
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    print(fill(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))


# ---------------------------------------------------------------- automatic (18 Nov 2026)
# Alina: when she picks Cinema Lexicon the example clips are found by the engine itself. Pexels' official API (free key
# from pexels.com/api, saved in ENG/.secrets.json or $PEXELS_API_KEY) searches each slot's query; the first portrait clip
# that is long enough and not used yet fills the slot. Claude can still swap any clip later (fill()).
SECRETS = ROOT / ".secrets.json"


def pexels_key():
    import os
    if os.environ.get("PEXELS_API_KEY"):
        return os.environ["PEXELS_API_KEY"]
    try:
        return json.loads(SECRETS.read_text()).get("pexels") or None
    except Exception:
        return None


def save_key(key):
    data = json.loads(SECRETS.read_text()) if SECRETS.exists() else {}
    data["pexels"] = key.strip()
    SECRETS.write_text(json.dumps(data))
    SECRETS.chmod(0o600)


def search(query, key, per_page=12):
    import urllib.parse
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({"query": query, "orientation": "portrait", "per_page": per_page, "size": "medium"})
    p = subprocess.run(["curl", "-sS", "--fail", "--max-time", "30", "-H", f"Authorization: {key}", url], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Pexels search failed ({p.stderr.strip()[-200:]}): is the key right?")
    return json.loads(p.stdout).get("videos", [])


def best_file(v):
    """the video file to download: portrait, about 1080 wide (never a huge 4K file when a 1080 one exists)"""
    fs = [f for f in v.get("video_files", []) if f.get("link") and f.get("width") and f.get("height")]
    if not fs:
        return None
    good = [f for f in fs if f["height"] >= f["width"] and 1000 <= f["width"] <= 1440] or [f for f in fs if f["height"] >= 1280] or fs
    return min(good, key=lambda f: abs(f["width"] - 1080))["link"]


def _commit_file(pid, fn):
    pj = ROOT / "projects" / pid / "project.json"
    p = json.loads(pj.read_text())
    fn(p)
    pj.write_text(json.dumps(p, ensure_ascii=False, indent=1))


# Mixkit (no key needed, free licence for commercial use, no watermark, no credit needed): used when there is no Pexels key.
# Its search works on short tags, so each slot carries `tags` (director._tags); results are ranked by how many words of the
# clip's title match what the phrase means.
MIXKIT = "https://mixkit.co/free-stock-video/discover/{}/"


def mixkit_search(tag):
    import re
    p = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "30", "-A", UA, MIXKIT.format(tag)], capture_output=True, text=True)
    if p.returncode != 0:
        return []
    out = []
    for slug, vid in re.findall(r'href="/free-stock-video/([a-z0-9-]+)-(\d+)/"', p.stdout):
        if (vid, slug) not in out:
            out.append((vid, slug))
    return out


def probe_remote(url):
    p = subprocess.run([str(ROOT / "bin" / "ffprobe"), "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", url],
                       capture_output=True, text=True, timeout=40)
    try:
        d = json.loads(p.stdout)
        st = next(x for x in d["streams"] if x.get("width"))
        return {"w": st["width"], "h": st["height"], "dur": float(d["format"]["duration"])}
    except Exception:
        return None


def _mixkit_pick(o, used, log):
    # 24 Nov 2026 (Alina: "the first one used irrelevant photos"): a clip goes in only when its title names the concrete
    # thing said in the phrase (apple, car, chocolate…). A phrase with nothing concrete keeps the speaker on screen.
    words = concrete_words(o.get("phrase", ""))
    if not words:
        log(f"{o['id']}: nothing concrete to show in “{o.get('phrase')}”: the speaker stays on screen")
        return None
    cands = []
    for tag in (sorted(words) + [t for t in (o.get("tags") or []) if t in words])[:4]:
        for rank, (vid, slug) in enumerate(mixkit_search(tag)[:24]):
            if vid in used or any(c[1] == vid for c in cands):
                continue
            hit = words & {_singular(x) for x in slug.split("-")}
            if not hit:
                continue                      # the title does not name the thing: never a loose match
            score = len(hit) * 2 - rank * .05 + (1 if "vertical" in slug else 0)
            cands.append((score, vid, slug))
        if len([c for c in cands if c[0] >= 2]) >= 3:
            break
    for score, vid, slug in sorted(cands, reverse=True)[:6]:
        for size in ("1080", "720"):
            url = f"https://assets.mixkit.co/videos/{vid}/{vid}-{size}.mp4"
            info = probe_remote(url)
            if info and info["dur"] >= float(o.get("hold", 2)) + .4:
                return vid, slug, url, info
    return None


def auto(pid, version_id=None, log=print, commit=None):
    """fill every empty example-clip slot of the version from Pexels. Returns {filled, missing, reason}."""
    key = pexels_key()
    pj = ROOT / "projects" / pid / "project.json"
    p = json.loads(pj.read_text())
    v = next(x for x in p["versions"] if x["id"] == (version_id or p["current"]))
    slots = [o for o in v.get("overlays", []) if o.get("kind") == "clip" and not o.get("image")]
    if not slots:
        return {"filled": 0, "missing": 0}
    used = {str(o.get("source", "")).split()[1] for x in p["versions"] for o in x.get("overlays", [])
            if str(o.get("source", "")).startswith(("Pexels ", "Mixkit "))}
    out_dir = ROOT / "projects" / pid / "clips"
    out_dir.mkdir(exist_ok=True)
    filled = 0
    for o in slots:
        hold = float(o.get("hold", 2))
        if not key:      # no Pexels key: Mixkit
            m = _mixkit_pick(o, used, log)
            if not m:
                log(f"{o['id']}: nothing on Mixkit for {o.get('tags')}")
                continue
            vid, slug, url, info = m
            raw = out_dir / f"mixkit_{vid}_raw.mp4"
            if not raw.exists():
                p2 = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "300", "-o", str(raw), url], capture_output=True, text=True)
                if p2.returncode != 0:
                    continue
            dst = out_dir / f"{o['id']}_mixkit{vid}.mp4"
            conform(raw, dst)
            used.add(vid)
            ms = round(min(1.0, max(0.0, info["dur"] - hold - .2)), 2)
            src = f"Mixkit {vid} “{slug.replace('-', ' ')}” (https://mixkit.co/free-stock-video/{slug}-{vid}/), Mixkit free licence"

            def put(p, oid=o["id"], dst=dst, ms=ms, src=src):
                for x in p["versions"]:
                    for oo in x.get("overlays", []):
                        if oo["id"] == oid and not oo.get("image"):
                            oo.update(image=str(dst), media_start=ms, status="proposed", source=src)
            (commit or (lambda fn: _commit_file(pid, fn)))(put)
            filled += 1
            log(f"{o['id']}: Mixkit {vid} {slug}")
            continue
        pick = None
        thing = concrete_words(o.get("phrase", ""))
        if not thing:
            log(f"{o['id']}: nothing concrete to show in “{o.get('phrase')}”: the speaker stays on screen")
            continue
        for q in sorted(thing) + [o.get("query", "")] + list(o.get("queries_more", [])):
            if not q:
                continue
            for vid in search(q, key):
                if str(vid["id"]) in used or float(vid.get("duration", 0)) < hold + 1.0:
                    continue
                if not thing & {_singular(x) for x in re.findall(r"[a-z]+", str(vid.get("url", "")).lower())}:
                    continue                  # its page title does not name the thing
                link = best_file(vid)
                if link:
                    pick = (vid, link, q)
                    break
            if pick:
                break
        if not pick:
            log(f"{o['id']}: nothing on Pexels for “{o.get('query')}”")
            continue
        vid, link, q = pick
        raw = out_dir / f"pexels_{vid['id']}_raw.mp4"
        if not raw.exists():
            p2 = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "120", "-o", str(raw), link], capture_output=True, text=True)
            if p2.returncode != 0:
                log(f"{o['id']}: download failed")
                continue
        dst = out_dir / f"{o['id']}_{vid['id']}.mp4"
        conform(raw, dst)
        used.add(str(vid["id"]))
        # start a little into the clip, where the action is, leaving room for the hold
        ms = round(min(1.0, max(0.0, float(vid.get("duration", 0)) - hold - .2)), 2)
        src = f"Pexels {vid['id']} by {vid.get('user', {}).get('name', '?')} ({vid.get('url', '')}), Pexels licence, found for “{q}”"

        def put(p, oid=o["id"], dst=dst, ms=ms, src=src):     # on the newest copy (the server commits it under its lock)
            for x in p["versions"]:
                for oo in x.get("overlays", []):
                    if oo["id"] == oid and not oo.get("image"):
                        oo.update(image=str(dst), media_start=ms, status="proposed", source=src)
        (commit or (lambda fn: _commit_file(pid, fn)))(put)
        filled += 1
        log(f"{o['id']}: Pexels {vid['id']} for “{q}”")
    return {"filled": filled, "missing": len(slots) - filled, "source": "Pexels" if key else "Mixkit"}


# ---------------------------------------------------------------- stock on your words (24 Nov 2026, all styles)
# Alina: "if I ever mention that I need to add stock images or videos, pick them up from Pexels (pexels.com/search/food
# delivery). When you analyse a video and hear words that could use a supporting photo as a pop-up image on screen, or an
# embedded video, integrate this feature in the engine." The engine finds the words that name something you can show,
# searches Pexels (photos + portrait videos) for each, and places the one she picks: a photo pop-up on the word (the
# image-on-word overlay) or an embedded clip (a full-frame cutaway, the voice goes on).
STOPW = set("""the a an and or but so to of in on at for with from by is are was were be been it its this that these those i
me my you your we our they them he she his her what when then just really very like gonna wanna yeah okay ok hey guys
one two more some any all much many have has had do does did not no yes can could would should will about out up down
there here now today time thing things stuff way""".split())
# words that name something you can show (FeedMe first: food, ordering, delivery, eating, everyday life)
SHOWABLE = set("""pizza burger burgers fries sushi pasta noodles ramen salad salads soup tacos taco kebab kapsalon sandwich
sandwiches chicken tenders wings steak rice curry dumplings bowl bowls breakfast lunch dinner brunch snack snacks dessert
cake cookies cookie icecream ice coffee tea latte smoothie juice drink drinks beer wine cocktail food foods meal meals
restaurant restaurants kitchen cooking cook chef fridge oven menu order ordering delivery deliver rider courier scooter bike
bag takeaway takeout groceries grocery supermarket market table plate fork spoon phone app screen laptop notification
money cash wallet card price euro euros bonus discount friends friend family party birthday date couple roommate
roommates student students study exam school university library office team work meeting boss desk home sofa couch bed
sleep tired hungry rain snow sun beach summer winter city street car train bus airport travel holiday vacation gym
workout run running dog cat dogs cats baby kids music dance shopping shirt tshirt merch clothes shoes""".split())
CONTEXT = {"order", "ordering", "delivery", "deliver", "rider", "courier", "app", "food", "foods", "meal", "meals", "hungry",
           "dinner", "lunch", "bag", "takeaway", "takeout", "menu", "restaurant", "restaurants"}


def _norm(w):
    import re
    return re.sub(r"[^a-z]", "", w.lower())


def suggest_words(project, version, limit=10):
    """kept words that name something showable, first time each, not already carrying a picture"""
    have = {o.get("word_i") for o in version.get("overlays", []) if o.get("status") != "removed"}
    out, seen = [], set()
    for w in project["edl"]["words"]:
        if w.get("cut") or w["i"] in have:
            continue
        n = _norm(w["text"])
        base = _singular(n)
        if (base in SHOWABLE or base in EXTRA_THINGS) and base not in GENERIC and base not in seen and base not in STOPW:
            seen.add(base)
            q = f"food delivery {base}" if base in CONTEXT else base
            out.append({"word_i": w["i"], "word": w["text"].strip(".,!?-"), "at": w["start"], "query": q})
        if len(out) >= limit:
            break
    return out


def search_photos(query, key, per_page=8):
    import urllib.parse
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": query, "orientation": "portrait", "per_page": per_page})
    pr = subprocess.run(["curl", "-sS", "--fail", "--max-time", "30", "-H", f"Authorization: {key}", url], capture_output=True, text=True)
    if pr.returncode != 0:
        raise RuntimeError(f"Pexels photo search failed ({pr.stderr.strip()[-200:]}): is the key right?")
    return json.loads(pr.stdout).get("photos", [])


def _photo_item(x):
    return {"kind": "photo", "id": x["id"], "thumb": x["src"].get("medium") or x["src"].get("small"), "src": x["src"].get("large2x") or x["src"].get("original"),
            "alt": x.get("alt", ""), "by": x.get("photographer", ""), "url": x.get("url", "")}


def _video_item(v):
    return {"kind": "video", "id": v["id"], "thumb": v.get("image"), "src": best_file(v), "duration": v.get("duration", 0),
            "by": (v.get("user") or {}).get("name", ""), "url": v.get("url", "")}


def find(project, version, query=None, per=4):
    """suggestions with Pexels results: [{word_i, word, at, query, items[]}] (a typed query searches just that)"""
    key = pexels_key()
    if not key:
        raise RuntimeError("Add your free Pexels key first (pexels.com/api → Your API key), then press Find stock again.")
    words = [{"word_i": None, "word": query, "at": None, "query": query}] if query else suggest_words(project, version)
    for s_ in words:
        items = []
        try:
            items += [_photo_item(x) for x in search_photos(s_["query"], key, per_page=per)]
            items += [_video_item(v) for v in search(s_["query"], key, per_page=per) if best_file(v)]
        except Exception as e:
            s_["error"] = str(e)[:200]
        s_["items"] = items
    return words


def place(pid, version_id, word_i, item, mode="popup"):
    """download the picked Pexels photo / video and put it on the word: photo → pop-up card, video → embedded clip"""
    pdir = ROOT / "projects" / pid
    pj = pdir / "project.json"
    p = json.loads(pj.read_text())
    w = p["edl"]["words"][int(word_i)]
    if item["kind"] == "photo":
        (pdir / "images").mkdir(exist_ok=True)
        dst = pdir / "images" / f"pexels_{item['id']}.jpg"
        if not dst.exists():
            pr = subprocess.run(["curl", "-sSL", "-A", UA, "--fail", "--max-time", "60", "-o", str(dst), item["src"]], capture_output=True, text=True)
            if pr.returncode != 0:
                raise RuntimeError("Pexels photo download failed: " + pr.stderr[-200:])
        # away from the face at that moment (a frame + Apple Vision), else the upper right
        x, y = "right", "upper"
        try:
            import preview
            _, boxes = preview.frame(pdir, p, w["start"])
            f = boxes.get("face")
            if f:
                cx, top, bottom = (f[0] + f[2] / 2) / 1080, f[1] / 1920, (f[1] + f[3]) / 1920
                x = "left" if cx > .5 else "right"
                y = "top" if top > .38 else ("middle" if bottom < .5 else "upper")
        except Exception:
            pass
        ov = {"id": "o" + str(item["id"])[-5:] + "p", "image": str(dst), "word_i": w["i"], "at": w["start"], "hold": 1.6,
              "x": x, "y": y, "tilt": -3, "scale": 0.42, "status": "kept", "by": "stock", "phrase": w["text"],
              "source": f"Pexels photo {item['id']} by {item.get('by', '')} ({item.get('url', '')}), Pexels licence", "why": f"stock photo on “{w['text']}”"}
    else:
        out_dir = pdir / "clips"
        out_dir.mkdir(exist_ok=True)
        raw = out_dir / f"pexels_{item['id']}_raw.mp4"
        if not raw.exists():
            try:
                download_pexels(item["id"], raw)
            except Exception:
                pr = subprocess.run(["curl", "-sSL", "-A", UA, "--fail", "-o", str(raw), item["src"]], capture_output=True, text=True)
                if pr.returncode != 0:
                    raise RuntimeError("Pexels video download failed: " + pr.stderr[-200:])
        dst = out_dir / f"stock_{item['id']}.mp4"
        if not dst.exists():
            conform(raw, dst)
        ov = {"id": "o" + str(item["id"])[-5:] + "v", "kind": "clip", "mode": "full", "image": str(dst), "word_i": w["i"], "at": w["start"],
              "hold": round(min(2.4, max(1.2, float(item.get("duration") or 2))), 2), "media_start": 0, "focus": .5, "status": "kept",
              "by": "stock", "phrase": w["text"], "source": f"Pexels video {item['id']} by {item.get('by', '')} ({item.get('url', '')}), Pexels licence",
              "why": f"stock clip on “{w['text']}”"}
    p = json.loads(pj.read_text())        # newest copy (the editor may have saved meanwhile)
    v = next(x for x in p["versions"] if x["id"] == version_id)
    v["overlays"] = [o for o in v.get("overlays", []) if o["id"] != ov["id"]] + [ov]
    pj.write_text(json.dumps(p, ensure_ascii=False, indent=1))
    return ov


if __name__ == "__main__":
    _main()


# ---------------------------------------------------------------- concrete things (24 Nov 2026)
EXTRA_THINGS = set("""apple apples banana bananas orange oranges strawberry strawberries fruit fruits vegetable vegetables
tomato tomatoes potato potatoes bread cheese egg eggs milk water chocolate candy sweets donut donuts croissant pancake pancakes
waffle waffles avocado lemon carrot onion garlic pepper honey sugar popcorn chips nachos hotdog car cars truck van motorcycle
plane house flat apartment garden tree trees flower flowers dog puppy kitten bird horse fish ocean sea mountain forest park
computer keyboard mouse camera headphones watch clock book books pen notebook backpack umbrella guitar piano ball football
basketball game console tv television shoe dress jacket hat glasses ring gift present box door window chair desk table""".split())
GENERIC = set("""photo photos picture video videos clip footage person people man woman girl boy guy family couple session
time good great nice place thing things stuff day night life world way hope work edit edited editing engine test testing
filming film camera""".split()) - {"camera"}


def _singular(w):
    return w[:-1] if w.endswith("s") and (w[:-1] in SHOWABLE or w[:-1] in EXTRA_THINGS) else w


def concrete_words(text):
    """the concrete things named in a phrase (things you can show), singular, never generic words like photo / video / time"""
    ws = {_singular(w) for w in re.findall(r"[a-z]+", str(text).lower())}
    return {w for w in ws if (w in SHOWABLE or w in EXTRA_THINGS) and w not in GENERIC and w not in STOPW}


# ---------------------------------------------------------------- object pop-ups (24 Nov 2026, every style)
# Alina: "when I say this (a photo of an apple, a chocolate bar and a car), all the versions should have a png pop up
# picture of the object I am mentioning". Every concrete object named gets a cut-out PNG popping up on its word, placed away
# from the face. Photos: Pexels only (her key); the background is removed on this Mac (HyperFrames remove-background).
def openverse_photo(query):
    import urllib.parse
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": query, "license": "cc0,by", "page_size": 12, "mature": "false"})
    pr = subprocess.run(["curl", "-sS", "--fail", "--max-time", "30", "-A", "vetto-video-engine/1.0", url], capture_output=True, text=True)
    if pr.returncode != 0:
        return []
    out = []
    for r in json.loads(pr.stdout).get("results", []):
        if (r.get("width") or 0) >= 500 and r.get("url"):
            out.append({"kind": "photo", "id": "ov" + r["id"][:8], "src": r["url"], "by": r.get("creator") or "", "url": r.get("foreign_landing_url") or "",
                        "licence": f"CC {str(r.get('license', '')).upper()} {r.get('license_version', '')}".strip(), "title": r.get("title", "")})
    return out


def object_photo(word):
    key = pexels_key()
    if key:
        for q in (f"{word} isolated white background", word):
            try:
                ph = search_photos(q, key, per_page=6)
            except Exception:
                ph = []
            if ph:
                it = _photo_item(ph[0]); it["licence"] = "Pexels licence"; return it
    return None     # Pexels only (Alina, 24 Nov 2026): without her key the built-in path skips; Edit now finds photos by id


def cutout_png(src_jpg, dst_png):
    hf = ROOT / "bin" / "hyperframes"
    pr = subprocess.run([str(hf), "remove-background", str(src_jpg), "-o", str(dst_png)], capture_output=True, text=True)
    if pr.returncode != 0 or not Path(dst_png).exists():
        raise RuntimeError("cut-out failed: " + (pr.stderr or pr.stdout)[-300:])
    return dst_png


def auto_objects(pid, version_id, log=print):
    """a cut-out PNG pop-up on every concrete object named (first time each), unless something is already on that word.
    Only for styles without stock pictures (Alina, 24 Nov 2026); stock styles show objects with their own photos / clips."""
    from claude_edit import STOCK_STYLES
    pdir = ROOT / "projects" / pid
    pj = pdir / "project.json"
    p = json.loads(pj.read_text())
    v = next(x for x in p["versions"] if x["id"] == version_id)
    if (v.get("style_id") or p.get("style_id")) in STOCK_STYLES:
        return {"placed": [], "skipped": "this style shows objects with its own stock photos / clips"}
    have = {o.get("word_i") for o in v.get("overlays", []) if o.get("status") != "removed"}
    done, seen = [], set()
    (pdir / "images").mkdir(exist_ok=True)
    words = [w for w in p["edl"]["words"] if not w.get("cut")]
    for k, w in enumerate(words):
        n = _singular(_norm(w["text"]))
        if not n or n in seen or n in GENERIC or not (n in SHOWABLE or n in EXTRA_THINGS) or w["i"] in have:
            continue
        # two-word objects ("chocolate bar"): search with the next word when it is a noun-ish word
        nxt = _norm(words[k + 1]["text"]) if k + 1 < len(words) else ""
        q = f"{n} {nxt}" if nxt in ("bar", "cake", "bowl", "box", "bottle", "cup", "slice", "bag") else n
        seen.add(n)
        it = object_photo(q)
        if not it:
            log(f"{q}: no photo found"); continue
        raw = pdir / "images" / f"obj_{n}.jpg"
        pr = subprocess.run(["curl", "-sSL", "-A", UA, "--fail", "--max-time", "60", "-o", str(raw), it["src"]], capture_output=True, text=True)
        if pr.returncode != 0:
            log(f"{q}: download failed"); continue
        png = pdir / "images" / f"obj_{n}.png"
        try:
            cutout_png(raw, png)
        except Exception as e:
            log(f"{q}: {e}"); continue
        raw.unlink(missing_ok=True)
        x, y = "right", "upper"
        try:
            import preview
            _, boxes = preview.frame(pdir, p, w["start"])
            f = boxes.get("face")
            if f:
                x = "left" if (f[0] + f[2] / 2) / 1080 > .5 else "right"
                y = "top" if f[1] / 1920 > .38 else ("middle" if (f[1] + f[3]) / 1920 < .5 else "upper")
        except Exception:
            pass
        done.append({"id": f"o{w['i']:03d}ob", "image": str(png), "cutout": True, "word_i": w["i"], "at": w["start"], "hold": 1.2,
                     "x": x, "y": y, "tilt": -4, "scale": 0.36, "status": "proposed", "by": "objects", "phrase": w["text"],
                     "source": f"{it.get('title') or q} by {it.get('by', '')} ({it.get('url', '')}), {it.get('licence', '')}", "why": f"cut-out of “{q}”, named here"})
        log(f"{q}: {png.name}")
    p = json.loads(pj.read_text())
    v = next(x for x in p["versions"] if x["id"] == version_id)
    ids = {d["id"] for d in done}
    v["overlays"] = [o for o in v.get("overlays", []) if o["id"] not in ids] + done
    pj.write_text(json.dumps(p, ensure_ascii=False, indent=1))
    return {"placed": [d["phrase"] for d in done]}
