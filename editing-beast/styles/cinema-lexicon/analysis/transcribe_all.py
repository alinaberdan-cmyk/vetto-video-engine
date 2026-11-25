import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("medium",device="cpu",compute_type="int8")
for i in (1,3,4,5,6):
    segs,info=m.transcribe(f"ref{i}_16k.wav",word_timestamps=True,language="en",beam_size=5,condition_on_previous_text=False)
    words=[{"w":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2),"p":round(w.probability,2)} for s in segs for w in s.words]
    json.dump(words,open(f"ref{i}_words.json","w"),indent=0)
    print(i,len(words),flush=True)
