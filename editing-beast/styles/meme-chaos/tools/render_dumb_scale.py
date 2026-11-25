"""Gen Z edit of ~/Desktop/IMG_6003.MOV (Teammate A, Teammate B, Alina: tongue contest + Moldovan dumb scale).

Run with the engine venv:  ../vetto-video-engine/.venv/bin/python render.py [--stills 1.0,22.2,63.4]
Times below are SOURCE times (seconds in the original take). Cuts are applied at the end.
"""
import math, subprocess, sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).parent
ENGINE = HERE.parent / "vetto-video-engine"
FF = str(ENGINE / "bin" / "ffmpeg")
FONTS = ENGINE / "library" / "fonts"
SRC = HERE / "work" / "proxy.mp4"           # 1080x1920 30 fps copy of the iPhone take
EXPLO = HERE / "downloads" / "refs" / "capcut_explosion.mp4"
LOGO = HERE / "downloads" / "logo" / "prosus-logo.png"
SFX = HERE / "sfx"
OUT = HERE / "prosus-dumb-scale-edit.mp4"
W, H, FPS = 1080, 1920, 30
DUR = 71.28

# ---------------------------------------------------------------- the edit (source times)
HOOK = ["who's the dumbest", "in our office?"]   # Claude's pick, Alina to approve
HOOK_T = (0.0, 4.6)

CUTS_KEEP = [(0.0, 30.0), (32.8, 37.8), (40.3, DUR)]   # removes 2 silent waits

CAPTIONS = [
    (0.00, 0.62, "okay"), (0.64, 1.26, "hi guys"), (1.28, 2.04, "my name is Teammate A"),
    (2.06, 3.22, "this is Teammate B"), (3.24, 4.60, "guys"), (4.70, 5.66, "this is"),
    (5.68, 6.80, "Alina"), (6.84, 8.30, "and today we're gonna"), (8.32, 9.42, "do a contest"),
    (9.44, 10.60, "okay"), (10.66, 12.38, "so first one"), (12.40, 13.40, "Alina"),
    (16.10, 17.78, "do we have to"), (17.80, 18.56, "go easy or hard"), (18.58, 19.54, "like the hardest?"),
    (19.56, 20.62, "it's a contest"), (20.64, 21.50, "it's a contest, okay"),
    (24.10, 24.54, "okay"), (24.56, 25.40, "here you go"),
    (26.74, 27.70, "you can give them"), (27.72, 28.60, "applause"),
    (29.54, 30.00, "okay"),
    (47.14, 48.12, "okay guys"), (48.14, 49.20, "now all three"),
    (51.94, 53.90, "this is called"), (53.92, 54.70, "the dumb scale"),
    (54.74, 55.30, "if you sit"), (55.32, 56.00, "like this"), (56.02, 56.88, "in Moldova people say"),
    (56.90, 57.96, "it's a dumb scale"), (57.98, 58.90, "like from the tallest"), (58.92, 59.16, "to the..."),
    (59.18, 60.70, "I guess you're the dumbest"),
    (60.90, 61.84, "this is how the company"), (61.86, 62.60, "Prosus..."),
    (64.68, 65.26, "okay"), (65.28, 65.94, "one"), (65.96, 66.32, "two"), (66.34, 67.40, "three!"),
]

# sound effects: (file, source time, volume, max length or None)
SOUNDS = [
    ("spawn.wav", 3.20, 0.55, None),        # Teammate B pops into frame
    ("spawn.wav", 5.55, 0.55, None),        # Alina appears
    ("explosion.wav", 22.10, 0.95, None),   # Alina's tongue move
    ("applause.wav", 27.72, 0.55, 2.2),     # "you can give them applause" + claps
    ("vine_boom.wav", 33.15, 0.5, None),   # Teammate A's tongue move
    ("applause.wav", 35.85, 0.55, 1.9),     # claps after Teammate A
    ("spawn.wav", 40.35, 0.55, None),       # Teammate B walks in
    ("windows_xp.wav", 42.62, 0.75, None),  # Teammate B (in blue) does the pose
    ("applause.wav", 44.55, 0.60, None),    # everyone claps
    ("vine_boom.wav", 54.08, 0.5, None),   # "the dumb scale"
    ("faa.wav", 63.70, 0.85, None),         # Prosus crashes off screen
]
MUSIC_SWITCH = 54.32   # after "the dumb scale": Island Medium -> elevator music
ISLAND_VOL, ELEVATOR_VOL = 0.30, 0.45

