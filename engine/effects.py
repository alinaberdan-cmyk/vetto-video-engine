"""Effects that the engine renders itself on a 1080x1920 base reel (before captions are burned).

Native here: text-behind-me, split-clones (from the neurofam PDF, numbers kept).
Person cutouts come from HyperFrames (`bin/hyperframes remove-background`, CoreML on this Mac).
Every other effect in library/effects.json is built by Claude as a HyperFrames scene from its prompt.
"""
import subprocess
from pathlib import Path

from media import run

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "library" / "fonts"
HF = ROOT / "bin" / "hyperframes"
NATIVE = {"text-behind-me", "split-clones", "vhs-glitch"}
import hfx  # noqa: E402  (HyperFrames templates: engine/hf/<effect>.html)
RENDERABLE = NATIVE | hfx.TEMPLATES
PIECE = 3.0  # every PDF effect is a 3 s piece


def cutout(piece, out_mov):
    """Person cutout with alpha (ProRes 4444), same frames as `piece`."""
    if Path(out_mov).exists():
        return out_mov
    p = subprocess.run([str(HF), "remove-background", str(piece), "-o", str(out_mov)], capture_output=True, text=True)
    if p.returncode != 0 or not Path(out_mov).exists():
        raise RuntimeError("cutout failed: " + p.stderr[-800:])
    return out_mov


def head_top(cut_mov, work):
    """Highest row of the person (first frame alpha), to place things relative to the head."""
    from PIL import Image
    png = Path(work) / "alpha0.png"
    run(["-i", cut_mov, "-frames:v", "1", "-vf", "alphaextract", png])
    im = Image.open(png).convert("L")
    w, h = im.size
    box = im.crop((int(w * .2), 0, int(w * .8), h)).point(lambda v: 255 if v > 128 else 0)
    bb = box.getbbox()
    return bb[1] if bb else int(h * .25)


def _metrics(font_file):
    """libass sizes a font by its line height (winAscent + winDescent), not by the em."""
    from fontTools.ttLib import TTFont
    f = TTFont(str(font_file))
    os2, upm = f["OS/2"], f["head"].unitsPerEm
    line = os2.usWinAscent + os2.usWinDescent
    cap = getattr(os2, "sCapHeight", 0) or int(upm * 0.7)
    return f, upm, line, os2.usWinDescent, cap


def _advances(font_file, text, size):
    f, upm, line, _, _ = _metrics(font_file)
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    em = size * upm / line
    return [hmtx[cmap.get(ord(c), cmap.get(ord("?")))][0] * em / upm for c in text]


def _ts(t):
    m, s = divmod(max(0, t), 60)
    return f"0:{int(m):02d}:{s:05.2f}"


