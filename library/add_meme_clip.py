"""Turn a green-screen meme clip into transparent frames for the meme effects (18 Nov 2026).

  .venv/bin/python library/add_meme_clip.py <clip.mp4> <name> [--start 0.95] [--end 3.75] [--mode green|fire]

Writes engine/hf/fx/memes/<name>/f000.webp … (with alpha) + meta.json {fps, n, w, h}. The effects
`meme-explosion` and `greenscreen-meme` play these frames in step with the timeline (one <img> per frame,
shown in turn), so the live preview and the export look the same.

Key: the green is measured on the clip's border. mode=green: alpha from how much greener than red/blue a pixel is;
mode=fire (bright fire, sparks, smoke on green): alpha from the red channel, which green never has. Both then
un-mix the green out of half-transparent pixels (fg = (C - (1-a)·K) / a) and clamp any green spill left, so edges
don't turn olive. First used on the CapCut template "Explosion for Meme" (7462869341453716797).
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FF = str(ROOT / "bin" / "ffmpeg")

a = argparse.ArgumentParser()
a.add_argument("clip"); a.add_argument("name")
a.add_argument("--start", type=float, default=0.0); a.add_argument("--end", type=float, default=None)
a.add_argument("--mode", choices=["green", "fire"], default="green")
a.add_argument("--fps", type=float, default=None, help="default: the clip's own frame rate")
a.add_argument("--quality", type=int, default=82)
a.add_argument("--vertical", action="store_true", help="centre-crop a landscape clip to 9:16")
a.add_argument("--height", type=int, default=1280, help="output height in px (width follows)")
a.add_argument("--fade-out", type=float, default=0.0, help="fade the last N s to transparent")
a.add_argument("--source", default="", help="where the clip comes from + licence (kept in meta.json)")
o = a.parse_args()

probe = subprocess.run([str(ROOT / "bin" / "ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate", "-of", "json", o.clip], capture_output=True, text=True)
st = json.loads(probe.stdout)["streams"][0]
w, h = st["width"], st["height"]
vf = []
if o.vertical and w * 16 > h * 9:
    cw = int(round(h * 9 / 16 / 2) * 2); vf.append(f"crop={cw}:{h}:{(w - cw) // 2}:0"); w = cw
if h != o.height:
    nw = int(round(w * o.height / h / 2) * 2); vf.append(f"scale={nw}:{o.height}"); w, h = nw, o.height
num, den = st["r_frame_rate"].split("/")
fps = o.fps or float(num) / float(den)
args = [FF, "-v", "error", "-ss", str(o.start), "-i", o.clip]
if o.end:
    args += ["-t", str(o.end - o.start)]
args += ["-vf", ",".join(vf + [f"fps={fps}"]), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
raw = subprocess.run(args, capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)

# key colour = median of the border pixels of the first frames that look green
border = np.concatenate([frames[:5, :8].reshape(-1, 3), frames[:5, -8:].reshape(-1, 3),
                         frames[:5, :, :8].reshape(-1, 3), frames[:5, :, -8:].reshape(-1, 3)]).astype(np.float32)
greenish = border[(border[:, 1] > border[:, 0] + 40) & (border[:, 1] > border[:, 2] + 40)]
K = np.median(greenish if len(greenish) > 50 else border, axis=0)
print("key colour", K.round(), "frames", len(frames), "fps", round(fps, 3))

out = ROOT / "engine" / "hf" / "fx" / "memes" / o.name
out.mkdir(parents=True, exist_ok=True)
for f in out.glob("f*.webp"):
    f.unlink()
kx = K[1] - max(K[0], K[2])
for i, fr in enumerate(frames):
    C = fr.astype(np.float32)
    if o.mode == "fire":
        # fire is red-heavy (R ≈ G or more), the screen is not; compare red with half the green, with a margin for
        # compression noise in the green (Pixabay 221022: R up to ~40 inside the ring)
        m, mk = C[..., 0] - 0.5 * C[..., 1], K[0] - 0.5 * K[1]
        alpha = np.clip((m - (mk + 45)) / 190.0, 0, 1) ** 0.9
        # the colour is un-mixed with the generous red-only alpha (true fire colours, no pink edges)
        unmix = np.clip((C[..., 0] - (K[0] + 8)) / 215.0, 0, 1) ** 0.85
    else:
        gx = C[..., 1] - np.maximum(C[..., 0], C[..., 2])
        alpha = 1 - np.clip((gx - kx * 0.25) / (kx * 0.55), 0, 1)
        unmix = alpha
    a3 = np.maximum(unmix, 1e-3)[..., None]
    fg = (C - (1 - a3) * K) / a3
    left = (len(frames) - 1 - i) / fps
    if o.fade_out and left < o.fade_out:
        alpha = alpha * (left / o.fade_out)
    fg[..., 1] = np.minimum(fg[..., 1], np.maximum(fg[..., 0], fg[..., 2]))   # no green spill
    rgba = np.dstack([np.clip(fg, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba).save(out / f"f{i:03d}.webp", quality=o.quality, method=4)
(out / "meta.json").write_text(json.dumps({"fps": fps, "n": len(frames), "w": w, "h": h, "source": o.clip,
                                           "start": o.start, "end": o.end, "mode": o.mode,
                                           "vertical": o.vertical, "fade_out": o.fade_out, "credit": o.source}, indent=1))
print("wrote", len(frames), "frames to", out)
