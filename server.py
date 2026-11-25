"""Vetto Video Engine: local server for the editor (ui/) and the engine (engine/).

Run:  vetto-video-engine/.venv/bin/python vetto-video-engine/server.py   →  http://127.0.0.1:8770
Raw footage never leaves the Mac. Projects live in projects/<id>/project.json.
"""
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engine"))
import edit  # noqa: E402
import media  # noqa: E402
import render  # noqa: E402
import director  # noqa: E402
import claude_edit  # noqa: E402
import memes  # noqa: E402
import preview  # noqa: E402

PROJECTS = ROOT / "projects"
LIB = ROOT / "library"
UI = ROOT / "ui"
PLAN = ROOT / "plan"
PORT = int(os.environ.get("PORT") or os.environ.get("VETTO_PORT") or 8770)   # the app may hand over a free port in PORT
JOBS = {}
LOCK = threading.Lock()

STEPS = ["footage", "brief", "cut", "style", "hook", "effects", "text", "sound", "outputs", "storyboard", "export"]


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "project"


def pdir(pid):
    d = (PROJECTS / pid).resolve()
    if PROJECTS.resolve() not in d.parents:
        raise ValueError("bad project id")
    return d


def load(pid):
    return media.load_json(pdir(pid) / "project.json")


def save(pid, p, bump=False):
    # a save from an editor page bumps the revision, so a page holding an older copy cannot overwrite it (do_PUT).
    # Background jobs (transcribe, render, export) don't bump: their fields are merged in do_PUT instead.
    if bump:
        p["rev"] = int(p.get("rev") or 0) + 1
    p["updated"] = now()
    media.save_json(pdir(pid) / "project.json", p)
    return p


def new_version(name, style_id=None):
    return {
        "id": "v" + uuid.uuid4().hex[:6], "name": name, "style_id": style_id, "format_id": None,
        "text": {"font": "TikTok Sans", "color": "#FFFFFF", "highlight": "#FCDB1D", "outline": "#000000",
                 "box": "none", "size": 78, "position": "lower", "words_per_line": 3, "case": "as spoken",
                 "title_font": "TikTok Sans", "title_color": "#FFFFFF"},
        "hook": {"id": None, "text": "", "duration": 2.6, "variants": []},
        "effects": [], "overlays": [], "sfx": [], "captions": True,
        "outputs": {"reel": True, "stories": [], "carousel": {"slides": []}},
        "steps": {s: {"status": "open"} for s in STEPS},
        "renders": [],
    }


def new_project(name):
    pid = time.strftime("%Y%m%d-") + slug(name) + "-" + uuid.uuid4().hex[:4]
    d = PROJECTS / pid
    (d / "media").mkdir(parents=True)
    (d / "images").mkdir()
    (d / "renders").mkdir()
    p = {
        "id": pid, "name": name, "created": now(), "updated": now(),
        "account": None, "plan_unit": None,
        "brief": {"prompt": "", "polish": "Full", "pace": "Medium", "closing_word": "", "outputs": ["reel"], "language": "auto"},
        "source": None, "transcript": None, "edl": None,
        "versions": [new_version("Version 1")], "current": None,
        "requests": [], "log": [],
    }
    p["current"] = p["versions"][0]["id"]
    return save(pid, p)


# ------------------------------------------------------------------ jobs
def do_claude_edit(pid, vid, style, jid):
    """Edit now: Claude makes the whole edit in the Editing Beast style; the finished reel joins this version's renders"""
    p = load(pid)
    if style == "meme-chaos":     # the engine's own meme picks first, so Claude builds on them (25 Nov 2026)
        v = next(x for x in p["versions"] if x["id"] == vid)
        if not any(o.get("kind") == "meme" and o.get("status") != "removed" for o in v.get("overlays", [])):
            try:
                memes.auto(pid, vid, log=lambda m: None)
            except Exception:
                pass
            p = load(pid)
    res = claude_edit.run(pid, vid, style, pdir(pid), p, JOBS[jid])
    d = pdir(pid) / "renders"
    d.mkdir(exist_ok=True)
    name = Path(res["final"]).name
    shutil.copy(res["final"], d / name)
    dur = media.probe(d / name).get("duration", 0)
    with LOCK:
        p = load(pid)
        v = next(x for x in p["versions"] if x["id"] == vid)
        v["renders"].append({"file": "renders/" + name, "fmt": "reel", "preview": False, "claude": True, "style": style, "at": now(),
                             "duration": dur, "summary": res["summary"], "credits": res["credits"], "work": res["work"],
                             "effects_done": [], "effects_for_hyperframes": [], "effects_skipped": []})
        save(pid, p)
    return {"file": "renders/" + name, "summary": res["summary"]}


