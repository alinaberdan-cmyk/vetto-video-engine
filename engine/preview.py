"""Live effect previews for the editor's Effects step (17 Nov 2026).

Each effect box plays the effect's own template (engine/hf/<id>.html, or engine/hf/preview/<id>.html for the ffmpeg
effects) on one still frame of the take at the selected words, with those words as the text. Per moment the engine
makes, once: the frame (9:16, like the export's crop), the face and hand boxes (bin/vision), and, only when an
effect needs it, a still person cutout (bin/hyperframes remove-background). Nothing leaves the Mac.
"""
import json
import subprocess
import threading
from pathlib import Path

import hfx
from media import run

_GL = threading.Lock()
_LOCKS = {}


def _lock(key):
    with _GL:
        return _LOCKS.setdefault(key, threading.Lock())


def moment_dir(pdir, t):
    key = f"{max(0.0, float(t)):.1f}"
    return Path(pdir) / "media" / "fxprev" / key, key


def frame(pdir, project, t):
    """The still frame at t (540x960, cropped to 9:16 around focus_x) and its face/hand boxes in 1080x1920 pixels."""
    d, _ = moment_dir(pdir, t)
    f, bj = d / "frame.jpg", d / "boxes.json"
    with _lock(str(f)):
        if not f.exists():
            d.mkdir(parents=True, exist_ok=True)
            src = Path(pdir) / project["source"]["proxy"]
            fx = project.get("focus_x")
            fx = 0.5 if fx is None else float(fx)
            vf = (f"crop=w='min(iw,ih*9/16)':h='min(ih,iw*16/9)':x='max(0,min(iw-ow,{fx}*iw-ow/2))':y='(ih-oh)/2',"
                  "scale=540:960,setsar=1")
            run(["-ss", f"{max(0.0, float(t) + 0.15):.2f}", "-i", src, "-frames:v", "1", "-vf", vf, "-q:v", "3", f])
        if not bj.exists():
            found = (hfx.vision([f]) or [{}])[0]
            px = lambda b: [round(b[0] * 1080), round(b[1] * 1920), round(b[2] * 1080), round(b[3] * 1920)]
            faces = sorted(found.get("faces", []), key=lambda b: -b[2] * b[3])
            bj.write_text(json.dumps({"face": px(faces[0]) if faces else None, "faces": [px(b) for b in faces],
                                      "hands": [px(h) for h in found.get("hands", [])]}))
    return f, json.loads(bj.read_text())


def cutout(pdir, project, t):
    """Still person cutout (PNG with alpha) of the frame at t; made once, a few seconds the first time."""
    f, _ = frame(pdir, project, t)
    out = f.parent / "cut.png"
    with _lock(str(out)):
        if not out.exists():
            p = subprocess.run([str(hfx.HF), "remove-background", str(f), "-o", str(out)], capture_output=True, text=True)
            if p.returncode != 0 or not out.exists():
                raise RuntimeError("cutout failed: " + (p.stderr or p.stdout)[-600:])
    return out


def bg_preview(pdir, pid, attachments, params):
    """the background a Green-screen background preview shows: the attached photo, or a frame of the attached video"""
    a = hfx.pick_attachment(params, attachments)
    if not a:
        return None
    if a.suffix.lower() not in hfx.VIDEO_EXT:
        return f"/files/{pid}/attachments/{a.name}"
    th = Path(pdir) / "attachments" / ".thumbs" / (a.stem + ".jpg")
    with _lock(str(th)):
        if not th.exists():
            th.parent.mkdir(parents=True, exist_ok=True)
            run(["-ss", "0.5", "-i", a, "-frames:v", "1", "-vf", "scale=540:-2", "-q:v", "3", th])
    return f"/files/{pid}/attachments/.thumbs/{th.name}"


def page(pdir, project, pid, effect, t, text, words, params, images, attachments=None):
    import brand as brandmod
    """The preview page for one effect box."""
    if not hfx.template_path(effect):
        return None
    _, boxes = frame(pdir, project, t)
    face = boxes["face"] or [324, 346, 432, 422]
    key = moment_dir(pdir, t)[1]
    need = hfx.NEEDS.get(effect, {"cutout"} if effect == "text-behind-me" else set())
    base = f"/prev/{pid}/f/{key}/"
    V = {"W": 1080, "H": 1920, "D": 3.0, "word": text, "params": params or {}, "words": words or [],
         "images": images, "face": face,
         "track": [{"t": k * .5, "face": face, "faces": boxes.get("faces") or [face], "hands": boxes["hands"]} for k in range(6)],
         "cutout": "cutout" in need, "frame": base + "frame.jpg", "cut": base + "cut.png", "preview": True,
         # meme clips play from /prev/a/fx/…; a still frame has no sound, so the clap pulse previews 5 claps
         "memes": hfx.meme_meta(effect, params), "onsets": [.25, .45, .65, .85, 1.05] if "onsets" in need else [],
         "bg_preview": bg_preview(pdir, pid, attachments, params) if "background" in need else None,
         "brand": brandmod.for_template(brandmod.load(pid), f"/files/{pid}/brand/")}
    try:
        hfx._check(effect, params or {}, images, attachments, preview=True, brand=V["brand"]) if effect in hfx.NEEDS else None
    except hfx.NeedsInput as why:
        return (f'<!doctype html><html><body style="margin:0;width:1080px;height:1920px;background:#000 url({V["frame"]}) center/cover;'
                f'font:600 64px/1.3 -apple-system,sans-serif;color:#fff;display:flex;align-items:center;justify-content:center;'
                f'text-align:center"><div style="background:rgba(0,0,0,.6);padding:60px;margin:80px;border-radius:40px">'
                f'{str(why)}</div></body></html>')
    return hfx.build_html(effect, V, assets="/prev/a/", preview=True)
