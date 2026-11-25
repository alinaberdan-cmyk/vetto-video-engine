"""Cut every sound out of the links Alina sent for the dumb-scale edit (2026-11-17) into single files.

Run:  <engine venv python> extract_sounds.py <downloads dir> <out dir>
<downloads dir> = video-prosus-dumb-scale/downloads (audio/*.wav pulled with yt-dlp, refs/*.mp4).
Each cut (not the whole music/explosion/CapCut files, which are kept untrimmed): boundary snapped to the quietest 10 ms near the marker, leading/trailing silence trimmed (-50 dB),
5 ms fades, 48 kHz stereo 16-bit WAV. Levels are NOT normalised (kept as in the source).
"""
import subprocess, sys, re, json
from pathlib import Path
import numpy as np

FF = str(Path(__file__).resolve().parents[4] / "Content Matrix FeedMe" / "vetto-video-engine" / "bin" / "ffmpeg")
SR = 48000
src, out = Path(sys.argv[1]), Path(sys.argv[2])

def load(p):
    r = subprocess.run([FF, "-v", "error", "-i", str(p), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, 2).copy()

def rms(x, a, b, hop=480):
    seg = x[int(a * SR):int(b * SR)].mean(1)
    return np.array([np.sqrt(np.mean(seg[i:i + hop] ** 2)) for i in range(0, max(1, len(seg) - hop), hop)])

def snap(x, t, before=0.15, after=0.25):
    a = max(0, t - before); e = rms(x, a, t + after)
    return a + int(np.argmin(e)) * 0.01 if len(e) else t

def trim(seg, thr_db=-50):
    m = np.abs(seg).max(1); thr = 10 ** (thr_db / 20)
    idx = np.where(m > thr)[0]
    if not len(idx): return seg
    a = max(0, idx[0] - int(0.01 * SR)); b = min(len(seg), idx[-1] + int(0.05 * SR))
    return seg[a:b]

def write(seg, path, do_trim=True):
    if do_trim:
        seg = trim(seg)
    pk = float(np.abs(seg).max()) if len(seg) else 0
    if pk > 0.99: seg = seg * (0.99 / pk)   # resampling overshoot: scale, never clip
    n = int(0.005 * SR); ramp = np.linspace(0, 1, n)[:, None]
    if len(seg) > 2 * n: seg[:n] *= ramp; seg[-n:] *= ramp[::-1]
    path.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", str(path)], input=seg.astype(np.float32).tobytes())
    return len(seg) / SR

def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")

def cut_list(x, marks, folder, prefix, snap_it=True, end=None):
    """marks: [(start_s, name)], each sound runs to the next mark."""
    end = end or len(x) / SR
    rows = []
    bounds = [snap(x, t) if (snap_it and t > 0) else t for t, _ in marks] + [end]
    for i, (_, name) in enumerate(marks):
        a, b = bounds[i], bounds[i + 1]
        fn = out / folder / f"{prefix}{i + 1:02d}_{slug(name)}.wav"
        d = write(x[int(a * SR):int(b * SR)].copy(), fn)
        rows.append((fn.relative_to(out).as_posix(), name, round(a, 2), round(b, 2), round(d, 2)))
    return rows

manifest = []

# 1) Top 40 Viral TikTok Meme Sound Effects (2026), Warrior SFX, youtube QRQEHtIiuDc (chapters from the description)
top40 = [(0, "God Damn"), (2, "Spawn"), (5, "Metal Pipe Falling Loud"), (8, "Undertakers Bell"), (13, "Travis Scott Meme"),
         (17, "Mentality"), (19, "PS2 Startup Screen"), (26, "French Meme"), (30, "Bass Drop"), (35, "Windows 95 Startup"),
         (41, "Windows XP Start"), (46, "Windows XP Shutdown"), (49, "English OR Spanish"), (56, "Flashbang"),
         (60, "999 Credit Score Siren"), (65, "Exaggerated Among Us"), (71, "Long Brain Fart"), (77, "Gay Echo Voice"),
         (81, "Bye Bye Mewing"), (82, "Crowd Laugh"), (86, "Get Out"), (88, "Glass Breaking"), (91, "RDR2 Low Honor"),
         (95, "Grandma House"), (100, "Collect Gold"), (103, "Slow Motion"), (109, "Spongebob Walking"),
         (113, "I Be Poppin Bottles Boosted"), (120, "Depressed Penguin"), (125, "Super Idol"), (131, "Fortnite Shield Potion"),
         (139, "Don Pollo Ahh Sound"), (146, "Dark Piano Dexter"), (152, "Optimus Prime"), (160, "Hells Kitchen Suspense"),
         (164, "Bone Crack"), (166, "Magic Spells"), (169, "Laugh Toy World Animation"), (173, "You Are My Sunshine"),
         (180, "Taco Bell"), (183, "Fahh")]
x = load(src / "audio" / "QRQEHtIiuDc.wav")
for r in cut_list(x, [(float(t), n) for t, n in top40], "meme-top40_QRQEHtIiuDc", ""):
    manifest.append(("Top 40 Viral TikTok Meme SFX 2026 (Warrior SFX)", "https://www.youtube.com/watch?v=QRQEHtIiuDc", *r))

# 2) Top 5 Meme Sound Effect 2026, Supplier XD, youtube DogH-RgansQ (title changes read from the frames)
x = load(src / "audio" / "DogH-RgansQ.wav")
for r in cut_list(x, [(0, "Faaa"), (1.83, "Vine boom"), (3.13, "Get out"), (4.10, "Yoooooo"), (6.67, "Rizz")], "meme-top5_DogH-RgansQ", ""):
    manifest.append(("Top 5 Meme Sound Effect 2026 (Supplier XD)", "https://www.youtube.com/watch?v=DogH-RgansQ", *r))

# 3) Sound effects Emma Chamberlain uses, youtube h2lJsTaBBU0 (silence gaps + on-screen numbers)
x = load(src / "audio" / "emma.wav")
emma = [(0.43, 6.31, "00_intro_Emma_talking"), (7.34, 11.12, "Crowd Applause"), (11.76, 12.09, "Golf Hit"), (14.22, 15.05, "Fart"),
        (16.91, 18.06, "Censor Beep"), (19.91, 20.38, "Camera click"), (22.37, 24.51, "Booing Crowd"), (25.72, 27.06, "Bass Boosted"),
        (27.91, 29.05, "Bell"), (30.60, 34.68, "Awkward Crickets"), (36.33, 37.31, "Smash Glass"), (39.03, len(x) / SR, "outro music")]
for i, (a, b, name) in enumerate(emma):
    fn = out / "emma-chamberlain-10_h2lJsTaBBU0" / (f"{name}.wav" if name.startswith("00") else f"{i:02d}_{slug(name)}.wav")
    d = write(x[int((a - 0.05) * SR):int((b + 0.1) * SR)].copy(), fn)
    manifest.append(("Sound effects Emma Chamberlain uses (your assistant)", "https://www.youtube.com/watch?v=h2lJsTaBBU0", fn.relative_to(out).as_posix(), name, a, b, round(d, 2)))

# 4) explosion, music, CapCut template audio: whole files
for f, folder, name, title, url in [
    ("explosion_src.wav", "explosion_hryVXjkxs8w", "explosion_full.wav", "Explosion / bomb blast meme video (NERDIFIED)", "https://www.youtube.com/watch?v=hryVXjkxs8w"),
    ("capcut.wav", "capcut-explosion-for-meme_7462869341453716797", "capcut_template_audio.wav", "CapCut template 'Explosion for Meme'", "https://www.capcut.com/template-detail/7462869341453716797"),
    ("kG9yv_iXqVE.wav", "music", "Island_Medium_iMovie.wav", "Island Medium | iMovie Song (iMusic)", "https://www.youtube.com/watch?v=kG9yv_iXqVE"),
    ("xy_NKN75Jhw.wav", "music", "Local_Forecast_Slower_Kevin_MacLeod_elevator.wav", "Elevator Music: Local Forecast - Slower, Kevin MacLeod, CC BY 4.0", "https://www.youtube.com/watch?v=xy_NKN75Jhw")]:
    x = load(src / "audio" / f); fn = out / folder / name
    d = write(x.copy(), fn, do_trim=False)
    manifest.append((title, url, fn.relative_to(out).as_posix(), name, 0, round(len(x) / SR, 2), round(d, 2)))

with open(out / "MANIFEST.tsv", "w") as fh:
    fh.write("source\turl\tfile\tname\tstart_s\tend_s\tduration_s\n")
    for row in manifest:
        fh.write("\t".join(str(v) for v in row) + "\n")
print(len(manifest), "files")