def job(kind, fn, *a):
    jid = uuid.uuid4().hex[:8]
    JOBS[jid] = {"id": jid, "kind": kind, "status": "running", "started": now(), "result": None, "error": None,
                 "args": [x for x in a if isinstance(x, str)]}

    def run():
        try:
            JOBS[jid]["result"] = fn(*a, jid) if kind == "claude-edit" else fn(*a)
            JOBS[jid]["status"] = "done"
        except Exception as e:  # surfaced to the UI as is
            JOBS[jid]["status"] = "error"
            JOBS[jid]["error"] = f"{e}\n{traceback.format_exc()[-1500:]}"
    threading.Thread(target=run, daemon=True).start()
    return JOBS[jid]


def lexicon_prep(pid, vid):
    """Cinema Lexicon, after the style edit (Alina, 18 Nov 2026): (1) the brand kit, only when she gave a link (the Style
    step's product link or a link in the brief) or attached a brand kit, then the edit again so the graphics use it;
    (2) the example clips, found on Pexels by the engine itself. What it could not do stays a request for Claude."""
    import brand as brandmod
    import stock
    out = {"brand": None, "brand_note": "", "clips_filled": 0, "clips_missing": 0, "reason": ""}
    p = load(pid)
    url = (p.get("brand_url") or "").strip() or brandmod.link_in((p.get("brief") or {}).get("prompt", ""))
    kit = brandmod.load(pid)
    files = brandmod.kit_files(attachments(pid))
    made = None
    if url and (not kit or kit.get("source") != url):
        made = brandmod.from_link(pid, url)
    elif files and not kit:
        made = brandmod.from_files(pid, files)
    if made:
        out["brand"], out["brand_note"] = made.get("name"), made.get("note", "")
        st = next((x for x in media.load_json(LIB / "styles.json", []) if x["id"] == "cinema-lexicon"), None)
        with LOCK:
            p = load(pid)
            v = next(x for x in p["versions"] if x["id"] == vid)
            if v.get("style_id") in (None, "cinema-lexicon") and st:
                director.direct(p, v, st, pdir(pid) / "renders" / "work")
                p["log"].append({"at": now(), "what": f"brand kit made from {url or 'your files'}: {made.get('name')}; Cinema Lexicon edit made again"})
                save(pid, p, bump=True)
    elif kit:
        out["brand"] = kit.get("name")

    def commit(fn):
        with LOCK:
            q = load(pid)
            fn(q)
            save(pid, q, bump=True)
    res = stock.auto(pid, vid, log=lambda m: None, commit=commit)
    out["clips_filled"], out["clips_missing"], out["reason"], out["clips_source"] = res.get("filled", 0), res.get("missing", 0), res.get("reason", ""), res.get("source", "")
    with LOCK:
        p = load(pid)
        v = next(x for x in p["versions"] if x["id"] == vid)
        left = [o for o in v.get("overlays", []) if o.get("kind") == "clip" and not o.get("image")]
        for r in p.get("requests", []):
            if r.get("kind") == "example-clips" and r.get("version") == vid and r.get("status") == "waiting for Claude" and not left:
                r["status"], r["reply"] = "done", f"the engine found all {out['clips_filled']} example clips on {out['clips_source']}"
        if v.get("style_edit"):
            v["style_edit"]["clips_missing"] = len(left)
            v["style_edit"]["brand"] = (brandmod.load(pid) or {}).get("name", "")
        save(pid, p, bump=True)
    return out


