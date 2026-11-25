"""Style director (18 Nov 2026): picking a style makes the whole edit, the way the Editing Beast style guides do it.

Alina: "if I want to paste a style on a video in the engine, it needs to come with all the sound effects, video and
text effects and transitions already". So a style is not only a text look: for Clean White, Cinema Lexicon and Neon
Dimension this module reads the transcript and places, in the rhythm of each ~/Editing Beast/styles/<id>/STYLE.md,
  - the caption tier (size, place above the head / on the chest from the face, motion),
  - the signature effects on the right words (statement stacks, the card, bookends, key words, neon worlds…),
  - transitions (light leaks, flashes, light burns) and punch-ins at phrase changes,
  - the sound map (celf pack + Neon kit) on those events, at the guide's volumes and offsets,
  - the music bed and the loudness.
Everything it adds is marked `"by": "style:<id>"` and `"status": "proposed"` (Alina keeps, changes or removes it in the
Effects and Sound steps); applying a style again replaces only what a style added, never what she placed herself.
Times are worked out in the reel's own (output) time from the kept words, then anchored back on words.
"""
import json
import re
from pathlib import Path

from edit import keep_ranges, map_time

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"
DIRECTED = {"clean-white", "cinema-lexicon", "neon-dimension"}


def _rid(prefix, k):
    return f"{prefix}{k:03d}x"


class Plan:
    def __init__(self, style, proj, face):
        self.style, self.p, self.face = style, proj, face
        edl = proj["edl"]
        self.ranges = keep_ranges(edl, proj["source"]["duration"])
        self.dur = sum(b - a for a, b in self.ranges)
        self.words = []
        for w in edl["words"]:
            if w.get("cut"):
                continue
            t = map_time(w["start"], self.ranges)
            e = map_time(min(w["end"], w["start"] + 1.2), self.ranges)
            if t is not None:
                self.words.append(dict(w, o=t, oe=e if e is not None else t + .3))
        self.sentences = []
        cur = []
        for k, w in enumerate(self.words):
            cur.append(w)
            nxt = self.words[k + 1] if k + 1 < len(self.words) else None
            if re.search(r"[.?!…]$", w["text"]) or (nxt and nxt["o"] - w["oe"] > .6 and len(cur) > 2) or not nxt:
                self.sentences.append(cur)
                cur = []
        self.busy = []          # output windows taken by full-frame / text effects
        self.effects, self.sfx, self.punches = [], [], []
        self.why = f"{style['name']} style (Editing Beast STYLE.md)"

    # ---- helpers
    def free(self, a, b, pad=0.0):
        return all(b + pad <= x or a - pad >= y for x, y in self.busy) and b <= self.dur + .05

    def word_at(self, t):
        """the first kept word starting at or after output time t"""
        return next((w for w in self.words if w["o"] >= t - 1e-3), None)

    def effect(self, eid, w, params=None, note="", window=3.0, text=None, end_w=None):
        self.effects.append({"id": _rid("e", len(self.effects)) + eid[:3], "effect": eid, "word_i": w["i"],
                             "word_end_i": (end_w or w)["i"], "word": text or w["text"], "at": w["start"],
                             "status": "proposed", "params": params or {}, "note": note or self.why, "by": "style:" + self.style["id"]})
        self.busy.append((w["o"], w["o"] + window))

    def sound(self, file, t, vol, note):
        if t < 0 or t > self.dur:
            return
        meta = next((s for s in json.loads((LIB / "sfx.json").read_text()) if s["file"] == file), {"name": file})
        near = min(self.words, key=lambda w: abs(w["o"] - t)) if self.words else {"i": 0}
        self.sfx.append({"id": _rid("s", len(self.sfx)) + "st", "file": file, "name": meta.get("name", file), "at": round(t, 3), "word_i": near["i"],
                         "clock": "output", "volume": vol, "status": "proposed", "why": note, "by": "style:" + self.style["id"]})

    def phrase_end(self, s, n_min=3, n_max=6):
        """the last clause of a sentence, 3–6 words (Clean White statement / Neon lead-in + key word)"""
        ws = s[-n_max:]
        for k in range(len(ws) - n_min, -1, -1):          # start after a comma inside the window
            if k > 0 and ws[k - 1]["text"].endswith(","):
                ws = ws[k:]
                break
        return ws if len(ws) >= min(n_min, len(s)) else s

    def caption_place(self, where):
        f = self.face
        if where == "above":
            return {"x": .5, "y": round(max(.07, min(.2, f[1] - .06)), 4), "w": .86}
        return {"x": .5, "y": round(max(.5, min(.84, f[1] + f[3] + .1)), 4), "w": .86}


def _spaced(times, gap):
    out = []
    for t in sorted(times):
        if not out or t - out[-1] >= gap:
            out.append(round(t, 3))
    return out


STOP = {"that", "this", "with", "from", "have", "what", "when", "your", "they", "them", "then", "just", "really", "would",
        "there", "their", "about", "because", "since", "which", "these", "those", "were", "will", "been", "being", "much",
        "very", "into", "than", "some", "also", "even", "still", "here", "where", "could", "should", "going", "gonna",
        "first", "look", "like", "want", "know", "think", "make", "used", "something", "anything", "everything", "nothing",
        "someone", "anyone", "everyone", "thing", "things", "stuff"}


def _key(ws):
    """the strongest word: digits / money first, then the longest word that is not a filler, with the voice as a
    tie-breaker: each unit of measured emphasis (`stress`, engine/rhythm.py: louder / higher / held longer than the
    words around it) counts as 2 more letters (18 Nov 2026, idea from rea-video's prosody measures)"""
    num = [w for w in ws if re.search(r"[\d€$%]", w["text"])]
    if num:
        return num[0]
    words = [w for w in ws if re.sub(r"\W", "", w["text"].lower()) not in STOP] or ws
    return max(words, key=lambda w: len(re.sub(r"\W", "", w["text"])) + 2 * min(1.5, w.get("stress", 0)))


def _said(key):
    """a note when the voice stressed the key word"""
    return f", “{key['text']}” said with emphasis" if key.get("stress", 0) >= 1 else ""


def _content(w):
    t = re.sub(r"[^\w€$%]", "", w["text"].lower())
    return len(t) > 3 and t not in STOP


