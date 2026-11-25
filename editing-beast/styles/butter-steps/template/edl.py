"""Butter Steps cut list: keep speech, remove pauses > 0.25 s as hard jump cuts (STYLE.md §3).
Writes work/edl.json = [[src_in, src_out, out_start], ...] and prints it."""
import json, sys
T = json.load(open(sys.argv[1]))
W = [(w["s"], w["e"], w["w"].strip()) for s in T["segments"] for w in s["words"]]
GAP, PRE, POST, END = 0.25, 0.06, 0.12, 39.50
segs = []
a, b = max(0, W[0][0] - PRE), W[0][1]
for s, e, _ in W[1:]:
    if s - b > GAP:
        segs.append([a, min(b + POST, s - 0.02)])
        a = s - PRE
    b = e
segs.append([a, min(b + POST, END)])
# manual fixes after review: drop the phone-flip fumble "over here" pause is speech, keep
out, t = [], 0.0
for a, b in segs:
    out.append([round(a, 3), round(b, 3), round(t, 3)]); t += b - a
json.dump(out, open(sys.argv[2], "w"))
for a, b, o in out: print(f"src {a:6.2f}-{b:6.2f}  ({b-a:4.2f}s)  out {o:6.2f}")
print("total", round(t, 2), "s,", len(out), "segments,", len(out) - 1, "cuts")