def ingest(pid, src_path):
    d = pdir(pid)
    info = media.probe(src_path)
    if not info["width"]:
        raise RuntimeError("This file has no video picture (a TikTok photo post or an audio file?). Use a video.")
    proxy = d / "media" / "proxy.mp4"
    media.proxy(src_path, proxy)
    thumbs = media.thumbnails(proxy, d / "media" / "thumbs", every_s=1.0)
    with LOCK:
        p = load(pid)
        p["source"] = dict(info, file=str(src_path), proxy="media/proxy.mp4", thumbs=["media/thumbs/" + t for t in thumbs])
        p["log"].append({"at": now(), "what": f"footage added: {Path(src_path).name} ({info['duration']:.1f} s)"})
        save(pid, p)
    return p["source"]


def analyze(pid):
    d = pdir(pid)
    p = load(pid)
    import transcribe
    wav = d / "media" / "audio16k.wav"
    media.extract_audio(p["source"]["file"], wav)
    tr = transcribe.transcribe(wav, p["brief"].get("language", "auto"))
    pace = {x["name"]: x for x in media.load_json(LIB / "pacing.json", [])}.get(p["brief"].get("pace", "Medium"), {})
    edl = edit.propose(tr, p["source"]["duration"], pace)
    edit.refine_edges(edl["words"], wav)
    with LOCK:
        p = load(pid)
        p["transcript"] = {"language": tr["language"], "text": tr["text"], "score": tr["score"]}
        p["edl"] = edl
        match_images(p)
        p["log"].append({"at": now(), "what": f"transcribed ({tr['language']}), {len(tr['words'])} words; cuts proposed"})
        save(pid, p)
    return edit.stats(edl, p["source"]["duration"])