def clean_white(pl):
    """Clean White: Tier S captions + 3–6 statement stacks per 15 s (one with background blur), the clean-white card once,
    light leaks at a few sentence changes, a white flash out of the card, punch-ins 1.0 ↔ 1.15 at phrase changes,
    the celf whooshes / snapshot on the transitions only, Hip-Hop 2 ~13 dB under the voice, −15 LUFS."""
    f = pl.face
    above = f[1] > .22                       # room above the head: Tier S there (ref1); else on the chest
    text = {"size": 54, "words_per_line": 2, "anim": "blurin", "glow": "#FFFFFF", "outline_w": 0,
            "cap_pos": pl.caption_place("above" if above else "chest")}
    # the card: once, at the start of a sentence in the middle of the reel (an intro / name moment reads best)
    mid = [s for s in pl.sentences if pl.dur * .3 <= s[0]["o"] <= pl.dur * .7 and pl.free(s[0]["o"], s[0]["o"] + 3)]
    intro = [s for s in pl.sentences if re.match(r"(?i)(my name|i'?m |i am |this is|meet)", " ".join(w["text"] for w in s))]
    card_s = (intro or mid or [None])[0]
    if card_s:
        w = card_s[0]
        ws = card_s[:6]
        key = _key(ws[1:]) if len(ws) > 1 else ws[0]
        ws = ws[:ws.index(key) + 1]
        pl.effect("white-card", w, {"text": " ".join(x["text"] for x in ws[:-1]) or ws[0]["text"], "italic": key["text"]},
                  "the clean-white card set-piece (§6.1)", text=" ".join(x["text"] for x in ws), end_w=ws[-1])
        pl.sound("Whoosh_01_Sway.wav", w["o"] + .05, .28, "card push (Clean White sound map)")
        after = pl.word_at(w["o"] + 3.0)
        if after and after["o"] - (w["o"] + 3) < .8:
            pl.effect("light-leak", after, {"tone": "flash", "punch": "no"}, "white flash out of the card (§5)", window=.4)
            pl.sound("Camera_01_Snapshot.wav", after["o"] + .05, .25, "white flash (Clean White sound map)")
    # statement stacks: the closing clause of sentences, spaced, 3–6 per 15 s
    want = max(1, round(pl.dur / 15 * 3))
    cands = sorted(pl.sentences, key=lambda s: -sum(_content(w) for w in pl.phrase_end(s)))
    stacks = []
    for s in cands:
        ph = pl.phrase_end(s)
        a = ph[0]["o"]
        if len(stacks) >= want or not pl.free(a, a + 3, .2):
            continue
        stacks.append(ph)
        pl.busy.append((a, a + 3))
    stacks.sort(key=lambda ph: ph[0]["o"])
    pl.busy = [b for b in pl.busy if all(abs(b[0] - ph[0]["o"]) > 1e-6 for ph in stacks)]
    for k, ph in enumerate(stacks):
        focus = k == len(stacks) // 2 and len(stacks) > 1
        pl.effect("statement-stack", ph[0], {"text": " ".join(w["text"] for w in ph), "focus": "yes" if focus else "no"},
                  "statement stack (§4.2)" + (", background-blur focus (§6.3)" if focus else ""),
                  text=" ".join(w["text"] for w in ph), end_w=ph[-1])
        if focus:
            pl.sound("Whoosh_03_Reverse_Rise.wav", ph[0]["o"] + .05 - .69, .30, "into the blur focus (Clean White sound map)")
    # light leaks: at sentence changes outside the effects, about one every 8 s (≤ 3 transitions per 15 s with the card)
    # candidates: every sentence or clause start; a leak may run into the start of a statement (it is drawn first, the
    # words blur in over it) but never lands in the middle of one, nor on the card
    starts = [s[0] for s in pl.sentences[1:]] + [w for k, w in enumerate(pl.words) if k and pl.words[k - 1]["text"].endswith(",")]
    starts.sort(key=lambda w: w["o"])
    last, budget = -9.0, max(1, round(pl.dur / 15 * 2))
    for w in starts:
        t = w["o"]
        card_t = [e for e in pl.effects if e["effect"] == "white-card"]
        on_card = any(abs(t - pl.words[[x["i"] for x in pl.words].index(c["word_i"])]["o"]) < .6 for c in card_t)
        if budget and not on_card and t - last >= 5 and t > 1.0 and all(not (x + .05 < t < y) for x, y in pl.busy):
            pl.effect("light-leak", w, {"tone": "cool", "punch": "no"}, "light leak at a thought change (§5)", window=.5)
            pl.sound("Whoosh_02_Wave.wav", t - .06, .28, "light leak (Clean White sound map)")
            last, budget = t, budget - 1
    # punch-ins: a hard step at phrase changes, about one per talking-head segment
    pl.punches = _spaced([s[0]["o"] for s in pl.sentences[1:]], 1.5)
    action_sounds(pl, .22)
    return {"text": text, "punch_in": 1.15, "music": {"id": "deff-hiphop-2", "volume": .115, "fade_in": .3, "fade_out": .8}, "lufs": -15}


# ---- Cinema Lexicon, rebuilt 18 Nov 2026 on Alina's approved CL01 v6 (~/Editing Beast/projects/cl01/out/CL01_cinema-lexicon_v6.mp4)
# and the CL02 lessons (STYLE.md §10). Levels: v6 mixed the sounds against the raw voice (−27 LUFS); this engine mixes
# them against the voice already at −15 LUFS, so every v6 volume is multiplied by K (12 dB) to keep the same balance.
K = 4.0
FILLER = {"i", "i'm", "im", "want", "to", "wait", "wait,", "so", "okay", "ok", "guys", "hi", "hey", "um", "uh", "gonna", "going",
          "let", "me", "just", "and", "like", "well", "now", "you", "know", "yeah", "the", "a", "really", "we're", "we", "let's",
          "were", "gotta", "about"}
TRAIL = {"right", "now", "today", "guys", "too", "as", "well", "here", "though", "okay", "ok"}
# the creator shows the product or talks to the viewer: her own take stays (Alina, CL01: "remove the video at much FUN to use")
DEICTIC = re.compile(r"(?i)\b(this app|the app|over here|right here|this button|look at this|here it is|on my phone|this one|look how|look at|show (it|this) to you|to you as well|my name|name is|meet (me|my))\b")
NUMWORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "fifteen": 15, "twenty": 20, "thirty": 30, "fifty": 50, "hundred": 100}
UNIT = re.compile(r"(?i)^(minutes?|mins?|seconds?|secs?|hours?|days?|weeks?|months?|years?|percent|%|euros?|dollars?|times|x|steps?|clicks?|taps?|people|users)\W*$")
PUNCHY = re.compile(r"(?i)^(wait|literally|never|forever|always|stop|fun|insane|crazy|free|everything|nothing|none|best|worst|love|hate|obsessed)\W*$")
NO_PICTURES = re.compile(r"(?i)(no|without|don'?t (?:need|want|add)(?: any)?) (pictures|images|photos|stock|b-?roll|clips|example clips)|just (my|our|the) (own )?footage")


