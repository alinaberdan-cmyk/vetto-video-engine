# Notifications over my head  (`notification-stack`)

**Group:** Word & notifications · **Status:** from source · **Source:** neurofam PDF p.7

**Use it when:** 'my phone blew up', orders, messages, reactions

**What it does:** Make a 'notification stack' effect in HyperFrames over [video] from second [start]: 1080x1920, 3 s. iPhone-like notifications drop from the top: dark frosted glass, radius 34, app icon on the left, app name and 'now' on top, bold title and one line below. Four notifications at 0.05, 0.4, 0.75 and 1.1 s with texts [app, title, line for each]. Each new one lands on top and springs the older ones down; older ones shrink and darken slightly. The stack sits above the head, never on the face. Draw the icons yourself, no real company logos.

**Layer:** over video · **Needs:** 4 notification texts · **Captions during it:** stay

## Fields (`params`)
- `n1_app`: Notification 1 app
- `n1_title`: Notification 1 title
- `n1_line`: Notification 1 line
- `n2_app`: Notification 2 app
- `n2_title`: Notification 2 title
- `n2_line`: Notification 2 line
- `n3_app`: Notification 3 app
- `n3_title`: Notification 3 title
- `n3_line`: Notification 3 line
- `n4_app`: Notification 4 app
- `n4_title`: Notification 4 title
- `n4_line`: Notification 4 line

## Files
- `template.html`: the HyperFrames composition, 1080x1920, 3 s. Same file the Vetto Video Engine renders on export.
- `example.mp4`: 3 s test render on a sample take.
- Shared files in `../_shared/` (GSAP 3.14.2, motion curves, text-hook helpers, fonts).

## Use in a project
```bash
python3 ../make_effect.py notification-stack --piece piece.mp4 --text "your words" --out ./fx_notification-stack
```
Then render inside the folder it made with HyperFrames (see `../INDEX.md`). Extra inputs it needs: none.
