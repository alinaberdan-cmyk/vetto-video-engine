"""Rendering with ffmpeg: word cuts, 9:16 crop, captions (libass), hook title, images on words, sound effects.

Effects that need a cutout or 3D (text behind me, clones, sticker, phone...) are rendered by HyperFrames
through Claude (see skills/vetto-edit/SKILL.md); this file renders everything ffmpeg can do on its own and
leaves a clean base clip for those effects.
"""
from pathlib import Path

from media import run, load_json, sdr_vf
from edit import keep_ranges, map_time

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "library" / "fonts"
SFX = ROOT / "library" / "sfx"

SIZES = {"reel": (1080, 1920), "story": (1080, 1920), "carousel": (1080, 1350), "square": (1080, 1080)}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def clip_windows(project, ranges):
    """output windows of full-frame example clips (Cinema Lexicon `overlays` with a video file): captions sit mid-frame
    over them (CL01 v6: 49 % on stock, low on the creator's own footage)"""
    out = []
    for ov in project.get("overlays", []):
        if ov.get("status") == "removed" or not ov.get("image") or Path(ov["image"]).suffix.lower() not in VIDEO_EXT:
            continue
        t0 = map_time(ov["at"], ranges)
        if t0 is not None:
            out.append((t0, t0 + float(ov.get("hold", 1.6)), ov.get("caption", "mid")))
    return out


