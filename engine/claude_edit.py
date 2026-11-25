"""Edit now (Alina, 18 Nov 2026): one click in the editor makes the whole edit the way Claude does it in a chat in the
Editing Beast folder: the style's STYLE.md adapted to this video's content (captions, text effects, transitions,
B-roll / stock, sound effects, music, set-pieces), rendered to a finished reel.

The engine runs Claude Code headless (`claude -p`, the copy bundled with the Claude app, or `claude` on PATH) with the
Editing Beast folder as its working directory and this project's folder added. Claude cannot ask questions here, so
it makes the calls the style guide implies and lists them in NOTES.md. What it may fetch without asking (Alina's
answer, 18 Nov 2026): Apple emoji icons, transition / sound / text-effect assets, free stock clips and photos (no
watermark), CC music that allows posting. Never: paid AI generation, uploading her footage, signing in, posting.
The finished reel is copied into the project's renders and listed like any render ("Claude edit · <style>").
"""
import glob
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
def _beast():
    """the Editing Beast folder, wherever Alina keeps it (it moved to the Desktop on 18 Nov 2026)"""
    import os
    for c in [os.environ.get("VETTO_BEAST"), Path.home() / "Desktop" / "Editing Beast", Path.home() / "Editing Beast"]:
        if c and (Path(c) / "styles" / "INDEX.md").exists():
            return Path(c)
    try:
        out = subprocess.run(["mdfind", "-name", "Editing Beast"], capture_output=True, text=True, timeout=10).stdout.split("\n")
        for c in out:
            if c and (Path(c) / "styles" / "INDEX.md").exists():
                return Path(c)
    except Exception:
        pass
    return Path.home() / "Desktop" / "Editing Beast"


class _Beast:   # resolved on use, so a moved folder is found again without restarting the engine
    def __truediv__(self, other):
        return _beast() / other

    def __str__(self):
        return str(_beast())

    def __fspath__(self):
        return str(_beast())


BEAST = _Beast()
TOOLS = "Bash Read Write Edit Glob Grep WebFetch WebSearch Skill TodoWrite"


def binary():
    if os.environ.get("VETTO_CLAUDE"):
        return os.environ["VETTO_CLAUDE"]
    found = sorted(glob.glob(str(Path.home() / "Library/Application Support/Claude/claude-code/*/*/claude.app/Contents/MacOS/claude")),
                   key=lambda p: [int(x) if x.isdigit() else x for x in Path(p).parts[-6].split(".")])
    if found:
        return found[-1]
    return shutil.which("claude")


_STATUS = {"t": 0, "v": None}


def status():
    """{"ready": bool, "reason": str}: is the background Claude installed and signed in (cached 30 s)"""
    if time.time() - _STATUS["t"] < 30 and _STATUS["v"]:
        return _STATUS["v"]
    b = binary()
    if not b:
        v = {"ready": False, "reason": "Claude Code is not installed on this Mac."}
    else:
        try:
            out = subprocess.run([b, "auth", "status"], capture_output=True, text=True, timeout=20).stdout
            ok = json.loads(out).get("loggedIn")
        except Exception:
            ok = False
        v = {"ready": bool(ok), "binary": b,
             "reason": "" if ok else "The background Claude is not signed in yet. Open Terminal and run: \"" + b + "\" auth login"}
    _STATUS.update(t=time.time(), v=v)
    return v


# Alina, 24 Nov 2026: "when I say this (a photo of an apple, a chocolate bar and a car), all the versions should have a png
# pop up picture of the object I am mentioning" + "this rule applies only for the versions with no stock/video images".
# Styles that show things with their own stock photos / video clips (Clean White B-roll, Cinema Lexicon literal clips,
# Neon Dimension footage worlds) keep doing that; the PNG cut-out pop-ups are for the styles without stock pictures.
STOCK_STYLES = {"clean-white", "cinema-lexicon", "neon-dimension"}


