# Butter Steps template (from the approved BS01 edit)

1. New project folder `projects/<id>/` with `raw/take.*` (presenter) and `raw/screen.mp4` (optional screen recording).
2. Transcribe with word timestamps → `analysis/transcript.json`. Find pauses (`silencedetect=n=-34dB:d=0.22`) and write `work/edl.json` (see `edl.py`; BS01 used the detected pauses, keeping 70 ms after / 60 ms before each).
3. Copy `build.py`, edit `CARDS` (screen-recording in/out, crop box, spoken start/end), `HEADERS`, `KEY` words, hook text, pill text and stickers.
4. `python -I build.py prep` then `python -I build.py html`, `npx hyperframes@0.9.7 check`, snapshots, `render --sdr`, 1 fps contact sheet of the MP4.
5. Icons from a screen recording: extract frames to `work/srframes/f_<t>.png`, set boxes in `extract_icons.py`, run it.

ffmpeg/ffprobe must be on PATH for HyperFrames (openmotion cache binaries).