# zoom punches: (start, end, zoom, centre x, centre y, kind)
ZOOMS = [
    (22.10, 22.95, 1.18, 434, 1056, "punch"),   # explosion
    (33.15, 34.15, 1.28, 540, 800, "punch"),    # Teammate A pose
    (42.62, 43.60, 1.22, 540, 820, "push"),     # Teammate B pose (XP)
    (54.08, 54.70, 1.15, 560, 900, "punch"),    # dumb scale
]
SHAKE = (22.10, 22.80)
FLASH = (22.08, 22.22)
EXPLO_ALIGN = (22.12, 1.05)    # source time where the burst hits, burst time inside the CapCut clip
EXPLO_CENTER = (434, 1056)     # Alina's face at 22.2 s (Apple Vision)

# Prosus crash line: logo pops on "Prosus" where Alina's hand is, line follows her arm sweep down-left
PROSUS_IN, LINE_FADE = 61.86, (64.45, 64.90)
HAND_KEYS = [  # (time, x, y) read from frames, hand of Alina
    (63.10, 575, 835), (63.20, 592, 1005), (63.30, 585, 1080), (63.40, 505, 1200),
    (63.50, 335, 1275), (63.60, 180, 1350), (63.75, 40, 1450), (63.98, -140, 1590),
]

# ---------------------------------------------------------------- helpers
def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

def ease_out_back(x, s=1.9):
    x = min(max(x, 0), 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2

def ease_out(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3

def smooth(x):
    x = min(max(x, 0), 1)
    return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- hook title (wavy, floating, sparkles)
HOOK_FONT = font("Coiny-Regular.ttf", 92)
HOOK_FILL, HOOK_EDGE = (255, 255, 255, 255), (28, 84, 40, 255)   # white + dark green edge like the reference

def glyph(ch):
    pad = 30
    l, t, r, b = HOOK_FONT.getbbox(ch, stroke_width=9)
    im = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pad - l + 4, pad - t + 7), ch, font=HOOK_FONT, fill=(0, 0, 0, 120), stroke_width=9, stroke_fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text((pad - l, pad - t), ch, font=HOOK_FONT, fill=HOOK_FILL, stroke_width=9, stroke_fill=HOOK_EDGE)
    return im, pad - l, pad - t

HOOK_LINES = []
for li, line in enumerate(HOOK):
    total = HOOK_FONT.getlength(line)
    x0 = (W - total) / 2
    chars = []
    for i, ch in enumerate(line):
        if ch == " ":
            continue
        g, ox, oy = glyph(ch)
        chars.append((g, x0 + HOOK_FONT.getlength(line[:i]) - ox, -oy, i))
    HOOK_LINES.append(chars)

def sparkle(size, alpha):
    s = int(size * 2.6)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    c, r, k = s / 2, size, size * 0.18
    pts = [(c, c - r), (c + k, c - k), (c + r, c), (c + k, c + k), (c, c + r), (c - k, c + k), (c - r, c), (c - k, c - k)]
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon(pts, fill=(255, 245, 190, int(200 * alpha)))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(size * 0.25)))
    ImageDraw.Draw(im).polygon(pts, fill=(255, 255, 255, int(255 * alpha)))
    return im