def objects_rule(style):
    full = ("  - NEVER A BARE EDIT (Alina, 24 Nov 2026: \"there's no music, effects, transitions, photos\"; \"you didn't use any\n"
            "    effects like in the example video\"): every signature effect, transition, sound and the music bed of the example\n"
            "    is in, on this video's moments. Check the rendered contact sheet and the audio against the example before RESULT.json.\n")
    if style == "meme-chaos":
        return full + ("  - OBJECT MEMES (Alina, 24 Nov 2026): every concrete object she names gets a FUNNY PICTURE of that object, never\n"
                       "    a text meme (an apple with a face, a cat stuck in a chocolate bar, a banana car), in the meme sticker look; sources in order and details in\n"
                       "    STYLE.md §0c. List the objects and the source of each picture in NOTES.md.\n"
                       "  - THE ENGINE'S MEME PICKS (25 Nov 2026): the overlays with kind \"meme\" in project.json (by \"memes\" = Alina's own\n"
                       "    picks, keep them; by \"memes-auto\" = the engine's picks from GIPHY and her Pinterest library) are the memes and\n"
                       "    GIFs for this video, with their files in the project's images/ folder. Use them on their times: a GIF plays as an\n"
                       "    animated sticker WITHOUT a white frame, kept clear of her face. Swap an engine pick only when it fails the §0b\n"
                       "    relevance test, and say which and why in NOTES.md.")
    return full + _objects_rule(style)


def _objects_rule(style):
    if style in STOCK_STYLES:
        return (f"  - OBJECTS SHE NAMES ({style} shows things with stock photos / video clips): every concrete object she names\n"
                "    (\"a photo of an apple, a chocolate bar and a car\" = 3 objects) is shown with THIS style's own stock picture or\n"
                "    clip of exactly that object, on its word. NO PNG cut-out pop-ups in this style (Alina, 24 Nov 2026: the cut-out\n"
                "    rule is only for the styles without stock pictures). List the objects in NOTES.md with their word times.")
    return f"""  - OBJECT POP-UPS, MANDATORY IN THIS STYLE (Alina, 24 Nov 2026: "when I say this, all the versions should have a png
    pop up picture of the object I am mentioning"; it applies to the styles with no stock photos / video clips, which this
    one is): every concrete object she names ("a photo of an apple, a chocolate bar and a car" = 3 objects) gets a PNG
    CUT-OUT of exactly that object popping up on its word's onset. Get a clean photo of the object (her images/attachments
    first, else Pexels), cut it out with `"{ROOT}/bin/hyperframes" remove-background in.jpg -o object.png` (check the PNG:
    only the object, clean edges), place it beside her, never over the face, about 30–40% of the frame width, held until
    the next object or ~1.2 s, popping in and out the way THIS style animates things (its own ease, shadow/outline, sound on
    the same frame). One picture per object, each a different image; list the objects in NOTES.md with their word times.
    These cut-outs are the only stock pictures this style gets; never skipped."""


