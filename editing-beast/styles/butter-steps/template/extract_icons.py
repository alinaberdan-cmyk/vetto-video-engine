"""Cut icons/stickers out of the feedmeplzthanks screen recording (1206x2622 frames).
Background removal: pixels close to the local background colour (sampled on the crop border)
that are connected to the crop border become transparent. Black outlines stop the fill.
Usage: python -I extract_icons.py <srframes_dir> <out_dir>"""
import sys, os, json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# name: (frame time, (x0, y0, x1, y1), tolerance, mode)   mode: cut = remove bg, rect = keep box with rounded corners
ICONS = {
    # brand / chrome
    "logo_wink":          (9.0,  (60, 225, 240, 375), 38, "cut"),
    "btn_settings_gear":  (9.0,  (990, 225, 1155, 385), 38, "cut"),
    "btn_heart":          (11.3, (825, 225, 990, 385), 38, "cut"),
    "btn_home":           (11.3, (990, 225, 1160, 385), 38, "cut"),
    # mood pills + dice
    "pill_cluster_all":   (9.0,  (20, 1140, 1185, 2340), 40, "cut"),
    "dice":               (9.0,  (945, 1575, 1175, 1830), 40, "largest"),
    "pill_chinese":       (9.0,  (570, 2120, 1145, 2320), 40, "largest"),
    "pill_mexican":       (9.0,  (22, 1760, 222, 2325), 40, "largest"),
    "pill_surprise_me":   (9.0,  (218, 1822, 412, 2325), 40, "largest"),
    "search_bar":         (9.0,  (55, 2320, 1150, 2510), 40, "cut"),
    # loader illustrations ("Out scouting." / "Doing the reading.")
    "loader_toastie":     (11.3, (420, 1170, 790, 1420), 40, "cut"),
    "loader_burger":      (13.2, (420, 1150, 790, 1430), 40, "cut"),
    "loader_biryani":       (14.3, (420, 1150, 790, 1430), 40, "cut"),
    "loader_calzone":       (17.3, (420, 1150, 790, 1430), 40, "cut"),
    # swipe cards (full card stacks)
    "card_biryani":       (32.0, (40, 540, 1180, 2320), 40, "cut"),
    "card_pasta_pollo":   (36.0, (40, 490, 1190, 2380), 40, "cut"),
    # treats / receipt
    "ticket_15_off":      (42.0, (210, 1060, 1010, 1745), 40, "cut"),
    # people / roles
    "role_partner_heart": (57.0, (110, 690, 330, 905), 40, "cut"),
    # settings row icons (on the light card)
    "ic_profile":         (78.5, (110, 715, 260, 890), 34, "cut"),
    "ic_household":       (78.5, (105, 1205, 230, 1315), 34, "cut"),
    "ic_dietary":         (78.5, (105, 1385, 230, 1505), 34, "cut"),
    "ic_addresses":       (78.5, (105, 1565, 230, 1690), 34, "cut"),
    "ic_order_together":  (78.5, (105, 1745, 230, 1875), 34, "cut"),
    "ic_start_fresh":     (78.5, (105, 1925, 230, 2058), 34, "cut"),
    "ic_notifications":   (78.5, (105, 2330, 230, 2455), 34, "cut"),
    # diet chips icons (small)
    "diet_vegetarian":    (66.0, (165, 688, 252, 772), 34, "cut"),
    "diet_vegan":         (66.0, (775, 688, 852, 772), 34, "cut"),
    "diet_no_shellfish":  (66.0, (165, 862, 244, 942), 34, "cut"),
    "diet_no_fish":       (66.0, (765, 868, 842, 936), 34, "cut"),
    "diet_no_beef":       (66.0, (205, 1042, 282, 1118), 34, "cut"),
    "diet_no_poultry":    (66.0, (730, 1036, 800, 1112), 34, "cut"),
    "diet_no_pork":       (66.0, (205, 1207, 287, 1292), 34, "cut"),
    "diet_no_spicy":      (66.0, (750, 1207, 828, 1292), 34, "cut"),
}

def cut(img, tol, largest=False):
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    dist = np.abs(a - bg).max(-1)
    near = dist < tol
    lab, n = ndimage.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgmask = np.isin(lab, list(edge))
    # fill tiny holes inside the subject (doodle specks next to edges) and soften the edge
    fg = ndimage.binary_opening(~bgmask, iterations=1)
    fg = ndimage.binary_fill_holes(fg)
    lab2, n2 = ndimage.label(fg)
    if n2 > 1 and largest:  # keep only the main object
        sizes = ndimage.sum(fg, lab2, range(1, n2 + 1)); fg = lab2 == (int(np.argmax(sizes)) + 1)
    elif n2 > 1:  # drop specks smaller than 0.5% of the crop
        sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s > 0.005 * h * w]
        fg = np.isin(lab2, keep)
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    out = img.convert("RGBA"); out.putalpha(alpha)
    bb = out.getbbox()
    return out.crop(bb) if bb else out

manifest = {}
frames = {}
for name, (t, box, tol, mode) in ICONS.items():
    if t not in frames:
        frames[t] = Image.open(os.path.join(SRC, f"f_{t}.png")).convert("RGB")
    crop = frames[t].crop(box)
    res = cut(crop, tol, largest=(mode == "largest"))
    p = os.path.join(OUT, f"{name}.png"); res.save(p)
    manifest[name] = {"source_time_s": t, "box": box, "size": res.size}
    print(f"{name:22s} {res.size}")
json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