CLAUSE = re.compile(r"(?i)^(and|but|so|if|because|since|or|when|then|which|while|until|unless|cause)$")
FUNC = STOP | {"the", "and", "but", "you", "your", "for", "are", "was", "has", "had", "its", "it's", "i'm", "i've", "i'd", "don't", "didn't",
               "can", "can't", "all", "out", "how", "who", "why", "our", "his", "her", "she", "him", "yes", "not", "one", "get", "got",
               "let", "did", "does", "doing", "well", "over", "end", "used", "able", "way", "lot", "now", "too", "any", "each", "own",
               "we're", "they're", "you're", "he's", "she's", "that's", "there's", "gonna", "wanna", "yeah", "guys", "okay"}


def _word(w):
    return re.sub(r"[^\w'€$%]", "", w["text"].lower())


def _meaning(ws):
    """how many words of a phrase carry meaning (a thing, an action, a feeling): what an example clip can show"""
    return sum(1 for w in ws if len(_word(w)) >= 3 and _word(w) not in FUNC)


def _phrases(pl, breaks=()):
    """sentences split into spoken phrases, as CL01 v6 cut them: at commas, at pauses over 0.35 s, before a new clause
    ("and", "but", "so", "if"… once the phrase has 3 words), at a short breath once it has 4, and before 2.6 s"""
    out = []
    for s in pl.sentences:
        cur = []
        for w in s:
            gap = w["o"] - cur[-1]["oe"] if cur else 0
            if cur and (gap > .35 or w["o"] - cur[0]["o"] > 2.6 or (len(cur) >= 3 and CLAUSE.match(_word(w))) or w["i"] in breaks
                        or (len(cur) >= 4 and gap > .15)):
                out.append(cur)
                cur = []
            cur.append(w)
            if re.search(r"[,;:]$", w["text"]) and len(cur) >= 2:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
    merged = []
    for ph in out:                       # a lone word joins the next phrase of its sentence
        if merged and len(merged[-1]) == 1 and not re.search(r"[.?!…]$", merged[-1][0]["text"]) and ph[0]["o"] - merged[-1][-1]["oe"] < .35:
            merged[-1] = merged[-1] + ph
        else:
            merged.append(ph)
    return merged


def _span(pl, phs, k):
    """(start, end) of phrase k in output time: until the next phrase starts (short gaps) or its last word ends"""
    a = phs[k][0]["o"]
    nxt = phs[k + 1][0]["o"] if k + 1 < len(phs) else pl.dur
    b = nxt if nxt - phs[k][-1]["oe"] < .6 else phs[k][-1]["oe"] + .2
    return a, min(b, pl.dur)


def _txt(ws):
    return " ".join(w["text"] for w in ws)


# the human meaning of common phrases → what a stock clip can show (CL01 feedback: "showed it to me" → two people on one
# phone, "fun" → friends laughing at dinner, "take forever / what to eat" → someone thinking, torn between two dishes)
MEANING = [   # (what the phrase says, a Pexels search, short Mixkit tags)
    (r"\b(show(ed|s)?|told|recommend\w*)\b.*\b(me|us)\b|\bfriend\w* (showed|told)", "two friends looking at a phone", ["friends-phone", "phone"]),
    (r"\b(fun|laugh\w*|enjoy\w*|happy|party)\b", "friends laughing together", ["laughing-friends", "friends"]),
    (r"\b(decid\w*|indecisive|can'?t choose|make up my mind|what to eat|choose|choosing)\b", "person thinking indecisive", ["woman-thinking", "thinking"]),
    (r"\b(forever|wait\w*|takes? (so )?long|slow|bored)\b", "person waiting bored", ["bored", "waiting"]),
    (r"\b(craving\w*|hungry|starving)\b", "pizza cheese pull", ["pizza", "burger"]),
    (r"\b(eat\w*|dinner|lunch|food|meal|tast\w*|delicious)\b", "person eating food", ["eating", "food"]),
    (r"\b(lik(e|ing)|love)\b.*\b(something|it|this)\b", "person tasting food happy", ["eating", "tasting"]),
    (r"\b(don'?t like|hate|disgust\w*|gross)\b", "person disgusted face", ["disgusted", "disgust"]),
    (r"\b(share|send|tell your friends|with your friends)\b", "friends sharing a phone", ["friends-phone", "smartphone"]),
    (r"\b(deliver\w*|order\w*|arriv\w*|door)\b", "food delivery at the door", ["delivery", "food-delivery"]),
    (r"\b(money|price|cheap|expensive|pay\w*|save)\b", "person paying with phone", ["payment", "money"]),
    (r"\b(work\w*|office|job|boss|meeting)\b", "people working in an office", ["office", "working"]),
    (r"\b(stress\w*|tired|overwhelm\w*|busy)\b", "stressed tired person", ["stressed", "tired"]),
    (r"\b(sleep\w*|morning|wake)\b", "person waking up morning", ["morning", "waking-up"]),
    (r"\b(gym|workout|fit|run\w*)\b", "person working out", ["workout", "gym"]),
    (r"\b(video|film\w*|camera|record\w*|content)\b", "person filming with a camera", ["filming", "camera"]),
]


def _queries(ws):
    """Pexels searches for a phrase: what it means first (MEANING), then its own meaningful words"""
    line = _txt(ws).lower()
    out = [q for rx, q, _ in MEANING if re.search(rx, line)][:2]
    c = [_word(w) for w in ws if len(_word(w)) >= 3 and _word(w) not in FUNC and _word(w) not in ("literally", "really", "actually", "today")]
    if c:
        out.append(" ".join(c[:3]))
    return list(dict.fromkeys(out)) or [line]


def _tags(ws):
    """short Mixkit search tags (its search finds 1–2 word tags): the meaning's tags, then the phrase's own words"""
    line = _txt(ws).lower()
    out = [t for rx, _, tags in MEANING if re.search(rx, line) for t in tags][:4]
    c = [_word(w) for w in ws if len(_word(w)) >= 4 and _word(w) not in FUNC and _word(w) not in ("literally", "really", "actually", "today")]
    out += c[:2]
    return list(dict.fromkeys(re.sub(r"[^a-z\-]", "", t) for t in out if t))


def _query(ws):
    return _queries(ws)[0]


def _num(w):
    t = re.sub(r"[^\w%€$.]", "", w["text"].lower())
    if re.match(r"^[€$]?\d+([.,]\d+)?%?$", t):
        return t
    return str(NUMWORDS[t]) if t in NUMWORDS else None


