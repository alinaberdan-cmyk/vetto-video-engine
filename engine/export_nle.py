"""Export the approved cut for other editors (structure after auto-editor's exporters, public domain / Unlicense):
- <name>.xml  FCP7 xmeml v5: opens in Premiere Pro and DaVinci Resolve (one video + one stereo audio track, one clip per
              kept range, pointing at the original footage, so every cut can still be trimmed there)
- <name>.edl  CMX 3600: the most basic list, opens almost anywhere
- <name>.srt  the captions on the cut's timeline (CapCut, Premiere, Resolve, YouTube…)
The engine's own effects, grade and burned captions are NOT in these files: they carry the cut and the words.
"""
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

FPS = 30


def _f(t):
    return int(round(t * FPS))


def _tc(frames):
    h, r = divmod(frames, 3600 * FPS)
    m, r = divmod(r, 60 * FPS)
    s, f = divmod(r, FPS)
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def _srt_t(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(project, ranges, per=3):
    from edit import map_time
    kept = []
    for w in project["edl"]["words"]:
        if w["cut"]:
            continue
        s = map_time(w["start"], ranges)
        if s is not None:
            e = map_time(w["end"], ranges)
            kept.append((s, e if e is not None else s + .3, w["text"]))
    out, n = [], 0
    for i in range(0, len(kept), per):
        g = kept[i:i + per]
        end = kept[i + per][0] if i + per < len(kept) else g[-1][1] + .3
        n += 1
        if i + per >= len(kept):
            end = max(end, g[0][0] + .5)      # the last line stays at least half a second; others end where the next starts
        out.append(f"{n}\n{_srt_t(g[0][0])} --> {_srt_t(end)}\n{' '.join(t for _, _, t in g)}\n")
    return "\n".join(out)


def edl(name, src, ranges):
    reel = "AX"
    lines = [f"TITLE: {name}", "FCM: NON-DROP FRAME", ""]
    rec = 0
    for k, (a, b) in enumerate(ranges, 1):
        sin, sout = _f(a), _f(b)
        dur = sout - sin
        lines.append(f"{k:03d}  {reel:<8} AA/V  C        {_tc(sin)} {_tc(sout)} {_tc(rec)} {_tc(rec + dur)}")
        lines.append(f"* FROM CLIP NAME: {Path(src).name}")
        rec += dur
    return "\n".join(lines) + "\n"


def xmeml(name, src, info, ranges):
    W, H = info.get("width") or 1080, info.get("height") or 1920
    total = _f(info.get("duration") or 0)
    url = "file://localhost" + quote(str(Path(src).resolve()))
    rate = f"<rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>"
    file_full = (f'<file id="file-1"><name>{escape(Path(src).name)}</name><pathurl>{url}</pathurl>{rate}<duration>{total}</duration>'
                 f"<media><video><samplecharacteristics><width>{W}</width><height>{H}</height></samplecharacteristics></video>"
                 f"<audio><channelcount>2</channelcount></audio></media></file>")
    v, a, rec = [], [[], []], 0
    for k, (s, e) in enumerate(ranges, 1):
        sin, sout = _f(s), _f(e)
        dur = sout - sin
        f = file_full if k == 1 else '<file id="file-1"/>'
        v.append(f'<clipitem id="v{k}"><name>{escape(Path(src).name)}</name><duration>{total}</duration>{rate}'
                 f"<start>{rec}</start><end>{rec + dur}</end><in>{sin}</in><out>{sout}</out>{f}</clipitem>")
        for ch in (1, 2):   # Resolve reads every audio clipitem as mono: one per channel
            a[ch - 1].append(f'<clipitem id="a{ch}-{k}"><name>{escape(Path(src).name)}</name><duration>{total}</duration>{rate}'
                             f'<start>{rec}</start><end>{rec + dur}</end><in>{sin}</in><out>{sout}</out><file id="file-1"/>'
                             f"<sourcetrack><mediatype>audio</mediatype><trackindex>{ch}</trackindex></sourcetrack></clipitem>")
        rec += dur
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence>'
            f"<name>{escape(name)}</name><duration>{rec}</duration>{rate}<media>"
            f"<video><format><samplecharacteristics><width>{W}</width><height>{H}</height></samplecharacteristics></format>"
            f"<track>{''.join(v)}</track></video>"
            f"<audio><track>{''.join(a[0])}</track><track>{''.join(a[1])}</track></audio>"
            "</media></sequence></xmeml>\n")


def export(project, version, ranges, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    src = project["source"]["file"]
    name = f"{project['name']} – {version['name']}"
    per = int(version.get("text", {}).get("words_per_line", 3))
    files = {
        "xml": out / "cut-premiere-resolve.xml",
        "edl": out / "cut.edl",
        "srt": out / "captions.srt",
    }
    files["xml"].write_text(xmeml(name, src, project["source"], ranges), encoding="utf-8")
    files["edl"].write_text(edl(name, src, ranges), encoding="utf-8")
    files["srt"].write_text(srt(project, ranges, per), encoding="utf-8")
    return {k: str(v) for k, v in files.items()}
