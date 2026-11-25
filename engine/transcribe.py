"""Word-level transcription with MLX Whisper on the Mac GPU.

Lessons from earlier transcripts on this Mac (see memory notes):
- auto language detection labels Moldovan-accented Romanian as Russian and translates;
  so we decode as each candidate language and keep the one with the best avg logprob.
- forcing `ro` on English speech makes Whisper translate, so English is always a candidate.
- temperature fallback avoids greedy loops.
"""
import wave
from pathlib import Path

import numpy as np

HALLUCINATIONS = ("mulțumim pentru vizionare", "multumim pentru vizionare", "thanks for watching",
                  "thank you for watching", "abonați-vă", "subscribe to", "subtitrarea", "amara.org")

MODEL = "mlx-community/whisper-large-v3-mlx"   # already in ~/.cache/huggingface


def _load_wav(path):
    with wave.open(str(path), "rb") as w:
        frames = w.readframes(w.getnframes())
    return np.frombuffer(frames, np.int16).astype(np.float32) / 32768.0


def _score(result):
    segs = result.get("segments", [])
    if not segs:
        return -99.0
    lp = [s.get("avg_logprob", -5) for s in segs]
    texts = [s.get("text", "").strip() for s in segs]
    repeats = len(texts) - len(set(texts))
    return float(np.mean(lp)) - 0.3 * repeats


def _decode(audio, lang):
    import mlx_whisper
    return mlx_whisper.transcribe(
        audio, path_or_hf_repo=MODEL, language=lang, word_timestamps=True,
        temperature=(0.0, 0.2, 0.4, 0.6), condition_on_previous_text=False,
    )


def detect_language(audio):
    """Whisper's own guess on the first 30 s. Note: forcing a wrong language makes Whisper
    translate with a *good* logprob, so logprob alone cannot pick the language."""
    import mlx_whisper
    r = mlx_whisper.transcribe(audio[: 16000 * 30], path_or_hf_repo=MODEL, language=None,
                               temperature=0.0, condition_on_previous_text=False)
    return r.get("language") or "en"


def transcribe(wav_path, language="auto"):
    """language: 'auto' or a code ('en', 'ro', 'ru', 'nl', ...)."""
    audio = _load_wav(wav_path)
    if language and language != "auto":
        best_lang, best = language, _decode(audio, language)
    else:
        guess = detect_language(audio)
        if guess in ("ru", "ro"):
            # Moldovan-accented Romanian is often detected as Russian: keep ru only if clearly better.
            ro, ru = _decode(audio, "ro"), _decode(audio, "ru")
            best_lang, best = ("ru", ru) if _score(ru) > _score(ro) + 0.5 else ("ro", ro)
        else:
            best_lang, best = guess, _decode(audio, guess)
    best_score = _score(best)
    words = []
    for seg_i, seg in enumerate(best.get("segments", [])):
        # Whisper invents outro lines on silence ("mulțumim pentru vizionare", "thanks for watching")
        if seg.get("no_speech_prob", 0) > 0.6 and seg.get("avg_logprob", 0) < -0.5:
            continue
        low = seg.get("text", "").lower()
        if any(h in low for h in HALLUCINATIONS):
            continue
        for w in seg.get("words", []):
            t = w["word"].strip()
            if not t:
                continue
            words.append({
                "i": len(words), "text": t, "start": round(float(w["start"]), 3),
                "end": round(float(w["end"]), 3), "p": round(float(w.get("probability", 1)), 3),
                "seg": seg_i,
            })
    return {"language": best_lang, "score": round(best_score, 3), "words": words,
            "text": " ".join(w["text"] for w in words)}


if __name__ == "__main__":
    import json, sys
    print(json.dumps(transcribe(sys.argv[1], *(sys.argv[2:3] or ['auto'])), ensure_ascii=False, indent=1)[:3000])
