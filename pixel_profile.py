"""pixel-profile: animated pixel-art SVGs for a GitHub profile README.

Generates banner.svg, status.svg, divider.svg and footer.svg. Every glyph and
sprite is drawn from rectangles and animated with SMIL, so the images need no
fonts, scripts or external services and render inside GitHub's image proxy.

Usage:
    python pixel_profile.py --config profile.json --out assets
    python pixel_profile.py --title "NEO" --handle neo --stack TS,GO --out assets
"""
import argparse
import json
import os
import random
import sys
from xml.sax.saxutils import escape

OUT = "assets"

DEFAULTS = {
    "title": "THE GHOST",
    "handle": "your-username",
    "tagline": "BUILDING THINGS FOR THE WEB",
    "card_title": "STATUS.EXE",
    "player": "PLAYER 1",
    "fields": [["NAME", "THE GHOST"], ["CLASS", "CODER"], ["BASE", "EARTH"]],
    "stack": ["TS", "JS", "PY"],
    "status": "ONLINE",
    "quest": "BUILDING THINGS FOR THE WEB",
    "footer": "THANKS FOR VISITING *",
    "footer_hint": "PRESS START",
}

# ---------------------------------------------------------------- palette
INK = "#1b1035"
CARD = "#1c1433"
CARD_LINE = "#3a2b63"
CREAM = "#fff3d6"
PINK = "#ff77a8"
SAKURA = "#ffb7c5"
SAKURA_DARK = "#ff8fab"
LAVENDER = "#c3a6ff"
CYAN = "#7ae7ff"
MINT = "#8cffc1"
PEACH = "#ffb38a"
YELLOW = "#ffe27a"
MUTED = "#8b7fb8"
WINDOW = "#ffd56b"
BUILDING = "#120822"
SKY = ["#120a26", "#170d2e", "#1d1037", "#241340", "#2d174a", "#381b53",
       "#45205c", "#542564", "#662a6b", "#7a3070"]

# ---------------------------------------------------------------- 5x7 pixel font
FONT = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": ["  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "],
    " ": ["     "] * 7,
    ">": ["#    ", " #   ", "  #  ", "   # ", "  #  ", " #   ", "#    "],
    "_": ["     "] * 6 + ["#####"],
    ".": ["     "] * 5 + [" ##  ", " ##  "],
    ":": ["     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "],
    "/": ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "],
    "-": ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    "!": ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
    "?": [" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "],
    "*": ["     ", " # # ", "#####", "#####", " ### ", "  #  ", "     "],  # heart
    "&": [" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"],
    "(": ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "],
    ")": [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
    "[": [" ### ", " #   ", " #   ", " #   ", " #   ", " #   ", " ### "],
    "]": [" ### ", "   # ", "   # ", "   # ", "   # ", "   # ", " ### "],
    "<": ["    #", "   # ", "  #  ", " #   ", "  #  ", "   # ", "    #"],
    "+": ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "],
    "=": ["     ", "     ", "#####", "     ", "#####", "     ", "     "],
    ",": ["     "] * 5 + ["  #  ", " #   "],
    "'": ["  #  ", "  #  ", "     ", "     ", "     ", "     ", "     "],
    "#": [" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "],
    "@": [" ### ", "#   #", "# ###", "# # #", "# ###", "#    ", " ####"],
    "$": ["  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "],
    "%": ["##  #", "##  #", "   # ", "  #  ", " #   ", "#  ##", "#  ##"],
    "|": ["  #  "] * 7,
    "~": ["     ", "     ", " #   ", "# # #", "   # ", "     ", "     "],
    "·": ["     ", "     ", "     ", "  #  ", "     ", "     ", "     "],
}
for ch, rows in FONT.items():
    assert len(rows) == 7 and all(len(r) == 5 for r in rows), ch


def text_width(s, px, gap=1):
    return (len(s) * (5 + gap) - gap) * px


def text_path(s, x, y, px, gap=1):
    """Path data for pixel text with its top-left corner at (x, y)."""
    d = []
    cx = x
    for ch in s.upper():
        for r, row in enumerate(FONT.get(ch, FONT["?"])):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    w = (c - start) * px
                    d.append(f"M{cx + start * px} {y + r * px}h{w}v{px}h{-w}z")
                else:
                    c += 1
        cx += (5 + gap) * px
    return "".join(d)


