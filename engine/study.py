"""Study a reference video: measure how it is edited, before teaching the engine a style from it (18 Nov 2026).

    vetto-video-engine/.venv/bin/python vetto-video-engine/engine/study.py <video> [<video> ...] [--out DIR]

For each video it writes `<out>/<name>/` (default `research/studies/<name>/`):
  - study.json    every measurement
  - STUDY.md      the same in plain words: pace, punch-ins, flashes, grade, colours, music and beat sync, loudness,
                  possible sound hits; the numbers to copy into a style entry (pace, punch_in, lufs)
  - storyboard.jpg  one still per shot with its time, to look at before writing the style

The idea comes from JuneYaooo/rea-video (Apache-2.0, research/repos/rea-video): measure first, back every claim with a
number, and say what is only a guess. Our own code, local only: ffmpeg + numpy + Pillow, nothing leaves the Mac.
It does not read captions or fonts (no OCR here): look at the storyboard for those (StyleLab's frame breakdowns).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rhythm  # noqa: E402
from media import ffmpeg_bin, probe, sdr_vf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LW, LH = 90, 160            # low-res analysis frames (9:16); landscape videos are squeezed, which is fine for diffs


def _lowres(path, fps):
    """every frame as a small grey image + its mean RGB (n x LH x LW, n x 3)"""
    cmd = [ffmpeg_bin(), "-hide_banner", "-v", "error", "-i", str(path), "-vf",
           f"{sdr_vf(str(path))}scale={LW}:{LH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (LW * LH * 3)
    rgb = np.frombuffer(raw[:n * LW * LH * 3], np.uint8).reshape(n, LH, LW, 3).astype(np.float32)
    grey = rgb[..., 0] * .299 + rgb[..., 1] * .587 + rgb[..., 2] * .114
    return grey, rgb.mean(axis=(1, 2))


def _cuts(grey, fps):
    """hard cuts: frames whose difference from the previous one is far above the local norm"""
    if len(grey) < 3:
        return []
    d = np.abs(np.diff(grey, axis=0)).mean(axis=(1, 2))            # d[k] = change from frame k to k+1
    cuts, last = [], -10
    for k in range(len(d)):
        loc = np.median(d[max(0, k - int(fps)):k + int(fps) + 1])
        if d[k] > max(14.0, 3.5 * loc) and k - last >= max(2, int(fps * .2)):
            cuts.append(k + 1)
            last = k
    return cuts


def _pool(x):
    """2x2 average: a softer picture, so a head that moved a little between takes still matches"""
    h, w = x.shape[0] // 2 * 2, x.shape[1] // 2 * 2
    return x[:h, :w].reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))


def _zoom(a, b):
    """is frame b the same picture as a, scaled up (or down)? returns (scale, error ratio) or None.
    Tries crops of 1.05-1.40 around a grid of centres (a punch-in is centred on the face, not the frame), on softened
    frames; it counts when the best zoom explains the change at least 40 % better than "nothing moved"."""
    a, b = _pool(a), _pool(b)
    H, W = a.shape
    base = np.abs(a - b).mean()
    if base < 4:
        return None
    best = (None, base)
    for big, small, sign in ((a, b, 1), (b, a, -1)):              # punch in (b is a zoomed) or out (a is b zoomed)
        for s in (1.05, 1.08, 1.1, 1.12, 1.15, 1.2, 1.25, 1.3, 1.4):
            h, w = int(round(H / s)), int(round(W / s))
            yi = (np.arange(H) * h / H).astype(int)
            xi = (np.arange(W) * w / W).astype(int)
            for cy in (.3, .4, .5, .6, .7):
                for cx in (.4, .5, .6):
                    y0 = int(min(H - h, max(0, cy * H - h / 2)))
                    x0 = int(min(W - w, max(0, cx * W - w / 2)))
                    err = np.abs(big[y0:y0 + h, x0:x0 + w][yi][:, xi] - small).mean()
                    if err < best[1]:
                        best = (s ** sign, err)
    if best[0] and best[1] < base * .6:
        return round(float(best[0]), 2), round(float(best[1] / base), 2)
    return None


def _grade(rgb_frames):
    """grade numbers from a few full-colour stills (n x H x W x 3, 0-255)"""
    px = rgb_frames.reshape(-1, 3)
    luma = px[:, 0] * .299 + px[:, 1] * .587 + px[:, 2] * .114
    mx, mn = px.max(axis=1), px.min(axis=1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    r, g, b = px.mean(axis=0)
    out = {"brightness": round(float(luma.mean()), 1), "contrast": round(float(luma.std()), 1),
           "black_point": round(float(np.percentile(luma, 2)), 1), "white_point": round(float(np.percentile(luma, 98)), 1),
           "saturation": round(float(sat.mean()), 3), "warmth": round(float(r - b), 1), "tint": round(float(g - (r + b) / 2), 1)}
    words = []
    words.append("warm" if out["warmth"] > 12 else "cool" if out["warmth"] < -8 else "neutral white balance")
    words.append("high contrast" if out["contrast"] > 62 else "soft / low contrast" if out["contrast"] < 42 else "medium contrast")
    words.append("saturated" if out["saturation"] > .38 else "muted" if out["saturation"] < .2 else "natural saturation")
    if out["black_point"] > 22:
        words.append("lifted blacks (matte / faded)")
    if out["brightness"] > 150:
        words.append("bright, airy")
    elif out["brightness"] < 80:
        words.append("dark, moody")
    if out["tint"] > 6:
        words.append("green tint")
    elif out["tint"] < -6:
        words.append("magenta tint")
    out["words"] = words
    return out


def _palette(stills, k=6):
    from PIL import Image
    mosaic = np.concatenate([s[::4, ::4] for s in stills], axis=0).astype(np.uint8)
    q = Image.fromarray(mosaic).quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal, counts = q.getpalette(), np.bincount(np.array(q).ravel(), minlength=k)
    tot = counts.sum()
    return [{"hex": "#%02X%02X%02X" % tuple(pal[i * 3:i * 3 + 3]), "share": round(float(counts[i] / tot), 3)}
            for i in np.argsort(-counts) if counts[i] / tot >= .03]


def _still(path, t, w=360):
    from PIL import Image
    cmd = [ffmpeg_bin(), "-hide_banner", "-v", "error", "-ss", f"{max(0, t):.3f}", "-i", str(path), "-frames:v", "1",
           "-vf", f"{sdr_vf(str(path))}scale={w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"]
    from io import BytesIO
    data = subprocess.run(cmd, capture_output=True).stdout
    return Image.open(BytesIO(data)).convert("RGB") if data else None


def _storyboard(stills, labels, out, cols=6):
    from PIL import Image, ImageDraw
    if not stills:
        return None
    w = 200
    h = int(stills[0].height * w / stills[0].width)
    rows = (len(stills) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 22)), "white")
    d = ImageDraw.Draw(sheet)
    for k, (im, lab) in enumerate(zip(stills, labels)):
        x, y = (k % cols) * w, (k // cols) * (h + 22)
        sheet.paste(im.resize((w, h)), (x, y))
        d.text((x + 4, y + h + 4), lab, fill=(20, 20, 20))
    sheet.save(out, quality=85)
    return out


def _loudness(path):
    p = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    lra = re.search(r"LRA:\s+([\d.]+) LU", tail)
    pk = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return {"lufs": float(i.group(1)) if i else None, "lra": float(lra.group(1)) if lra else None,
            "true_peak": float(pk.group(1)) if pk else None}


def study(path, out_root):
    path = Path(path)
    info = probe(path)
    fps = float(info.get("fps") or 30)
    dur = float(info.get("duration") or 0)
    name = re.sub(r"[^\w\-]+", "-", path.stem)[:60]
    out = Path(out_root) / name
    out.mkdir(parents=True, exist_ok=True)
    grey, mean_rgb = _lowres(path, fps)
    fps = len(grey) / dur if dur and len(grey) else fps
    cuts = _cuts(grey, fps)
    luma = mean_rgb[:, 0] * .299 + mean_rgb[:, 1] * .587 + mean_rgb[:, 2] * .114
    # what happens at each cut: a punch-in / zoom-out of the same take, a flash, a fade through black, or a new shot
    events = []
    for c in cuts:
        a, b = grey[c - 1], grey[c]
        ev = {"t": round(c / fps, 3)}
        z = _zoom(a, b)
        win = luma[max(0, c - int(fps * .25)):c + int(fps * .25) + 1]
        around = np.median(luma[max(0, c - int(fps)):c + int(fps) + 1])
        if z:
            ev.update(kind="punch-in" if z[0] > 1 else "zoom-out", scale=z[0])
        elif win.max() > max(200, around + 50):
            ev["kind"] = "flash"
        elif win.min() < min(18, around * .25):
            ev["kind"] = "through black"
        else:
            ev["kind"] = "cut"
        events.append(ev)
    bounds = [0] + cuts + [len(grey)]
    shots = [round((b - a) / fps, 3) for a, b in zip(bounds, bounds[1:]) if b > a]
    new_shots = [e for e in events if e["kind"] != "punch-in" and e["kind"] != "zoom-out"]
    punches = [e for e in events if e["kind"] in ("punch-in", "zoom-out")]
    # stills: the middle of each shot (at most 36)
    mids = [((a + b) / 2) / fps for a, b in zip(bounds, bounds[1:]) if b > a]
    pick = mids if len(mids) <= 36 else [mids[int(k * len(mids) / 36)] for k in range(36)]
    stills = [s for s in (_still(path, t) for t in pick) if s is not None]
    sb = _storyboard(stills, [f"{t:.1f}s" for t in pick], out / "storyboard.jpg")
    arr = np.stack([np.asarray(s.resize((180, int(180 * s.height / s.width))), np.float32) for s in stills]) if stills else None
    res = {"video": str(path), "duration": round(dur, 2), "size": [info.get("width"), info.get("height")], "fps": round(fps, 2),
           "cuts": [e["t"] for e in events], "events": events,
           "pace": {"shots": len(shots), "cuts_per_min": round(len(cuts) / dur * 60, 1) if dur else None,
                    "median_shot_s": round(float(np.median(shots)), 2) if shots else None,
                    "shortest_s": min(shots) if shots else None, "longest_s": max(shots) if shots else None,
                    "new_shots": len(new_shots), "punch_ins": len(punches),
                    "punch_scale": round(float(np.median([max(e["scale"], 1 / e["scale"]) for e in punches])), 2) if punches else None,
                    "flashes": sum(e["kind"] == "flash" for e in events),
                    "through_black": sum(e["kind"] == "through black" for e in events)},
           "grade": _grade(arr) if arr is not None else None,
           "palette": _palette([np.asarray(s) for s in stills]) if stills else []}
    # sound: loudness, the beat, cuts on the beat, strong hits
    if info.get("has_audio"):
        res["loudness"] = _loudness(path)
        b = rhythm.beats(path, max_s=min(dur, 180) or 180)
        if b:
            res["music"] = {"bpm": b["bpm"], "beat_strength": b["strength"], "clear_beat": b["strength"] >= .3}
            if b["strength"] >= .3:
                on, chance = rhythm.cuts_on_beat(res["cuts"], b["beats"], dur)
                res["music"].update(cuts_on_beat=on, by_chance=chance,
                                    beat_synced=bool(on is not None and len(cuts) >= 4 and on > max(.5, chance * 1.8)))
        x = rhythm.load(path)
        if x is not None and len(x) > rhythm.SR:
            perc, share = rhythm.onsets(x)
            thr = float(np.percentile(perc, 99.3))
            pk = rhythm._peaks(perc, int(.25 / rhythm.T_HOP), thr)
            pk = [p for p in pk if share[max(0, p - 2):p + 3].max() > .5][:40]
            res["hits"] = [round(float(p * rhythm.T_HOP), 2) for p in pk]
    (out / "study.json").write_text(json.dumps(res, indent=1))
    (out / "STUDY.md").write_text(_md(res, sb))
    return out


def _md(r, sb):
    p, g, m = r["pace"], r.get("grade") or {}, r.get("music") or {}
    L = [f"# Study: {Path(r['video']).name}", "",
         f"Measured on {r['duration']} s, {r['size'][0]}x{r['size'][1]}, {r['fps']} fps (engine/study.py). "
         "Numbers are measurements; lines marked *guess* are not.", "", "## Pace"]
    if p["shots"]:
        every = r["duration"] / max(1, p["shots"])
        L.append(f"- {p['shots']} shots: a change every {every:.1f} s ({p['cuts_per_min']} cuts a minute), "
                 f"median shot {p['median_shot_s']} s, shortest {p['shortest_s']} s, longest {p['longest_s']} s.")
        L.append(f"- Of the {len(r['cuts'])} cuts: {p['new_shots']} to a new picture, {p['punch_ins']} punch-ins / zoom-outs of the same take"
                 + (f" (typical ×{p['punch_scale']})" if p["punch_scale"] else "") + f", {p['flashes']} flashes, "
                 f"{p['through_black']} through black.")
        pace = "Very lively" if every < 1.6 else "Medium" if every < 3.5 else "Calm"
        L.append(f"- Engine pace closest to this: **{pace}**.")
    if g:
        L += ["", "## Look", f"- Grade: {', '.join(g['words'])}.",
              f"- brightness {g['brightness']}, contrast {g['contrast']}, black point {g['black_point']}, white point "
              f"{g['white_point']}, saturation {g['saturation']}, warmth (R−B) {g['warmth']}, tint {g['tint']}."]
    if r.get("palette"):
        L.append("- Main colours: " + ", ".join(f"{c['hex']} ({round(c['share'] * 100)} %)" for c in r["palette"]) + ".")
    L += ["", "## Sound"]
    if r.get("loudness", {}).get("lufs") is not None:
        lo = r["loudness"]
        L.append(f"- Loudness {lo['lufs']} LUFS (range {lo['lra']} LU, true peak {lo['true_peak']} dBFS).")
    if m:
        if m.get("clear_beat"):
            line = f"- Music: about {m['bpm']} BPM (beat strength {m['beat_strength']})."
            if m.get("cuts_on_beat") is not None:
                line += (f" {round(m['cuts_on_beat'] * 100)} % of cuts land on a beat (chance would give "
                         f"{round(m['by_chance'] * 100)} %): " + ("**cut to the beat**." if m["beat_synced"] else "not cut to the beat."))
            L.append(line)
        else:
            L.append(f"- No clear beat (strength {m['beat_strength']}): talk only, or soft music without drums.")
    if r.get("hits"):
        L.append(f"- *Guess*: strong hits (possible sound effects, or drums) at {', '.join(str(t) + ' s' for t in r['hits'][:15])}"
                 + (" …" if len(r["hits"]) > 15 else "") + ". Listen before copying them into a sound map.")
    L += ["", "## Not measured", "- Caption font, size, colours and motion; titles; stickers: look at the storyboard "
          "(and frame breakdowns in StyleLab).", "- What is said (words a minute): transcribe the reference if it matters."]
    if sb:
        L += ["", f"Storyboard: `{Path(sb).name}` (middle of every shot)."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out", default=str(ROOT / "research" / "studies"))
    a = ap.parse_args()
    for v in a.videos:
        print(study(v, a.out))
