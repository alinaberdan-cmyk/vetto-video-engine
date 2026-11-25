"""SG01: first Star Glitch edit (styles/star-glitch/STYLE.md).
Alina's feedmeplzthanks "dare you to try this app" selfie take + the app screen recording.
  python3 -I build.py prep   ffmpeg: base video (take + inserted dish montage), audio mix, PiP card clips
  python3 -I build.py html   writes hf/index.html (captions + moves)"""
import json, os, subprocess, sys

FF = os.environ.get("FFMPEG", "ffmpeg")      # any ffmpeg 6+
HERE = os.path.dirname(os.path.abspath(__file__))
TAKE, SCREEN = f"{HERE}/src/take.MOV", f"{HERE}/src/screen.MP4"
W_ = f"{HERE}/work"; A = f"{HERE}/hf/assets"
MUSIC = os.path.join(HERE, "..", "..", "..", "..", "library", "music", "tropical-risa.mp3")   # the repo's library/music
MUSIC_AT = 87.36            # loudest on-beat stretch (129.2 BPM, beat #188)
FPS = 30

# ---------------- cut list: BS01's approved pause trims, split at 6.10 for the montage ----------------
SPLIT = 6.10                # between "as well." (6.04) and "First" (6.14)
DISH_T = [18.25, 19.25, 20.25, 21.25, 22.25, 24.25, 26.0, 27.25, 29.25, 30.25, 31.25, 32.25, 33.25, 34.25]
CUT_F = 7                   # frames per dish = one half-beat at 129 BPM
FLASH_AT = 8                # glitch flash on the first frame of this dish
MD = round(len(DISH_T) * CUT_F / FPS, 4)   # montage duration
segs = []
for a, b, _ in json.load(open(f"{W_}/edl_bs01.json")):
    if a < SPLIT < b: segs += [[a, SPLIT], [SPLIT, b]]
    else: segs.append([a, b])
TL, t = [], 0.0             # (src_a, src_b, out_start)
for a, b in segs:
    if abs(a - SPLIT) < 1e-6: MONT0 = round(t, 4); t += MD
    TL.append((a, b, round(t, 4))); t += b - a
DUR = round(t, 3)

def O(s):
    """source time -> output time (inside a removed pause it snaps to the next segment)."""
    for a, b, o in TL:
        if s < a: return o
        if s <= b: return round(o + s - a, 4)
    return DUR

def run(cmd): subprocess.run(cmd, check=True)

# ---------------- PiP cards: list of (rec_in, length) pieces, jump cuts inside the card ----------------
def pieces_main():
    p = []
    # "look how much fun it is to use… categories… even if you don't…" -> pills settle; dice tap (rec 10.65) lands on "surprise"
    d = O(13.60) - O(6.84); p.append((10.65 - d, d))
    # "surprise button over here" -> Out scouting loader
    d = O(16.00) - O(13.60); p.append((10.65, d))
    # "finds food based on your cravings" -> Doing the reading -> Found it -> first card
    d = O(18.04) - O(16.00); p.append((18.02 - d, d))
    # "look how many options there are" -> card flicks (4 dishes)
    d = O(19.82) - O(18.04); q = d / 4
    for r in (18.3, 20.3, 22.3, 27.3): p.append((r, q))
    # "swipe left" -> SKIP stamp (rec 31.65) on "left" (21.60)
    d = O(22.12) - O(19.82); p.append((31.65 - (O(21.60) - O(19.82)), d))
    # "swipe right" -> GET IT (rec 36.15) on "right" (25.36), hold to end of "right."
    d = O(25.72) - O(22.12); p.append((36.15 - (O(25.36) - O(22.12)), d))
    return p
PIP = dict(id="pip", s=6.84, e=25.72, w=800, h=1740, left=140, top=48, crop=None, pieces=pieces_main)
PAY = dict(id="pay", s=37.08, e=38.32, w=972, h=1728, left=54, top=96, crop=(1206, 2144, 0, 478),
           pieces=lambda: [(70.95, O(38.32) - O(37.08))])