def cinema_lexicon(pl):
    """Cinema Lexicon as in CL01 v6: the creator's take carries the voice; one literal example clip per phrase that needs a
    picture (Pexels, never more than 2 in a row, the creator between); the brand's open card on the first call to action;
    the product's real UI dropped on the take when its features are named (buttons falling on "categories", a button
    popping on its name, swipe chips, the official screen recording in a phone on "options"); a giant number on cream;
    for ads, a close card (take shrinks into a rounded card under the app icon + name, chat bubbles, slogan) and a held
    last frame; interviews and opinion pieces end on the punchline instead (CL02). Small centred captions cut on the word,
    1 key word in about 3–4 big. Swish on every example-clip cut, pops on buttons, a reverse rise into the cards, the bed
    9 dB under the voice. "No pictures" in the brief (CL02): no clips, punch-ins on the key words instead."""
    B = pl.brand or {}
    pills = B.get("pills") or []
    labels = [p["label"] for p in pills] + ([B["cta_pill"]["label"]] if B.get("cta_pill") else [])
    # numbers with a unit get their own phrase ("in less than | 10 minutes"), so the giant number has its own beat
    LEAD = {"in", "less", "than", "under", "only", "just", "about", "over", "more", "around", "within", "for", "like", "almost", "nearly"}
    nums, breaks = [], set()
    for j, w in enumerate(pl.words[:-1]):
        if _num(w) and UNIT.match(pl.words[j + 1]["text"]):
            i0 = j
            while i0 > 0 and j - i0 < 3 and _word(pl.words[i0 - 1]) in LEAD:
                i0 -= 1
            nums.append((i0, j, j + 1))
            breaks.add(pl.words[i0]["i"])
            if j + 2 < len(pl.words):
                breaks.add(pl.words[j + 2]["i"])
    for j, w in enumerate(pl.words[:-1]):       # someone introduces themself: their own beat (Alina, IMG_5978 feedback)
        if _word(w) == "my" and _word(pl.words[j + 1]) == "name" or _word(w) in ("i'm", "i") and j + 1 < len(pl.words) and pl.words[j + 1]["text"][:1].isupper() and _word(pl.words[j + 1]) not in FUNC:
            breaks.add(w["i"])
    phs = _phrases(pl, breaks)
    spans = [_span(pl, phs, k) for k in range(len(phs))]
    used = set()                               # phrases already given a picture
    text_all = " ".join(w["text"].lower() for w in pl.words)
    brief = (pl.p.get("_brief") or {}).get("prompt", "")
    no_pictures = bool(NO_PICTURES.search(brief))
    is_ad = bool(B.get("name")) and B.get("kind", "app") in ("app", "product", "brand", "") and bool(
        re.search(r"\b(app|download|try|link|order|get it|use it|share|sign up|subscribe|buy|shop)\b", text_all))
    hide, dark, upper = "hide", "dark", "upper"

    # 1. close bookend for ads: the last phrase; the last frame is held 1.3 s so the slogan is read (v6: 38.44 → 40.80)
    tail = 0.0
    if is_ad and len(phs) > 3:
        k = len(phs) - 1
        a, _ = spans[k]
        if pl.dur - a < 3.2:
            pl.effect("lexicon-close", phs[k][0], {"name": B.get("name", ""), "slogan": B.get("slogan") or B.get("tagline") or "", "hold": 3, "caption": dark},
                      "close bookend for an ad: take into a card, app icon + name, bubbles, slogan (CL01 v6)", window=pl.dur + 2 - a,
                      text=_txt(phs[k]), end_w=phs[k][-1])
            pl.sound("Whoosh_01_Sway.wav", a - .02, .22 * K, "into the close card (CL01 v6)")
            pl.sound("Pop_02_Quick.wav", a + .26, .22 * K, "chat bubble (CL01 v6)")
            pl.sound("Pop_01_Tap.wav", a + .42, .22 * K, "chat bubble (CL01 v6)")
            pl.sound("Sparkle_04_Scene_Reveal.wav", a + .58, .18 * K, "end card (CL01 v6)")
            used.add(k)
            tail = 1.3

    # 2. open bookend: the first call to action / claim in the first 4.5 s, from its first strong word (v6 "dare you to try this app.")
    cands = [k for k in range(len(phs)) if spans[k][0] < 4.5 and k not in used]
    pick = next((k for k in cands if re.search(r"(?i)\b(try|dare|need|must|stop|watch|look|this app|you have to|here's|meet|introduc)", _txt(phs[k]))), None)
    if pick is None and cands:
        pick = max(cands, key=lambda k: sum(_content(w) for w in phs[k]))
    if pick is not None:
        ph = phs[pick]
        j = 0
        while j < len(ph) - 2 and re.sub(r"[^\w']", "", ph[j]["text"].lower()) in FILLER:
            j += 1
        card = ph[j:]
        while len(card) > 2 and _word(card[-1]) in TRAIL:       # "…system right now." → the card ends on the thing itself
            card = card[:-1]
        a, b = card[0]["o"], spans[pick][1]
        if len(card) >= 3:
            script, small, big = card[0]["text"].strip(",."), _txt(card[1:-2]), _txt(card[-2:])
        else:
            script, small, big = "", "", _txt(card)
        hold = round(max(.8, min(2.2, b - a)), 2)
        pl.effect("lexicon-open", card[0], {"text": _txt(card), "script": script, "small": small, "big": big, "hold": hold, "caption": hide},
                  "open bookend on the first call to action (CL01 v6)", window=hold, text=_txt(card), end_w=card[-1])
        pl.sound("Whoosh_03_Reverse_Rise.wav", max(0, a - .68), .25 * K, "into the open card (CL01 v6)")
        for i in range(min(3, len(pills))):
            pl.sound(["Pop_01_Tap.wav", "Pop_02_Quick.wav"][i % 2], a + .22 + i * .16, .22 * K, "app button pops on the open card (CL01 v6)")
        used.add(pick)

    # 3. the product's own UI, when its features are named (needs the brand kit's buttons)
    for k, ph in enumerate(phs):
        if k in used:
            continue
        a, b = spans[k]
        line = _txt(ph).lower()
        if not pl.free(a + .02, b - .02):
            continue
        m = next((i for i, w in enumerate(ph) if re.match(r"(?i)^(categor\w*|menus?|filters?|cuisines?|genres?|flavou?rs|types|kinds)\W*$", w["text"])), None)
        if pills and m is not None:
            i0 = m - 1 if m and len(_word(ph[m - 1])) >= 3 and _word(ph[m - 1]) not in FUNC else m     # "food categories": from "food"
            w0, a = ph[i0], ph[i0]["o"]
            hold = round(max(.9, min(1.6, max(ph[m]["oe"] + .3, b) - a if b - ph[m]["oe"] < .5 else ph[m]["oe"] + .3 - a)), 2)
            pl.effect("lexicon-ui-drop", w0, {"hold": hold, "caption": upper},
                      f"the app's real buttons drop on “{_txt(ph[i0:m + 1])}” (CL01 v6 food categories)", window=hold, text=_txt(ph[i0:m + 1]), end_w=ph[m])
            pl.sound("Whoosh_02_Wave.wav", a - .04, .16 * K, "buttons fall (CL01 v6)")
            for i in range(4):
                pl.sound(["Pop_01_Tap.wav", "Pop_02_Quick.wav"][i % 2], a + .30 + i * .17, .16 * K, "button lands (CL01 v6)")
            used.add(k)
            continue
        hit = next(((w, lab) for w in ph for lab in labels if lab.split()[0].lower() not in FUNC
                    and lab.split()[0].lower() in re.sub(r"[^\w]", " ", w["text"].lower()).split()), None)
        if not hit and re.search(r"\b(button|tap|press|click)\b", line) and B.get("cta_pill"):
            hit = (next(w for w in ph if re.search(r"(?i)button|tap|press|click", w["text"])), B["cta_pill"]["label"])
        if hit:
            w, lab = hit
            t = w["o"]
            pl.effect("lexicon-ui-pop", w, {"label": lab, "hold": round(max(.7, min(2.4, b - t)), 2)},
                      f"the “{lab}” button pops when it is named (CL01 v6 surprise button)", window=b - t, text=w["text"])
            pl.sound("Mouse_Click_02_Tactile.wav", t - .02, .35 * K, "button tap (CL01 v6)")
            pl.sound("Pop_02_Quick.wav", t + .04, .25 * K, "button pops (CL01 v6)")
            used.add(k)
            continue
        sw = next((w for i, w in enumerate(ph) if re.match(r"(?i)^(left|right)\W*$", w["text"]) and re.search(r"(?i)swip|slid", _txt(ph[max(0, i - 3):i]))), None)
        if sw:
            right = sw["text"].lower().startswith("right")
            pl.swipe_keys = getattr(pl, "swipe_keys", []) + [sw["i"]]
            pl.effect("lexicon-swipe", sw, {"dir": "right" if right else "left", "hold": .5}, f"swipe chip flies {'right' if right else 'left'} (CL01 v6)",
                      window=.5, text=sw["text"])
            if right:
                pl.sound("Pop_01_Tap.wav", sw["o"], .28 * K, "swipe right (CL01 v6)")
                pl.sound("Whoosh_05_Fast_Flick.wav", sw["o"] + .04, .2 * K, "swipe right (CL01 v6)")
            else:
                pl.sound("Whoosh_05_Fast_Flick.wav", sw["o"], .25 * K, "swipe left (CL01 v6)")
            used.add(k)
            continue
        if (B.get("screen_video") or B.get("phone")) and re.search(r"\b(how many|so many|options|choices|scroll\w*|swipe through|look at all)\b", line):
            pl.effect("lexicon-phone-demo", ph[0], {"hold": round(max(.8, min(2.4, b - a)), 2), "caption": dark},
                      f"the app's own screen recording in a phone on “{_txt(ph)}” (CL01 v6 options)", window=b - a, text=_txt(ph), end_w=ph[-1])
            for i in range(3):
                pl.sound(["Pop_02_Quick.wav", "Pop_01_Tap.wav"][i % 2], a + .12 + i * .16, .14 * K, "app buttons pop (CL01 v6)")
            used.add(k)

    # 4. a number with its unit: the giant number on the brand's cream card (v6 "in less than 10 minutes.")
    for k, ph in enumerate(phs):
        if k in used:
            continue
        a, b = spans[k]
        i = next((i for i, w in enumerate(ph) if _num(w) and i + 1 < len(ph) and UNIT.match(ph[i + 1]["text"])), None)
        if i is None or not pl.free(a + .02, b - .02):
            continue
        lead = _txt(ph[:i])
        n = _num(ph[i])
        if re.search(r"(?i)less than|under|below", lead):
            n = "<" + n
        elif re.search(r"(?i)more than|over|above", lead):
            n = n + "+"
        hold = round(max(.9, min(2.4, b - a)), 2)
        tn = round(max(.1, ph[i]["o"] - a), 2)
        pl.effect("lexicon-number", ph[0], {"lead": lead, "number": n, "unit": _txt(ph[i + 1:]), "t_number": tn,
                                            "t_unit": round(max(tn + .1, ph[i + 1]["o"] - a), 2), "hold": hold, "caption": hide},
                  f"giant number “{n}” on a cream card (CL01 v6)", window=hold, text=_txt(ph), end_w=ph[-1])
        pl.sound("Whoosh_03_Reverse_Rise.wav", a + tn - .65, .3 * K, "into the giant number (CL01 v6)")
        used.add(k)

    # 5. example clips: one literal clip per phrase that names a thing, an action or a feeling; never more than 2 in a row
    clips = []
    if not no_pictures:
        cap = max(1, round(pl.dur / 5))          # v6: 8 clips in 40 s
        # 24 Nov 2026 (Alina: irrelevant pictures): a phrase that names a concrete thing (apple, car, phone…) comes first and
        # may be short ("and a car"); a phrase with nothing concrete only gets a clip slot when its meaning is strong
        import stock as _stock
        thing = lambda ph: bool(_stock.concrete_words(_txt(ph)))
        ok = [k for k, ph in enumerate(phs) if k > 0 and k not in used and pl.free(spans[k][0] + .02, spans[k][1] - .02)
              and not DEICTIC.search(_txt(ph))
              and ((thing(ph) and spans[k][1] - spans[k][0] >= .45)
                   or (spans[k][1] - spans[k][0] >= .8 and (_meaning(ph) >= 2 or (_meaning(ph) == 1 and spans[k][1] - spans[k][0] >= 1.4))))]
        if any(thing(phs[k]) for k in ok):        # concrete things named: only those get pictures
            ok = [k for k in ok if thing(phs[k])]
        score = lambda k: (3 if thing(phs[k]) else 0) + _meaning(phs[k]) + (1 if 1.2 <= spans[k][1] - spans[k][0] <= 2.8 else 0) + .01 * (k % 7)
        chosen = set()
        for k in sorted(ok, key=score, reverse=True):
            if len(chosen) >= cap:
                break
            c = chosen | {k}
            if any({j, j + 1, j + 2} <= c for j in range(k - 2, k + 1)):     # never 3 example clips in a row
                continue
            chosen.add(k)
        clips = [(k, *spans[k]) for k in sorted(chosen)]
        for k, a, b in clips:
            pl.busy.append((a, b))
        swish = [("Whoosh_05_Fast_Flick.wav", .14), ("Whoosh_02_Wave.wav", .16), ("Whoosh_01_Sway.wav", .12)]
        for n, (k, a, b) in enumerate(clips):
            f, v = swish[n % 3]
            pl.sound(f, a - .02, v * K, "cut to the example clip (CL01 v6)")
    pl.clips = [{"word_i": phs[k][0]["i"], "at": phs[k][0]["start"], "word_end_i": phs[k][-1]["i"], "phrase": _txt(phs[k]),
                 "query": _query(phs[k]), "queries_more": _queries(phs[k])[1:], "tags": _tags(phs[k]), "hold": round(b - a, 2)} for k, a, b in clips]

    # 6. key words: ~1 in 3–4 phrases, the stressed or punchy word, shown alone and big
    keys, last_key = [], -9
    hide_w = [(o, o + float(e["params"].get("hold", 3))) for e in pl.effects if (e["params"] or {}).get("caption") == hide
              for o in [next(w["o"] for w in pl.words if w["i"] == e["word_i"])]]
    for k, ph in enumerate(phs):
        mid = (ph[0]["o"] + ph[-1]["oe"]) / 2
        if any(x <= mid < y for x, y in hide_w):
            continue
        cand = [w for w in ph if PUNCHY.match(w["text"])]
        if cand:
            pick = cand[0]
        elif k - last_key >= 2 or re.search(r"[.!?]$", ph[-1]["text"]):
            mean = [w for w in ph if len(_word(w)) >= 4 and _word(w) not in FUNC]
            # the stressed word, or the last word that carries meaning (sentence ends carry the stress in speech)
            pick = max(mean, key=lambda w: w.get("stress", 0) + (1.5 if w is mean[-1] else 0) + (.5 if len(_word(w)) >= 6 else 0)) if mean else None
        else:
            pick = None
        if pick:
            keys.append(pick["i"])
            last_key = k
    keys += getattr(pl, "swipe_keys", [])
    if phs and phs[0][0]["i"] not in keys and re.match(r"(?i)^(wait|stop|okay|guys|so|look)\W*$", phs[0][0]["text"]):
        keys.append(phs[0][0]["i"])                # v6: the hook word "WAIT," big on the first frame

    text = {"font": "Inter Tight 800", "size": 50, "anim": "lexicon", "shadow": True, "outline_w": 0, "color": "#FFFFFF",
            "case": "lower", "cap_pos": {"x": .5, "y": .82, "w": .86}, "keys": sorted(set(keys)), "key_scale": 2.8, "dark": "#1B1B1F"}
    if no_pictures:                                # CL02: punch-ins on the key words, captions at chest height
        pl.punches = _spaced([w["o"] for w in pl.words if w["i"] in set(keys)], .9)
        text["cap_pos"] = pl.caption_place("chest")
        pin = 1.12
    else:
        pl.punches = []                            # v6: no punch-ins on the take, the example clips are the cuts
        pin = 1.0
    action_sounds(pl, .25, gap=2.5, per15=1)
    return {"text": text, "punch_in": pin, "music": {"id": "jazzy-funk", "volume": .28, "fade_in": .2, "fade_out": 1.0}, "lufs": -15, "tail": tail}


