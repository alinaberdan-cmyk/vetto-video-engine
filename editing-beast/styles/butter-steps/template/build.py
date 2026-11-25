"""BS01 — first Butter Steps edit (styles/butter-steps/STYLE.md).
Alina's feedmeplzthanks "dare you to try this app" selfie take + the clean app screen recording.
Run: python -I build.py prep   (ffmpeg: rough cut, card clips, thumbs)   then   python -I build.py html"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

FF = os.environ.get("FFMPEG", "ffmpeg")      # any ffmpeg 6+
HERE = os.path.dirname(os.path.abspath(__file__))
TAKE, SCREEN = f"{HERE}/raw/take.MOV", f"{HERE}/raw/screen.mp4"
A = f"{HERE}/hf/assets"
EDL = json.load(open(f"{HERE}/work/edl.json"))           # [src_in, src_out, out_start]
WORDS = [(w["s"], w["e"], w["w"].strip()) for s in json.load(open(f"{HERE}/analysis/transcript.json"))["segments"] for w in s["words"]]
DUR = round(EDL[-1][2] + EDL[-1][1] - EDL[-1][0], 3)

def O(t):
    """source time -> output time (a time inside a removed pause snaps to the next segment)."""
    for a, b, o in EDL:
        if t < a: return o
        if t <= b: return round(o + t - a, 3)
    return DUR

def run(cmd): subprocess.run(cmd, check=True)

# ---------------- cards: (id, sr_in, sr_out_or_None, crop box in SR px, src_start, src_end) ----------------
CARD_MAX_W, CARD_MAX_H = 950, 620
CARDS = [
    # STEP 1: the mood pills falling in (app intro animation)
    ("k_pills",    2.00, 10.0, (0, 1140, 1206, 2340), 9.70, 16.00),
    # "it finds food based on your cravings" -> scouting loader
    ("k_scout",   11.00, 17.8, (0, 1110, 1206, 1960), 16.00, 18.10),
    # STEP 2: "look how many options" -> deck flicking
    ("k_deck",    19.00, 21.0, (0, 500, 1206, 1440), 18.10, 19.90),
    # "swipe left" -> SKIPs (first SKIP lands on "left")
    ("k_skip",    None,  None, (0, 500, 1206, 1440), 19.90, 23.02),
    # "swipe right" -> GET IT (lands on "right")
    ("k_getit",   None,  None, (0, 500, 1206, 1440), 23.02, 26.20),
    # STEP 3: the order receipt
    ("k_receipt", 39.60, 41.5, (0, 1040, 1206, 2010), 26.16, 36.30),
    # CTA: "Who's eating?" (share with friends)
    ("k_who",     71.20, 73.30, (0, 1560, 1206, 2460), 36.30, 39.45),
]
# align SKIP (SR 31.65) with "left" (21.56) and GET IT (SR 36.15) with "right" (25.36)
def _align(card, sr_event, src_word):
    i = [c[0] for c in CARDS].index(card); c = list(CARDS[i])
    c[1] = round(sr_event - (O(src_word) - O(c[4])), 3); CARDS[i] = tuple(c)
_align("k_skip", 31.65, 21.56)
_align("k_getit", 36.15, 25.36)

def card_size(box):
    w, h = box[2] - box[0], box[3] - box[1]
    s = min(CARD_MAX_W / w, CARD_MAX_H / h)
    return int(round(w * s / 2) * 2), int(round(h * s / 2) * 2)

def prep():
    os.makedirs(f"{A}/cards", exist_ok=True); os.makedirs(f"{A}/thumbs", exist_ok=True)
    # 1) rough cut: hard jump cuts, 10 ms audio fades at each joint, voice chain -> ~-14 LUFS
    parts, fc = [], []
    for i, (a, b, _) in enumerate(EDL):
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b-a-0.012:.3f}:d=0.012[a{i}]")
        parts.append(f"[v{i}][a{i}]")
    fc.append(f"{''.join(parts)}concat=n={len(EDL)}:v=1:a=1[v][a0]")
    fc.append("[a0]highpass=f=85,acompressor=threshold=-22dB:ratio=3.5:attack=4:release=90:makeup=4,"
              "loudnorm=I=-14:TP=-1.2:LRA=3[a]")
    run([FF, "-v", "error", "-y", "-i", TAKE, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", "30",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", f"{A}/rough.mp4"])
    # 2) card clips (silent, exact card size, last frame held to fill the slot)
    for cid, sr_in, sr_out, box, s0, s1 in CARDS:
        dur = O(s1) - O(s0)
        w, h = card_size(box)
        length = dur if sr_out is None else min(dur, sr_out - sr_in)
        hold = max(0, dur - length) + 0.2
        vf = (f"crop={box[2]-box[0]}:{box[3]-box[1]}:{box[0]}:{box[1]},scale={w}:{h}:flags=lanczos,fps=30,"
              f"tpad=stop_mode=clone:stop_duration={hold:.2f},format=yuv420p")
        run([FF, "-v", "error", "-y", "-ss", f"{sr_in}", "-t", f"{length:.3f}", "-i", SCREEN, "-an", "-vf", vf,
             "-c:v", "libx264", "-crf", "16", "-preset", "medium", f"{A}/cards/{cid}.mp4"])
        print(f"{cid}: SR {sr_in}-{sr_in+length:.2f}  out {O(s0):.2f}-{O(s1):.2f}  {w}x{h}")
    # 3) proof-wall dish thumbnails (portrait crops of the swipe-card photos)
    for i, t in enumerate([18.6, 20.6, 22.6, 24.6, 26.6, 29.2]):
        p = f"{HERE}/work/thumb_src_{i}.png"
        run([FF, "-v", "error", "-y", "-ss", f"{t}", "-i", SCREEN, "-frames:v", "1", p])
        im = Image.open(p).convert("RGB")
        # photo sits around x 60-1150, y 560-1180 on the card; take a portrait slice + the dish title strip
        x0 = [330, 380, 300, 360, 340, 320][i]
        th = im.crop((x0 + 60, 560, x0 + 420, 1160)).resize((180, 300), Image.LANCZOS)
        m = Image.new("L", th.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 179, 299), 16, fill=255)
        th = th.convert("RGBA"); th.putalpha(m); th.save(f"{A}/thumbs/dish_{i}.png")
    print("rough", DUR, "s")

# ---------------- timeline content ----------------
HEADERS = [  # (src_start, src_end, yellow part, white part)
    (9.70, 13.64, "STEP 1", "PICK YOUR MOOD"),
    (13.64, 18.10, "STEP 1", "OR HIT SURPRISE 🎲"),
    (18.10, 21.32, "STEP 2", "SWIPE THROUGH"),
    (21.32, 25.02, "STEP 2", "SWIPE LEFT TO SKIP 👈"),
    (25.02, 26.16, "STEP 2", "SWIPE RIGHT TO ORDER 👉"),
    (26.16, 36.30, "STEP 3", "DECIDE IN MINUTES ⏱️"),
    (36.30, 39.45, "", "SEND IT TO YOUR FRIENDS 💬"),
]
KEY = {"app": [1.92], "fun": [8.04, 32.74], "surprise": [13.64], "cravings": [17.24], "swipe": [21.32, 25.02],
       "10": [35.58], "minutes": [35.78], "friends": [37.6]}

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

def caption_rows():
    rows = []
    for i, (s, e, w) in enumerate(WORDS):
        t = "".join(ch for ch in w.lower() if ch.isalnum() or ch in "'-")
        if not t: continue
        st = O(s)
        nxt = O(WORDS[i + 1][0]) if i + 1 < len(WORDS) else DUR
        en = min(nxt, st + 1.2)
        if en - st < 0.05: continue
        key = any(abs(s - k) < 0.05 for k in KEY.get(t, []))
        rows.append(f'<div id="w{i:03d}" class="cap clip{" key" if key else ""}" data-start="{st:.3f}" data-duration="{en-st:.3f}" data-track-index="20">{esc(t)}</div>')
    return rows

def html():
    js, els = [], []
    # hook title (on from frame 0, hard off at the pill)
    hook_end = O(6.18)
    els.append(f'''<div id="hook" class="clip" data-start="0" data-duration="{hook_end:.3f}" data-track-index="10">
      <div class="h1">I DARE YOU TO TRY</div>
      <div class="h2">this food app</div>
      <div class="h3"><span>IN</span><img src="assets/icons/logo_wink_white.png" alt=""><b>feedmeplzthanks</b></div>
    </div>''')
    # proof wall: 6 dish cards, 3 each side of the face, staggered pops
    POS = [(34, 560, -4), (858, 600, 4), (60, 900, 3), (884, 930, -3), (24, 1235, -2), (870, 1260, 2)]
    wall_end = O(6.60)
    imgs = "".join(f'<img id="th{i}" class="th" src="assets/thumbs/dish_{i}.png" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">'
                   for i, (x, y, r) in enumerate(POS))
    els.append(f'<div id="wall" class="clip" data-start="0" data-duration="{wall_end:.3f}" data-track-index="9">{imgs}</div>')
    for i in range(6):
        t0 = 0.40 + 0.11 * i
        js.append(f'tl.fromTo("#th{i}",{{scale:0.6,opacity:0}},{{scale:1,opacity:1,duration:0.12,ease:"back.out(2)"}},{t0:.2f});')
    js.append(f'tl.to("#wall",{{opacity:0,scale:0.96,duration:0.1}},{wall_end-0.1:.3f});')
    # pill
    p0, p1 = O(6.18), O(9.62)
    els.append(f'<div id="pillw" class="clip" data-start="{p0:.3f}" data-duration="{p1-p0:.3f}" data-track-index="11"><div id="pill">3 steps → find your food 👇</div></div>')
    js.append(f'tl.fromTo("#pill",{{scale:0.5,opacity:0}},{{scale:1,opacity:1,duration:0.2,ease:"back.out(2.2)"}},{p0:.3f});')
    js.append(f'tl.to("#pill",{{opacity:0,duration:0.1}},{p1-0.1:.3f});')
    # headers
    for i, (s, e, y, w) in enumerate(HEADERS):
        a, b = O(s), O(e)
        yy = f'<span class="y">{y}</span> ' if y else ""
        els.append(f'<div id="hdr{i}" class="hdr clip" data-start="{a:.3f}" data-duration="{b-a:.3f}" data-track-index="12">{yy}{esc(w)}</div>')
    # cards (glass in, hard cut out)
    prev_end = None
    for cid, sr_in, sr_out, box, s0, s1 in CARDS:
        a, b = O(s0), O(s1); w, h = card_size(box)
        new_card = prev_end is None or abs(prev_end - a) > 0.05 or cid in ("k_deck", "k_receipt", "k_who")
        els.append(f'''<div id="{cid}" class="card" style="visibility:hidden">
        <video id="{cid}-v" class="clip cv" src="assets/cards/{cid}.mp4" muted playsinline data-start="{a:.3f}" data-duration="{b-a:.3f}" data-media-start="0" data-track-index="14" style="width:{w}px;height:{h}px;left:{(950-w)//2}px"></video></div>''')
        js.append(f'tl.set("#{cid}",{{autoAlpha:1}},{a:.3f});tl.set("#{cid}",{{autoAlpha:0}},{b:.3f});')
        if new_card:
            js.append(f'tl.fromTo("#{cid}",{{opacity:0.35,filter:"blur(18px)"}},{{opacity:1,filter:"blur(0px)",duration:0.13,ease:"none",immediateRender:false}},{a:.3f});')
        prev_end = b
    # stickers / badges
    def sticker(sid, s, e, inner, anim="pop"):
        a, b = O(s), O(e)
        els.append(f'<div id="{sid}w" class="clip" data-start="{a:.3f}" data-duration="{b-a:.3f}" data-track-index="15">{inner}</div>')
        js.append(f'tl.fromTo("#{sid}",{{scale:0.6,opacity:0}},{{scale:1,opacity:1,duration:0.12,ease:"back.out(2.4)"}},{a:.3f});')
    sticker("dice", 13.64, 16.00, '<img id="dice" class="stk" src="assets/icons/dice.png" style="left:860px;top:690px;width:150px">')
    js.append(f'tl.to("#dice",{{rotation:18,duration:0.12,yoyo:true,repeat:3,ease:"sine.inOut"}},{O(13.64)+0.15:.3f});')
    sticker("tick", 32.74, 36.30, '<img id="tick" class="stk" src="assets/icons/ticket_15_off.png" style="left:790px;top:850px;width:230px;transform:rotate(-8deg)">')
    sticker("badge", 35.58, 36.30, '<div id="badge" class="badge">✓ ORDERED IN UNDER 10 MIN</div>')
    sticker("dm", 38.58, 39.45, '<div id="dm" class="dm"><img src="assets/icons/role_partner_heart.png"><span><b>ana</b> ok we\'re ordering tonight 🍜</span></div>')
    caps = caption_rows()
    sfx = []
    for i in range(6):
        sfx.append(f'<audio id="sx-th{i}" class="clip" src="assets/sfx/Pop_02_Quick.wav" data-start="{0.40+0.11*i:.2f}" data-duration="0.11" data-track-index="{30+i%2}" data-volume="0.10"></audio>')
    sfx.append(f'<audio id="sx-pill" class="clip" src="assets/sfx/Pop_01_Tap.wav" data-start="{p0:.3f}" data-duration="0.14" data-track-index="32" data-volume="0.14"></audio>')
    return f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
 @font-face {{ font-family: "Inter"; font-weight: 700; src: url("assets/fonts/Inter-700.woff2") format("woff2"); }}
 @font-face {{ font-family: "Inter"; font-weight: 800; src: url("assets/fonts/Inter-800.woff2") format("woff2"); }}
 @font-face {{ font-family: "Montserrat"; font-weight: 800; src: url("assets/fonts/Montserrat-800.woff2") format("woff2"); }}
 @font-face {{ font-family: "Playfair Display"; font-style: italic; src: url("assets/fonts/PlayfairDisplay-400i.woff2") format("woff2"); }}
 :root {{ --butter:#F5EEA8; --butter-pill:#F5EEA6; --ink:#2D2216; --app:#FAECCC; --ok:#2FA35B;
   --card-shadow:0 18px 50px rgba(0,0,0,.22), 0 2px 6px rgba(0,0,0,.10); }}
 * {{ margin:0; padding:0; box-sizing:border-box; }}
 html, body {{ width:1080px; height:1920px; overflow:hidden; background:#000; }}
 #root {{ position:relative; width:1080px; height:1920px; overflow:hidden; }}
 #base {{ position:absolute; inset:0; width:1080px; height:1920px; object-fit:cover; }}
 #scrim {{ position:absolute; left:0; top:0; width:1080px; height:900px; background:linear-gradient(180deg, rgba(0,0,0,.30), rgba(0,0,0,.12) 55%, rgba(0,0,0,0)); }}
 .clip {{ position:absolute; }}
 #hook {{ left:0; top:0; width:1080px; height:600px; text-align:center; color:#fff; }}
 .h1 {{ position:absolute; top:150px; width:100%; font:800 36px/1 "Montserrat"; letter-spacing:.03em; text-shadow:0 2px 12px rgba(0,0,0,.45); }}
 .h2 {{ position:absolute; top:196px; width:100%; font:italic 400 112px/1.05 "Playfair Display"; color:var(--butter); text-shadow:0 3px 18px rgba(0,0,0,.45); }}
 .h3 {{ position:absolute; top:336px; width:100%; display:flex; justify-content:center; align-items:center; gap:14px; text-shadow:0 2px 12px rgba(0,0,0,.45); }}
 .h3 span {{ font:800 40px/1 "Montserrat"; }} .h3 img {{ height:46px; filter:drop-shadow(0 2px 8px rgba(0,0,0,.45)); }}
 .h3 b {{ font:800 44px/1 "Inter"; letter-spacing:-.02em; }}
 #wall {{ left:0; top:0; width:1080px; height:1920px; transform-origin:540px 900px; }}
 .th {{ position:absolute; width:180px; height:300px; border-radius:16px; box-shadow:0 10px 28px rgba(0,0,0,.35); }}
 #pillw {{ left:0; top:300px; width:1080px; height:120px; display:flex; justify-content:center; }}
 #pill {{ background:var(--butter-pill); color:var(--ink); font:800 44px/1 "Inter"; letter-spacing:-.02em; padding:20px 34px; border-radius:999px;
   transform:rotate(-3deg); box-shadow:0 8px 24px rgba(0,0,0,.25); white-space:nowrap; }}
 .hdr {{ left:0; top:160px; width:1080px; text-align:center; font:800 40px/1 "Montserrat"; color:#fff; letter-spacing:.01em; text-transform:uppercase;
   text-shadow:0 2px 12px rgba(0,0,0,.5); white-space:nowrap; }}
 .hdr .y {{ color:#F4EFAB; }}
 .card {{ position:absolute; left:65px; top:222px; width:950px; height:620px; border-radius:22px; background:var(--app); box-shadow:var(--card-shadow); overflow:hidden; }}
 .cv {{ position:absolute; top:0; height:620px; -webkit-mask-image:linear-gradient(90deg,transparent,#000 30px,#000 calc(100% - 30px),transparent); }}
 .stk {{ position:absolute; filter:drop-shadow(0 10px 20px rgba(0,0,0,.3)); }}
 #badgew {{ left:0; top:0; width:1080px; height:1920px; }}
 .badge {{ position:absolute; left:80px; top:866px; background:var(--ok); color:#fff; font:800 30px/1 "Montserrat"; letter-spacing:.03em; padding:14px 22px; border-radius:999px;
   box-shadow:0 8px 20px rgba(0,0,0,.25); transform-origin:0% 50%; }}
 #dmw {{ left:0; top:0; width:1080px; height:1920px; }}
 .dm {{ position:absolute; right:70px; top:868px; display:flex; align-items:center; gap:12px; background:#fff; padding:10px 22px 10px 10px; border-radius:999px;
   box-shadow:0 8px 24px rgba(0,0,0,.25); font:700 28px/1 "Inter"; color:#1D1D1F; transform-origin:100% 50%; }}
 .dm img {{ width:48px; height:48px; }} .dm b {{ font-weight:800; }}
 .cap {{ left:0; top:1262px; width:1080px; text-align:center; font:700 66px/1 "Inter"; letter-spacing:-.025em; color:#fff;
   text-shadow:0 0 3px rgba(0,0,0,.65), 0 0 10px rgba(0,0,0,.35), 0 3px 16px rgba(0,0,0,.6); }}
 .cap.key {{ color:var(--butter); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
  <video id="base" class="clip" src="assets/rough.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR:.3f}" data-media-start="0" data-track-index="0"></video>
  <div id="scrim"></div>
  {chr(10).join("  " + e for e in els)}
  {chr(10).join("  " + c for c in caps)}
  {chr(10).join("  " + s for s in sfx)}
</div>
<script>
 window.__timelines = window.__timelines || {{}};
 const tl = gsap.timeline({{ paused: true }});
 {chr(10).join(" " + j for j in js)}
 tl.set({{}}, {{}}, {DUR:.3f});
 window.__timelines["main"] = tl;
</script>
</body>
</html>
'''

if __name__ == "__main__":
    if sys.argv[1] == "prep": prep()
    else:
        open(f"{HERE}/hf/index.html", "w").write(html())
        print("index.html written; duration", DUR)
