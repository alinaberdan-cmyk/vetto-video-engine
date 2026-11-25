"""The edit decision list (EDL): from words to what stays.

A project's timeline is the list of words plus the pauses between them. Each word has `cut` (bool) and a
`why` when the engine proposed the cut; each pause has `keep` (bool). Everything here is a *proposal*:
the editor shows it, Alina clicks to change it, and nothing renders until she approves the step.
"""
import re

FILLERS = {"um", "uh", "uhm", "erm", "hmm", "ăă", "ăăă", "îî", "îîî", "ee", "eee", "mm", "э", "ээ", "эм"}
PAUSE_MIN = 0.45        # gaps longer than this become a pause chip
PAUSE_SHORT_TO = 0.15   # a shortened pause keeps this much air
MERGE_GAP = 0.25        # silences shorter than this are never cut out (auto-editor's "mincut"); cut WORDS always go
LEAD, TAIL = 0.06, 0.10 # air before / after a kept word at a cut (auto-editor margins; per pace in pacing.json)


def _norm(t):
    return re.sub(r"[^\w']+", "", t.lower())


def find_pauses(words, total, pause_min=PAUSE_MIN):
    pauses = []
    edges = [(0.0, words[0]["start"], None, 0)] if words else []
    edges += [(a["end"], b["start"], a["i"], b["i"]) for a, b in zip(words, words[1:])]
    if words:
        edges.append((words[-1]["end"], total, words[-1]["i"], None))
    for s, e, before, after in edges:
        d = e - s
        if d >= pause_min:
            prev = words[before]["text"] if before is not None else ""
            worth = prev.endswith("?")
            pauses.append({
                "id": f"p{len(pauses)}", "start": round(s, 3), "end": round(e, 3), "dur": round(d, 2),
                "after_word": before, "before_word": after,
                "keep": False,
                "hint": "after a question: worth keeping?" if worth else None,
                "edge": before is None or after is None,
            })
    return pauses


def find_retakes(words, n=3, window=25.0):
    """Repeated phrases (n+ words) within `window` seconds: the earlier attempt is a retake.
    We keep the LAST good take, like the reference engines do. Returns a list of word index ranges."""
    toks = [_norm(w["text"]) for w in words]
    cuts = []
    i = 0
    while i < len(words) - n:
        gram = toks[i:i + n]
        if not all(gram):
            i += 1
            continue
        # look ahead for the same opening within the window
        j = i + n
        found = None
        while j < len(words) - n + 1 and words[j]["start"] - words[i]["start"] < window:
            if toks[j:j + n] == gram:
                found = j
            j += 1
        if found is not None:
            cuts.append({"from": i, "to": found - 1, "why": "retake: you said it again later"})
            i = found
        else:
            i += 1
    return cuts


def propose(transcript, total, settings=None):
    """First proposal: fillers out, retakes out, long pauses shortened."""
    settings = settings or {}
    words = [dict(w, cut=False, why=None) for w in transcript["words"]]
    for w in words:
        if _norm(w["text"]) in FILLERS:
            w["cut"], w["why"] = True, "filler"
    retakes = find_retakes(words) if settings.get("retakes", True) else []
    for r in retakes:
        for k in range(r["from"], r["to"] + 1):
            words[k]["cut"], words[k]["why"] = True, r["why"]
    pause_min = float(settings.get("shorten_pauses_over", PAUSE_MIN))
    pauses = find_pauses(words, total, pause_min)
    return {"words": words, "pauses": pauses, "retakes": retakes, "pause_min": pause_min, **pace_fields(settings)}


def pace_fields(settings):
    """The pace preset's numbers the cut uses (library/pacing.json)."""
    g = lambda k, d: float(settings.get(k) if settings.get(k) is not None else d)
    return {"short_to": g("beat_mid", PAUSE_SHORT_TO), "beat_sentence": g("beat_sentence", .45), "beat_topic": g("beat_topic", .9),
            "min_cut": g("min_cut", MERGE_GAP), "lead": g("lead", LEAD), "tail": g("tail", TAIL),
            "punch_in": settings.get("punch_in"), "lufs": g("lufs", -14)}