NEON = [("green", r"(€|\$|\d|money|free|save|bonus|win|yes|success|best|easy|grow)"),
        ("red", r"(never|no\b|not|problem|forever|waste|hard|bad|hate|stop|lose|broke|fail)"),
        ("purple", r"(ai|app|game|magic|surprise|fun|swipe|random)"),
        ("cyan", r"(calm|simple|clear|fast|quick|smart|tech|phone|sorted)")]


def neon_dimension(pl):
    """Neon Dimension: glowing wide caps on the chest; a neon world (dark room + lead-in + slammed key word in the colour
    of its meaning) for the claims, about every other sentence; a light burn back to the presenter after each; jump
    zooms 1.0 ↔ 1.2; the CTA in a neon pill at the end; sub boom + swish on every slam, a flash hit on every burn,
    the dark 70 BPM bed ~7–8 dB under the voice, −14 LUFS."""
    text = {"size": 70, "words_per_line": 2, "anim": "glowpop", "glow": "#FFFFFF", "outline_w": 0, "case": "upper",
            "cap_pos": pl.caption_place("chest")}
    last = pl.sentences[-1] if len(pl.sentences) > 1 else None
    for n, s in enumerate(pl.sentences):
        if s is last:
            break
        ph = pl.phrase_end(s, 2, 6)
        a = ph[0]["o"]
        if n % 2 and not any(re.search(NEON[0][1], w["text"].lower()) for w in ph):
            continue
        if not pl.free(a, a + 3.4, .1):
            continue
        key = next((w for w in ph if re.search(NEON[0][1], w["text"].lower())), None) or _key(ph)
        colour = next((c for c, rx in NEON if re.search(rx, key["text"].lower())), "green" if n % 3 == 0 else "cyan" if n % 3 == 1 else "purple")
        pl.effect("neon-keyword", ph[0], {"text": " ".join(w["text"] for w in ph), "key": key["text"], "neon": colour},
                  f"neon world, {colour} (§4.2)" + _said(key), text=" ".join(w["text"] for w in ph), end_w=ph[-1])
        slam = a + .15 + (len(ph) - 1) * .14 + .1
        pl.sound("ND_sub_boom.wav", slam, .45, "key-word slam (Neon kit)")
        pl.sound("ND_swish.wav", slam - .05, .35, "key-word slam (Neon kit)")
        back = pl.word_at(a + 2.95)
        if back and back["o"] - (a + 2.95) < .9 and pl.free(back["o"], back["o"] + .4):
            pl.effect("light-burn", back, {"kind": "glitch" if colour == "red" else "burn"}, "back to the presenter (§7)", window=.4)
            pl.sound("ND_glitch.wav" if colour == "red" else "ND_flash_hit.wav", back["o"] - .06, .4, "transition (Neon kit)")
            pl.sound("ND_sub_boom.wav", back["o"], .3, "transition (Neon kit)")
    if last and pl.free(last[0]["o"], last[0]["o"] + 3):
        cta = pl.phrase_end(last, 2, 4)
        pl.effect("neon-pill", cta[0], {"text": " ".join(w["text"] for w in cta)}, "CTA in a neon pill (§3, §6)", text=" ".join(w["text"] for w in cta), end_w=cta[-1])
        pl.sound("Pop_01_Tap.wav", cta[0]["o"] + .05, .4, "neon pill (Neon Dimension sound map)")
    pl.punches = _spaced([w["o"] for k, w in enumerate(pl.words) if k and k % 3 == 0], .9)
    action_sounds(pl, .3, gap=1.5)
    return {"text": text, "punch_in": 1.2, "music": {"id": "nd-dark-bed", "volume": .32, "fade_in": .2, "fade_out": .8}, "lufs": -14}