def card_clip(c):
    parts, fc = c["pieces"](), []
    for i, (r, d) in enumerate(parts):
        crop = f"crop={c['crop'][0]}:{c['crop'][1]}:{c['crop'][2]}:{c['crop'][3]}," if c["crop"] else ""
        fc.append(f"[{i}:v]{crop}scale={c['w']}:{c['h']}:flags=lanczos,fps={FPS},setsar=1,trim=duration={d:.4f},setpts=PTS-STARTPTS[p{i}]")
    fc.append("".join(f"[p{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0,tpad=stop_mode=clone:stop_duration=0.3,format=yuv420p[v]")
    ins = []
    for r, d in parts: ins += ["-ss", f"{r:.3f}", "-t", f"{d + 0.2:.3f}", "-i", SCREEN]
    run([FF, "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-an",
         "-c:v", "libx264", "-crf", "15", "-preset", "medium", f"{A}/cards/{c['id']}.mp4"])
    print(c["id"], [(round(r, 2), round(d, 2)) for r, d in parts])

def prep():
    os.makedirs(f"{A}/cards", exist_ok=True)
    # 1) dish montage: 14 x 7 frames, app card centred, one overexposed RGB-split glitch frame
    fc, ins = [], []
    for i, r in enumerate(DISH_T):
        ins += ["-ss", f"{r:.3f}", "-t", "0.5", "-i", SCREEN]
        v = f"[{i}:v]crop=1100:1956:53:380,scale=1080:1920:flags=lanczos,fps={FPS},setsar=1,trim=end_frame={CUT_F},setpts=PTS-STARTPTS"
        if i == FLASH_AT:
            v += (",split[fa{0}][fb{0}];[fa{0}]trim=end_frame=1,setpts=PTS-STARTPTS,eq=brightness=0.42:contrast=0.55:saturation=0.35,"
                  "rgbashift=rh=-18:bh=18:gv=6,colorbalance=rh=0.25:bh=0.2[fx{0}];[fb{0}]trim=start_frame=1,setpts=PTS-STARTPTS[fy{0}];"
                  "[fx{0}][fy{0}]concat=n=2:v=1:a=0").format(i)
        fc.append(v + f"[m{i}]")
    fc.append("".join(f"[m{i}]" for i in range(len(DISH_T))) + f"concat=n={len(DISH_T)}:v=1:a=0,format=yuv420p[v]")
    run([FF, "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-an", "-r", str(FPS),
         "-c:v", "libx264", "-crf", "15", "-preset", "medium", f"{W_}/montage.mp4"])
    # 2) picture: take segments + montage; voice: take segments + silence; hard joints with 10 ms audio fades
    fc, vs, as_ = [], [], []
    for i, (a, b, o) in enumerate(TL):
        if abs(a - SPLIT) < 1e-6:
            vs.append("[1:v]"); fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={MD}[sil]"); as_.append("[sil]")
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS},setsar=1[v{i}]")
        fc.append(f"[0:a]aresample=48000,atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b-a-0.012:.3f}:d=0.012[a{i}]")
        vs.append(f"[v{i}]"); as_.append(f"[a{i}]")
    fc.append("".join(v + a for v, a in zip(vs, as_)) + f"concat=n={len(vs)}:v=1:a=1[v][vo]")
    fc.append("[vo]highpass=f=85,acompressor=threshold=-22dB:ratio=3.5:attack=4:release=90:makeup=4,loudnorm=I=-15:TP=-2:LRA=4[voice]")
    # music only under the montage, ~5 dB under the voice; hard stop on the cut back (8 ms fade)
    fc.append(f"[2:a]aresample=48000,atrim={MUSIC_AT}:{MUSIC_AT + MD},asetpts=PTS-STARTPTS,volume=-9dB,"
              f"afade=t=in:d=0.006,afade=t=out:st={MD-0.008:.3f}:d=0.008,adelay={int(MONT0*1000)}:all=1[mus]")
    zoom_at = MONT0 - 6 / FPS - 0.05
    fc.append(f"[3:a]aresample=48000,volume=-9dB,adelay={int(zoom_at*1000)}:all=1[wh]")
    fc.append(f"[4:a]aresample=48000,volume=-12dB,adelay={int((MONT0 + FLASH_AT*CUT_F/FPS)*1000)}:all=1[sn]")
    fc.append("[voice][mus][wh][sn]amix=inputs=4:duration=first:normalize=0,alimiter=limit=0.84:level=false[a]")
    run([FF, "-v", "error", "-y", "-i", TAKE, "-i", f"{W_}/montage.mp4", "-i", MUSIC,
         "-i", f"{W_}/Whoosh_05_Fast_Flick.wav", "-i", f"{W_}/Camera_01_Snapshot.wav",
         "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", f"{A}/base.mp4"])
    for c in (PIP, PAY): card_clip(c)
    print("montage", MONT0, "->", round(MONT0 + MD, 3), "| duration", DUR)