def sprite_paths(rows, x, y, px):
    """Path data per colour key for a sprite given as strings; '.' is empty."""
    out = {}
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            key = row[c]
            if key == ".":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == key:
                c += 1
            w = (c - start) * px
            out.setdefault(key, []).append(f"M{x + start * px} {y + r * px}h{w}v{px}h{-w}z")
    return {k: "".join(v) for k, v in out.items()}


# ---------------------------------------------------------------- sprites
# O outline, W body, S shade, B blush, E eye, H eye highlight
GHOST = [
    ".....OOOOOO.....",
    "...OOWWWWWWOO...",
    "..OWWWWWWWWWWO..",
    ".OWWWWWWWWWWWWO.",
    ".OWWWWWWWWWWWWO.",
    ".OWWWHEWWWHEWWO.",
    ".OWWWEEWWWEEWWO.",
    ".OWBBWWWWWWWBBO.",
    ".OWWWWWWWWWWWWO.",
    ".OWWWWWWWWWWWSO.",
    ".OWWWWWWWWWWWSO.",
    ".OWWWWWWWWWWSSO.",
    ".OWWWWWWWWWWWSO.",
    ".OWWOOOWWOOOWSO.",
    "..OO...OO...OO..",
    "................",
]
assert all(len(r) == 16 for r in GHOST)
GHOST_COLORS = {"O": "#2a1747", "W": "#f4f1ff", "S": "#c9c1f0", "B": SAKURA_DARK}


def ghost(x, y, px, bob=6, blink_dur="4s", extra_anim=""):
    """A floating ghost that bobs in pixel steps and blinks."""
    body = [row.replace("E", "W").replace("H", "W") for row in GHOST]
    eyes_open = ["".join(ch if ch in "EH" else "." for ch in row) for row in GHOST]
    eyes_closed = ["." * 16 for _ in GHOST]
    eyes_closed[6] = ".....EE...EE...."
    parts = sprite_paths(body, 0, 0, px)
    op = sprite_paths(eyes_open, 0, 0, px)
    cl = sprite_paths(eyes_closed, 0, 0, px)
    s = [f'<g transform="translate({x} {y})">{extra_anim}<g>',
         f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-bob};0 {-2 * bob};0 {-bob}" '
         f'dur="1.6s" calcMode="discrete" repeatCount="indefinite"/>']
    for key in "OWSB":
        s.append(f'<path d="{parts[key]}" fill="{GHOST_COLORS[key]}"/>')
    s.append(f'<g><animate attributeName="opacity" values="1;0;1" keyTimes="0;0.92;0.97" dur="{blink_dur}" '
             f'calcMode="discrete" repeatCount="indefinite"/>'
             f'<path d="{op["E"]}" fill="{INK}"/><path d="{op["H"]}" fill="#ffffff"/></g>')
    s.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;0.92;0.97" dur="{blink_dur}" '
             f'calcMode="discrete" repeatCount="indefinite"/><path d="{cl["E"]}" fill="{INK}"/></g>')
    s.append("</g></g>")
    return "".join(s)


CLOUD = [
    "......######..........",
    "...############.......",
    "..################....",
    ".######################",
    "########################",
]
PETAL = [".P", "PD"]
SPARKLE = ["..#..", "..#..", "##.##", "..#..", "..#.."]
MOON = 9  # radius in cells


def moon(cx, cy, px):
    rows = []
    for dy in range(-MOON, MOON + 1):
        row = ""
        for dx in range(-MOON, MOON + 1):
            row += "M" if dx * dx + dy * dy <= MOON * MOON else "."
        rows.append(row)
    # a few craters
    for (r, c) in [(5, 6), (5, 7), (6, 6), (10, 12), (11, 12), (11, 13), (13, 5)]:
        rows[r] = rows[r][:c] + "C" + rows[r][c + 1:]
    p = sprite_paths(rows, cx - MOON * px, cy - MOON * px, px)
    return (f'<circle cx="{cx}" cy="{cy}" r="{MOON * px * 2}" fill="{YELLOW}" opacity="0.10"/>'
            f'<path d="{p["M"]}" fill="#fff1c1"/><path d="{p["C"]}" fill="#f2d98d"/>')