def refine_edges(words, wav_path):
    """Snap each word's start and end to where the voice really starts and stops (Whisper's word times are often
    50-200 ms off, which clips first sounds and trailing s/t). 10 ms peak envelope, like auto-editor's audio
    analysis; writes start_r / end_r and never crosses into the neighbouring word."""
    import wave
    import numpy as np
    with wave.open(str(wav_path), "rb") as f:
        sr = f.getframerate()
        a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768.0
    hop = sr // 100
    n = len(a) // hop
    env = np.abs(a[: n * hop]).reshape(n, hop).max(axis=1)
    thr = max(0.012, 0.08 * float(np.percentile(env, 99)))   # quiet = under ~8 % of the loud parts
    loud = env > thr
    fr = lambda t: int(max(0, min(n - 1, round(t * 100))))
    for k, w in enumerate(words):
        s, e = w["start"], w["end"]
        lo = words[k - 1]["end"] if k else 0.0
        hi = words[k + 1]["start"] if k + 1 < len(words) else n / 100
        # onset: first loud frame in [start-150ms, start+100ms]; offset: last loud frame in [end-100ms, end+200ms]
        a0, a1 = fr(max(lo, s - .15)), fr(min(e, s + .10))
        on = next((i for i in range(a0, a1 + 1) if loud[i]), None)
        b0, b1 = fr(max(s, e - .10)), fr(min(hi, e + .20))
        off = next((i for i in range(b1, b0 - 1, -1) if loud[i]), None)
        w["start_r"] = round(max(lo, (on / 100 - .02) if on is not None else s), 3)
        w["end_r"] = round(min(hi, (off / 100 + .03) if off is not None else e), 3)
        if w["end_r"] <= w["start_r"]:
            w["start_r"], w["end_r"] = s, e
    return words


def _ws(w):
    return w.get("start_r", w["start"])


def _we(w):
    return w.get("end_r", w["end"])


def keep_ranges(edl, total):
    """Source-time ranges that stay, after word cuts and pause shortening.
    - a kept word keeps a little air at a cut (lead before, tail after), never reaching into a cut word;
    - a shortened pause keeps the pace's beat: longer after a sentence and at a topic change, split 60/40
      between the end of one word and the start of the next;
    - only silence is merged back (gaps under min_cut); a word Alina cut never comes back."""
    words, pauses = edl["words"], edl["pauses"]
    short_to = edl.get("short_to", PAUSE_SHORT_TO)
    pause_min = edl.get("pause_min", PAUSE_MIN)
    lead_m, tail_m = edl.get("lead", LEAD), edl.get("tail", TAIL)
    min_cut = edl.get("min_cut", MERGE_GAP)
    pause_by_after = {p["after_word"]: p for p in pauses}
    lead_pause = next((p for p in pauses if p["after_word"] is None), None)

    def beat(w):
        nxt = words[w["i"] + 1] if w["i"] + 1 < len(words) else None
        if nxt is not None and nxt.get("seg") != w.get("seg") and w["text"][-1:] in ".!?":
            return edl.get("beat_topic", .9)
        if w["text"][-1:] in ".!?…":
            return edl.get("beat_sentence", .45)
        return short_to

    ranges = []  # [start, end, has_cut_word_before]
    for w in words:
        if w["cut"]:
            continue
        i = w["i"]
        prev = words[i - 1] if i else None
        nxt = words[i + 1] if i + 1 < len(words) else None
        s, e = _ws(w), _we(w)
        # air before the word: the 40 % share of a shortened pause, else a margin (not into a cut word)
        pp = pause_by_after.get(i - 1) if i else lead_pause
        if pp and not pp["keep"]:
            s = max(pp["start"], s - beat(prev) * .4 if prev else s - lead_m)
        elif pp and pp["keep"]:
            s = pp["start"] if prev is None else s
        elif prev is not None and prev["cut"]:
            s = max((_we(prev) + s) / 2, s - lead_m)
        elif prev is None:
            s = max(0.0, s - lead_m)
        # air after the word
        p = pause_by_after.get(i)
        if p:
            e = p["end"] if p["keep"] else min(p["end"], e + beat(w) * .6)
        elif nxt is not None and nxt["cut"]:
            e = min((e + _ws(nxt)) / 2, e + tail_m)
        elif nxt is not None:
            e = max(e, min(_ws(nxt), e + pause_min))   # a small natural gap stays
        else:
            e = min(total, e + tail_m)
        ranges.append([s, e, prev is not None and prev["cut"]])
    merged = []
    for r in ranges:
        if merged and r[0] - merged[-1][1] < min_cut and not r[2] and r[0] >= merged[-1][0]:
            merged[-1][1] = max(merged[-1][1], r[1])       # only silence in between: keep it whole
        else:
            merged.append(r)
    return [[round(a, 3), round(min(b, total), 3)] for a, b, _ in merged if b - a > 0.04]


def stats(edl, total):
    kr = keep_ranges(edl, total)
    out = sum(b - a for a, b in kr)
    return {
        "source_s": round(total, 1), "result_s": round(out, 1),
        "words": len(edl["words"]), "words_cut": sum(w["cut"] for w in edl["words"]),
        "pauses": len(edl["pauses"]), "pauses_shortened": sum(not p["keep"] for p in edl["pauses"]),
    }


def map_time(t, ranges):
    """Source time -> output time (None when t falls in a cut)."""
    acc = 0.0
    for a, b in ranges:
        if t < a:
            return None
        if t <= b:
            return acc + (t - a)
        acc += b - a
    return None