# ---------------- captions & moves ----------------
TIER = {"XL": 360, "L": 200, "M": 118, "S": 62}
els, js = [], []
_n = [0]
def fr(a, b):
    """snap a clip to whole frames and end it 1 ms early, so two flip-book states never share a frame (v1 bug: doubled name)."""
    # start 0.5 ms before its frame (4-decimal rounding can push it past the frame: v2 bug, name blinked out)
    fa, fb = round(a * FPS), round(b * FPS)
    return max(0.0, fa / FPS - 0.0005), max(fb - fa, 0) / FPS - 0.001

def cap(text, tier, x, y, s, e, src=True, extra="", cls="cap"):
    """one caption: centred on (x%, y%), hard in at s, hard out at e (source times unless src=False)."""
    a, b = (O(s), O(e)) if src else (s, e)
    a, d = fr(a, b)
    if d < 0.02: return None
    _n[0] += 1; i = f"c{_n[0]:03d}"
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    els.append(f'<div id="{i}" class="clip {cls}" data-start="{a:.4f}" data-duration="{d:.4f}" data-track-index="{20 + _n[0] % 6}" '
               f'style="left:{x}%;top:{y}%;font-size:{TIER.get(tier, tier)}px;{extra}">{t}</div>')
    return i

def frames(states, tier, x, y, a0, step, end, extra=""):
    """output-time flipbook: states[i] shown for `step` s each, the last one held to `end` (output time)."""
    for k, st in enumerate(states):
        a = a0 + k * step; b = end if k == len(states) - 1 else a + step
        cap(st, tier, x, y, a, b, src=False, extra=extra)