# ---- sound and music follow the content (Alina, 18 Nov 2026: "the text effects and video/photo templates need to be
# kinda the same, but the sound effects and background music need to be different according to the actions happening,
# information, or I can mention a vibe for the song")
ACTION_SFX = [   # (what is said, celf pack sound): the action or information gets its own sound, once, on its word
    (r"^(swip|scroll|slid)", "Whoosh_05_Fast_Flick.wav", "a swipe"),
    (r"^(tap|tapp|click|press|button|select|choos|pick)", "Mouse_Click_02_Tactile.wav", "a tap / choice"),
    (r"^(typ|writ|search|messag|text)", "Typing_03_Short_Phrase.wav", "typing / writing"),
    (r"^(photo|pic|camera|screenshot|film|selfie)", "Camera_02_Shutter_Click.wav", "a photo"),
    (r"(€|\$|^money|^price|^pay|^cheap|^free$|^save|^bonus|^coin|^discount|^deal|^euro)", "Chime_01_Coin_Pickup.wav", "money"),
    (r"^(done|finish|sorted|decid|ready|perfect|solved|win|won)", "Chime_03_Bright_Ding.wav", "done / decided"),
    (r"^(magic|surpris|wow|discover|reveal|secret|new$|love|amazing)", "Sparkle_05_Airy_Star.wav", "a surprise / discovery"),
    (r"^(pop|open|appear|notif|ping|show)", "Pop_02_Quick.wav", "something appears"),
    (r"^(fun|funny|laugh|lol|crazy)", "Pop_01_Tap.wav", "fun"),
    (r"^(minute|second|fast|quick|instant)", "UI_01_Tiny_Bleep.wav", "time / speed"),
]