SPARKS = [(x, y + 490, s, ph, sp) for x, y, s, ph, sp in [  # (x, y, size, phase, speed)
    (150, 250, 30, 0.0, 1.6), (930, 235, 26, 1.7, 1.9), (110, 470, 22, 3.1, 1.4), (965, 455, 32, 0.8, 1.7),
    (520, 195, 20, 2.4, 2.1), (300, 545, 18, 4.0, 1.8), (780, 560, 22, 5.0, 1.5), (60, 360, 16, 1.2, 2.3),
    (1020, 345, 18, 2.9, 2.0), (690, 200, 14, 4.4, 2.4),
]]

def draw_hook(frame, t):
    a, b = HOOK_T
    if not (a <= t < b):
        return
    life = t - a
    out = smooth((b - t) / 0.4)                       # fade + float away at the end
    fy = 10 * math.sin(2 * math.pi * 0.45 * t) - (1 - out) * 60
    fx = 8 * math.sin(2 * math.pi * 0.3 * t + 1)
    base_y = [790, 900]
    for li, chars in enumerate(HOOK_LINES):
        for (g, gx, gy, i) in chars:
            k = li * 18 + i
            appear = ease_out_back((life - 0.03 * k) / 0.35)
            if appear <= 0.01:
                continue
            ph = 2 * math.pi * 1.0 * t - k * 0.55
            dy = 16 * math.sin(ph)
            rot = 6 * math.sin(ph + 1.2)
            gg = g.rotate(rot, resample=Image.BICUBIC, expand=False)
            if appear != 1:
                sw, shh = max(1, int(gg.width * appear)), max(1, int(gg.height * appear))
                gg = gg.resize((sw, shh), Image.BICUBIC)
            if out < 1:
                al = gg.getchannel("A").point(lambda v: int(v * out))
                gg.putalpha(al)
            cx = gx + g.width / 2 + fx
            cy = base_y[li] + gy + g.height / 2 + dy + fy
            frame.alpha_composite(gg, (int(cx - gg.width / 2), int(cy - gg.height / 2)))
    for (x, y, size, ph, sp) in SPARKS:
        tw = 0.5 + 0.5 * math.sin(2 * math.pi * sp * t * 0.5 + ph)
        tw = tw ** 2 * min(1, max(0, (life - 0.2) / 0.3)) * out
        if tw < 0.05:
            continue
        sz = size * (0.5 + 0.7 * tw)
        sp_im = sparkle(sz, tw)
        sp_im = sp_im.rotate(25 * math.sin(t * 2 + ph), resample=Image.BICUBIC)
        frame.alpha_composite(sp_im, (int(x + fx - sp_im.width / 2), int(y + fy - sp_im.height / 2)))

# ---------------------------------------------------------------- captions (simple white sans)
CAP_FONT = font("TikTokSans-Bold.ttf", 66)
CAP_Y = 1440
_cap_cache = {}

def caption_img(text):
    if text in _cap_cache:
        return _cap_cache[text]
    l, t, r, b = CAP_FONT.getbbox(text, stroke_width=3)
    pad = 24
    im = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pad - l, pad - t + 4), text, font=CAP_FONT, fill=(0, 0, 0, 170), stroke_width=6, stroke_fill=(0, 0, 0, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=CAP_FONT, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(20, 20, 20, 255))
    _cap_cache[text] = im
    return im

def draw_caption(frame, t):
    for a, b, text in CAPTIONS:
        if a <= t < b:
            im = caption_img(text)
            p = ease_out_back((t - a) / 0.12, 1.4)
            s = 0.85 + 0.15 * p
            if s != 1:
                im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
            frame.alpha_composite(im, (int(W / 2 - im.width / 2), int(CAP_Y - im.height / 2)))
            return