def build():
    # ---- HOOK ----
    typed = ["w", "wa", "waa", "waaa", "waaai", "waaait", "waaait_"]
    frames(typed, "S", 36, 50, 0.0, 1 / FPS, O(0.30))
    cap("waaait…!", "S", 38, 50, 0.30, 0.58)
    cap("i", "L", 50, 50, 0.58, 0.64)
    cap("want", "L", 50, 50, 0.64, 0.84)
    cap("to", "S", 50, 50, 0.84, 1.02)
    cap("dare", "XL", 50, 50, 1.02, 1.20)
    cap("you", "L", 50, 50, 1.20, 1.32)
    cap("to", "S", 50, 50, 1.32, 1.44)
    cap("try", "L", 50, 50, 1.44, 1.68)
    cap("this", "M", 24, 41.5, 1.68, 2.40)
    cap("app", "M", 80, 61, 1.90, 2.40)
    # glitch name: the star hops between two E's every 5 frames
    a0, end = O(1.90), O(2.40)
    for k in range(int((end - a0) * FPS / 5) + 1):
        st = a0 + k * 5 / FPS
        if st >= end: break
        cap(["FEEDM★PLZTHANKS", "F★EDMEPLZTHANKS"][k % 2], 112, 50, 50, st, min(end, st + 5 / FPS), src=False, cls="cap name")
    cap("my friend", "M", 50, 12, 2.42, 4.40)
    line = ">literally showed it to me<"
    a0, a1 = O(3.14), O(4.16)
    n = len(line); step = (a1 - a0) / n
    frames([line[:k] for k in range(1, n + 1)], "S", 50, 51, a0, step, a1)
    cap("today", "L", 50, 51, 4.16, 4.40)
    cap("i have to", "S", 50, 51, 4.56, 5.06)
    cap("show", "M", 30, 16, 5.06, 5.52)
    cap("it", "M", 80, 29, 5.28, 5.52)
    cap("to", "M", 45, 41, 5.40, 5.52)
    # "you (as well)" block, then the zoom-through into the montage
    blk0 = O(5.52)
    els.append(f'<div id="zt" class="clip" data-start="{blk0:.4f}" data-duration="{MONT0-blk0:.4f}" data-track-index="27">'
               f'<div id="ztin"><div class="cap rel" style="font-size:{TIER["XL"]}px">you</div>'
               f'<div id="aswell" class="cap rel" style="font-size:{TIER["M"]}px;visibility:hidden">(as well)</div></div></div>')
    js.append(f'tl.set("#aswell",{{visibility:"visible"}},{O(5.64):.4f});')
    z0 = MONT0 - 6 / FPS
    js.append(f'tl.to("#ztin",{{scale:14,duration:{6/FPS:.4f},ease:"power3.in"}},{z0:.4f});')
    els.append(f'<div id="ztflash" class="clip" data-start="{MONT0-2/FPS:.4f}" data-duration="{2/FPS:.4f}" data-track-index="28"></div>')
    # ---- MONTAGE: name over the cuts, then the fly-through ----
    # alternating timed wrappers (star hops every 5 frames) over the dark food-photo band; the fly-through scales every inner
    fly0 = MONT0 + MD - 0.80
    k = 0; t_ = MONT0
    while t_ < MONT0 + MD - 1e-3:
        e_ = min(MONT0 + MD, t_ + 5 / FPS)
        sa, sd = fr(t_, e_)
        els.append(f'<div class="clip mn" data-start="{sa:.4f}" data-duration="{sd:.4f}" data-track-index="{29 + k % 2}">'
                   f'<div class="mnin"><div class="cap rel name" style="font-size:112px">{["FEEDM★PLZTHANKS", "F★EDMEPLZTHANKS"][k % 2]}</div></div></div>')
        k += 1; t_ = e_
    js.append(f'tl.to(".mnin",{{scale:9,x:-2300,duration:0.80,ease:"power2.in"}},{fly0:.4f});')
    # ---- BODY ----
    cap("(forever)", "M", 50, 52, 28.02, 29.50)
    # logo lockup on "discovered this app": feedme + script plz / thanks writing on
    l0, l1 = O(30.30), O(31.58)
    els.append(f'<div id="logo" class="clip" data-start="{l0:.4f}" data-duration="{l1-l0:.4f}" data-track-index="30">'
               f'<div class="cap logo-main">feedme</div><div id="plz" class="script" style="left:150px;top:640px;font-size:250px">plz</div>'
               f'<div id="thx" class="script" style="left:430px;top:1105px;font-size:230px">thanks</div></div>')
    js.append('tl.set("#plz",{clipPath:"inset(0 100% 0 0)"},0);tl.set("#thx",{clipPath:"inset(0 100% 0 0)"},0);')
    js.append(f'tl.to("#plz",{{clipPath:"inset(0 0% 0 0)",duration:0.16,ease:"none"}},{O(30.72):.4f});')
    js.append(f'tl.to("#thx",{{clipPath:"inset(0 0% 0 0)",duration:0.20,ease:"none"}},{O(31.02):.4f});')
    cap("(so)", "M", 50, 12, 32.24, 33.22)
    cap("(much)", "M", 50, 52, 32.52, 32.70)
    f0, f1 = O(32.70), O(33.22)
    g0 = f0 + 6 / FPS          # 6-frame font glitch burst, then it settles
    cap("fun", "L", 50, 52, f0, g0, src=False)
    for k, (cls, txt) in enumerate([("g-anton", "FUN"), ("g-anton", "FUN"), ("g-thin", "fun"), ("g-pixel", "fun"), ("g-script", "fun"), ("g-pixel", "fun")]):
        cap(txt, "L", 50, 52, g0 + k / FPS, g0 + (k + 1) / FPS, src=False, cls=f"cap {cls}")
    cap("fun", "L", 50, 52, g0 + 6 / FPS, f1, src=False)
    # counter: 01 holds 4 frames, then +1 per frame, landing "10" on the spoken "10"
    c_land = O(35.58); c0 = c_land - 12 / FPS
    cap("01", "XL", 50, 47, c0, c0 + 4 / FPS, src=False, cls="cap num")
    for k in range(2, 11):
        b = c_land + 9999 if k == 10 else c0 + (4 + k - 1) / FPS
        cap(f"{k:02d}", "XL", 50, 47, c0 + (4 + k - 2) / FPS, min(b, O(36.26)), src=False, cls="cap num")
    cap("(minutes)", "M", 50, 60, 35.74, 36.26)
    cap("go on !", "L", 50, 52, 36.26, 37.08)
    cap("lmk", "L", 50, 50, 38.32, 99)
    cap("(what u think !)", "M", 50, 59, 38.94, 99)