def stars(rng, n, w, h, top=0, avoid=()):
    """Twinkling pixel stars, kept out of the `avoid` boxes (x0, y0, x1, y1)."""
    s = []
    for _ in range(n):
        while True:
            x = rng.randrange(0, w // 4) * 4
            y = top + rng.randrange(0, h // 4) * 4
            if not any(x0 - 8 <= x <= x1 + 8 and y0 - 8 <= y <= y1 + 8 for x0, y0, x1, y1 in avoid):
                break
        size = rng.choice([4, 4, 4, 8])
        dur = round(rng.uniform(1.4, 4.0), 1)
        begin = round(rng.uniform(0, 3), 1)
        color = rng.choice([CREAM, CREAM, "#ffffff", LAVENDER, CYAN])
        s.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{color}">'
                 f'<animate attributeName="opacity" values="1;0.25;1" dur="{dur}s" begin="-{begin}s" '
                 f'calcMode="discrete" repeatCount="indefinite"/></rect>')
    return "".join(s)


def sparkle(x, y, px, color, dur, begin):
    p = sprite_paths(SPARKLE, x, y, px)["#"]
    return (f'<path d="{p}" fill="{color}"><animate attributeName="opacity" values="1;0;0;1" '
            f'keyTimes="0;0.4;0.8;1" dur="{dur}s" begin="-{begin}s" calcMode="discrete" repeatCount="indefinite"/></path>')


def petals(rng, n, w, h, px=4, drift=(-220, 420)):
    s = []
    for _ in range(n):
        x = rng.randrange(80, w + 200)
        y = rng.randrange(-60, 0)
        dur = round(rng.uniform(7, 12), 1)
        begin = round(rng.uniform(0, dur), 1)
        p = sprite_paths(PETAL, x, y, px)
        s.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;{drift[0] // 2} {drift[1] // 2};{drift[0]} {drift[1]}" '
                 f'dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
                 f'<path d="{p["P"]}" fill="{SAKURA}"/><path d="{p["D"]}" fill="{SAKURA_DARK}"/></g>')
    return "".join(s)


def cloud(x, y, px, dur, begin, travel):
    p = sprite_paths(CLOUD, 0, 0, px)["#"]
    return (f'<g transform="translate({x} {y})"><g opacity="0.55">'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{travel} 0" dur="{dur}s" '
            f'begin="-{begin}s" repeatCount="indefinite"/><path d="{p}" fill="#4a2e73"/></g></g>')


def sky(w, h, rx):
    band = h / len(SKY)
    rects = "".join(f'<rect y="{round(i * band)}" width="{w}" height="{round(band) + 1}" fill="{c}"/>'
                    for i, c in enumerate(SKY))
    return f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>', rects


def skyline(rng, w, base, px=4):
    s = []
    x = -10
    while x < w:
        bw = rng.randrange(10, 24) * px
        bh = rng.randrange(8, 20) * px
        top = base - bh
        s.append(f'<rect x="{x}" y="{top}" width="{bw}" height="{bh + 40}" fill="{BUILDING}"/>')
        for wy in range(top + 2 * px, base - px, 3 * px):
            for wx in range(x + 2 * px, x + bw - 2 * px, 3 * px):
                if rng.random() < 0.28:
                    if rng.random() < 0.25:
                        dur = round(rng.uniform(3, 8), 1)
                        s.append(f'<rect x="{wx}" y="{wy}" width="{px}" height="{px + 2}" fill="{WINDOW}">'
                                 f'<animate attributeName="opacity" values="1;0.15;1" dur="{dur}s" calcMode="discrete" '
                                 f'begin="-{rng.uniform(0, dur):.1f}s" repeatCount="indefinite"/></rect>')
                    else:
                        s.append(f'<rect x="{wx}" y="{wy}" width="{px}" height="{px + 2}" fill="{WINDOW}" opacity="0.85"/>')
        x += bw + rng.randrange(0, 3) * px
    return "".join(s)


def svg(w, h, body, label):
    label = escape(label, {'"': "&quot;"})
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{label}">{body}</svg>\n')


def fit_px(text, max_width, largest, smallest=1):
    """Largest pixel scale at which `text` fits in `max_width`."""
    for px in range(largest, smallest - 1, -1):
        if text_width(text, px) <= max_width:
            return px
    return smallest


def clean(text):
    """Uppercase, and replace characters the pixel font cannot draw with '?'."""
    return "".join(ch if ch in FONT else "?" for ch in str(text).upper())


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"{name}: {len(content) / 1024:.1f} KB")


