"""Rhythm and emphasis, measured from the sound (18 Nov 2026).

Ideas from JuneYaooo/rea-video (Apache-2.0, research/repos/rea-video), rewritten here in our own code for the engine:
  - `beats()`: the tempo and beat grid of a music track. The percussive part of the sound (median-filter harmonic /
    percussive split) gives an onset curve; its autocorrelation gives the beat period (60-190 BPM, slow results
    doubled into 75-180); the best phase of a comb at that period, snapped to the nearest onset peak, gives the beats
    (rea-video audio.py `_tempo_and_beats`). Used to land a style's punch-ins on the music's beat.
  - `stress()`: which words are said with emphasis. Per word: loudness (75th percentile of 20 ms frames), pitch
    (autocorrelation) and how long the word is held, each against the median word of the take (rea-video prosody.py
    measures whole lines the same way). Used to pick the key word of a phrase for key-word effects.
  - `cuts_on_beat()`: share of cuts that land within 70 ms of a beat, with the share expected by chance
    (rea-video audio.py), for studying reference videos (engine/study.py).
numpy + scipy only; runs on Python 3.9 (the engine's venv).
"""
from __future__ import annotations

import subprocess

import numpy as np

SR = 22050
N_FFT, HOP = 1024, 256
T_HOP = HOP / SR