def text_behind_me(piece, cut_mov, word, out, work, font="Anton", font_file="Anton-Regular.ttf", color="F3EDE3"):
    """PDF p.7: room, huge word, me on top. Word full width, ~350 px tall, at the top of the head so the head
    covers the bottom of the letters. Milky colour, warm glow. Letters rise one by one from under a mask in
    the first 0.45 s, then the word drifts up 20 px. Room slightly darkened."""
    word = word.upper().strip(" .,!?:;\"'“”")
    W, H = 1080, 1920
    _, upm, line, desc, cap = _metrics(FONTS / font_file)
    size = 600.0
    adv = _advances(FONTS / font_file, word, size)
    size *= (W * 0.94) / sum(adv)                       # full frame width (PDF: "во всю ширину кадра")
    adv = _advances(FONTS / font_file, word, size)
    cap_h = size * cap / line                            # rendered capital height in px
    if cap_h > 420:                                      # PDF: about 350 px tall; short words stay near that
        size *= 420 / cap_h
        adv = _advances(FONTS / font_file, word, size)
        cap_h = size * cap / line
    top = head_top(cut_mov, work)
    margin = 70                                          # keep the letters inside the frame
    if cap_h * 0.58 > top - margin:                      # not enough room above the head: smaller word...
        target = max((top - margin) / 0.58, 240)
        size *= target / cap_h
        adv = _advances(FONTS / font_file, word, size)
        cap_h = size * cap / line
    baseline = max(top + cap_h * 0.42, margin + cap_h)   # ...and if still too tall, the head covers more of it
    base_y = baseline + size * desc / line               # \an1 anchors the bottom of the line box (descent included)
    x = (W - sum(adv)) / 2
    bgr = color[4:6] + color[2:4] + color[0:2]
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
             "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             f"Style: W,{font},{size:.0f},&H00{bgr},&H00{bgr},&H6038A0FF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,1,0,0,0,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    rise, n = 0.45, max(1, len(word))
    for k, (ch, a) in enumerate(zip(word, adv)):
        cx = x + sum(adv[:k])
        t0 = rise * k / n
        t1 = t0 + 0.28
        mask = f"\\clip(0,0,{W},{baseline + 4:.0f})"       # the mask line: letters come up from under it
        glow = "\\blur3\\bord6\\3a&HB0&"
        lines.append(f"Dialogue: 0,{_ts(0)},{_ts(rise)},W,,0,0,0,,{{\\an1{glow}{mask}\\move({cx:.0f},{base_y + cap_h * 1.05:.0f},{cx:.0f},{base_y:.0f},{t0 * 1000:.0f},{t1 * 1000:.0f})}}{ch}")
        lines.append(f"Dialogue: 0,{_ts(rise)},{_ts(PIECE)},W,,0,0,0,,{{\\an1{glow}\\move({cx:.0f},{base_y:.0f},{cx:.0f},{base_y - 20:.0f})}}{ch}")
    ass = Path(work) / "tbm.ass"
    ass.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run(["-i", piece, "-i", cut_mov, "-filter_complex",
         f"[0:v]eq=brightness=-0.07:saturation=0.95,ass='{ass}':fontsdir='{FONTS}'[bg];[1:v]format=yuva444p10le[fg];"
         f"[bg][fg]overlay=0:0:format=auto,format=yuv420p[v]",
         "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "copy", out])
    return out


def split_clones(base, start, out, work):
    """PDF p.8: three vertical strips of 352 px with dark 12 px gaps; each holds the video, face centred and a
    little larger; offset in time (left from start, middle +0.25 s, right +0.5 s). In the first 0.5 s the left
    strip slides in from the top, the right from the bottom. Then the strips drift slowly. At 0.6 s a thin orange
    line slides under the middle strip."""
    W, H, SW, G = 1080, 1920, 352, 12
    d = PIECE
    strip = "scale=-2:{h},crop={w}:{h}:(iw-{w})/2:0,setsar=1".format(w=SW, h=int(H * 1.08))
    fc = [
        f"[0:v]trim={start}:{start + d},setpts=PTS-STARTPTS,{strip}[l]",
        f"[0:v]trim={start + .25}:{start + .25 + d},setpts=PTS-STARTPTS,{strip}[m]",
        f"[0:v]trim={start + .5}:{start + .5 + d},setpts=PTS-STARTPTS,{strip}[r]",
        f"color=c=0x0E0D0C:s={W}x{H}:d={d}:r=30[bg]",
        # left: from the top in 0.5 s (ease-out), then drift up; right: from the bottom, then drift down
        f"[bg][l]overlay=x=0:y='if(lt(t,0.5),-{H}*pow(1-t/0.5,3),0)-t*6-{int(H * .04)}':shortest=1[a]",
        f"[a][m]overlay=x={SW + G}:y='-{int(H * .04)}+t*4':shortest=1[b]",
        f"[b][r]overlay=x={2 * (SW + G)}:y='if(lt(t,0.5),{H}*pow(1-t/0.5,3),0)+t*6-{int(H * .04)}':shortest=1[c]",
        f"color=c=0xE8572A:s={SW}x6:d={d}:r=30[line]",
        f"[c][line]overlay=x='{SW + G}-{SW}+min(1,max(0,(t-0.6)/0.35))*{SW}':y={int(H * .86)}:enable='gte(t,0.6)'[v]",
    ]
    run(["-i", base, "-filter_complex", ";".join(fc), "-map", "[v]", "-t", d, "-c:v", "libx264", "-crf", "17", "-an", out])
    return out


def vhs_glitch(piece, out):
    """VHS / CRT look for 3 s (idea: lemo-opuscar core/post/crt, rebuilt in ffmpeg): red and blue shifted apart,
    scanlines every 4 px, moving noise, a slight horizontal tracking wobble, a short roll at the start, a vignette."""
    W, H = 1080, 1920
    run(["-i", piece, "-filter_complex",
         f"[0:v]rgbashift=rh=-7:bh=7:gv=2,noise=alls=22:allf=t+u,eq=saturation=1.25:contrast=1.08,"
         f"crop=w=iw-24:h=ih-24:x='12+6*sin(n*1.9)+if(lt(t,0.35),10*sin(n*7),0)':y='12+if(lt(t,0.25),(0.25-t)*40,0)',"
         f"scale={W}:{H},drawgrid=w=iw:h=4:t=1:c=black@0.28,vignette=PI/4.5,format=yuv420p[v]",
         "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-c:a", "copy", out])
    return out


def apply(base, effects, work):
    """Replace each native effect's 3 s window in `base` (1080x1920, already cut) with the effect.
    `effects`: [{"effect", "out_at", "word"}] in output time. Returns the new base and what was skipped."""
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    done, skipped, cur = [], [], Path(base)
    for k, e in enumerate(sorted(effects, key=lambda e: e["out_at"])):
        if e["effect"] not in RENDERABLE:
            skipped.append(dict(e, reason="no template yet: Claude builds it in HyperFrames"))
            continue
        t = max(0.0, e["out_at"])
        piece = work / f"fx{k}_piece.mp4"
        run(["-ss", f"{t:.3f}", "-i", cur, "-t", PIECE, "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", piece])
        fxv = work / f"fx{k}.mp4"
        if e["effect"] == "text-behind-me":
            text_behind_me(piece, cutout(piece, work / f"fx{k}_cut.mov"), (e.get("params") or {}).get("word") or e.get("word") or "FOOD", fxv, work)
        elif e["effect"] == "split-clones":
            split_clones(cur, t, fxv, work)
        elif e["effect"] == "vhs-glitch":
            vhs_glitch(piece, fxv)
        else:
            try:
                fxv = hfx.render(e["effect"], piece, e.get("params"), e.get("words", []), e.get("images", []),
                                 work / f"fx{k}_hf", e.get("word") or "", attachments=e.get("attachments", []),
                                 brand=e.get("brand"))
            except hfx.NeedsInput as why:
                skipped.append(dict(e, reason=str(why)))
                continue
        nxt = work / f"base_fx{k}.mov"
        # the effect's picture replaces the base picture for 3 s; the voice is untouched
        run(["-i", cur, "-itsoffset", f"{t:.3f}", "-i", fxv, "-filter_complex",
             f"[0:v][1:v]overlay=0:0:eof_action=pass:enable='between(t,{t:.3f},{t + PIECE - 0.001:.3f})'[v]",
             "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-c:a", "copy", nxt])
        cur = nxt
        done.append(e)
    return str(cur), done, skipped