def action_sounds(pl, vol, gap=2.0, per15=4):
    """one sound per action or piece of information said, spaced, never on top of a transition sound"""
    taken = [s["at"] for s in pl.sfx]
    budget = max(1, round(pl.dur / 15 * per15))
    for w in pl.words:
        word = re.sub(r"[^\w€$]", "", w["text"].lower())
        hit = next(((f, why) for rx, f, why in ACTION_SFX if re.search(rx, word)), None)
        if not hit or budget <= 0:
            continue
        t = w["o"] + .03
        if any(abs(t - x) < gap for x in taken):
            continue
        pl.sound(hit[0], t, vol, f"“{w['text']}”: {hit[1]}")
        taken.append(t)
        budget -= 1


MOOD = [   # mood of what is said → a vibe tag in library/music.json
    ("food", r"^(food|eat|eating|hungry|dinner|lunch|breakfast|pizza|burger|sushi|tasty|delicious|cook|recipe|restaurant|order)"),
    ("fun", r"^(fun|funny|lol|crazy|silly|joke|laugh|weird|chaos|wild)"),
    ("upbeat", r"^(app|swipe|easy|love|best|amazing|try|new|friends|party|today)"),
    ("motivational", r"^(goal|grow|success|work|business|money|win|better|learn|start|build|dream|plan|system|content)"),
    ("emotional", r"^(feel|heart|miss|alone|sad|cry|life|remember|story|lost|hard)"),
    ("dramatic", r"^(never|forever|everything|nothing|biggest|insane|shock|secret|warning|truth)"),
    ("tech", r"^(ai|tech|code|data|robot|future|digital|software|algorithm)"),
    ("chill", r"^(relax|calm|slow|chill|cozy|morning|weekend|study|coffee|sleep)"),
]


def pick_music(pl, default_id, vibe_text=""):
    """the bed: Alina's vibe words win (matched on the tracks' vibe tags), else the mood of what is said, else the
    style's default. Ties keep the style's default. Returns (track id, why)."""
    tracks = json.loads((LIB / "music.json").read_text())
    def score(words, weights=None, penalise=True):
        weights = weights or [1] * len(words)
        hit = lambda w, v: len(w) > 2 and (w == v or w.startswith(v[:5]) and len(v) >= 4 or v.startswith(w) and len(w) >= 4)
        sc = {t["id"]: sum(wt for w, wt in zip(words, weights) if any(hit(w, v) for v in t.get("vibe", [])))
              - (.5 if penalise and "placeholder" in t.get("note", "") else 0) for t in tracks}   # the placeholder only when it clearly fits best
        best = max(sc.values()) if sc else 0
        if sc.get(default_id) == best and "placeholder" not in next((t.get("note", "") for t in tracks if t["id"] == default_id), ""):
            return default_id, best
        # among equal scores: tracks that are fine to post first (not a placeholder, not share-alike)
        tops = [t for t in tracks if sc[t["id"]] == best]
        tops.sort(key=lambda t: ("placeholder" in t.get("note", "")) + ("SA" in t.get("licence", "")))
        return tops[0]["id"], best
    if vibe_text.strip():
        tid, best = score(re.findall(r"[a-z\-]+", vibe_text.lower()), penalise=False)
        if best:
            return tid, f"your vibe “{vibe_text.strip()}”"
        return default_id, f"no track in the library fits “{vibe_text.strip()}” yet: ask Claude for one"
    moods = {}
    for w in pl.words:
        word = re.sub(r"\W", "", w["text"].lower())
        for mood, rx in MOOD:
            if re.search(rx, word):
                moods[mood] = moods.get(mood, 0) + 1
    top = sorted(moods, key=moods.get, reverse=True)[:2]
    if top and moods[top[0]] >= 2:
        tid, best = score(top, [moods[m] for m in top])
        if best:
            return tid, "what you say sounds " + " and ".join(f"{m} ({moods[m]} words)" for m in top)
    return default_id, "the style's default bed"