def prompt(p, v, style, pdir, work):
    st_dir = BEAST / "styles" / style
    words = [w for w in p["edl"]["words"]]
    if (st_dir / "STYLE.md").exists():
        ex = sorted((st_dir / "examples").glob("*.mp4")) if (st_dir / "examples").exists() else []
        guide = (f"STYLE: read styles/INDEX.md (shared conventions) and {st_dir}/STYLE.md fully (also BREAKDOWN.md if there is one). "
                 "THE GOAL (Alina, 24 Nov 2026): what stays EXACTLY THE SAME as her approved example is the style itself: the editing "
                 "style (pace, cut rhythm, framing, punch-in rules), the FONTS, the COLOURS, the TRANSITION EFFECTS and the TEXT "
                 "TEMPLATES (caption system, title / statement / name / CTA layouts and their animations), taken from the template and the "
                 "example's own code, not re-invented. What changes for every video is the CONTENT: which words, which moments, B-roll, "
                 "sound effects and music, chosen for what happens in this video (see ANALYSE below).\n"
                 "NEVER ADD ELEMENTS FROM OTHER STYLES: use only this style's fonts, colours, transitions, text templates and set-pieces. "
                 "No silver card unless this is Clean White, no neon key words unless Neon Dimension, no ★ glitch names unless Star Glitch, "
                 "no meme pops unless Meme Chaos, no step headers unless Butter Steps, and so on; nothing from the engine's other effect "
                 "templates either unless this style's guide uses it. If the content seems to want something the style does not have, "
                 "solve it with this style's own tools and note it in NOTES.md.\n"
                 f"- Approved example video(s): {', '.join(str(x) for x in ex) or 'see STYLE.md'}. Make a contact sheet of the example "
                 "first and keep it next to yours.\n"
                 f"- If {st_dir}/template/ exists, BUILD FROM IT (read its README and build.py and use them): it is the approved build.\n"
                 "- Open the example's project folder in projects/ (named in STYLE.md) and reuse its compositions, timings and assets.\n"
                 "- Before you finish, compare your rendered contact sheet with the example's at matching beats (fonts, sizes, colours, "
                 "placement, the signature moves) and fix every difference you can; list any you could not fix in NOTES.md.")
    else:   # an engine-only style (neurofam PDF / drafts): its library entry is the guide
        entry = next((x for x in json.loads((ROOT / "library" / "styles.json").read_text()) if x["id"] == style), {})
        guide = ("STYLE: this style lives only in the Vetto Video Engine. Its definition (fonts, colours, captions, pacing, effects "
                 "that fit) is below; build it with the same care as an Editing Beast style, and read styles/INDEX.md for the "
                 "shared conventions.\n" + json.dumps(entry, ensure_ascii=False, indent=1)[:6000])
    return f"""You are editing a video for Alina, exactly as you would if she pasted it into a Claude chat in this Editing Beast
folder and said "edit this in the {style} style". She clicked "Edit now" in her Vetto Video Engine; nobody is watching
this run and nobody can answer questions, so do not ask: make the calls the style guide implies and list every choice
(and anything you could not do) in {work}/NOTES.md.

{guide}

ANALYSE THIS VIDEO FIRST (Alina, 24 Nov 2026: "you don't copy and paste the same effects, music and sound effects, you adapt
everything so that it fits the context and situation of what is happening in the video"). Before building anything:
- Watch it: contact sheets at 2–4 fps of the footage, plus the transcript. Write an "## Analysis" section at the top of
  NOTES.md: who is on screen and how many people, the setting, what they DO (actions, gestures, objects they hold or show,
  camera moves), what is SAID (topic, the key claims, names, numbers, questions, jokes), the mood and energy beat by beat,
  where the turning points and the punchline are.
- Then derive every choice from that analysis and say in NOTES.md which moment or line each one answers:
  - which words become statements / key words / set-pieces, and which signature move fits which moment (an intro gets the
    name treatment, a number gets the counter, a product gets its UI, a reaction gets its beat…); skip a move the content
    has no moment for rather than forcing it;
{objects_rule(style)}
  - FONTS AND COLOURS: read the template's / example's CSS and use exactly those font files, sizes, weights and colour hex
    values (Butter Steps: its butter yellow, its header and caption faces, its white rounded UI cards in the top third
    that glass in on the spoken word, as in its template). Check the rendered contact sheet against the example for this.
  - B-roll, stock, icons and emoji: chosen for what is said at that exact moment. SUPPORTING PICTURES (Alina, 24 Nov 2026):
    when a word or phrase names something you can show (a food, a phone/app, delivery, friends, a place, an object, an
    action), add a supporting Pexels photo as a pop-up or an embedded clip on that word, in THIS style's own way of showing
    pictures (Clean White: sharp card over a blurred copy; Cinema Lexicon: full-frame literal clip; Neon Dimension: in a
    neon frame / 3D phone; Meme Chaos: tilted sticker card; Butter Steps: white UI card in the top third; Star Glitch: PiP
    card). Her own photos/attachments come first; only clear, literal matches; never two in a row of the same thing;
  - SOUND EFFECTS: picked for the actions and moments in THIS video (a swipe, a tap, a reveal, a laugh, a fail, a name…),
    from the style's sound map as the starting palette, not as fixed positions copied from the example;
  - MUSIC: chosen for THIS video's mood, pace and topic (and her music vibe if she gave one). Treat the track named in the
    style or the example as an example of the treatment (level, where it plays, how it ends), not a fixed choice: pick from
    `library/music.json` in the Vetto engine (vibe tags, measured loudness) or fetch a fitting CC track. Explain the pick.
- Do NOT reuse the example's or other projects' assets (their photos, clips, screen recordings, music windows, logos,
  texts) unless they belong to this video or she supplied them for it (this project's images/ and attachments/). The
  template's CODE, fonts and generic effect files are fine to reuse.

FOOTAGE: {p['source']['file']} ({p['source']['width']}x{p['source']['height']}, {p['source']['duration']:.1f} s).
TRANSCRIPT (word timestamps, source time): {pdir}/project.json → "edl"."words" ({len(words)} words). Words with "cut": true
are cut by Alina: leave them out (her cut is final). Long pauses are already marked in "edl"."pauses".
HER SETTINGS for this version ("versions" with id "{v['id']}"): hook text "{(v.get('hook') or {}).get('text') or ''}",
brief "{(p.get('brief') or {}).get('prompt') or ''}", music vibe "{v.get('music_vibe') or ''}". Effects, images and sounds she
placed herself (status "kept") must stay in, at their words. Her meme picture library sorted by emotion is in
~/Desktop/Pinterest FeedMe - Emotii/ (use it where this style's guide says so). Photos she added are in {pdir}/images/, files she attached in
the chat bar are in {pdir}/attachments/ (use them first: her own material before stock).

YOU MAY download without asking: Apple emoji icon images for specific moments, transition / sound effect / visual text
effect assets, stock clips and photos from PEXELS ONLY (Alina, 24 Nov 2026; her starting search is
https://www.pexels.com/search/food%20delivery/ — free licence, never watermarked): search with
`"{ROOT}/.venv/bin/python" "{ROOT}/engine/stock.py" search videos|photos "<query>"` (uses her Pexels key) or a web search for
pexels.com links, then download videos from https://www.pexels.com/download/video/<id>/ and photos from the
images.pexels.com URL; credit each in NOTES.md,
and CC music whose licence allows posting (put the credit line in NOTES.md). You may NOT: use paid AI generation (Weave,
Kling, …), upload her footage anywhere, sign in to anything, post anything, or touch other projects or the engine's code.

WORK in {work} (a new HyperFrames project; copy what you need from the style's template/example). Render with HyperFrames
(phone footage: render with --sdr), master to the style's loudness, then check the RENDERED mp4 with a contact sheet and
fix what looks wrong. Final name: {style}_<topic>_<people>_{time.strftime('%Y-%m-%d')}.mp4 inside {work}.

WHEN DONE write {work}/RESULT.json: {{"final": "<absolute path to the final mp4>", "summary": "<3–6 plain sentences for
Alina: what you made and the main choices>", "credits": ["<music / stock credit lines>"]}}. If you cannot finish, still
write RESULT.json with "final": null and the reason in "summary".
"""