def _ass_color(hex_or_rgba, alpha=0):
    h = (hex_or_rgba or "#FFFFFF").lstrip("#")[:6]
    if len(h) != 6:
        h = "FFFFFF"
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def _ts(t):
    t = max(0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _esc(t):
    return t.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def _face(family):
    """CSS family -> (libass name, bold, italic)."""
    for f in (load_json(ROOT / "library" / "looks.json", {}) or {}).get("fonts", []):
        if f["family"] == family and f.get("ass"):
            a = f["ass"]
            # libass takes a numeric weight in the Bold field (700 = bold); older entries only say bold yes/no
            bold = a["weight"] if a.get("weight") else (-1 if a["bold"] else 0)
            return a["name"], bold, -1 if a["italic"] else 0
    return family, -1, 0


_LINE = {}


def _em(family):
    """libass sizes text by the font's line height (winAscent + winDescent), the editor preview (CSS) by the em. This
    is the factor that makes an ASS font size draw letters as big as the same size in the preview (18 Nov 2026: exported
    captions were 57–74 % of the preview size, depending on the font)."""
    if family not in _LINE:
        k = 1.0
        for f in (load_json(ROOT / "library" / "looks.json", {}) or {}).get("fonts", []):
            if f["family"] == family and f.get("file"):
                try:
                    from fontTools.ttLib import TTFont
                    t = TTFont(str(ROOT / "library" / "fonts" / Path(f["file"]).name), lazy=True)
                    k = (t["OS/2"].usWinAscent + t["OS/2"].usWinDescent) / t["head"].unitsPerEm
                except Exception:
                    pass
                break
        _LINE[family] = k
    return _LINE[family]


def face_point(src, project, work):
    """Where to centre the 9:16 frame and punch-ins: Alina's slider (focus_x) wins; otherwise the face found by
    Apple Vision in 3 frames of the take; otherwise the middle."""
    fx_set = project.get("focus_x")
    try:
        import hfx
        fr = Path(work) / "facefr"
        fr.mkdir(parents=True, exist_ok=True)
        dur = float(project["source"]["duration"])
        frames = []
        for k, t in enumerate((dur * .2, dur * .5, dur * .8)):
            f = fr / f"f{k}.jpg"
            run(["-ss", f"{t:.2f}", "-i", project["source"].get("file"), "-frames:v", "1", "-vf", "scale=640:-2", f])
            frames.append(f)
        faces = [sorted(x.get("faces", []), key=lambda b: -b[2] * b[3])[0] for x in hfx.vision(frames) if x.get("faces")]
    except Exception:
        faces = []
    if faces:
        cx = sum(b[0] + b[2] / 2 for b in faces) / len(faces)
        cy = sum(b[1] + b[3] / 2 for b in faces) / len(faces)
        return (float(fx_set) if fx_set is not None else cx), min(.62, max(.38, cy + .06))   # keep a little headroom
    return (float(fx_set) if fx_set is not None else .5), .5


def words_between(project, ranges, t0, t1):
    """Kept words said between output times t0 and t1, with times relative to t0 (for effect templates)."""
    out = []
    for w in project["edl"]["words"]:
        if w["cut"]:
            continue
        s = map_time(w["start"], ranges)
        if s is not None and t0 <= s < t1:
            e = map_time(w["end"], ranges)
            out.append({"text": w["text"], "t": round(s - t0, 3), "e": round((e if e is not None else s + .3) - t0, 3)})
    return out


def caption_zones(project, ranges):
    """While an effect is on screen the captions move out of its way (or hide over full-screen inserts):
    library/effects.json `caption_zone` per effect: above-card | upper | hide (default: stay)."""
    lib = {e["id"]: e for e in (load_json(ROOT / "library" / "effects.json", []) or [])}
    zones = []
    for e in project.get("effects", []):
        z = (e.get("params") or {}).get("caption") or lib.get(e["effect"], {}).get("caption_zone")
        t = map_time(e["at"], ranges)
        if z and t is not None and e.get("status") != "removed":
            hold = float((e.get("params") or {}).get("hold") or 3.0)    # a short graphic gives the captions back when it ends
            zones.append((t, t + min(3.0, hold), z))
    return zones + clip_windows(project, ranges)


def _placed(pos, W, H):
    """A dragged place → an ASS override (centre anchor at x, y) and side margins that set the wrap width."""
    if not pos:
        return "", 0, 0
    x, y, w = float(pos.get("x", .5)), float(pos.get("y", .5)), float(pos.get("w", .86))
    w = max(.15, min(1.0, w))
    # the wrap box is centred on x: margins are measured from the frame edges
    ml = max(0, int((x - w / 2) * W)); mr = max(0, int((1 - x - w / 2) * W))
    return r"{\an5\pos(%d,%d)}" % (round(x * W), round(y * H)), ml, mr


def lexicon_captions(project, ranges, size, look, lines):
    """Cinema Lexicon captions (CL01 v6): small centred lines of 1–3 words, cut hard on the spoken word, no motion;
    about one word in four is a key word, shown alone and big (≤ 5 letters in CAPS, longer ones in italic). Low on the
    creator's own footage, mid-frame on example clips, high while UI buttons drop, dark on cream cards, hidden on cards
    that carry the words themselves."""
    W, H = size
    keys = {int(k) for k in (look.get("keys") or [])}
    kept = []
    for w in project["edl"]["words"]:
        if w["cut"]:
            continue
        s, e = map_time(w["start"], ranges), map_time(min(w["end"], w["start"] + 1.2), ranges)
        if s is not None:
            kept.append((s, e if e is not None else s + .3, w["text"], w["i"]))
    groups, cur = [], []
    for k, (s, e, t, i) in enumerate(kept):
        prev = kept[k - 1] if k else None
        new = (not cur or len(cur) >= 3 or i in keys or (prev and prev[3] in keys)
               or (prev and prev[2][-1:] in ".,?!…") or (prev and s - prev[1] > .35))
        if new and cur:
            groups.append(cur)
            cur = []
        cur.append((s, e, t, i))
    if cur:
        groups.append(cur)
    base = look.get("cap_pos") or {"x": .5, "y": .82}
    x0, y0 = float(base.get("x", .5)), float(base.get("y", .82))
    case = look.get("case", "as spoken")
    cs = lambda t: t.upper() if case == "upper" else t.lower() if case == "lower" else t
    for gi, g in enumerate(groups):
        s = g[0][0]
        nxt = groups[gi + 1][0][0] if gi + 1 < len(groups) else None
        end = g[-1][1] + .25
        if nxt is not None:
            end = nxt if nxt - g[-1][1] < .6 else end
        zone = next((z for a, b, z in reversed(project.get("_zones", [])) if a - 1e-3 <= s < b), None)
        if zone == "hide":
            continue
        y = {"mid": .49, "upper": .2, "dark": .875, "above-card": .2, "lower-only": .82}.get(zone, y0)
        dark = zone == "dark"
        txt = " ".join(t for _, _, t, _ in g)
        if len(g) == 1 and g[0][3] in keys:
            word = g[0][2]
            core = word.strip(".,!?…\"'“”")
            big = word.upper() if len(core) <= 5 else cs(word)
            ital = r"\i1" if len(core) > 5 else ""
            style = "KeyDark" if dark else "Key"
            lines.append(f"Dialogue: 0,{_ts(s)},{_ts(end)},{style},,0,0,0,,{{\\an5\\pos({round(x0 * W)},{round((y - .02) * H)}){ital}}}{_esc(big)}")
        else:
            style = "CapDark" if dark else "Cap"
            lines.append(f"Dialogue: 0,{_ts(s)},{_ts(end)},{style},,0,0,0,,{{\\an5\\pos({round(x0 * W)},{round(y * H)})}}{_esc(cs(txt))}")


def build_ass(project, ranges, size, out_path):
    """Captions in the project's text look: groups of up to N words, the spoken word highlighted."""
    W, H = size
    look = project.get("text", {})
    font = look.get("font", "TikTok Sans")
    color = look.get("color", "#FFFFFF")
    hi = look.get("highlight", "#FCDB1D")
    outline = look.get("outline", "#000000")
    box = look.get("box", "none")              # none | box | plate
    size_px = int(look.get("size", 78))
    pos = look.get("position", "lower")        # upper | middle | lower
    per = int(look.get("words_per_line", 3))
    case = look.get("case", "as spoken")
    margin_v = {"upper": int(H * 0.18), "middle": int(H * 0.45), "lower": int(H * 0.24)}[pos]
    align = 8 if pos == "upper" else 2
    border_style = 3 if box in ("box", "plate") else 1
    back = _ass_color(look.get("box_color", "#000000"), 0x40 if box == "plate" else 0x00)
    # stroke width, glow and soft shadow (Editing Beast styles: Clean White and Neon Dimension glow, Cinema Lexicon no stroke)
    glow = look.get("glow")
    ow = int(look.get("outline_w", 6))
    ol_col = _ass_color(glow, 0x70) if glow else _ass_color(outline)
    if glow:
        ow = 5
    shadow = 2 if look.get("shadow") else 0
    if shadow and border_style == 1:
        back = _ass_color("#000000", 0xA0)

    title = project.get("hook", {})
    tfont = look.get("title_font", font)
    cf, cb, ci = _face(font)
    tf, tb, ti = _face(tfont)
    # sizes are in 1080-wide units (as in the editor preview); scale for half-size previews and to libass' line-height sizing
    size_px = int(size_px * W / 1080 * _em(font) * (1.5 if look.get("anim") == "punch" else 1))   # the preview shows "one big word" 1.5x
    t_size = int((float(look["title_size"]) if look.get("title_size") else float(look.get("size", 78)) * 1.15) * W / 1080 * _em(tfont))
    ow = max(0, round(ow * W / 1080))
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,{cf},{size_px},{_ass_color(color)},{_ass_color(hi)},{ol_col},{back},{cb},{ci},0,0,100,100,0,0,"
        f"{border_style},{ow if border_style == 1 else 14},{shadow},{align},80,80,{margin_v},1",
        f"Style: CapBox,{cf},{size_px},{_ass_color(color)},{_ass_color(hi)},{_ass_color(hi, 0xFF)},{_ass_color('#000000', 0xFF)},{cb},{ci},0,0,100,100,0,0,"
        f"3,12,0,{align},80,80,{margin_v},1",
        f"Style: CapCard,{cf},{size_px},{_ass_color(color)},{_ass_color(hi)},{ol_col},{back},{cb},{ci},0,0,100,100,0,0,"
        f"{border_style},{ow if border_style == 1 else 14},{shadow},2,80,80,{int(H * 0.41)},1",
        f"Style: CapTop,{cf},{size_px},{_ass_color(color)},{_ass_color(hi)},{ol_col},{back},{cb},{ci},0,0,100,100,0,0,"
        f"{border_style},{ow if border_style == 1 else 14},{shadow},8,80,80,{int(H * 0.14)},1",
        f"Style: CapDark,{cf},{size_px},{_ass_color(look.get('dark', '#1B1B1F'))},{_ass_color(hi)},{_ass_color('#000000', 0xFF)},{_ass_color('#000000', 0xFF)},{cb},{ci},0,0,100,100,0,0,"
        f"1,0,0,5,80,80,0,1",
        f"Style: Key,{cf},{int(size_px * float(look.get('key_scale', 2.8)))},{_ass_color(color)},{_ass_color(hi)},{ol_col},{back},{cb},{ci},0,0,100,100,-2,0,"
        f"{border_style},{ow if border_style == 1 else 14},{shadow},5,40,40,0,1",
        f"Style: KeyDark,{cf},{int(size_px * float(look.get('key_scale', 2.8)) * .86)},{_ass_color(look.get('dark', '#1B1B1F'))},{_ass_color(hi)},{_ass_color('#000000', 0xFF)},{_ass_color('#000000', 0xFF)},{cb},{ci},0,0,100,100,-2,0,"
        f"1,0,0,5,40,40,0,1",
        f"Style: Title,{tf},{t_size},{_ass_color(look.get('title_color', color))},{_ass_color(hi)},"
        f"{ol_col},{_ass_color('#000000', 0xA0) if shadow else _ass_color('#000000', 0x60)},{tb},{ti},0,0,100,100,0,0,1,{ow},{shadow},8,90,90,{int(H * 0.12)},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    if project.get("captions", True):
        kept = []
        for w in project["edl"]["words"]:
            if w["cut"]:
                continue
            s, e = map_time(w["start"], ranges), map_time(min(w["end"], w["start"] + 1.2), ranges)
            if s is None:
                continue
            kept.append((s, e if e is not None else s + 0.3, w["text"]))
        anim = look.get("anim", "pop")
        if anim == "punch":
            per = 1
        if anim == "lexicon":
            lexicon_captions(project, ranges, (W, H), look, lines)
            kept = []
        # a place Alina dragged on the preview: centre (x, y) and width w, as fractions of the frame
        CPOS, CML, CMR = _placed(look.get("cap_pos"), W, H)
        HI, TX, OL = _ass_color(hi), _ass_color(color), _ass_color(outline)
        # the spoken word, per animation (ASS \t with accel < 1 eases out; no ease-in on entrances)
        SPOKEN = {
            "pop": r"{\c" + HI + r"\fscx94\fscy94\t(0,90,0.5,\fscx108\fscy108)}",
            "bounce": r"{\c" + HI + r"\fscx70\fscy70\t(0,100,0.6,\fscx116\fscy116)\t(100,190,\fscx100\fscy100)}",
            "reveal": r"{\c" + HI + "}",
            "rise": r"{\c" + HI + "}",
            "box": r"{\c" + _ass_color(look.get("box_text", "#111111")) + r"\3c" + HI + r"\3a&H00&}",
            "glow": r"{\c" + HI + r"\3c" + HI + r"\bord7\blur9}",
            "punch": r"{\c" + HI + r"\fscx124\fscy124\t(0,140,0.5,\fscx100\fscy100)}",
            "slam": r"{\c" + HI + "}",
            "still": r"{\c" + HI + "}",
            "glowpop": r"{\c" + HI + "}",
        }.get(anim, r"{\c" + HI + r"\fscx108\fscy108}")
        GB = r"\blur7" if glow else ""          # the glow: a blurred light border
        groups = [kept[i:i + per] for i in range(0, len(kept), per)]
        for gi, g in enumerate(groups):
            g_end = groups[gi + 1][0][0] if gi + 1 < len(groups) else g[-1][1] + 0.3
            zone = next((z for a, b, z in project.get("_zones", []) if a <= g[0][0] < b), None)
            if zone == "hide":
                continue
            style = "Cap" if look.get("cap_pos") else {"above-card": "CapCard", "upper": "CapTop"}.get(zone, "Cap")
            if anim == "box":
                style = "CapBox"
            cs = lambda t: t.upper() if case == "upper" else t.lower() if case == "lower" else t
            if anim == "karaoke":
                # one line per group; the highlight fills each word while it is said (\kf: secondary → primary)
                ks = "".join(r"{\kf%d}" % max(1, round(((g[k + 1][0] if k + 1 < len(g) else min(e, g_end)) - s) * 100)) + _esc(cs(t)) + " "
                             for k, (s, e, t) in enumerate(g))
                lines.append(f"Dialogue: 0,{_ts(g[0][0])},{_ts(g_end)},{style},,{CML},{CMR},0,,{CPOS}{{\\1c{HI}\\2c{TX}}}{ks.strip()}")
                continue
            # the longest word of a group is its keyword (slam: it carries the colour block)
            if anim == "blurin":
                # Clean White: each word blurs in (14 px → 0, 0.2 s) when said; later words keep their place, invisible
                for k, (s, e, _) in enumerate(g):
                    e2 = g[k + 1][0] if k + 1 < len(g) else g_end
                    txt = ""
                    for kk, (_, _, t) in enumerate(g):
                        t = _esc(cs(t))
                        if kk < k:
                            txt += t + " "
                        elif kk == k:
                            txt += r"{\alpha&HFF&\blur14\t(0,200,0.5,\alpha&H00&" + (GB or r"\blur0") + ")}" + t + " "
                        else:
                            txt += r"{\alpha&HFF&}" + t + " "
                    lines.append(f"Dialogue: 0,{_ts(s)},{_ts(e2)},{style},,{CML},{CMR},0,,{CPOS}{{{GB}}}{txt.strip()}")
                continue
            key = max(range(len(g)), key=lambda k: len(g[k][2].strip(".,!?"))) if anim == "slam" else -1
            for k, (s, e, _) in enumerate(g):
                e2 = g[k + 1][0] if k + 1 < len(g) else g_end
                parts = []
                for kk, (_, _, t) in enumerate(g):
                    t = _esc(cs(t))
                    if anim == "reveal" and kk > k:
                        parts.append(r"{\alpha&HFF&}" + t + r"{\r}")          # not said yet: keeps its place, invisible
                    elif anim == "slam" and kk == key:
                        parts.append(r"{\c" + _ass_color(look.get("box_text", "#111111")) + r"\3c" + HI + r"\bord10\blur0}" + t + r"{\r}")
                    elif kk == k:
                        parts.append(SPOKEN + t + r"{\r}")
                    elif anim == "box":
                        parts.append(r"{\3a&HFF&}" + t + r"{\r}")
                    else:
                        parts.append(t)
                intro = ""
                if k == 0 and anim == "rise":
                    intro = r"{\fad(140,0)\fscy70\t(0,160,0.5,\fscy100)}"
                if k == 0 and anim == "slam":
                    intro = r"{\fscx130\fscy130\t(0,90,0.5,\fscx96\fscy96)\t(90,150,\fscx100\fscy100)}"
                if k == 0 and anim in ("pop", "bounce", "glow", "box", "still", "karaoke"):
                    intro = r"{\fad(60,0)}"
                if k == 0 and anim == "glowpop":
                    intro = r"{\fscx112\fscy112\t(0,90,\fscx100\fscy100)}"
                gtag = "{" + GB + "}" if GB else ""
                body = " ".join(parts)
                if GB:
                    body = body.replace("{\\r}", "{\\r" + GB + "}")
                lines.append(f"Dialogue: 0,{_ts(s)},{_ts(e2)},{style},,{CML},{CMR},0,,{CPOS}{gtag}{intro}{body}")
    if title.get("text"):
        # a title-type effect (big words of its own) takes the screen: the hook steps aside when it starts
        t_end = float(title.get("duration", 2.6))
        for e in project.get("effects", []):
            if e.get("status") != "removed" and e["effect"] in ("title-mask-rise", "zoom-through-text", "match-cut", "screen-push-digital"):
                t0 = map_time(e["at"], ranges)
                if t0 is not None and t0 < t_end:
                    t_end = max(0.4, t0)
        TPOS, TML, TMR = _placed(look.get("title_pos"), W, H)
        lines.append(f"Dialogue: 1,{_ts(0)},{_ts(t_end)},Title,,{TML},{TMR},0,,{TPOS}"
                     r"{\fad(0,200)" + (r"\blur7" if glow else "") + "}" + _esc(title["text"]))       # full strength on frame 1: the first frame is the cover
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def render(project, src, out_path, fmt="reel", work_dir=None, preview=False):
    work = Path(work_dir or Path(out_path).parent)
    work.mkdir(parents=True, exist_ok=True)
    total = project["source"]["duration"]
    ranges = project.get("ranges_override") or keep_ranges(project["edl"], total)
    W, H = SIZES[fmt]
    if preview:
        W, H = W // 2, H // 2
    zones = caption_zones(project, ranges)
    ass = build_ass(dict(project, _zones=zones), ranges, (W, H), work / f"captions_{fmt}.ass")

    # stage 1: the cut, cropped to 9:16 at full size (effects need 1080x1920)
    base = work / f"base_{fmt}.mp4"
    fc1 = []
    n = len(ranges)
    FW, FH = SIZES[fmt]
    fxp, fyp = face_point(src, project, work)        # the face, as a fraction of the source frame
    # jump cuts: at every join where something was cut out, alternate the framing between 1.0 and the pace's punch-in
    # (Medium 1.10, Very lively 1.15), centred on the face, so a cut reads as a camera change, not a glitch
    pin = project.get("punch_in") or (project.get("edl") or {}).get("punch_in") or 0
    # a style's director can ask for punch-ins at phrase changes (output times in `punches`) instead of at the joins:
    # the range is split there and the framing steps 1.0 <-> punch_in (a hard step, Clean White §3)
    segs = []                                   # (source a, source b, zoom, fade in, fade out)
    punches = sorted(float(t) for t in (project.get("punches") or []))
    z, out0, pk = 1.0, 0.0, 0
    for i, (a, b) in enumerate(ranges):
        if not punches and i and pin and a - ranges[i - 1][1] >= 0.3:
            z = pin if z == 1.0 else 1.0
        cur = a
        while punches and pk < len(punches) and pin and punches[pk] < out0 + (b - a) - .05:
            cut = a + (punches[pk] - out0)
            if cut - cur > .05:
                segs.append((cur, cut, z, cur == a, False))
                cur = cut
            z = pin if z == 1.0 else 1.0
            pk += 1
        segs.append((cur, b, z, cur == a, True))
        out0 += b - a
    ranges_v = segs
    n = len(segs)
    for i, (a, b, zm, fin, fout) in enumerate(segs):
        zw, zh = int(FW * zm) // 2 * 2, int(FH * zm) // 2 * 2
        # iPhone footage is stored sideways with a "rotate 90°" flag: ffmpeg already turns the frames upright, so the flag
        # must not travel into the output, or players rotate the upright picture a second time (sideways, squashed)
        fc1.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,sidedata=mode=delete:type=DISPLAYMATRIX,{sdr_vf(src)}"
                   f"scale={zw}:{zh}:force_original_aspect_ratio=increase,"
                   f"crop={FW}:{FH}:'max(0,min(iw-{FW},iw*{fxp:.4f}-{FW}/2))':'max(0,min(ih-{FH},ih*{fyp:.4f}-{FH}/2))',setsar=1,fps=30[v{i}]")
        af = (",afade=t=in:d=0.01" if fin else "") + (f",afade=t=out:st={max(0, b - a - 0.012):.3f}:d=0.012" if fout else "")
        fc1.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS{af}[a{i}]")
    tail = float(project.get("tail") or 0)       # hold the last frame (Cinema Lexicon close card: the slogan is read)
    if tail > 0:
        fc1.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vb0][ac0]")
        fc1.append(f"[vb0]tpad=stop_mode=clone:stop_duration={tail:.2f}[vb]")
        fc1.append(f"[ac0]apad=pad_dur={tail:.2f}[ac]")
    else:
        fc1.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vb][ac]")
    run(["-i", src, "-filter_complex", ";".join(fc1), "-map", "[vb]", "-map", "[ac]", "-c:v", "libx264", "-crf", "16",
         "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(base).replace(".mp4", ".mov")])
    base = Path(str(base).replace(".mp4", ".mov"))

    # stage 2: effects on words that the engine renders itself (text behind me, clones)
    fx_list = []
    for e in project.get("effects", []):
        if e.get("status") in ("removed",) or fmt not in ("reel", "story"):
            continue
        t = map_time(e["at"], ranges)
        if t is not None:
            fx_list.append({"effect": e["effect"], "out_at": t, "word": e.get("word"), "id": e.get("id"),
                            "params": e.get("params") or {}, "words": words_between(project, ranges, t, t + 3.0),
                            "images": project.get("_images", []), "attachments": project.get("_attachments", []),
                            "brand": project.get("_brand")})
    import effects as fxmod
    base_fx, fx_done, fx_skipped = fxmod.apply(base, fx_list, work / "fx")

    # stage 3: images on words, captions and hook, voice and sound effects
    inputs = ["-i", str(base_fx)]
    grade = next((g for g in (load_json(ROOT / "library" / "looks.json", {}) or {}).get("grades", [])
                  if g["id"] == project.get("grade")), None)
    gf = ("," + grade["ffmpeg"]) if grade and grade.get("ffmpeg") else ""
    fc = [f"[0:v]sidedata=mode=delete:type=DISPLAYMATRIX,scale={W}:{H},setsar=1{gf}[vs]", "[0:a]anull[ac]"]
    last_v = "vs"

    # images on the words that name them (the native 'word-image-pop' effect)
    in_idx = 1
    for k, ov in enumerate(project.get("overlays", [])):
        if ov.get("status") == "removed" or not ov.get("image"):
            continue
        t0 = map_time(ov["at"], ranges)
        if t0 is None:
            continue
        t1 = t0 + float(ov.get("hold", 1.6))
        if Path(ov["image"]).suffix.lower() == ".gif":
            # a reaction GIF from Memes (GIPHY): an animated card on the phrase, looping for its hold, away from the face
            if not Path(ov["image"]).exists():
                continue
            inputs += ["-ignore_loop", "0", "-t", f"{t1 - t0 + 0.1:.2f}", "-i", ov["image"]]
            iw = int(W * float(ov.get("scale", 0.4)))
            x = {"left": "W*0.06", "right": "W-w-W*0.06", "center": "(W-w)/2"}[ov.get("x", "right")]
            y = {"top": "H*0.10", "upper": "H*0.20", "middle": "(H-h)/2"}[ov.get("y", "upper")]
            fit = f"scale=w={iw}:h={int(H * float(ov['max_h']))}:force_original_aspect_ratio=decrease,scale=trunc(iw/2)*2:trunc(ih/2)*2" \
                if ov.get("max_h") else f"scale={iw}:-2"          # a meme card never grows down over her face
            # no white frame (Alina, 25 Nov 2026: "don't put the gifs in this white frame"): the GIF itself, tilted
            fc.append(f"[{in_idx}:v]setpts=PTS-STARTPTS+{t0:.3f}/TB,{fit},format=rgba,"
                      f"rotate={ov.get('tilt', -3)}*PI/180:c=none:ow=rotw(iw):oh=roth(ih)[im{k}]")
            fc.append(f"[{last_v}][im{k}]overlay={x}:{y}:eof_action=pass:enable='between(t,{t0:.2f},{t1:.2f})'[ov{k}]")
            last_v = f"ov{k}"
            in_idx += 1
            continue
        if Path(ov["image"]).suffix.lower() in VIDEO_EXT:
            # an example clip (Cinema Lexicon): full frame over the take, cut in on the phrase; the voice goes on
            if not Path(ov["image"]).exists():
                continue
            ms = float(ov.get("media_start", 0))
            inputs += ["-ss", f"{ms:.2f}", "-t", f"{t1 - t0 + 0.2:.2f}", "-i", ov["image"]]
            fx = max(0.0, min(1.0, float(ov.get("focus", .5))))
            fc.append(f"[{in_idx}:v]setpts=PTS-STARTPTS+{t0:.3f}/TB,scale={W}:{H}:force_original_aspect_ratio=increase,"
                      f"crop={W}:{H}:(iw-{W})*{fx:.3f}:(ih-{H})/2,setsar=1,format=yuv420p[im{k}]")
            fc.append(f"[{last_v}][im{k}]overlay=0:0:eof_action=pass:enable='between(t,{t0:.3f},{t1 - 0.001:.3f})'[ov{k}]")
            last_v = f"ov{k}"
            in_idx += 1
            continue
        inputs += ["-loop", "1", "-t", f"{t1 + 0.1:.2f}", "-i", ov["image"]]
        iw = int(W * float(ov.get("scale", 0.42)))
        x = {"left": "W*0.06", "right": "W-w-W*0.06", "center": "(W-w)/2"}[ov.get("x", "right")]
        y = {"top": "H*0.10", "upper": "H*0.20", "middle": "(H-h)/2"}[ov.get("y", "upper")]
        frame = "format=rgba," if ov.get("cutout") else "pad=iw+16:ih+16:8:8:white,"     # a cut-out PNG: no white frame
        fit = f"scale=w={iw}:h={int(H * float(ov['max_h']))}:force_original_aspect_ratio=decrease" if ov.get("max_h") else f"scale={iw}:-1"
        fc.append(f"[{in_idx}:v]{fit},{frame}rotate={ov.get('tilt', -3)}*PI/180:c=none:"
                  f"ow=rotw(iw):oh=roth(ih),format=rgba[im{k}]")
        fc.append(f"[{last_v}][im{k}]overlay={x}:{y}:enable='between(t,{t0:.2f},{t1:.2f})'[ov{k}]")
        last_v = f"ov{k}"
        in_idx += 1

    fc.append(f"[{last_v}]ass='{ass}':fontsdir='{FONTS}'[vout]")

    # voice: light denoise + loudness; sound effects mixed under it
    lufs = float(project.get("lufs") or (project.get("edl") or {}).get("lufs") or -14)
    fc.append(f"[ac]highpass=f=70,afftdn=nf=-25,loudnorm=I={lufs}:TP=-1.5:LRA=11[voice]")
    mix = ["[voice]"]
    for k, s in enumerate(project.get("sfx", [])):
        if s.get("status") == "removed":
            continue
        t0 = map_time(s["at"], ranges) if s.get("clock", "source") == "source" else s["at"]
        if t0 is None:
            continue
        inputs += ["-i", str(SFX / s["file"])]
        ms = int(t0 * 1000)
        fc.append(f"[{in_idx}:a]volume={s.get('volume', 0.5)},adelay={ms}|{ms}[sx{k}]")
        mix.append(f"[sx{k}]")
        in_idx += 1
    # the style's music bed under everything (library/music.json), faded in and out
    mu = project.get("music") or {}
    if mu.get("id") and mu.get("status") != "removed":
        meta = next((m for m in load_json(ROOT / "library" / "music.json", []) if m["id"] == mu["id"]), None)
        if meta:
            total_out = sum(b - a for a, b in ranges) + float(project.get("tail") or 0)
            # looped, so a track shorter than the reel keeps going (it starts at the track's body, `start`)
            inputs += ["-stream_loop", "-1", "-ss", f"{float(mu.get('start', meta.get('start', 0))):.2f}", "-i", str(ROOT / "library" / "music" / meta["file"])]
            fo = float(mu.get("fade_out", .8))
            fc.append(f"[{in_idx}:a]aresample=48000,atrim=0:{total_out:.3f},asetpts=PTS-STARTPTS,volume={float(mu.get('volume', .12))},"
                      f"afade=t=in:d={float(mu.get('fade_in', .3))},afade=t=out:st={max(0, total_out - fo):.3f}:d={fo}[mus]")
            mix.append("[mus]")
            in_idx += 1
    if len(mix) > 1:
        # a soft limiter at −1.5 dBFS: sound effects on top of the levelled voice must never clip
        fc.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.84:attack=2:release=40:level=false[aout]")
    else:
        fc.append("[voice]anull[aout]")

    args = inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
                     "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "28" if preview else "19",
                     "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", out_path]
    run(args)
    return {"out": str(out_path), "ranges": ranges, "duration": round(sum(b - a for a, b in ranges) + float(project.get("tail") or 0), 2),
            "effects_done": [e.get("id") for e in fx_done], "effects_for_hyperframes": [e.get("id") for e in fx_skipped],
            "effects_skipped": [{"id": e.get("id"), "effect": e["effect"], "reason": e.get("reason", "")} for e in fx_skipped]}


def still(src, t, out_path, size=(1080, 1350)):
    W, H = size
    run(["-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf",
         f"{sdr_vf(src)}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-q:v", "3", out_path])
    return out_path