def match_images(p):
    """Images whose file name is a spoken word go on that word (proposal)."""
    d = pdir(p["id"]) / "images"
    imgs = {re.sub(r"[^a-z0-9ăâîșțşţ]+", "", f.stem.lower()): f for f in d.glob("*") if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")}
    if not imgs or not p.get("edl"):
        return
    v = cur(p)
    have = {o["image"] for o in v["overlays"]}
    for w in p["edl"]["words"]:
        k = re.sub(r"[^a-z0-9ăâîșțşţ]+", "", w["text"].lower())
        f = imgs.get(k) or imgs.get(k.rstrip("s"))
        if f and str(f) not in have and not w["cut"]:
            v["overlays"].append({"id": "o" + uuid.uuid4().hex[:5], "word_i": w["i"], "at": w["start"], "image": str(f),
                                  "hold": 1.6, "x": "right", "y": "upper", "tilt": -3, "scale": 0.42,
                                  "status": "proposed", "why": f"file name matches the word “{w['text']}”"})
            have.add(str(f))


def cur(p):
    return next(v for v in p["versions"] if v["id"] == p["current"])


def attachments(pid):
    """files Alina attached in the chat bar, oldest first (the last one is the default background)"""
    d = pdir(pid) / "attachments"
    return sorted((f for f in d.glob("*") if f.is_file() and not f.name.startswith(".")), key=lambda f: f.stat().st_mtime) if d.exists() else []


def do_render(pid, vid, fmt, preview, quick=False):
    p = load(pid)
    v = next(x for x in p["versions"] if x["id"] == vid)
    bank = sorted(str(f) for f in (pdir(pid) / "images").glob("*") if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    proj = dict(v, source=p["source"], edl=p["edl"], focus_x=p.get("focus_x"), _images=bank,
                _attachments=[str(f) for f in attachments(pid)],
                _brand=str(pdir(pid) / "brand") if (pdir(pid) / "brand" / "brand.json").exists() else None)
    d = pdir(pid) / "renders"
    name = f"{slug(v['name'])}-{fmt}{'-preview' if preview else ''}-{time.strftime('%H%M%S')}.mp4"
    res = render.render(proj, p["source"]["file"], str(d / name), fmt=fmt, work_dir=d / "work", preview=preview)
    with LOCK:
        p = load(pid)
        v = next(x for x in p["versions"] if x["id"] == vid)
        v["renders"].append({"file": "renders/" + name, "fmt": fmt, "preview": preview, "quick": quick, "at": now(), "duration": res["duration"],
                             "effects_done": res["effects_done"], "effects_for_hyperframes": res["effects_for_hyperframes"],
                             "effects_skipped": res["effects_skipped"]})
        save(pid, p)
    return {"file": "renders/" + name, "duration": res["duration"]}


def do_carousel(pid, vid):
    p = load(pid)
    v = next(x for x in p["versions"] if x["id"] == vid)
    out = pdir(pid) / "renders" / f"carousel-{slug(v['name'])}"
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for i, s in enumerate(v["outputs"]["carousel"]["slides"]):
        f = out / f"frame_{i + 1:02d}.jpg"
        render.still(p["source"]["file"], float(s.get("t", 0)), str(f))
        files.append(f"renders/{out.name}/{f.name}")
    return {"frames": files}


# ------------------------------------------------------------------ http
class H(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def _file(self, path):
        path = Path(path)
        if not path.is_file():
            return self._json({"error": "not found"}, 404)
        size = path.stat().st_size
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m:
                if m[1]:
                    start = int(m[1])
                    end = int(m[2]) if m[2] else size - 1
                else:
                    start = size - int(m[2])
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def do_GET(self):
        u = urlparse(self.path)
        parts = [unquote(x) for x in u.path.strip("/").split("/") if x]
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if not parts:
                return self._file(UI / "index.html")
            if parts[:2] == ["static", "fonts"]:          # Vetto's fonts.css paths
                return self._file(LIB / "fonts" / Path(parts[2]).name)
            if parts[:3] == ["static", "brand", "art"]:   # Vetto's theme.css art
                return self._file(UI / "vetto" / "art" / Path(parts[3]).name)
            if parts[0] == "ui":
                return self._file(UI.joinpath(*parts[1:]))
            if parts[0] == "memelib":                      # her Pinterest meme library (engine/memes.py)
                base = memes.lib_root().resolve()
                f = base.joinpath(*parts[1:]).resolve()
                if base not in f.parents:
                    return self._json({"error": "bad path"}, 400)
                return self._file(f)
            if parts[0] == "lib":
                f = LIB.joinpath(*parts[1:]).resolve()
                if LIB.resolve() not in f.parents:
                    return self._json({"error": "bad path"}, 400)
                return self._file(f)
            if parts[0] == "files":
                f = pdir(parts[1]).joinpath(*parts[2:]).resolve()
                if pdir(parts[1]) not in f.parents:
                    return self._json({"error": "bad path"}, 400)
                return self._file(f)
            if parts[:3] == ["prev", "a", "fx"]:           # keyed meme clip frames (engine/hf/fx/memes/<name>/fNNN.webp)
                base = (ROOT / "engine" / "hf" / "fx").resolve()
                f = base.joinpath(*parts[3:]).resolve()
                if base not in f.parents:
                    return self._json({"error": "bad path"}, 400)
                return self._file(f)
            if parts[:2] == ["prev", "a"]:                 # shared template files and fonts for the effect previews
                name = Path(parts[2]).name
                f = ROOT / "engine" / "hf" / name
                return self._file(f if f.exists() else LIB / "fonts" / name)
            if parts[0] == "prev" and len(parts) == 5 and parts[2] == "f":   # the moment's frame / cutout
                p = load(parts[1])
                t = float(parts[3])
                f = preview.cutout(pdir(parts[1]), p, t) if parts[4] == "cut.png" else preview.frame(pdir(parts[1]), p, t)[0]
                return self._file(f)
            if parts[0] == "prev" and len(parts) == 3:     # one effect box: /prev/<pid>/<effect>?t=&text=&ws=&params=
                q = parse_qs(u.query)
                g = lambda k, d="": (q.get(k) or [d])[0]
                p = load(parts[1])
                if not (p.get("source") or {}).get("proxy"):
                    return self._json({"error": "no footage yet"}, 404)
                imgs = [f"/files/{parts[1]}/images/{f.name}" for f in sorted((pdir(parts[1]) / "images").glob("*"))
                        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
                html = preview.page(pdir(parts[1]), p, parts[1], parts[2], float(g("t", "0") or 0), g("text"),
                                    json.loads(g("ws", "[]")), json.loads(g("params", "{}")), imgs, attachments(parts[1]))
                if html is None:
                    return self._json({"error": "no template"}, 404)
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parts[:2] == ["api", "library"]:
                lib = {k: media.load_json(LIB / f"{k}.json", []) for k in ("styles", "effects", "hooks", "formats", "sfx", "looks", "outputs", "pacing", "music")}
                return self._json(lib)
            if parts[:2] == ["api", "plan"]:
                return self._json(media.load_json(PLAN / "units.json", {"units": [], "note": "no Vetto plan synced yet"}))
            if parts[:2] == ["api", "projects"] and len(parts) == 2:
                out = []
                for f in sorted(PROJECTS.glob("*/project.json"), reverse=True):
                    p = json.loads(f.read_text())
                    out.append({"id": p["id"], "name": p["name"], "updated": p["updated"], "account": p.get("account"),
                                "versions": len(p["versions"]), "has_source": bool(p.get("source"))})
                return self._json(out)
            if parts[:2] == ["api", "projects"] and len(parts) == 3:
                return self._json(load(parts[2]))
            if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "images":
                d = pdir(parts[2]) / "images"
                return self._json([{"name": f.name, "path": str(f), "url": f"/files/{parts[2]}/images/{f.name}"}
                                   for f in sorted(d.glob("*")) if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")])
            if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "attachments":
                return self._json([{"name": f.name, "url": f"/files/{parts[2]}/attachments/{f.name}"} for f in attachments(parts[2])])
            if parts == ["api", "settings"]:
                import stock
                return self._json({"pexels": bool(stock.pexels_key()), "giphy": bool(memes.giphy_key())})
            if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "memes":     # meme moments + candidates
                return self._json({"moments": memes.moments(load(parts[2])), "giphy": bool(memes.giphy_key())})
            if parts == ["api", "memes", "library"]:            # her Pinterest library: categories, folders, pictures in one
                if q.get("folder"):
                    return self._json({"items": memes.folder_items(q["folder"])})
                if q.get("q"):
                    return self._json(memes.search(q["q"], int(q.get("offset") or 0)))
                return self._json({"cats": [{"id": c["id"], "name": c["name"]} for c in memes.CAT.values()],
                                   "folders": memes.FOLDERS + ["Din engine"], "giphy": bool(memes.giphy_key())})
            if parts[:2] == ["api", "claude"]:
                return self._json({k: v for k, v in claude_edit.status().items() if k != "binary"})
            if parts[:2] == ["api", "jobs"] and len(parts) == 2:     # running jobs (the editor finds an Edit now after a reload)
                return self._json([dict((k, v) for k, v in j.items() if k not in ("result",)) for j in JOBS.values() if j["status"] == "running"])
            if parts[:2] == ["api", "jobs"]:
                return self._json(JOBS.get(parts[2], {"status": "unknown"}))
            return self._json({"error": "not found"}, 404)
        except Exception as e:
            return self._json({"error": str(e)}, 500)

    def do_PUT(self):
        parts = [x for x in urlparse(self.path).path.strip("/").split("/") if x]
        if parts[:2] == ["api", "projects"] and len(parts) == 3:
            p = json.loads(self._body())
            with LOCK:
                old = load(parts[2]) or {}
                if int(p.get("rev") or 0) < int(old.get("rev") or 0):
                    # this page's copy is older than what is saved (another tab or a finished job changed it)
                    return self._json({"error": "stale", "project": old}, 409)
                # background jobs write source / transcript / renders: never let an older page copy erase them
                for k in ("source", "transcript", "edl"):
                    if not p.get(k) and old.get(k):
                        p[k] = old[k]
                if old.get("edl") and p.get("edl") and len(old["edl"]["words"]) != len(p["edl"]["words"]):
                    p["edl"] = old["edl"]          # a fresh transcript wins over a stale page
                oldv = {v["id"]: v for v in old.get("versions", [])}
                pd = pdir(parts[2])
                for v in p.get("versions", []):
                    have = {r["file"] for r in v.get("renders", [])}
                    v["renders"] = v.get("renders", []) + [r for r in oldv.get(v["id"], {}).get("renders", []) if r["file"] not in have]
                    v["renders"] = [r for r in v["renders"] if (pd / r["file"]).exists()]   # deleted renders stay deleted
                ids = {r["id"] for r in p.get("requests", [])}
                p["requests"] = p.get("requests", []) + [r for r in old.get("requests", []) if r["id"] not in ids]
                return self._json(save(parts[2], p, bump=True))
        return self._json({"error": "not found"}, 404)

    def do_POST(self):
        u = urlparse(self.path)
        parts = [unquote(x) for x in u.path.strip("/").split("/") if x]
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if parts == ["api", "settings"]:   # {"pexels_key": "..."}: kept in .secrets.json, never sent back
                import stock
                body = json.loads(self._body() or b"{}")
                if body.get("giphy_key"):
                    memes.save_giphy_key(body["giphy_key"].strip())
                    return self._json({"pexels": bool(stock.pexels_key()), "giphy": True})
                if body.get("pexels_key"):
                    key = body["pexels_key"].strip()
                    stock.search("food", key, per_page=1)       # raises when the key is wrong
                    stock.save_key(key)
                return self._json({"pexels": bool(stock.pexels_key()), "giphy": bool(memes.giphy_key())})
            if parts == ["api", "memes", "pin"]:            # {"url"}: a Pinterest pin link -> her library ("Din engine")
                body = json.loads(self._body() or b"{}")
                return self._json({"item": memes.import_pin(body.get("url", ""))})
            if parts == ["api", "projects"]:
                body = json.loads(self._body() or b"{}")
                return self._json(new_project(body.get("name") or "Untitled"))
            pid = parts[2]
            action = parts[3] if len(parts) > 3 else ""
            d = pdir(pid)
            if action == "upload":           # raw file body, ?name=clip.mov&kind=footage|image
                name = Path(q.get("name", "clip.mov")).name
                kind = q.get("kind", "footage")
                folder = {"footage": "media", "attachment": "attachments"}.get(kind, "images")
                (d / folder).mkdir(exist_ok=True)
                dest = d / folder / name
                with open(dest, "wb") as f:
                    left = int(self.headers.get("Content-Length", 0))
                    while left > 0:
                        chunk = self.rfile.read(min(1 << 20, left))
                        if not chunk:
                            break
                        f.write(chunk)
                        left -= len(chunk)
                if kind == "footage":
                    return self._json(job("ingest", ingest, pid, str(dest)))
                if kind == "attachment":     # a file sent to Claude from the chat bar (backgrounds, clips, logos…)
                    return self._json({"attachment": name, "url": f"/files/{pid}/attachments/{name}"})
                with LOCK:
                    p = load(pid)
                    match_images(p)
                    save(pid, p)
                return self._json({"image": str(dest)})
            if action == "import":           # {"path": "/Users/.../clip.mov"} — a file already on this Mac
                body = json.loads(self._body())
                src = Path(os.path.expanduser(body["path"]))
                if not src.is_file():
                    return self._json({"error": f"no file at {src}"}, 400)
                dest = d / "media" / src.name
                shutil.copy2(src, dest)
                return self._json(job("ingest", ingest, pid, str(dest)))
            if action == "pull":             # {"url": "..."} — your own reel via yt-dlp (bin/yt-dlp, 2026.10.26)
                body = json.loads(self._body())
                ytdlp = ROOT / "bin" / "yt-dlp"
                if not ytdlp.exists():
                    return self._json({"error": "yt-dlp is not installed in the engine"}, 400)

                def pull(url):
                    out = d / "media" / "pulled-%(id)s.%(ext)s"
                    r = subprocess.run([str(ytdlp), "--no-playlist", "--ffmpeg-location", media.ffmpeg_bin(),
                                        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b", "--merge-output-format", "mp4",
                                        "--print", "after_move:filepath", "-o", str(out), url],
                                       capture_output=True, text=True)
                    if r.returncode != 0:
                        raise RuntimeError("yt-dlp: " + (r.stderr.strip().splitlines() or ["failed"])[-1])
                    return ingest(pid, r.stdout.strip().splitlines()[-1])
                return self._json(job("pull", pull, body["url"]))
            if action == "analyze":
                return self._json(job("analyze", analyze, pid))
            if action == "render":
                body = json.loads(self._body() or b"{}")
                return self._json(job("render", do_render, pid, body["version"], body.get("fmt", "reel"), bool(body.get("preview")), bool(body.get("quick"))))
            if action == "carousel":
                body = json.loads(self._body() or b"{}")
                return self._json(job("carousel", do_carousel, pid, body["version"]))
            if action == "stock-find":       # {"version", "query"?}: words worth a picture + Pexels photos/videos for each
                import stock
                body = json.loads(self._body())
                p = load(pid)
                if not p.get("edl"):
                    return self._json({"error": "Transcribe first: stock is matched to your words."}, 400)
                v = next(x for x in p["versions"] if x["id"] == body["version"])
                try:
                    return self._json({"words": stock.find(p, v, (body.get("query") or "").strip() or None)})
                except RuntimeError as e:
                    return self._json({"error": str(e), "needs_key": not stock.pexels_key()}, 400)
            if action == "objects":          # {"version"}: a cut-out PNG pop-up on every object named
                import stock
                body = json.loads(self._body())
                return self._json(job("objects", lambda: stock.auto_objects(pid, body["version"], log=lambda m: None)))
            if action == "memes-place":      # {"version", "item", "at", "word_i", "phrase", "hold"}: a meme on a phrase
                body = json.loads(self._body())
                with LOCK:
                    r = memes.place(pid, body["version"], body["item"], float(body["at"]), body.get("word_i"),
                                    body.get("phrase", ""), float(body.get("hold") or 1.6))
                return self._json(r)
            if action == "stock-place":      # {"version", "word_i", "item"}: download it and put it on the word
                import stock
                body = json.loads(self._body())
                return self._json(job("stock", lambda: stock.place(pid, body["version"], body["word_i"], body["item"])))
            if action == "claude-edit":      # {"version", "style"}: Edit now (engine/claude_edit.py)
                body = json.loads(self._body())
                st = claude_edit.status()
                if not st["ready"]:
                    return self._json({"error": st["reason"], "login": True}, 409)
                running = [j for j in JOBS.values() if j["kind"] == "claude-edit" and j["status"] == "running" and pid in j.get("args", [])]
                if running:
                    return self._json(running[0])
                return self._json(job("claude-edit", do_claude_edit, pid, body["version"], body["style"]))
            if action == "claude-stop":       # stop a running Edit now
                for j in JOBS.values():
                    if j["kind"] == "claude-edit" and j["status"] == "running" and pid in j.get("args", []) and j.get("pid_proc"):
                        try:
                            os.kill(j["pid_proc"], 15)
                        except Exception:
                            pass
                return self._json({"ok": True})
            if action == "style-edit":       # {"version", "style"}: the style's whole edit (engine/director.py), as proposals
                body = json.loads(self._body())
                st = next((x for x in media.load_json(LIB / "styles.json", []) if x["id"] == body["style"]), None)
                with LOCK:
                    p = load(pid)
                    if not p.get("edl") or not p.get("source"):
                        return self._json({"error": "Transcribe first: the style edit is placed on your words."}, 400)
                    v = next(x for x in p["versions"] if x["id"] == body["version"])
                    summary = director.direct(p, v, st, d / "renders" / "work") if st else None
                    if summary is not None:
                        save(pid, p, bump=True)
                prep = job("lexicon-prep", lexicon_prep, pid, v["id"]) if st and st["id"] == "cinema-lexicon" else None
                # Meme Chaos (25 Nov 2026): memes and GIFs go on the video by themselves (engine/memes.py auto)
                mj = job("memes-auto", lambda: memes.auto(pid, v["id"], log=lambda m: None)) if body["style"] == "meme-chaos" else None
                return self._json({"summary": summary, "project": p, "prep_job": prep, "meme_job": mj})
            if action == "brand":            # {"version", "url"}: the product link for the brand kit (Cinema Lexicon)
                body = json.loads(self._body())
                with LOCK:
                    p = load(pid)
                    p["brand_url"] = (body.get("url") or "").strip()
                    save(pid, p, bump=True)
                return self._json(job("lexicon-prep", lexicon_prep, pid, body["version"]))
            if action == "delete-project":   # the whole project folder goes to the macOS Trash (recoverable there)
                if any(j["status"] == "running" and pid in j.get("args", []) for j in JOBS.values()):
                    return self._json({"error": "This video is still being worked on (transcribing or rendering). Try again when it finishes."}, 409)
                if not (d / "project.json").exists():
                    return self._json({"error": "no such project"}, 404)
                trash = Path.home() / ".Trash"
                dest, k = trash / f"vetto-video-{pid}", 1
                while dest.exists():
                    dest, k = trash / f"vetto-video-{pid}-{k}", k + 1
                with LOCK:
                    shutil.move(str(d), str(dest))
                return self._json({"ok": True, "trash": str(dest)})
            if action == "delete-render":    # {"version": id, "file": "renders/x.mp4"}: the file goes to the macOS Trash
                body = json.loads(self._body())
                f = (d / body["file"]).resolve()
                if (d / "renders").resolve() not in f.parents or f.suffix.lower() not in (".mp4", ".mov"):
                    return self._json({"error": "not a render of this project"}, 400)
                if f.exists():
                    trash = Path.home() / ".Trash"
                    dest = trash / f"{pid}-{f.name}"
                    k = 1
                    while dest.exists():
                        dest = trash / f"{pid}-{f.stem}-{k}{f.suffix}"
                        k += 1
                    shutil.move(str(f), str(dest))
                with LOCK:
                    p = load(pid)
                    for v in p["versions"]:
                        if v["id"] == body.get("version") or not body.get("version"):
                            v["renders"] = [r for r in v["renders"] if r["file"] != body["file"]]
                    p["log"].append({"at": now(), "what": f"render deleted (moved to the Trash): {body['file']}"})
                    save(pid, p)
                return self._json(p)
            if action == "export-nle":       # {"version": id}: Premiere/Resolve XML, EDL and SRT of the approved cut
                body = json.loads(self._body() or b"{}")
                import export_nle
                p = load(pid)
                v = next(x for x in p["versions"] if x["id"] == body["version"])
                ranges = edit.keep_ranges(p["edl"], p["source"]["duration"])
                files = export_nle.export(p, v, ranges, d / "renders" / f"nle-{slug(v['name'])}")
                rel = {k: str(Path(f).relative_to(d)) for k, f in files.items()}
                with LOCK:
                    p = load(pid)
                    v = next(x for x in p["versions"] if x["id"] == body["version"])
                    v["nle"] = {"at": now(), "files": rel}
                    save(pid, p)
                return self._json({"files": rel})
            if action == "request":          # a typed change for Claude: saved in the project, Claude applies it
                body = json.loads(self._body())
                with LOCK:
                    p = load(pid)
                    p["requests"].append({"id": uuid.uuid4().hex[:6], "at": now(), "text": body["text"],
                                          "step": body.get("step"), "version": body.get("version"), "kind": body.get("kind"), "status": "waiting for Claude",
                                          "files": [f"attachments/{Path(x).name}" for x in body.get("files", [])]})
                    save(pid, p)
                return self._json(p["requests"][-1])
            return self._json({"error": "unknown action"}, 404)
        except Exception as e:
            return self._json({"error": str(e), "trace": traceback.format_exc()[-1200:]}, 500)


if __name__ == "__main__":
    PROJECTS.mkdir(exist_ok=True)
    PLAN.mkdir(exist_ok=True)
    print(f"Vetto Video Engine on http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
