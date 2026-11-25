# Star Glitch template (from the approved SG01 edit)

`build.py` is SG01's script, which already worked end to end. Copy it into a new project and change the timings and words for the new take.

1. New folder `projects/<id>/` with `src/take.MOV` (presenter) and `src/screen.MP4` (optional screen recording). Copy `build.py` and `hf/` (config + fonts) there. Put the two SFX WAVs from here into `work/`.
2. Transcribe with word timestamps (MLX Whisper large-v3-turbo) and build the cut list `work/edl_bs01.json` = `[[src_in, src_out, out_start], …]`: jump cuts that remove pauses over ~0.25 s, keeping 60 ms before and 120 ms after each phrase. The Butter Steps `edl.py` does the same job.
3. In `build.py`, set:
   - `SPLIT`: the source time where the montage goes in (right after the hook's last word).
   - `DISH_T`: the montage frames (product/screen-recording moments or extra presenter clips), with `CUT_F` frames each (7 = a half-beat at ~129 BPM). `FLASH_AT` is the cut that gets the 1-frame glitch flash.
   - `MUSIC` / `MUSIC_AT`: a Vetto library track and an on-beat start (`rhythm.py beats`, choose a loud window).
   - `PIP` pieces: screen-recording in-points, each aligned to the spoken word (`_align`-style maths with `O()`). Also set the `PAY` card.
   - `build()`: the caption plan (tiers XL/L/M/S, slots, stacks, (asides), >typed<, ★ name, counter, script logo, font-glitch burst, sign-off). Rewrite the words the way a friend texts.
4. `python3 -I build.py prep`, then `python3 -I build.py html`. In `hf/`, run `npx --yes hyperframes@0.9.7 check`, then `snapshot --at …`, then `render --sdr -o ../out/<id>_v1.mp4`.
5. Review the **rendered** file: 1 fps contact sheet, a 30 fps strip at every ★ swap, typed word and counter (one state per frame, no blanks), and loudness (target −15 LUFS, peaks ≤ −1.5 dBTP; the montage music sits ~5 dB under the voice).

Notes:
- ffmpeg/ffprobe: use the binaries *inside* the openmotion cache folders (`…/ffmpeg-<sha>/ffmpeg`). HyperFrames and mlx_whisper need them on PATH: link the files into a fresh scratch folder, never `ln -sf` onto those cache folders.
- Every flip-book clip goes through `fr()` (whole frames, start 0.5 ms early, end 1 ms early). v1 doubled the ★ name without it.
- Cream type disappears on cream/white UI: put montage text over the darkest band (food photos here).
