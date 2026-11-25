"""Media helpers: ffmpeg location, probing, audio extraction, thumbnails.

ffmpeg comes from VETTO_FFMPEG, the PATH, or bin/ffmpeg (see README: Setup).
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

_CANDIDATES = [
    os.environ.get("VETTO_FFMPEG", ""),
    shutil.which("ffmpeg") or "",
    str(Path(__file__).resolve().parent.parent / "bin" / "ffmpeg"),
]


def ffmpeg_bin() -> str:
    for c in _CANDIDATES:
        if c and Path(c).exists():
            return c
    raise RuntimeError("ffmpeg not found. Set VETTO_FFMPEG to an ffmpeg binary.")


def run(args, **kw):
    """Run ffmpeg with args (list, without the binary). Raises with stderr tail on failure."""
    cmd = [ffmpeg_bin(), "-hide_banner", "-y"] + [str(a) for a in args]
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + p.stderr[-2500:])
    return p


def probe(path) -> dict:
    """Duration, size, fps, rotation and audio presence, parsed from `ffmpeg -i` (no ffprobe here)."""
    p = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    err = p.stderr
    info = {"path": str(path), "duration": 0.0, "width": 0, "height": 0, "fps": 30.0, "has_audio": False, "rotation": 0}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if m:
        info["duration"] = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    m = re.search(r"Video: .*?(\d{2,5})x(\d{2,5})", err)
    if m:
        info["width"], info["height"] = int(m[1]), int(m[2])
    m = re.search(r"([\d.]+) fps", err)
    if m:
        info["fps"] = float(m[1])
    m = re.search(r"rotate\s*:\s*(-?\d+)|rotation of (-?[\d.]+)", err)
    if m:
        info["rotation"] = int(float(m[1] or m[2]))
    if abs(info["rotation"]) in (90, 270):
        info["width"], info["height"] = info["height"], info["width"]
    info["has_audio"] = "Audio:" in err
    info["hdr"] = _hdr_kind(err)
    return info


# iPhone HDR (10-bit HLG, "Dolby Vision" in the camera) and HDR10 (PQ) footage: without tone mapping it comes out washed
# out in an 8-bit H.264 proxy, and a 10-bit piece makes HyperFrames take its HDR path, which drops the effect layers and
# squashes the picture (found on IMG_0780, 18 Nov 2026). Every place that decodes the original file prepends sdr_vf().
def _hdr_kind(ffmpeg_i_stderr):
    m = re.search(r"Video: [^\n]*", ffmpeg_i_stderr)
    line = m[0] if m else ""
    if "arib-std-b67" in line:
        return "hlg"
    if "smpte2084" in line:
        return "pq"
    return None


_HDR_CACHE = {}


def hdr_kind(path):
    """'hlg', 'pq' or None for a media file (cached per path)."""
    key = str(path)
    if key not in _HDR_CACHE:
        p = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", key], capture_output=True, text=True)
        _HDR_CACHE[key] = _hdr_kind(p.stderr)
    return _HDR_CACHE[key]


def sdr_vf(path_or_kind):
    """Filter chain (ending in a comma, or "") that tone-maps HDR to 8-bit BT.709 SDR. Hable curve, like the
    IMG_0780 edit; HLG is read with a 203-nit reference white."""
    kind = path_or_kind if path_or_kind in ("hlg", "pq", None) else hdr_kind(path_or_kind)
    if not kind:
        return ""
    npl = 203 if kind == "hlg" else 100
    peak = 2.5 if kind == "hlg" else 10
    return (f"zscale=t=linear:npl={npl},format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0:peak={peak},"
            "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")


def extract_audio(src, dst_wav, rate=16000):
    run(["-i", src, "-vn", "-ac", "1", "-ar", rate, "-c:a", "pcm_s16le", dst_wav])
    return dst_wav


def thumbnails(src, out_dir, every_s=1.0, width=240):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    run(["-i", src, "-vf", f"{sdr_vf(src)}fps=1/{every_s},scale={width}:-2", "-q:v", "5", out / "t_%04d.jpg"])
    return sorted(str(p.name) for p in out.glob("t_*.jpg"))


def proxy(src, dst, height=960):
    """Small H.264 proxy the browser can play (iPhone HEVC/10-bit often won't play in Chromium). HDR is tone-mapped
    to SDR first (sdr_vf), so the proxy and everything made from it (previews, effect pieces) look right."""
    tag = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"] if hdr_kind(src) else []
    run(["-i", src, "-map", "0:v:0", "-map", "0:a:0?", "-vf", f"{sdr_vf(src)}scale=-2:{height}", "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p", *tag, "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", dst])
    return dst


def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text())