def load(path, sr=SR, start=0.0, dur=None):
    """mono float32 samples of any audio/video file (ffmpeg), from `start` for `dur` seconds"""
    from media import ffmpeg_bin
    cmd = [ffmpeg_bin(), "-hide_banner", "-v", "error", "-ss", f"{float(start):.3f}"]
    if dur:
        cmd += ["-t", f"{float(dur):.3f}"]
    cmd += ["-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        return None
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def _stft(x):
    if len(x) < N_FFT:
        x = np.pad(x, (0, N_FFT - len(x)))
    w = np.hanning(N_FFT).astype(np.float32)
    n = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    return np.abs(np.fft.rfft(x[idx] * w, axis=1)).astype(np.float32)        # frames x bins


def _percussive(S):
    """the percussive part of a magnitude STFT (soft mask from median filters across time and across frequency)"""
    from scipy.ndimage import median_filter
    H = median_filter(S, size=(17, 1))          # steady over time = harmonic
    P = median_filter(S, size=(1, 17))          # broad over frequency = percussive
    return S * (P ** 2 / (H ** 2 + P ** 2 + 1e-12))


def onsets(x):
    """(percussive onset curve per frame, percussive share of each frame's energy)"""
    S = _stft(x)
    Sp = _percussive(S)
    curve = np.maximum(0, np.diff(np.log1p(Sp.sum(axis=1)), prepend=0))
    share = (Sp ** 2).sum(axis=1) / ((S ** 2).sum(axis=1) + 1e-12)
    return curve, share


def _peaks(env, min_gap, thr):
    out, last = [], -10 ** 9
    for i in range(1, len(env) - 1):
        if env[i] >= thr and env[i] >= env[i - 1] and env[i] >= env[i + 1] and i - last >= min_gap:
            out.append(i)
            last = i
    return np.array(out, dtype=int)


def beats(path, start=0.0, max_s=150.0):
    """{"bpm", "strength", "beats": [seconds in the FILE's time]} of a music track (or None). `strength` is the
    normalised autocorrelation at the beat period: under ~0.2 there are no drums to count (pads, piano), and the grid
    should not be trusted."""
    x = load(path, start=start, dur=max_s)
    if x is None or len(x) < SR * 2:
        return None
    perc, _ = onsets(x)
    env = perc - perc.mean()
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    ac /= ac[0] + 1e-9
    lo, hi = int(60 / 190 / T_HOP), int(60 / 60 / T_HOP)
    if hi >= len(ac):
        return None
    # a true beat period repeats: its 2nd, 3rd and 4th multiples are peaks too (a 4:3 cross-rhythm's are not), so each
    # period is scored on the mean of the autocorrelation at 1-4 times it, weighted towards ~110 BPM (one octave either
    # side keeps 60 % of the weight) so strong eighth notes are not read as the beat (Hip-Hop 2: 95 BPM, not 126 or 190)
    lags = np.arange(lo, hi)
    prior = np.exp(-0.5 * (np.log2(60 / (lags * T_HOP) / 110) / 1.0) ** 2)
    def at(l):
        l = int(round(l))
        return float(ac[max(0, l - 1):l + 2].max()) if l + 2 < len(ac) else 0.0
    comb = np.array([np.mean([at(l * k) for k in (1, 2, 3, 4)]) for l in lags])
    best = int(np.argmax(comb * prior))
    lag, strength = int(lags[best]), float(comb[best])
    tempo = 60 / (lag * T_HOP)
    if tempo < 70:                               # prefer the common 70-180 BPM octave
        tempo *= 2
        lag = max(1, lag // 2)
    phase = int(np.argmax([perc[p::lag].sum() for p in range(lag)]))
    grid = np.arange(phase, len(perc), lag)
    snapped = [a + int(np.argmax(perc[a:b])) for a, b in ((max(0, g - 3), min(len(perc), g + 4)) for g in grid)]
    return {"bpm": round(float(tempo), 1), "strength": round(strength, 3),
            "beats": [round(float(start + b * T_HOP), 3) for b in snapped]}


def cuts_on_beat(cuts, beat_times, dur, tol=0.07):
    """(share of cuts within tol of a beat, share expected by chance)"""
    cuts = np.array([c for c in cuts if c > 0.2])
    bt = np.array(beat_times)
    if not len(cuts) or not len(bt):
        return None, None
    d = np.min(np.abs(cuts[:, None] - bt[None, :]), axis=1)
    return round(float((d < tol).mean()), 3), round(float(min(1.0, len(bt) / max(dur, 1e-6) * 2 * tol)), 3)


def snap(times, beat_times, early=0.12, late=0.08):
    """move each time onto the nearest beat when one is close (up to `early` s before or `late` s after it);
    returns (new times, how many landed on a beat)"""
    bt = sorted(beat_times)
    out, n = [], 0
    for t in times:
        b = min(bt, key=lambda v: abs(v - t)) if bt else None
        if b is not None and -early <= b - t <= late:
            out.append(round(b, 3))
            n += 1
        else:
            out.append(t)
    return out, n


# ---- emphasis ------------------------------------------------------------------------------------------------------
def _frames(x, sr, frame_s=0.04, hop_s=0.02):
    """per 20 ms: (pitch in Hz or 0, level in dB)"""
    n, h = int(frame_s * sr), int(hop_s * sr)
    lo, hi = int(sr / 400), int(sr / 70)
    f0, db = [], []
    for s in range(0, max(0, len(x) - n), h):
        seg = x[s:s + n] - x[s:s + n].mean()
        rms = float(np.sqrt(np.mean(seg ** 2)))
        db.append(20 * np.log10(rms + 1e-9))
        ac = np.correlate(seg, seg, "full")[n - 1:]
        if rms < 0.01 or ac[0] <= 0 or hi >= len(ac):
            f0.append(0.0)
            continue
        lag = lo + int(np.argmax(ac[lo:hi]))
        f0.append(sr / lag if ac[lag] / ac[0] > 0.45 else 0.0)
    return np.array(f0), np.array(db)


def stress(audio, words, sr=16000):
    """{word i: {"stress", "loud_db", "pitch_st", "held"}} for the words of a take (source times `start`/`end`).
    `audio` is a path (the project's media/audio16k.wav) or samples. Each cue (louder, higher, held longer per letter)
    is measured against the ±6 words around it and counted in units of the take's own spread; stress = their sum / 2,
    so 1.0 ≈ one cue two spreads above the neighbours, or two cues one spread above: clearly emphasised."""
    x = load(audio, sr=sr) if not isinstance(audio, np.ndarray) else audio
    if x is None or not len(x):
        return {}
    m = {}
    for w in words:
        a, z = w.get("start_r", w.get("start")), w.get("end_r", w.get("end"))
        if not isinstance(a, (int, float)) or not isinstance(z, (int, float)) or z - a < 0.08:
            continue
        f0, db = _frames(x[int(a * sr):int(z * sr)], sr)
        if not len(db):
            continue
        voiced = f0[f0 > 0]
        letters = max(1, sum(ch.isalnum() for ch in w.get("text", "")))
        m[w["i"]] = {"db": float(np.percentile(db, 75)), "hz": float(np.median(voiced)) if len(voiced) >= 3 else None,
                     "per": (z - a) / letters, "letters": letters}
    if len(m) < 5:
        return {}
    # each cue against the words around it (±6 words: the level drifts as she moves), scaled by the take's spread
    keys = sorted(m)
    text = {w["i"]: w.get("text", "") for w in words}
    raw = {}
    for k, i in enumerate(keys):
        near = [m[j] for j in keys[max(0, k - 6):k + 7]]
        v = m[i]
        loud = v["db"] - float(np.median([n["db"] for n in near]))
        hzs = [n["hz"] for n in near if n["hz"]]
        pitch = 12 * np.log2(v["hz"] / float(np.median(hzs))) if v["hz"] and len(hzs) >= 4 else 0.0
        if abs(pitch) > 7:                       # an octave slip of the pitch tracker, not intonation
            pitch = 0.0
        held = 0.0
        if v["letters"] >= 3:
            held = np.log(v["per"] / float(np.median([n["per"] for n in near])))
            if text.get(i, "")[-1:] in ".?!,":   # the last word of a phrase is always drawn out a little
                held -= np.log(1.3)
        raw[i] = (loud, pitch, held)
    def scale(col):
        vals = np.array([r[col] for r in raw.values()])
        mad = float(np.median(np.abs(vals - np.median(vals)))) * 1.4826
        return max(mad, (1.5, 1.0, 0.15)[col])
    sl, sp, sh = scale(0), scale(1), scale(2)
    out = {}
    for i, (loud, pitch, held) in raw.items():
        z = [min(3.0, max(0.0, loud / sl)), min(3.0, max(0.0, pitch / sp)), min(3.0, max(0.0, held / sh))]
        out[i] = {"stress": round(float(sum(z)) / 2, 2), "loud_db": round(float(loud), 1), "pitch_st": round(float(pitch), 1),
                  "held": round(float(np.exp(held)), 2)}
    return out


# ---- command line (18 Nov 2026, also used from ~/Editing Beast) ---------------------------------------------------
def _words_from(path):
    """words from a transcript json: the engine's ({text,start,end}), Editing Beast's ({w,s,e}) or Whisper's segments"""
    import json
    d = json.loads(open(path).read())
    ws = d.get("words") if isinstance(d, dict) else d
    if not ws and isinstance(d, dict):
        ws = [w for s in d.get("segments", []) for w in s.get("words", [])]
    out = []
    for k, w in enumerate(ws or []):
        out.append({"i": w.get("i", k), "text": (w.get("text") or w.get("w") or w.get("word") or "").strip(),
                    "start": w.get("start", w.get("s")), "end": w.get("end", w.get("e"))})
    return out


if __name__ == "__main__":
    import argparse
    import json
    import sys
    import tempfile
    ap = argparse.ArgumentParser(description="beats of a song, or the stressed words of a take")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("beats", help="tempo and beat times of a music file")
    b.add_argument("file")
    b.add_argument("--start", type=float, default=0.0, help="where the music starts in the file (s)")
    s = sub.add_parser("stress", help="which words are said with emphasis")
    s.add_argument("file", help="video or audio of the take")
    s.add_argument("transcript", nargs="?", help="word timings json; without it the take is transcribed (MLX Whisper, local)")
    s.add_argument("--top", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "beats":
        r = beats(a.file, start=a.start)
        if r:
            r["clear_beat"] = r["strength"] >= .2
        print(json.dumps(r, indent=1))
    else:
        if a.transcript:
            words = _words_from(a.transcript)
        else:
            from media import extract_audio
            from transcribe import transcribe
            wav = tempfile.mktemp(suffix=".wav")
            extract_audio(a.file, wav)
            words = [dict(w, i=k) for k, w in enumerate(transcribe(wav)["words"])]
        st = stress(a.file, words)
        byi = {w["i"]: w for w in words}
        top = sorted(st.items(), key=lambda kv: -kv[1]["stress"])[:a.top]
        print(json.dumps({"stressed": [dict(word=byi[i]["text"], start=byi[i]["start"], **v) for i, v in top],
                          "note": "stress ≥ 1 = clearly emphasised (louder / higher / held longer than the words around it)"},
                         indent=1, ensure_ascii=False))
        sys.exit(0)
