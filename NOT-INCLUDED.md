# Not included (on purpose)

This repo is the engine and the know-how. These parts of the working setup are left out, because they belong to other
people, hold personal data, or have no licence that allows sharing them:

| Left out | Why | How to get your own |
|---|---|---|
| `projects/` (raw takes, edits, renders) and every finished edit with real people | private footage; people in it have not agreed to a public upload | your own takes |
| `.secrets.json` (Pexels and GIPHY keys) | keys are personal; a public key gets abused | free keys at pexels.com/api and developers.giphy.com, pasted in the editor |
| The Clean White, Cinema Lexicon and Meme Chaos example videos, and the effect preview videos | they show colleagues and creators | render your own with `editing-beast/effects/make_effect.py` |
| Reference videos (`styles/*/references/`), their frames, transcripts and audio snippets | other creators' content | the style guides describe what was learned from them |
| Meme sound set (YouTube compilations, the Emma set, CapCut audio), Mixkit sounds | licence unknown, or the licence forbids re-sharing the files | `library/sfx.json` lists every sound by name and category; add your own files with the same names |
| Pinterest meme pictures | other people's pictures | your own Pinterest board, downloaded into `library/memes/pinterest/<Emotion>/`; `library/memes/meme_pictures.json` is the catalogue format |
| Pixabay explosion frames (`engine/hf/fx/memes/`) | stock media, not to be redistributed as files | the Meme Chaos guide says how to key your own |
| `hooks.json`, `formats.json`, six styles from a PDF course | copied from third-party documents (100+ Viral Hooks, Short-Form Formats Breakdown, neurofam PDF) | write your own lists in the same format |
| Vetto's design files (theme, art) | belong to Vetto | the editor has its own stylesheet (`ui/app.css`) |
| `research/` (downloaded repos), `openmotion/`, binaries (ffmpeg, yt-dlp) | other projects with their own licences | see each project's own repository |