# ---------------------------------------------------------------- explosion (CapCut green screen)
def load_explosion():
    raw = subprocess.run([FF, "-v", "error", "-i", str(EXPLO), "-vf", f"fps={FPS},scale=1350:2400", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    n = len(raw) // (1350 * 2400 * 3)
    return np.frombuffer(raw, np.uint8)[: n * 1350 * 2400 * 3].reshape(n, 2400, 1350, 3)

EXPLO_FRAMES = None

def draw_explosion(frame, t):
    global EXPLO_FRAMES
    ct = t - EXPLO_ALIGN[0] + EXPLO_ALIGN[1]
    if not (0.95 <= ct < 3.75):
        return
    if EXPLO_FRAMES is None:
        EXPLO_FRAMES = load_explosion()
    fi = min(int(ct * FPS), len(EXPLO_FRAMES) - 1)
    C = EXPLO_FRAMES[fi].astype(np.float32)
    K = np.array([4, 185, 4], np.float32)
    # the screen has almost no red, the fire is always red-heavy: red tells how much fire covers the pixel
    alpha = np.clip((C[..., 0] - 12) / 215.0, 0, 1) ** 0.85
    # the CapCut watermark sits above the frame edge with this placement, so it never shows
    a3 = np.maximum(alpha, 1e-3)[..., None]
    fg = (C - (1 - a3) * K) / a3                                # un-mix the green screen
    fg[..., 1] = np.minimum(fg[..., 1], np.maximum(fg[..., 0], fg[..., 2]))   # despill what is left
    rgba = np.dstack([np.clip(fg, 0, 255).astype(np.uint8), (np.clip(alpha, 0, 1) * 255).astype(np.uint8)])
    ov = Image.fromarray(rgba, "RGBA")
    cx, cy = EXPLO_CENTER
    frame.alpha_composite(ov, (int(cx - 1350 / 2), int(cy - 2400 / 2)))

# ---------------------------------------------------------------- Prosus crash line
def build_badge():
    logo = Image.open(LOGO).convert("RGBA")
    a = np.array(logo).astype(np.int16)
    white = (a[..., 0] > 235) & (a[..., 1] > 235) & (a[..., 2] > 235)
    a[white, 3] = 0
    logo = Image.fromarray(a.astype(np.uint8), "RGBA").resize((128, 127), Image.LANCZOS)
    D = 190
    im = Image.new("RGBA", (D + 40, D + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([24, 30, 24 + D - 8, 30 + D - 8], fill=(0, 0, 0, 130))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).ellipse([20, 20, 20 + D - 8, 20 + D - 8], fill=(255, 255, 255, 255), outline=(230, 30, 30, 255), width=8)
    im.alpha_composite(logo, (20 + (D - 8 - 128) // 2, 20 + (D - 8 - 127) // 2 + 2))
    return im

BADGE = build_badge()

def catmull(points, n=24):
    out = []
    P = [points[0]] + points + [points[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.array, (P[i - 1], P[i], P[i + 1], P[i + 2]))
        for k in range(n):
            s = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(np.array(points[-1], float))
    return np.array(out)

KEY_PTS = [(x, y) for _, x, y in HAND_KEYS]
BASE = catmull(KEY_PTS)
SEG = np.linalg.norm(np.diff(BASE, axis=0), axis=1)
CUM = np.concatenate([[0], np.cumsum(SEG)])
KEY_L = [CUM[i * 24] for i in range(len(KEY_PTS))]
KEY_T = [t for t, _, _ in HAND_KEYS]

def base_at(L):
    L = min(max(L, 0), CUM[-1])
    i = min(np.searchsorted(CUM, L, side="right") - 1, len(SEG) - 1)
    f = (L - CUM[i]) / max(SEG[i], 1e-6)
    p = BASE[i] + (BASE[i + 1] - BASE[i]) * f
    tan = (BASE[i + 1] - BASE[i]) / max(SEG[i], 1e-6)
    return p, tan

# zigzag "stock chart crash" vertices along the arm path
ZIG = []
step, amp = 62, 30
for k, L in enumerate(np.arange(0, CUM[-1] + step, step)):
    p, tan = base_at(L)
    nrm = np.array([-tan[1], tan[0]])
    off = 0 if k == 0 else (amp if k % 2 else -amp * 0.6)
    ZIG.append((L, p + nrm * off))

def zig_at(L):
    for (l0, p0), (l1, p1) in zip(ZIG, ZIG[1:]):
        if L <= l1:
            f = (L - l0) / max(l1 - l0, 1e-6)
            return p0 + (p1 - p0) * f
    return ZIG[-1][1]

def draw_prosus(frame, t):
    if not (PROSUS_IN <= t < LINE_FADE[1]):
        return
    fade = 1 - smooth((t - LINE_FADE[0]) / (LINE_FADE[1] - LINE_FADE[0]))
    L = float(np.interp(t, KEY_T, KEY_L, left=0, right=KEY_L[-1]))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if L > 2:
        pts = [tuple(p) for l, p in ZIG if l < L] + [tuple(zig_at(L))]
        if len(pts) >= 2:
            jit = [(x + 3 * math.sin(i * 2.1), y + 3 * math.cos(i * 1.7)) for i, (x, y) in enumerate(pts)]
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).line([(x + 5, y + 8) for x, y in pts], fill=(0, 0, 0, 120), width=26, joint="curve")
            layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
            d = ImageDraw.Draw(layer)
            d.line(pts, fill=(255, 255, 255, 255), width=28, joint="curve")
            d.line(pts, fill=(235, 25, 25, 255), width=17, joint="curve")
            d.line(jit, fill=(255, 90, 90, 150), width=5, joint="curve")   # marker-sketch highlight
            for x, y in pts[:1]:
                d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(235, 25, 25, 255), outline=(255, 255, 255, 255), width=5)
    # logo badge rides the tip of the line
    tip = zig_at(L) if L > 2 else np.array(KEY_PTS[0], float)
    pop = ease_out_back((t - PROSUS_IN) / 0.35, 2.2)
    bob = 8 * math.sin(2 * math.pi * 1.4 * t) if L <= 2 else 0
    _, tan = base_at(L)
    ang = -math.degrees(math.atan2(tan[1], tan[0])) * 0.25 if L > 2 else 6 * math.sin(2 * math.pi * 0.9 * t)
    bd = BADGE.rotate(ang + (25 if L > 2 else 0) * min(1, L / 300), resample=Image.BICUBIC, expand=True)
    s = max(0.01, pop) * 0.9
    bd = bd.resize((max(1, int(bd.width * s)), max(1, int(bd.height * s))), Image.BICUBIC)
    layer.alpha_composite(bd, (int(tip[0] - bd.width / 2), int(tip[1] - bd.height / 2 - 6 + bob)))
    if fade < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * fade)))
    frame.alpha_composite(layer)

# ---------------------------------------------------------------- camera moves
def camera(img, t):
    z, cx, cy = 1.0, W / 2, H / 2
    for a, b, zm, x, y, kind in ZOOMS:
        if a <= t < b:
            if kind == "punch":
                k = ease_out((t - a) / 0.08) * (1 - smooth((t - (b - 0.15)) / 0.15))
            else:
                k = ease_out((t - a) / (b - a)) * (1 - smooth((t - (b - 0.12)) / 0.12))
            z, cx, cy = 1 + (zm - 1) * k, x, y
    dx = dy = 0.0
    if SHAKE[0] <= t < SHAKE[1]:
        amp = 26 * (1 - (t - SHAKE[0]) / (SHAKE[1] - SHAKE[0]))
        dx, dy = amp * math.sin(t * 97), amp * math.cos(t * 83)
    if z == 1.0 and dx == 0 and dy == 0:
        return img
    z = max(z, 1.06) if dx or dy else z
    cw, ch = W / z, H / z
    x0 = min(max(cx - cw / 2 + dx, 0), W - cw)
    y0 = min(max(cy - ch / 2 + dy, 0), H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def flash(frame, t):
    if FLASH[0] <= t < FLASH[1]:
        k = 1 - (t - FLASH[0]) / (FLASH[1] - FLASH[0])
        frame.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 230, int(220 * k))))