def run(pid, vid, style, pdir, project, job):
    """the Edit now job: runs Claude, keeps the job's `progress` up to date, returns the result"""
    st = status()
    if not st["ready"]:
        raise RuntimeError(st["reason"])
    v = next(x for x in project["versions"] if x["id"] == vid)
    work = BEAST / "projects" / f"engine-{pid}-{style}-{time.strftime('%H%M%S')}"
    work.mkdir(parents=True, exist_ok=True)
    (work / "PROMPT.md").write_text(prompt(project, v, style, pdir, work))
    cmd = [st["binary"], "-p", (work / "PROMPT.md").read_text(), "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits", "--allowedTools", TOOLS, "--add-dir", str(pdir), "--add-dir", str(ROOT / "library")]
    memes = Path.home() / "Desktop" / "Pinterest FeedMe - Emotii"     # her meme pictures by emotion (Meme Chaos §0b, 24 Nov 2026)
    if memes.exists():
        cmd += ["--add-dir", str(memes)]
    log = open(work / "claude.log", "w")
    proc = subprocess.Popen(cmd, cwd=str(_beast()), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, stdin=subprocess.DEVNULL)
    job["pid_proc"] = proc.pid
    job["work"] = str(work)
    t0 = time.time()
    for line in proc.stdout:
        log.write(line)
        log.flush()
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") == "assistant":
            for c in ev.get("message", {}).get("content", []):
                if c.get("type") == "text" and c.get("text", "").strip():
                    job["progress"] = c["text"].strip().splitlines()[0][:160]
                elif c.get("type") == "tool_use":
                    inp = c.get("input", {})
                    job["progress_tool"] = (c.get("name", "") + ": " + str(inp.get("description") or inp.get("command") or inp.get("file_path") or ""))[:160]
        if time.time() - t0 > 90 * 60:
            proc.kill()
            raise RuntimeError("Claude took longer than 90 minutes and was stopped. Its work so far: " + str(work))
    proc.wait()
    log.close()
    res_f = work / "RESULT.json"
    if not res_f.exists():
        raise RuntimeError("Claude stopped without finishing (no RESULT.json). Its log: " + str(work / "claude.log"))
    res = json.loads(res_f.read_text())
    if not res.get("final") or not Path(res["final"]).exists():
        raise RuntimeError("Claude could not finish: " + (res.get("summary") or "no reason given"))
    return {"final": res["final"], "summary": res.get("summary", ""), "credits": res.get("credits", []), "work": str(work)}