# ---------------------------------------------------------------- banner
def banner(cfg):
    rng = random.Random(7)
    W, H = 1200, 340
    clip, bands = sky(W, H, 24)
    title = clean(cfg["title"])
    gpx = 8                             # ghost sprite: 16 cells * 8px = 128
    left, moon_edge = 60, 990           # keep text clear of the moon
    room = moon_edge - left - 16 * gpx - 44
    tpx = fit_px(title, room, 10, 4)
    sub1 = clean("> " + cfg["handle"])
    sub2 = clean(cfg["tagline"])
    spx = min(fit_px(sub1, room - 24, 3), fit_px(sub2, room, 3))
    group_w = 16 * gpx + 44 + max(text_width(title, tpx), text_width(sub1, spx) + 24, text_width(sub2, spx))
    gx = max(left, min((W - group_w) // 2, moon_edge - group_w))
    tx = gx + 16 * gpx + 44
    ty = 92
    cur_x = tx + text_width(sub1, spx) + 3 * spx
    body = [
        f"<defs>{clip}</defs>",
        '<g clip-path="url(#frame)">',
        bands,
        stars(rng, 46, W, 230, avoid=[(gx, ty - 40, tx + text_width(sub2, spx) + 40, ty + 170),
                                      (tx, ty, tx + text_width(title, tpx) + 10, ty + 80)]),
        sparkle(150, 60, 4, CREAM, 2.6, 0.3), sparkle(1010, 200, 4, CYAN, 3.2, 1.1), sparkle(560, 26, 4, LAVENDER, 2.2, 0.8),
        moon(1080, 74, 5),
        cloud(-120, 130, 8, 70, 10, 1500), cloud(-120, 40, 6, 95, 60, 1500), cloud(-120, 210, 7, 80, 35, 1500),
        petals(rng, 16, W, H),
        skyline(rng, W, H - 4),
        f'<rect y="{H - 6}" width="{W}" height="6" fill="{PINK}" opacity="0.35"/>',
        ghost(gx, ty - 26, gpx, bob=6),
        f'<path d="{text_path(title, tx + max(2, tpx * 6 // 10), ty + max(2, tpx * 6 // 10), tpx)}" fill="{PINK}"/>',
        f'<path d="{text_path(title, tx, ty, tpx)}" fill="{CREAM}"/>',
        f'<path d="{text_path(sub1, tx, ty + 104, spx)}" fill="{CYAN}"/>',
        f'<rect x="{cur_x}" y="{ty + 104}" width="{5 * spx}" height="{7 * spx}" fill="{CYAN}">'
        f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>',
        f'<path d="{text_path(sub2, tx, ty + 140, spx)}" fill="{LAVENDER}"/>',
        "</g>",
        f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="23" fill="none" stroke="{CARD_LINE}" stroke-width="3"/>',
    ]
    write("banner.svg", svg(W, H, "".join(body), cfg["title"]))


# ---------------------------------------------------------------- status card
def chip(x, y, label, color, px=2):
    tw = text_width(label, px)
    w = tw + 28
    return (f'<rect x="{x}" y="{y}" width="{w}" height="32" rx="9" fill="{color}"/>'
            f'<path d="{text_path(label, x + 14, y + 9, px)}" fill="{INK}"/>'), w


CHIP_COLORS = [CYAN, YELLOW, MINT, LAVENDER, PEACH, SAKURA]


def status_card(cfg):
    W, H = 1200, 500
    cx, cy, cw, ch = 24, 16, W - 48, H - 44
    rows_x, val_x = 400, 560
    body = [
        '<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="120%">'
        f'<feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000000" flood-opacity="0.35"/></filter></defs>',
        f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="24" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="2" filter="url(#sh)"/>',
        # title bar, figma-style
        f'<rect x="{cx + 24}" y="{cy + 22}" width="14" height="14" rx="4" fill="{PINK}"/>',
        f'<rect x="{cx + 46}" y="{cy + 22}" width="14" height="14" rx="4" fill="{YELLOW}"/>',
        f'<rect x="{cx + 68}" y="{cy + 22}" width="14" height="14" rx="4" fill="{MINT}"/>',
        f'<path d="{text_path(clean(cfg["card_title"]), (W - text_width(clean(cfg["card_title"]), 2)) // 2, cy + 22, 2)}" fill="{MUTED}"/>',
        f'<rect x="{cx}" y="{cy + 56}" width="{cw}" height="2" fill="{CARD_LINE}"/>',
        # left panel
        f'<rect x="{cx + 40}" y="{cy + 90}" width="300" height="300" rx="20" fill="#241a42" stroke="{CARD_LINE}" stroke-width="2"/>',
    ]
    rng = random.Random(3)
    body.append(stars(rng, 10, 260, 120, top=cy + 104).replace('<rect x="', f'<rect transform="translate({cx + 60} 0)" x="'))
    body.append(ghost(cx + 40 + (300 - 160) // 2, cy + 150, 10, bob=5, blink_dur="3.4s"))
    plate, pw = chip(0, 0, clean(cfg["player"])[:16], PINK)
    body.append(f'<g transform="translate({cx + 40 + (300 - pw) // 2} {cy + 340})">{plate}</g>')
    body.append(sparkle(cx + 64, cy + 112, 4, LAVENDER, 2.4, 0.2))
    body.append(sparkle(cx + 296, cy + 150, 4, CYAN, 3.0, 1.3))

    y0, step = cy + 98, 50
    right = cx + cw - 30
    fields = [(clean(k)[:8], clean(v)) for k, v in cfg["fields"][:3]]
    labels = [k for k, _ in fields] + ["STACK", "STATUS", "QUEST", "NEXT"]
    for i, lab in enumerate(labels):
        body.append(f'<path d="{text_path(lab, rows_x, y0 + i * step + 4, 2)}" fill="{MUTED}"/>')

    def value(text, row, color=CREAM, x=val_x):
        px = fit_px(text, right - x, 3, 2)
        body.append(f'<path d="{text_path(text, x, y0 + row * step + (3 - px) * 3, px)}" fill="{color}"/>')

    for i, (_, v) in enumerate(fields):
        value(v, i)
    row = len(fields)
    x = val_x
    for i, lab in enumerate(clean(s) for s in cfg["stack"]):
        c, w = chip(x, y0 + row * step - 6, lab, CHIP_COLORS[i % len(CHIP_COLORS)])
        if x + w > right:
            break
        body.append(c)
        x += w + 10
    sy = y0 + (row + 1) * step
    body.append(f'<rect x="{val_x}" y="{sy + 4}" width="12" height="12" fill="{MINT}">'
                f'<animate attributeName="opacity" values="1;0.2" dur="1.2s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    value(clean(cfg["status"]), row + 1, MINT, val_x + 26)
    value(clean(cfg["quest"]), row + 2)
    # pixel loading bar
    by = y0 + (row + 3) * step - 2
    segs, sw = 24, 16
    body.append(f'<rect x="{val_x - 4}" y="{by - 4}" width="{segs * (sw + 4) + 4}" height="30" rx="6" fill="none" stroke="{CARD_LINE}" stroke-width="2"/>')
    body.append(f'<clipPath id="bar"><rect x="{val_x}" y="{by}" height="22" width="0">'
                f'<animate attributeName="width" values="{";".join(str(i * (sw + 4)) for i in range(segs + 1))};{segs * (sw + 4)}" '
                f'dur="5s" calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>')
    seg_path = "".join(f"M{val_x + i * (sw + 4)} {by}h{sw}v22h{-sw}z" for i in range(segs))
    body.append(f'<path d="{seg_path}" fill="{PINK}" clip-path="url(#bar)"/>')
    body.append(f'<path d="{text_path("LOADING", val_x + segs * (sw + 4) + 20, by + 4, 2)}" fill="{MUTED}">'
                f'<animate attributeName="opacity" values="1;0.3" dur="0.8s" calcMode="discrete" repeatCount="indefinite"/></path>')
    summary = ", ".join(f"{k}: {v}" for k, v in cfg["fields"][:3])
    write("status.svg", svg(W, H, "".join(body), f"Player status. {summary}. Stack: {', '.join(cfg['stack'])}"))


# ---------------------------------------------------------------- divider
def divider():
    W, H = 1200, 20
    dots = "".join(f"M{x} 8h8v4h-8z" for x in range(0, W, 16))
    comet = (f"M0 8h8v4h-8zM12 8h8v4h-8zM24 6h8v8h-8zM36 4h12v12h-12z")
    body = (f'<path d="{dots}" fill="{CARD_LINE}"/>'
            f'<g><animateTransform attributeName="transform" type="translate" from="-60 0" to="{W + 60} 0" dur="5s" repeatCount="indefinite"/>'
            f'<path d="{comet}" fill="{PINK}"/><rect x="40" y="8" width="4" height="4" fill="{CREAM}"/></g>')
    write("divider.svg", svg(W, H, body, ""))


# ---------------------------------------------------------------- footer
def footer(cfg):
    rng = random.Random(11)
    W, H = 1200, 220
    clip, bands = sky(W, H, 24)
    msg = clean(cfg["footer"])
    px = fit_px(msg, W - 120, 5, 2)
    mx = (W - text_width(msg, px)) // 2
    start = clean(cfg["footer_hint"])
    sx = (W - text_width(start, fit_px(start, W - 120, 3))) // 2
    body = [
        f"<defs>{clip}</defs>",
        '<g clip-path="url(#frame)">',
        bands,
        stars(rng, 30, W, 140, avoid=[(mx, 56, mx + text_width(msg, px) + 4, 144)]),
        petals(rng, 10, W, H, drift=(-160, 300)),
        skyline(rng, W, H - 4),
        f'<path d="{text_path(msg, mx + 4, 60 + 4, px)}" fill="{PINK}"/>',
        f'<path d="{text_path(msg, mx, 60, px)}" fill="{CREAM}"/>',
        f'<path d="{text_path(start, sx, 118, fit_px(start, W - 120, 3))}" fill="{CYAN}">'
        f'<animate attributeName="opacity" values="1;0" dur="1.1s" calcMode="discrete" repeatCount="indefinite"/></path>',
        # a little ghost drifting across the rooftops
        f'<g><animateTransform attributeName="transform" type="translate" from="-80 0" to="{W + 80} 0" dur="16s" repeatCount="indefinite"/>'
        + ghost(0, 140, 3, bob=3, blink_dur="2.8s") + "</g>",
        "</g>",
        f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="23" fill="none" stroke="{CARD_LINE}" stroke-width="3"/>',
    ]
    write("footer.svg", svg(W, H, "".join(body), cfg["footer"].replace("*", "").strip()))


def load_config(argv=None):
    p = argparse.ArgumentParser(description="Animated pixel-art SVGs for a GitHub profile README.")
    p.add_argument("--config", help="JSON file with any of: " + ", ".join(DEFAULTS))
    p.add_argument("--out", default="assets", help="output directory (default: assets)")
    p.add_argument("--title", help="big banner text")
    p.add_argument("--handle", help="your GitHub username, shown as '> handle'")
    p.add_argument("--tagline", help="second banner line")
    p.add_argument("--stack", help="comma-separated stack chips, e.g. TS,GO,RUST")
    args = p.parse_args(argv)

    cfg = dict(DEFAULTS)
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            user = json.load(f)
        unknown = set(user) - set(DEFAULTS)
        if unknown:
            p.error(f"unknown config keys: {', '.join(sorted(unknown))}")
        cfg.update(user)
    for key in ("title", "handle", "tagline"):
        if getattr(args, key):
            cfg[key] = getattr(args, key)
    if args.stack:
        cfg["stack"] = [s.strip() for s in args.stack.split(",") if s.strip()]
    return cfg, args.out


def main(argv=None):
    global OUT
    cfg, OUT = load_config(argv)
    os.makedirs(OUT, exist_ok=True)
    banner(cfg)
    status_card(cfg)
    divider()
    footer(cfg)


if __name__ == "__main__":
    sys.exit(main())