# ---------------------------------------------------------------- disco lights on Teammate A's move
DISCO_T = (33.10, 34.45)   # Teammate A: hands up at 33.15, down by 34.3
DISCO_COLS = [(255, 40, 200), (40, 220, 255), (255, 230, 40), (60, 255, 90), (120, 70, 255), (255, 70, 50)]
BALL_C, BALL_R = (540, 150), 78

def build_ball():
    s = BALL_R * 2 + 8
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    rng = np.random.default_rng(7)
    step = 13
    for yy in range(0, s, step):
        for xx in range(0, s, step):
            if (xx + step / 2 - c) ** 2 + (yy + step / 2 - c) ** 2 < (BALL_R - 2) ** 2:
                v = int(rng.uniform(110, 245))
                d.rectangle([xx, yy, xx + step - 2, yy + step - 2], fill=(v, v, min(255, v + 15), 255))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse([4, 4, s - 4, s - 4], fill=255)
    im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel("A")), np.array(mask))))
    return im

BALL = build_ball()

def disco(img, t):
    a, b = DISCO_T
    if not (a <= t < b):
        return img
    k = smooth((t - a) / 0.10) * (1 - smooth((t - (b - 0.25)) / 0.25))
    lw, lh = W // 2, H // 2
    light = Image.new("RGB", (lw, lh), (0, 0, 0))
    d = ImageDraw.Draw(light)
    ox, oy = BALL_C[0] / 2, BALL_C[1] / 2
    # rotating colour beams from the ball
    for i in range(6):
        ang = math.pi / 2 + 1.1 * math.sin(t * 2.6 + i * 1.05) + (i - 2.5) * 0.32
        half = 0.07
        L = 1400
        p1 = (ox + L * math.cos(ang - half), oy + L * math.sin(ang - half))
        p2 = (ox + L * math.cos(ang + half), oy + L * math.sin(ang + half))
        col = DISCO_COLS[(i + int(t * 6)) % 6]
        d.polygon([(ox, oy), p1, p2], fill=tuple(int(c * 0.55) for c in col))
    # moving colour spots on the walls and Teammate A
    for i in range(7):
        sx = lw / 2 + lw * 0.45 * math.sin(t * (2.1 + 0.3 * i) + i * 2.3)
        sy = lh * 0.45 + lh * 0.30 * math.sin(t * (1.7 + 0.25 * i) + i * 1.3)
        r = 34 + 10 * (i % 3)
        d.ellipse([sx - r, sy - r * 0.8, sx + r, sy + r * 0.8], fill=tuple(int(c * 0.5) for c in DISCO_COLS[(i + int(t * 4)) % 6]))
    light = light.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    base = np.asarray(img.convert("RGB"), np.float32) / 255
    li = np.asarray(light, np.float32) / 255
    strobe = 0.85 + 0.15 * math.sin(t * 40)
    dark = base * (1 - 0.45 * k)                       # dim the office
    lit = 1 - (1 - dark) * (1 - li * k * strobe * 1.25)  # screen the coloured light on top
    out = Image.fromarray((np.clip(lit, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    # the disco ball, dropping in on a string
    drop = ease_out_back(min(1, (t - a) / 0.25), 1.4) if k > 0 else 0
    cy = int(-BALL_R + (BALL_C[1] + BALL_R) * drop)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).line([(BALL_C[0], 0), (BALL_C[0], cy - BALL_R)], fill=(200, 200, 200, 255), width=4)
    ball = BALL.rotate(math.degrees(t * 3) % 360, resample=Image.BICUBIC)
    layer.alpha_composite(ball, (BALL_C[0] - ball.width // 2, cy - ball.height // 2))
    for j, (gx, gy, ph) in enumerate([(-30, -25, 0), (28, 10, 1.9), (-8, 35, 3.7)]):
        s = 0.5 + 0.5 * math.sin(t * 14 + ph)
        if s > 0.2:
            sp = sparkle(18, s)
            layer.alpha_composite(sp, (BALL_C[0] + gx - sp.width // 2, cy + gy - sp.height // 2))
    if k < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * k)))
    out.alpha_composite(layer)
    return out

def render_frame(rgb, t):
    img = camera(Image.fromarray(rgb, "RGB"), t).convert("RGBA")
    img = disco(img, t)
    draw_explosion(img, t)
    flash(img, t)
    draw_prosus(img, t)
    draw_caption(img, t)
    draw_hook(img, t)
    return img.convert("RGB")

# ---------------------------------------------------------------- audio
def build_audio(path):
    inputs, chains, labels = ["-i", str(SRC)], [], []
    chains.append("[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=80,acompressor=threshold=-26dB:ratio=3:attack=5:release=150:makeup=2,volume=2.0[voice]")
    for k, (f, at, vol, maxlen) in enumerate(SOUNDS):
        inputs += ["-i", str(SFX / f)]
        cut = f",atrim=0:{maxlen},afade=t=out:st={maxlen - 0.35}:d=0.35" if maxlen else ""
        ms = int(at * 1000)
        chains.append(f"[{k + 1}:a]aresample=48000{cut},volume={vol},adelay={ms}|{ms}[s{k}]")
        labels.append(f"[s{k}]")
    chains.append(f"[voice]{''.join(labels)}amix=inputs={len(labels) + 1}:normalize=0:duration=first[aout]")
    subprocess.run([FF, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chains), "-map", "[aout]", "-c:a", "pcm_s16le", str(path)], check=True)

def out_time(src_t):
    o = 0.0
    for a, b in CUTS_KEEP:
        if src_t < a:
            return o
        if src_t <= b:
            return o + src_t - a
        o += b - a
    return o

def finish(video_full, audio_full):
    n = len(CUTS_KEEP)
    parts = []
    for i, (a, b) in enumerate(CUTS_KEEP):
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]")
    cat = "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]"
    total = out_time(DUR)
    sw = out_time(MUSIC_SWITCH)
    music = (f"[2:a]aresample=48000,aloop=loop=-1:size=2147483647,atrim=0:{sw + 0.4},"
             f"afade=t=out:st={sw - 0.25}:d=0.5,volume={ISLAND_VOL}[m1];"
             f"[3:a]aresample=48000,afade=t=in:st=0:d=0.4,volume={ELEVATOR_VOL},atrim=0:{total - sw},"
             f"afade=t=out:st={total - sw - 1.2}:d=1.2,adelay={int(sw * 1000)}|{int(sw * 1000)}[m2];"
             f"[ac][m1][m2]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[afinal]")
    island = SFX / "island_loop.wav"
    # seamless-ish loop of the 16 s Island Medium clip
    subprocess.run([FF, "-y", "-v", "error", "-stream_loop", "6", "-i", str(SFX / "island_medium.wav"), "-t", "80", str(island)], check=True)
    elev = HERE / "downloads" / "audio" / "xy_NKN75Jhw.wav"
    subprocess.run([FF, "-y", "-v", "error", "-i", str(video_full), "-i", str(audio_full), "-i", str(island), "-i", str(elev),
                    "-filter_complex", ";".join(parts) + ";" + cat + ";" + music,
                    "-map", "[vc]", "-map", "[afinal]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)], check=True)

# ---------------------------------------------------------------- main
def main():
    stills = None
    if "--stills" in sys.argv:
        stills = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1].split(",")]
        (HERE / "work" / "stills").mkdir(exist_ok=True)
        for t in stills:
            raw = subprocess.run([FF, "-v", "error", "-ss", str(t), "-i", str(SRC), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            rgb = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
            render_frame(rgb, t).save(HERE / "work" / "stills" / f"{t:06.2f}.jpg", quality=88)
        return
    vfull = HERE / "work" / "overlay_full.mp4"
    afull = HERE / "work" / "audio_full.wav"
    build_audio(afull)
    dec = subprocess.Popen([FF, "-v", "error", "-i", str(SRC), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", str(vfull)], stdin=subprocess.PIPE)
    i, size = 0, W * H * 3
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        t = i / FPS
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        enc.stdin.write(render_frame(rgb, t).tobytes())
        i += 1
        if i % 300 == 0:
            print(f"{t:.1f}s", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()
    finish(vfull, afull)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