def card_html(c):
    a, b = O(c["s"]), O(c["e"])
    els.append(f'<div id="{c["id"]}" class="card" style="left:{c["left"]}px;top:{c["top"]}px;width:{c["w"]}px;height:{c["h"]}px;visibility:hidden">'
               f'<video id="{c["id"]}-v" class="clip cv" src="assets/cards/{c["id"]}.mp4" muted playsinline data-start="{a:.4f}" '
               f'data-duration="{b-a:.4f}" data-media-start="0" data-track-index="14" style="width:{c["w"]}px;height:{c["h"]}px"></video></div>')
    js.append(f'tl.set("#{c["id"]}",{{autoAlpha:1}},{a:.4f});tl.set("#{c["id"]}",{{autoAlpha:0}},{b:.4f});')

def html():
    build(); card_html(PIP); card_html(PAY)
    return f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
 @font-face {{ font-family:"Inter Tight"; font-weight:800; src:url("assets/fonts/InterTight-800.ttf"); }}
 @font-face {{ font-family:"Great Vibes"; src:url("assets/fonts/GreatVibes-400.ttf"); }}
 @font-face {{ font-family:"Anton"; src:url("assets/fonts/Anton-Regular.ttf"); }}
 @font-face {{ font-family:"Didact Gothic"; src:url("assets/fonts/DidactGothic-Regular.ttf"); }}
 @font-face {{ font-family:"Press Start 2P"; src:url("assets/fonts/PressStart2P-400.ttf"); }}
 :root {{ --cream:#FBFCDA; }}
 * {{ margin:0; padding:0; box-sizing:border-box; }}
 html, body {{ width:1080px; height:1920px; overflow:hidden; background:#000; }}
 #root {{ position:relative; width:1080px; height:1920px; overflow:hidden; }}
 #base {{ position:absolute; inset:0; width:1080px; height:1920px; object-fit:cover; }}
 .clip {{ position:absolute; }}
 .cap {{ position:absolute; transform:translate(-50%,-50%); white-space:nowrap; color:var(--cream);
   font-family:"Inter Tight"; font-weight:800; letter-spacing:-0.07em; line-height:.85; text-align:center;
   text-shadow:0 0 30px rgba(45,28,16,.30); /* bright-footage adaptation: faint warm halo, not a visible shadow */ }}
 .cap.rel {{ position:relative; transform:none; left:auto; top:auto; }}
 .name {{ letter-spacing:-0.06em; }}
 .num {{ letter-spacing:-0.06em; }}
 .g-anton {{ font-family:"Anton"; font-weight:400; letter-spacing:0; }}
 .g-thin {{ font-family:"Didact Gothic"; font-weight:400; letter-spacing:0; }}
 .g-pixel {{ font-family:"Press Start 2P"; font-weight:400; letter-spacing:0; font-size:120px !important; }}
 .g-script {{ font-family:"Great Vibes"; font-weight:400; letter-spacing:0; }}
 #zt {{ left:0; top:0; width:1080px; height:1920px; }}
 #ztin {{ position:absolute; left:0; top:790px; width:1080px; display:flex; flex-direction:column; align-items:center; transform-origin:540px 150px; }}
 #ztflash {{ left:0; top:0; width:1080px; height:1920px; background:var(--cream); }}
 .mn {{ left:0; top:0; width:1080px; height:1920px; }}
 .mnin {{ position:absolute; left:0; top:432px; width:1080px; display:flex; justify-content:center; transform-origin:600px 48px; }}
 #logo {{ left:0; top:0; width:1080px; height:1920px; }}
 .logo-main {{ left:540px; top:960px; font-size:330px; }}
 .script {{ position:absolute; font-family:"Great Vibes"; color:var(--cream); line-height:1; white-space:nowrap; text-shadow:0 0 30px rgba(45,28,16,.30); }}
 .card {{ position:absolute; overflow:hidden; }}
 .cv {{ position:absolute; left:0; top:0; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
  <video id="base" class="clip" src="assets/base.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR:.3f}" data-media-start="0" data-track-index="0"></video>
{chr(10).join("  " + e for e in els)}
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
        print("index.html written; duration", DUR, "| montage", MONT0, "->", round(MONT0 + MD, 3), "|", _n[0], "captions")