def face_of(project, work):
    """the face box (fractions of the 9:16 frame) over 5 frames of the take (median), for caption placement; when no
    face is found (a hand or the phone in front of it), the top of the person (Vision's saliency box)"""
    try:
        import hfx
        from media import run, sdr_vf
        src = project["source"]
        w = Path(work)
        w.mkdir(parents=True, exist_ok=True)
        fx = project.get("focus_x")
        fx = .5 if fx is None else float(fx)
        frames = []
        for k, q in enumerate((.15, .35, .5, .65, .85)):
            f = w / f"dir_face{k}.jpg"
            run(["-ss", f"{src['duration'] * q:.2f}", "-i", src["file"], "-frames:v", "1", "-vf",
                 f"{sdr_vf(src['file'])}crop=w='min(iw,ih*9/16)':h='min(ih,iw*16/9)':x='max(0,min(iw-ow,{fx}*iw-ow/2))':y='(ih-oh)/2',scale=540:960", f])
            frames.append(f)
        found = hfx.vision(frames)
        faces = [sorted(x.get("faces", []), key=lambda b: -b[2] * b[3])[0] for x in found if x.get("faces")]
        if not faces:
            faces = [[b[0] + b[2] * .3, b[1], b[2] * .4, b[3] * .3] for x in found for b in x.get("objects", [])[:1]]
        if faces:
            med = lambda i: sorted(f[i] for f in faces)[len(faces) // 2]
            return [med(0), med(1), med(2), med(3)]
    except Exception:
        pass
    return [.3, .18, .4, .22]


def voice_stress(project, work):
    """{word i: measured emphasis} of the take (engine/rhythm.py), cached next to the transcription audio"""
    try:
        import rhythm
        from media import extract_audio
        src = Path(project["source"]["file"])
        wav = src.parent / "audio16k.wav"
        if not wav.exists():
            wav = Path(work) / "audio16k.wav"
            Path(work).mkdir(parents=True, exist_ok=True)
            if not wav.exists():
                extract_audio(str(src), str(wav))
        cache = wav.parent / "stress.json"
        key = [len(project["edl"]["words"]), project["edl"]["words"][-1].get("end")] if project["edl"]["words"] else []
        if cache.exists():
            c = json.loads(cache.read_text())
            if c.get("key") == key:
                return {int(k): v for k, v in c["words"].items()}
        st = rhythm.stress(str(wav), project["edl"]["words"])
        cache.write_text(json.dumps({"key": key, "words": st}))
        return st
    except Exception:
        return {}


def music_beats(meta, start):
    """the bed's beats in the reel's (output) time, or [] when the track has no clear beat (strength < 0.2).
    Measured once per track (engine/rhythm.py) and kept in library/music_beats.json."""
    try:
        import rhythm
        cache_p = LIB / "music_beats.json"
        cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}
        f = LIB / "music" / meta["file"]
        key = f"{meta['file']}|{f.stat().st_size}"
        if key not in cache:
            b = rhythm.beats(f) or {"bpm": None, "strength": 0, "beats": []}
            cache[key] = b
            cache_p.write_text(json.dumps(cache))
        b = cache[key]
        if b.get("strength", 0) < .2:
            return []
        return [round(t - start, 3) for t in b["beats"] if t >= start]
    except Exception:
        return []


def direct(project, version, style, work):
    """Fill `version` (in place) with the style's full edit. Returns a short summary for the editor."""
    if style["id"] not in DIRECTED:
        return None
    proj = dict(version, source=project["source"], edl=project["edl"], focus_x=project.get("focus_x"))
    proj["_brief"] = project.get("brief") or {}
    pl = Plan(style, proj, face_of(proj, work))
    import brand as brandmod
    pl.brand = brandmod.load(project.get("id", ""))
    pl.clips = []
    stress = voice_stress(project, work)
    for w in pl.words:
        w["stress"] = stress.get(w["i"], {}).get("stress", 0)
    out = {"clean-white": clean_white, "cinema-lexicon": cinema_lexicon, "neon-dimension": neon_dimension}[style["id"]](pl)
    tag = "style:" + style["id"]
    # the bed follows the content or Alina's vibe; its level stays the style's (dB under the voice, by each track's loudness)
    tracks = {t["id"]: t for t in json.loads((LIB / "music.json").read_text())}
    tid, mwhy = pick_music(pl, out["music"]["id"], version.get("music_vibe", ""))
    if tid != out["music"]["id"]:
        under = tracks[out["music"]["id"]]["lufs"] + 20 * __import__("math").log10(out["music"]["volume"])   # the style's bed loudness
        out["music"] = dict(out["music"], id=tid, volume=round(10 ** ((under - tracks[tid]["lufs"]) / 20), 3), start=tracks[tid].get("start", 0))
    out["music"]["why"] = mwhy
    # punch-ins land on the bed's beat when one is within 0.12 s before / 0.08 s after (rea-video's beat grid idea)
    grid = music_beats(tracks[out["music"]["id"]], float(out["music"].get("start", tracks[out["music"]["id"]].get("start", 0))))
    on_beat = 0
    if grid:
        pl.punches, on_beat = __import__("rhythm").snap(pl.punches, grid)
    # replace only what a style added before; keep everything Alina placed
    version["effects"] = [e for e in version.get("effects", []) if not str(e.get("by", "")).startswith("style:")] + pl.effects
    version["sfx"] = [s for s in version.get("sfx", []) if not str(s.get("by", "")).startswith("style:")] + pl.sfx
    version["text"] = {**version.get("text", {}), **style.get("text", {}), **out["text"]}
    version["grade"] = style.get("grade", version.get("grade"))
    version["punch_in"] = out["punch_in"]
    version["punches"] = pl.punches
    version["music"] = dict(out["music"], status="proposed", by=tag)
    version["lufs"] = out["lufs"]
    version["tail"] = out.get("tail", 0)
    # example clips (Cinema Lexicon): slots on the phrases; a clip already found for the same phrase is kept
    old_clips = {o["word_i"]: o for o in version.get("overlays", []) if str(o.get("by", "")).startswith("style:") and o.get("kind") == "clip"}
    slots = []
    for n, c in enumerate(pl.clips):
        was = old_clips.get(c["word_i"], {})
        slots.append({"id": was.get("id") or f"o{c['word_i']:03d}cl", "kind": "clip", "word_i": c["word_i"], "word_end_i": c["word_end_i"],
                      "at": c["at"], "phrase": c["phrase"], "query": was.get("query") or c["query"], "queries_more": c.get("queries_more", []), "tags": c.get("tags", []), "image": was.get("image", ""),
                      "source": was.get("source", ""), "media_start": was.get("media_start", 0), "focus": was.get("focus", .5),
                      "hold": c["hold"], "mode": "full", "status": "proposed" if was.get("image") else "needs clip", "by": tag,
                      "why": f"example clip for “{c['phrase']}” (one phrase = one literal example, Pexels, max 2 in a row)"})
    version["overlays"] = [o for o in version.get("overlays", []) if not str(o.get("by", "")).startswith("style:")] + slots
    empty = [o for o in slots if not o["image"]]
    project["requests"] = [r for r in project.get("requests", []) if not (r.get("kind") == "example-clips" and r.get("version") == version["id"]
                                                                          and r.get("status") == "waiting for Claude")]
    if empty:
        project["requests"].append({"id": "clips" + version["id"][-4:], "at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"), "kind": "example-clips",
                                    "step": "effects", "version": version["id"], "status": "waiting for Claude", "files": [],
                                    "text": f"Find {len(empty)} example clips on Pexels (the human meaning of each phrase, portrait if possible, "
                                            "no watermark) and fill the slots with engine/stock.py: " +
                                            "; ".join(f"{o['id']} “{o['phrase']}” (start: {o['query']})" for o in empty)})
    version["style_edit"] = {"style": style["id"], "effects": len(pl.effects), "sounds": len(pl.sfx), "punches": len(pl.punches),
                             "punches_on_beat": on_beat, "stressed_words": sum(1 for w in pl.words if w.get("stress", 0) >= 1),
                             "music": out["music"]["id"], "duration": round(pl.dur, 2), "clips": len(pl.clips),
                             "clips_missing": sum(1 for o in version.get("overlays", []) if o.get("status") == "needs clip"),
                             "brand": (pl.brand or {}).get("name", "")}
    return version["style_edit"]
