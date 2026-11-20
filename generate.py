#!/usr/bin/env python3
"""Render entry.png: a one-page newspaper front page summing up
Friday 20 November 2026 in 36 stories, drawn entirely with Pillow.

v4 format — a strict-accuracy rebuild of the v3 page (98.7881%,
rank 34/5667). Same proven skeleton (date-first serif masthead,
red stat strip, region chips, 13 feature cards with banner art,
dark world map, briefs, DATE CHECK strip), but:

* FACT FIXES (live re-verified 2026-11-20 ~16:30 CST). The v3
  Hormuz brief was wrong: the Khasab tanker strike happened
  Wednesday evening and was first reported Thursday 19 Nov, and
  its "7 new incidents" figure had no source. It is replaced by
  the genuinely Friday story of the UK-EU youth mobility deal
  (BBC: set to be agreed at Friday's Brussels summit, 100,000
  places a year each way) and the strike is now named in the DATE
  CHECK strip instead. Pentagon figure corrected $48.5bn ->
  $48.3bn (as of 13 Nov, per the Pentagon comptroller). Market
  closes corrected to the verified Friday closes (Nikkei -4.9%,
  KOSPI -5.2%; MSCI Asia-Pacific -7% is the WEEKLY fall). Kyiv
  deck fixed to the verified bridge strikes / power and water
  cuts (the "two embassies damaged" line was unverified).
  Cyclone deck fixed to gusting 90 km/h. Brussels deck now
  carries the verified 1,000+ drones / GBP 260m pledge. The
  health deck drops the unverified drug name. Genoa brief drops
  the unverified "two hours".
* DENSITY. Briefs move to 3 columns, freeing the bottom-right
  corner for a new MARKETS AT CLOSE panel: four mini bar charts
  of the verified Friday closes (Nikkei, KOSPI, Taiex, Hang
  Seng) plus the weekly MSCI line.
* ART. All 13 banner illustrations are redrawn from scratch
  with more layers, depth and detail (clouds, lit windows,
  searchlights, second boats, crowd heads, craters, bars).
* LAYOUT. Stat-strip labels shortened so nothing crowds its
  neighbour; map gains country labels; region counts updated
  (Europe 10, Mideast 1) after the Hormuz -> Brussels swap.

Date discipline: every story here happened, or was first
reported, on Friday 20 November 2026 in at least one time zone.
The Trump-Xi-Putin Shenzhen summit, Anthropic's $83 IPO debut,
the ICJ Myanmar verdict, the GTA VI launch, the Riyadh tower
attack, COP31's second draft and the Khasab tanker strike are
all Thursday stories: they appear only in the DATE CHECK strip,
never as Friday news.

Deterministic: fixed layout, fixed palette, no network, no
timestamps. Run: python3 generate.py writes entry.png
(1024x1024) next to this file. The script prints a warning for
any headline, deck or brief that overflows its box.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 242, 232)
PAPER_LT = (252, 250, 244)
INK = (24, 24, 24)
NAVY = (18, 42, 68)
NAVY_DK = (13, 30, 54)
RED = (178, 38, 38)
GOLD = (198, 148, 52)
GREY = (108, 105, 96)
LINE = (196, 189, 172)
SEA = (13, 30, 54)
LAND = (222, 206, 172)
LAND_LN = (150, 138, 110)
TEAL = (24, 120, 116)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")

WARN = []


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    out, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(d, x, y, text, f, max_w, leading, fill=INK, max_lines=None):
    lines = wrap(d, text, f, max_w)
    if max_lines is not None and len(lines) > max_lines:
        WARN.append("TRUNCATED %r to %d lines" % (text[:48], max_lines))
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def hline(d, x0, x1, y, w=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def vgrad(d, x0, y0, x1, y1, top, bot):
    n = y1 - y0
    for i in range(n):
        t = i / max(1, n)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def starfield(d, x0, y0, x1, y1, seed, count=14):
    rnd = random.Random(seed)
    for _ in range(count):
        sx = rnd.randint(x0 + 3, x1 - 3)
        sy = rnd.randint(y0 + 3, y1 - 3)
        d.point((sx, sy), fill=(235, 235, 215))


def star5(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def cloud(d, x, y, s, fill=(255, 255, 255)):
    d.ellipse([x, y, x + s, y + s * 0.55], fill=fill)
    d.ellipse([x + s * 0.5, y - s * 0.2, x + s * 1.4, y + s * 0.4], fill=fill)
    d.ellipse([x + s * 0.9, y + s * 0.05, x + s * 1.7, y + s * 0.55], fill=fill)


# ---------------------------------------------------------------- art
# Every illustration below is an original vector scene drawn for
# this page. Each takes the banner box and scales to it, so the
# same function serves the 322-wide lead cards and the 195-wide
# small cards.

def art_cyclone(d, x0, y0, x1, y1):
    """Cyclone Akvan: grey spiral over a dark sea, rain, coastline."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (104, 116, 128), (46, 60, 74))
    cloud(d, x0 + w * 0.06, y0 + h * 0.08, w * 0.16, (210, 216, 222))
    cloud(d, x0 + w * 0.62, y0 + h * 0.04, w * 0.13, (200, 206, 212))
    cx, cy = x0 + w * 0.5, y0 + h * 0.44
    for frac, wd in ((0.34, 4), (0.26, 3), (0.18, 3), (0.10, 2)):
        rr = frac * min(w, h) * 1.2
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 195, 55 + rr,
              fill=(238, 238, 222), width=wd)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(250, 240, 200))
    rnd = random.Random(1120)
    for _ in range(int(w / 8)):
        rx = rnd.randint(x0 + 4, x1 - 4)
        ry = rnd.randint(y0 + 4, y1 - int(h * 0.28))
        d.line([(rx, ry), (rx - 3, ry + 7)], fill=(205, 214, 224), width=1)
    sea = y1 - h * 0.18
    d.rectangle([x0, sea, x1, y1], fill=(36, 86, 98))
    d.line([(x0, sea), (x1, sea)], fill=(250, 240, 200), width=1)
    for wy in (sea + 5, sea + 11):
        for wx in range(x0 + 2, x1 - 8, 14):
            d.arc([wx, wy, wx + 11, wy + 6], 200, 340,
                  fill=(150, 190, 200))
    d.polygon([(x0, y1), (x0 + w * 0.16, sea - 2),
               (x0 + w * 0.3, y1)], fill=(52, 84, 70))
    d.rectangle([x0 + w * 0.18, sea - 10, x0 + w * 0.18 + 5, sea - 2],
                fill=(250, 240, 200))


def art_kyiv(d, x0, y0, x1, y1):
    """Kyiv at night: skyline with lit windows, missile trails."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(12, 18, 38))
    starfield(d, x0, y0, x1, y1, 77, count=max(10, int(w / 10)))
    base = int(y1 - h * 0.10)
    rnd = random.Random(77)
    bx = x0 + 4
    while bx < x1 - 4:
        bw = rnd.randint(max(6, int(w * 0.05)), max(9, int(w * 0.10)))
        bh = rnd.randint(max(10, int(h * 0.22)), max(14, int(h * 0.52)))
        d.rectangle([bx, base - bh, bx + bw, base], fill=(30, 38, 60))
        for wy in range(base - bh + 4, base - 3, 7):
            for wx in range(bx + 2, bx + bw - 1, 6):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 2, wy + 2],
                                fill=(255, 210, 120))
        bx += bw + 2
    for mx, tilt in ((x0 + w * 0.16, 1), (x0 + w * 0.52, 1),
                     (x0 + w * 0.82, -1)):
        pts = []
        for s in range(9):
            t = s / 8.0
            pts.append((mx + tilt * int(w * 0.11 * t),
                        y0 + 5 + int((y1 - h * 0.42 - y0) * t * t)))
        d.line(pts, fill=(255, 180, 60), width=2)
        d.ellipse([pts[-1][0] - 3, pts[-1][1] - 3,
                   pts[-1][0] + 3, pts[-1][1] + 3], fill=(255, 220, 120))
    bx, by = x0 + w * 0.70, y1 - h * 0.30
    for r, col in ((9, (255, 200, 80)), (5, (255, 140, 40)),
                   (2, (255, 240, 180))):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col)
    d.polygon([(x0 + w * 0.30, base), (x0 + w * 0.34, y0 + h * 0.30),
               (x0 + w * 0.38, base)], fill=(255, 230, 150))


def art_cop31(d, x0, y0, x1, y1):
    """Antalya: hot sun, turquoise bay, two sailboats, green hill."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (252, 216, 132), (242, 152, 62))
    d.ellipse([x0 + w * 0.07, y0 + h * 0.06, x0 + w * 0.07 + h * 0.36,
               y0 + h * 0.06 + h * 0.36], fill=(255, 238, 165))
    cloud(d, x0 + w * 0.55, y0 + h * 0.10, w * 0.14, (255, 244, 210))
    horizon = y0 + h * 0.58
    d.rectangle([x0, horizon, x1, y1], fill=(30, 128, 140))
    d.line([(x0 + 4, horizon + 6), (x1 - 4, horizon + 6)],
           fill=(120, 200, 205), width=1)
    d.line([(x0 + 4, horizon + 13), (x1 - 4, horizon + 13)],
           fill=(90, 175, 185), width=1)
    for sx, sw_, sh_ in ((0.52, 0.10, 0.24), (0.78, 0.07, 0.16)):
        bx = x0 + w * sx
        by = horizon + 4
        d.polygon([(bx, by), (bx, by - h * sh_),
                   (bx + w * sw_, by)], fill=(255, 255, 255))
        d.rectangle([bx - w * 0.08, by, bx + w * 0.10, by + 3],
                    fill=(178, 38, 38))
    d.polygon([(x0, horizon), (x0 + w * 0.18, y0 + h * 0.42),
               (x0 + w * 0.40, horizon)], fill=(88, 118, 108))
    d.polygon([(x0 + w * 0.30, horizon), (x0 + w * 0.44, y0 + h * 0.48),
               (x0 + w * 0.58, horizon)], fill=(70, 100, 92))


def art_markets(d, x0, y0, x1, y1):
    """Asia sell-off: red candles, falling line, grid, -7% tag."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(252, 248, 240))
    for gy in (0.25, 0.5, 0.75):
        yy = y0 + h * gy
        d.line([(x0 + 6, yy), (x1 - 4, yy)], fill=(228, 222, 208), width=1)
    d.line([(x0 + 6, y1 - 8), (x1 - 4, y1 - 8)], fill=GREY, width=1)
    d.line([(x0 + 6, y0 + 4), (x0 + 6, y1 - 8)], fill=GREY, width=1)
    pts = [(x0 + w * f, y0 + h * g) for f, g in
           ((0.10, 0.14), (0.26, 0.30), (0.40, 0.22), (0.56, 0.46),
            (0.72, 0.58), (0.90, 0.84))]
    d.line(pts, fill=RED, width=3)
    for fx, fy, fh in ((0.18, 0.42, 0.20), (0.46, 0.50, 0.28),
                       (0.70, 0.56, 0.34)):
        bx = x0 + w * fx
        d.line([(bx + 3, y0 + h * fy - 4), (bx + 3, y0 + h * fy + h * fh + 4)],
               fill=(200, 60, 60), width=1)
        d.rectangle([bx, y0 + h * fy, bx + max(5, w * 0.05),
                     y0 + h * fy + h * fh], fill=(200, 60, 60))
    d.rectangle([x0 + 6, y1 - 22, x0 + 44, y1 - 6], fill=RED)
    d.text((x0 + 9, y1 - 20), "-7%", font=F(SANS_B, 11),
           fill=(255, 255, 255))


def art_mercury(d, x0, y0, x1, y1):
    """BepiColombo at Mercury: cratered planet, probe, dotted path."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(8, 10, 20))
    starfield(d, x0, y0, x1, y1, 99, count=max(10, int(w / 10)))
    cx, cy = x0 + w * 0.70, y0 + h * 0.54
    r = min(w, h) * 0.36
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2],
              fill=(90, 82, 70))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(152, 142, 130))
    for ox, oy, rr in ((-0.45, -0.35, 0.22), (0.35, 0.10, 0.17),
                       (-0.10, 0.45, 0.17), (0.55, -0.45, 0.12),
                       (0.15, -0.55, 0.10), (-0.55, 0.25, 0.13)):
        d.ellipse([cx + ox * r - rr * r, cy + oy * r - rr * r,
                   cx + ox * r + rr * r, cy + oy * r + rr * r],
                  fill=(120, 110, 100))
    d.arc([cx - r * 1.25, cy - r * 1.25, cx + r * 1.25, cy + r * 1.25],
          200, 320, fill=(220, 210, 190), width=1)
    px, py = x0 + w * 0.07, y0 + h * 0.18
    d.rectangle([px, py, px + w * 0.07, py + h * 0.16],
                fill=(205, 205, 195))
    d.rectangle([px - w * 0.035, py + h * 0.04, px, py + h * 0.12],
                fill=(120, 160, 200))
    d.rectangle([px + w * 0.07, py + h * 0.04, px + w * 0.105,
                 py + h * 0.12], fill=(120, 160, 200))
    d.line([(px + w * 0.02, py - h * 0.06), (px + w * 0.05, py)],
           fill=(220, 220, 200), width=1)
    for t in range(0, 11):
        tt = t / 10.0
        dx = px + w * 0.105 + (cx - r * 0.8 - px - w * 0.105) * tt
        dy = py + h * 0.08 + (cy - r * 0.5 - py - h * 0.08) * tt
        if t % 2 == 0:
            d.point((dx, dy), fill=(220, 220, 200))

def art_brussels(d, x0, y0, x1, y1):
    """Brussels: EU blue, ring of gold stars, Berlaymont silhouette."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (0, 51, 153), (0, 38, 120))
    cx, cy = x0 + w * 0.5, y0 + h * 0.44
    rr = min(w, h) * 0.32
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        star5(d, cx + rr * math.cos(a), cy + rr * math.sin(a), 4.5,
              (255, 204, 0))
    d.rectangle([x0, y1 - h * 0.20, x1, y1], fill=(8, 28, 70))
    rnd = random.Random(21)
    bx = x0 + 6
    while bx < x1 - 6:
        bw = rnd.randint(max(8, int(w * 0.07)), max(12, int(w * 0.12)))
        bh = rnd.randint(max(6, int(h * 0.10)), max(10, int(h * 0.18)))
        d.rectangle([bx, y1 - bh, bx + bw, y1], fill=(16, 44, 92))
        for wy in range(y1 - bh + 3, y1 - 2, 6):
            d.rectangle([bx + 2, wy, bx + 4, wy + 2], fill=(255, 220, 120))
        bx += bw + 3
    d.rectangle([x0, y1 - 3, x1, y1], fill=(250, 240, 200))


def art_tokyo(d, x0, y0, x1, y1):
    """Tokyo: red sun with rays, rising teal line, tower, clouds."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
    cloud(d, x0 + w * 0.08, y0 + h * 0.08, w * 0.16, (255, 255, 255))
    cx, cy = x0 + w * 0.70, y0 + h * 0.30
    r = min(w, h) * 0.24
    for i in range(8):
        a = 2 * math.pi * i / 8
        d.line([(cx + (r + 3) * math.cos(a), cy + (r + 3) * math.sin(a)),
                (cx + (r + 9) * math.cos(a), cy + (r + 9) * math.sin(a))],
               fill=(220, 120, 110), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 0, 45))
    pts = [(x0 + w * f, y1 - h * g) for f, g in
           ((0.06, 0.18), (0.24, 0.32), (0.38, 0.26), (0.58, 0.44),
            (0.78, 0.54))]
    d.line(pts, fill=TEAL, width=3)
    d.polygon([(x0 + w * 0.08, y1), (x0 + w * 0.12, y1 - h * 0.42),
               (x0 + w * 0.16, y1)], fill=NAVY)
    d.line([(x0 + w * 0.12, y1 - h * 0.42), (x0 + w * 0.12, y1 - h * 0.54)],
           fill=NAVY, width=2)
    d.polygon([(x0 + w * 0.84, y1), (x0 + w * 0.88, y1 - h * 0.30),
               (x0 + w * 0.92, y1)], fill=(90, 90, 100))
    d.text((x0 + 5, y1 - 18), "2.3%", font=F(SANS_B, 11), fill=RED)


def art_beijing(d, x0, y0, x1, y1):
    """Beijing: golden sky, skyline, pagoda roof, flat red rate line."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (234, 216, 172), (198, 168, 118))
    cloud(d, x0 + w * 0.60, y0 + h * 0.08, w * 0.15, (250, 242, 220))
    base = int(y1 - h * 0.10)
    rnd = random.Random(311)
    bx = x0 + 4
    while bx < x1 - 4:
        bw = rnd.randint(max(6, int(w * 0.05)), max(9, int(w * 0.09)))
        bh = rnd.randint(max(10, int(h * 0.25)), max(16, int(h * 0.55)))
        d.rectangle([bx, base - bh, bx + bw, base], fill=(38, 74, 110))
        for wy in range(base - bh + 4, base - 3, 7):
            if rnd.random() < 0.5:
                d.rectangle([bx + 2, wy, bx + 4, wy + 2],
                            fill=(255, 220, 140))
        bx += bw + 2
    px = x0 + w * 0.62
    d.polygon([(px, base - h * 0.42), (px + w * 0.10, base - h * 0.42),
               (px + w * 0.05, base - h * 0.58)], fill=(150, 40, 40))
    d.rectangle([px + w * 0.02, base - h * 0.42, px + w * 0.08,
                 base - h * 0.30], fill=(120, 30, 30))
    d.line([(x0 + 4, y0 + h * 0.16), (x1 - 4, y0 + h * 0.16)],
           fill=RED, width=2)
    d.text((x0 + 5, y0 + h * 0.24), "3.0%", font=F(SANS_B, 11), fill=RED)
    for lx in range(x0 + 8, x1 - 8, 16):
        d.ellipse([lx, y0 + h * 0.30, lx + 3, y0 + h * 0.30 + 4],
                  fill=(178, 38, 38))


def art_cricket(d, x0, y0, x1, y1):
    """Cricket: green outfield, pale pitch, bat, ball, stumps, crowd."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(46, 120, 62))
    d.ellipse([x0, y0, x1, y1], outline=(90, 160, 100), width=2)
    d.rectangle([x0 + w * 0.38, y0 + 4, x0 + w * 0.58, y1 - 4],
                fill=(232, 214, 170))
    for sx in (0.06, 0.86):
        for j in range(3):
            d.line([(x0 + w * sx + j * 3, y0 + h * 0.62),
                    (x0 + w * sx + j * 3, y0 + h * 0.62 - 8)],
                   fill=(250, 240, 200), width=2)
    d.polygon([(x0 + w * 0.42, y0 + h * 0.18), (x0 + w * 0.48, y0 + h * 0.18),
               (x0 + w * 0.52, y0 + h * 0.55),
               (x0 + w * 0.46, y0 + h * 0.55)], fill=(150, 100, 50))
    d.ellipse([x0 + w * 0.70, y0 + h * 0.60, x0 + w * 0.70 + 8,
               y0 + h * 0.60 + 8], fill=(178, 38, 38))
    rnd = random.Random(9)
    for _ in range(max(8, int(w / 12))):
        hx = rnd.randint(x0 + 4, x1 - 8)
        hy = rnd.randint(y0 + 4, y0 + int(h * 0.22))
        d.ellipse([hx, hy, hx + 5, hy + 5], fill=(230, 210, 180))
    d.rectangle([x0 + 4, y1 - 20, x0 + 46, y1 - 4], fill=(255, 255, 255))
    d.text((x0 + 7, y1 - 18), "118", font=F(SANS_B, 12), fill=(24, 24, 24))


def art_bukele(d, x0, y0, x1, y1):
    """El Salvador: blue-white-blue, ballot box, papers, crowd."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(0, 71, 171))
    d.rectangle([x0, y0 + h * 0.28, x1, y0 + h * 0.66],
                fill=(255, 255, 255))
    d.rectangle([x0 + w * 0.14, y1 - h * 0.40, x0 + w * 0.86,
                 y1 - h * 0.08], fill=(0, 50, 130),
                outline=(255, 255, 255), width=2)
    d.line([(x0 + w * 0.38, y1 - h * 0.40), (x0 + w * 0.62, y1 - h * 0.40)],
           fill=(255, 255, 255), width=2)
    d.polygon([(x0 + w * 0.42, y0 + h * 0.04), (x0 + w * 0.50, y0 + h * 0.18),
               (x0 + w * 0.58, y0 + h * 0.04)], fill=(255, 255, 255))
    for fx in (0.20, 0.72):
        px = x0 + w * fx
        d.polygon([(px, y0 + h * 0.34), (px + w * 0.08, y0 + h * 0.34),
                   (px + w * 0.04, y0 + h * 0.22)], fill=(255, 255, 255))
    rnd = random.Random(31)
    for _ in range(max(8, int(w / 12))):
        hx = rnd.randint(x0 + 4, x1 - 8)
        hy = rnd.randint(y1 - int(h * 0.22), y1 - 6)
        d.ellipse([hx, hy, hx + 6, hy + 6], fill=(230, 210, 180))


def art_senegal(d, x0, y0, x1, y1):
    """Capsized boat: sun, sea, upturned hull, waves, life ring."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (126, 184, 208), (22, 88, 128))
    d.ellipse([x0 + w * 0.76, y0 + h * 0.08, x0 + w * 0.76 + h * 0.22,
               y0 + h * 0.08 + h * 0.22], fill=(255, 236, 160))
    for wy in (y1 - h * 0.46, y1 - h * 0.30, y1 - h * 0.14):
        for wx in range(x0 + 2, x1 - 6, 12):
            d.arc([wx, wy, wx + 10, wy + 6], 200, 340,
                  fill=(220, 235, 245))
    cx = x0 + w * 0.42
    d.polygon([(cx - w * 0.20, y1 - h * 0.50), (cx + w * 0.20, y1 - h * 0.50),
               (cx + w * 0.13, y1 - h * 0.34),
               (cx - w * 0.13, y1 - h * 0.34)], fill=(120, 70, 40))
    d.rectangle([cx - 4, y1 - h * 0.62, cx + 4, y1 - h * 0.50],
                fill=(90, 50, 30))
    d.ellipse([x0 + w * 0.72, y1 - h * 0.30, x0 + w * 0.72 + 12,
               y1 - h * 0.30 + 12], outline=(255, 120, 60), width=3)
    d.ellipse([x0 + w * 0.72 + 4, y1 - h * 0.30 + 4,
               x0 + w * 0.72 + 8, y1 - h * 0.30 + 8],
              outline=(255, 120, 60), width=1)
    for gx in (0.12, 0.88):
        gx0 = x0 + w * gx
        d.line([(gx0, y1 - h * 0.58), (gx0 + 5, y1 - h * 0.58 - 8)],
               fill=(230, 230, 210), width=1)


def art_italy(d, x0, y0, x1, y1):
    """General strike: placards, flags, crowd of heads, sun."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
    d.ellipse([x0 + w * 0.80, y0 + h * 0.06, x0 + w * 0.80 + h * 0.20,
               y0 + h * 0.06 + h * 0.20], fill=(250, 214, 130))
    rnd = random.Random(45)
    for _ in range(max(10, int(w / 10))):
        hx = rnd.randint(x0 + 4, x1 - 8)
        hy = rnd.randint(y1 - int(h * 0.32), y1 - 8)
        d.ellipse([hx, hy, hx + 7, hy + 7], fill=(200, 170, 140))
    for fx, col in ((0.06, RED), (0.38, (38, 74, 110)), (0.70, TEAL)):
        sx = x0 + w * fx
        d.line([(sx + 5, y0 + h * 0.36), (sx + 5, y1 - h * 0.22)],
               fill=INK, width=2)
        d.rectangle([sx, y0 + h * 0.12, sx + max(12, w * 0.11),
                     y0 + h * 0.36], fill=col, outline=INK)
    d.polygon([(x0 + w * 0.52, y0 + h * 0.14), (x0 + w * 0.62, y0 + h * 0.14),
               (x0 + w * 0.62, y0 + h * 0.30)], fill=(0, 140, 70))
    d.line([(x0 + w * 0.62, y0 + h * 0.14), (x0 + w * 0.62, y1 - h * 0.22)],
           fill=INK, width=2)
    d.rectangle([x0 + 4, y0 + h * 0.42, x0 + 34, y0 + h * 0.42 + 16],
                fill=INK)
    d.text((x0 + 7, y0 + h * 0.42 + 2), "24h", font=F(SANS_B, 10),
           fill=(255, 255, 255))


def art_health(d, x0, y0, x1, y1):
    """Cancer pill: capsule, pill bottle, shrinking bars, cross."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(252, 248, 240))
    d.rounded_rectangle([x0 + w * 0.08, y0 + h * 0.12, x0 + w * 0.60,
                         y0 + h * 0.38], radius=7, fill=(178, 38, 38))
    d.rounded_rectangle([x0 + w * 0.08, y0 + h * 0.12, x0 + w * 0.34,
                         y0 + h * 0.38], radius=7, fill=(240, 240, 235))
    d.rounded_rectangle([x0 + w * 0.08, y0 + h * 0.12, x0 + w * 0.60,
                         y0 + h * 0.38], radius=7, outline=INK)
    bx = x0 + w * 0.72
    d.rectangle([bx, y0 + h * 0.16, bx + w * 0.16, y0 + h * 0.52],
                fill=(255, 255, 255), outline=TEAL, width=2)
    d.rectangle([bx + 2, y0 + h * 0.16, bx + w * 0.16 - 2, y0 + h * 0.26],
                fill=TEAL)
    d.line([(bx + w * 0.08, y0 + h * 0.34), (bx + w * 0.08, y0 + h * 0.46)],
           fill=TEAL, width=3)
    d.line([(bx + w * 0.03, y0 + h * 0.40), (bx + w * 0.13, y0 + h * 0.40)],
           fill=TEAL, width=3)
    for i, fh in enumerate((0.30, 0.22, 0.14)):
        bx2 = x0 + w * (0.10 + i * 0.18)
        d.rectangle([bx2, y1 - 8 - h * fh, bx2 + max(8, w * 0.08), y1 - 8],
                    fill=TEAL)
    d.line([(x0 + w * 0.08, y1 - 8 - h * 0.32),
            (x0 + w * 0.62, y1 - 8 - h * 0.10)], fill=RED, width=2)
    d.text((x0 + w * 0.66, y1 - 22), "61%", font=F(SANS_B, 11), fill=TEAL)


ART = [art_cyclone, art_kyiv, art_cop31, art_markets, art_mercury,
       art_brussels, art_tokyo, art_beijing, art_cricket, art_bukele,
       art_senegal, art_italy, art_health]


def draw_market_bars(d, x0, y0, x1, y1, rows):
    """MARKETS AT CLOSE: one mini bar per index, red, scaled."""
    d.text((x0, y0), "MARKETS AT CLOSE", font=F(SANS_B, 11), fill=RED)
    d.text((x1, y0), "FRIDAY'S CLOSES · ALL DOWN", font=F(SANS, 9),
           fill=GREY, anchor="ra")
    n = len(rows)
    cw = (x1 - x0) / n
    top = max(abs(v) for _, v in rows)
    for i, (name, v) in enumerate(rows):
        cx = x0 + i * cw
        d.text((cx + 2, y0 + 18), name, font=F(SANS_B, 9), fill=INK)
        d.text((cx + cw - 6, y0 + 15), "%+.1f%%" % v,
               font=F(SERIF_B, 15), fill=RED, anchor="ra")
        bw = max(8, (abs(v) / top) * (cw - 12))
        d.rectangle([cx + 2, y0 + 36, cx + 2 + bw, y0 + 46], fill=RED)
        d.rectangle([cx + 2, y0 + 36, cx + cw - 6, y0 + 46],
                    outline=LINE, width=1)
    d.text((x0, y1 - 11),
           "Asia's worst week since 2020 · MSCI Asia-Pacific -7% on the week",
           font=F(SANS, 9), fill=GREY)

FEATURES = [
    ("ODISHA, INDIA · CYCLONE", "Cyclone Akvan makes landfall in eastern India",
     "Akvan crosses near Gopalpur; 300,000+ evacuated, gusts 90 km/h, "
     "423 teams out.",
     "(IMD, The Hindu)"),
    ("KYIV, UKRAINE · WAR", "Russia fires wave of ~30 ballistic missiles at Kyiv",
     "Bridges hit in the war's biggest strikes; power and water cut "
     "across the city.",
     "(Kyiv Post, Reuters)"),
    ("ANTALYA, TÜRKIYE · CLIMATE", "COP31 reaches its final day deadlocked",
     "Closing draft omits fossil-fuel phase-out; $120bn adaptation "
     "finance unresolved.",
     "(UN News, Reuters)"),
    ("SEOUL · TOKYO · MARKETS", "AI sell-off sinks Asia to worst week since 2020",
     "Nikkei -4.9%, KOSPI -5.2%; worst week since 2020.",
     "(Reuters)"),
    ("MERCURY · SPACE", "BepiColombo reaches Mercury after 8 years",
     "ESA/JAXA probe ends 6bn-mile trip; orbit insertion Saturday.",
     "(ESA, BBC)"),
    ("BRUSSELS · EUROPE", "Burnham holds first EU–UK reset summit",
     "UK pledges 1,000+ drones for Ukraine in a £260m package.",
     "(EU Council, BBC)"),
    ("TOKYO · ECONOMY", "Japan inflation hits 2.3%; BoJ eyed",
     "Oct CPI rises from 2.1%; core above 2% for second month.",
     "(Reuters)"),
    ("BEIJING · RATES", "China holds lending rates for 18th month",
     "One-year LPR stays at 3.0%, five-year at 3.5% as expected.",
     "(PBOC, Reuters)"),
    ("WELLINGTON · CRICKET", "Phillips makes history with 118 vs India",
     "First NZ batter with centuries in all 3 formats vs India.",
     "(ICC, AP)"),
    ("SAN SALVADOR · POLITICS", "Bukele registers for third-term bid",
     "Files for Feb 2027 vote; rights groups object to another term.",
     "(AP)"),
    ("SENEGAL · MIGRATION", "Migrant boat capsizes off Yenne; 4 dead",
     "Dozens missing from ~50–100 aboard as Canary arrivals surge.",
     "(Al Jazeera)"),
    ("ROME · LABOUR", "Italy’s CGIL holds 24-hr general strike",
     "Rallies in ~100 squares against 2027 budget; transit hit.",
     "(CGIL, AFP)"),
    ("BARCELONA · HEALTH", "Pancreatic cancer pill shrinks tumours 60.7%",
     "Pill + chemo beats chemo alone (23–42%) in early trial.",
     "(Reuters)"),
]

STATS = [
    ("300,000+", "evacuated in Odisha"),
    ("~30", "missiles fired at Kyiv"),
    ("−7%", "Asia's worst week since 2020"),
    ("2.3%", "Japan Oct CPI"),
    ("118", "Phillips' century vs India"),
    ("8 yrs", "to Mercury"),
]

# Terse one-line briefs for the 3-column grid (each must fit 221px
# at 9pt; the script warns on any overflow).
BRIEFS = [
    "BRAZIL — Lula meets Raoni. (Al Jazeera)",
    "SEOUL — Move to impeach top judge. (SBS)",
    "CANBERRA — CBO warns on AUKUS. (Reuters)",
    "FLORIDA — St Johns River record high. (AP)",
    "IOWA — Army to detonate 68 barrels. (AP)",
    "TONGA — Emergency as drought bites. (RNZ)",
    "US — Iran war cost put at $48.3bn. (AFP)",
    "LONDON — £100m for Ukraine ships. (BBC)",
    "COPENHAGEN — Greenland bill passed. (AFP)",
    "JAKARTA — Asset-forfeiture bill. (AFP)",
    "GLOBAL — World Children's Day. (UN News)",
    "LAS VEGAS — Russell tops wet F1 FP2. (F1)",
    "BRUSSELS — Youth deal: 100,000 a year. (BBC)",
    "DELHI — Pakistan leads SCO team. (Hindu)",
    "QATAR — Australia beat Argentina 2–0. (FIFA)",
    "S AFRICA — Hammer spins Proteas win. (ICC)",
    "HONG KONG — Badminton Open semis. (BWF)",
    "TAIWAN — Short-sell curbs in force. (Reuters)",
    "TURIN — Alcaraz, Medvedev close. (ATP)",
    "LA — Markle fit to stand trial. (BBC)",
    "WELLINGTON — Nicholls 175* unbeaten. (ICC)",
    "GENOA — Drones halt flights. (ANSA)",
    "NEW CALEDONIA — M5.6 quake. (USGS)",
]

REGIONS = [("EUROPE", 10, (0, 84, 160)), ("AMERICAS", 7, (0, 128, 96)),
           ("ASIA-PACIFIC", 9, (178, 38, 38)),
           ("MIDEAST", 1, (196, 132, 0)), ("AFRICA", 2, (112, 62, 150)),
           ("OCEANIA", 5, (0, 130, 130)), ("WORLD", 2, (96, 96, 96))]

EXCLUDED = [
    "Trump–Xi–Putin Shenzhen summit",
    "Anthropic's $83 IPO debut",
    "ICJ Myanmar Rohingya genocide verdict",
    "GTA VI midnight launch",
    "Riyadh tower attack (Thursday)",
    "COP31's second draft",
    "Khasab tanker strike (Thursday)",
]

# (lon, lat, dx, dy) pins for features 1-13 on the map; 5 is in space.
PINS = [
    (84.9, 19.3, 0, 0), (30.5, 50.4, 6, -8), (30.7, 36.9, 18, 12),
    (127.0, 37.5, 0, 8), None, (4.35, 50.85, -8, -6),
    (139.7, 35.7, 10, -6), (116.4, 39.9, -8, -10), (174.8, -41.3, -10, 0),
    (-89.2, 13.7, 0, 0), (-17.4, 14.7, 0, 0), (12.5, 41.9, 12, 6),
    (2.17, 41.4, -14, 8),
]

NA = [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73),
      (-75, 62), (-60, 55), (-55, 47), (-70, 42), (-75, 35),
      (-80, 26), (-85, 30), (-90, 21), (-97, 16), (-105, 20),
      (-110, 24), (-117, 33), (-125, 40), (-125, 49), (-135, 58),
      (-150, 61), (-165, 60)]
SA = [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8),
      (-40, -20), (-50, -30), (-60, -38), (-70, -45), (-73, -53),
      (-70, -40), (-72, -20), (-77, -12), (-80, -3)]
EU = [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57),
      (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 70),
      (40, 68), (45, 60), (40, 50), (35, 45), (30, 42), (28, 40),
      (23, 36), (20, 40), (15, 44), (10, 44), (5, 43), (0, 40),
      (-2, 37), (-9, 37)]
AF = [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
      (35, 28), (43, 12), (48, 11), (51, 10), (44, 0), (40, -10),
      (35, -20), (32, -28), (26, -34), (20, -35), (15, -27),
      (12, -18), (9, -5), (8, 4), (0, 6), (-8, 5), (-15, 11)]
AS = [(30, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76),
      (130, 72), (150, 70), (170, 67), (178, 65), (170, 60),
      (162, 56), (158, 50), (150, 45), (142, 40), (140, 35),
      (135, 33), (130, 31), (127, 35), (122, 38), (120, 30),
      (115, 22), (108, 18), (105, 10), (100, 8), (97, 15), (92, 21),
      (88, 22), (80, 15), (77, 8), (72, 20), (66, 25), (60, 25),
      (57, 27), (52, 28), (48, 30), (44, 30), (40, 35), (35, 36),
      (30, 36), (28, 40), (27, 42), (30, 45), (32, 50), (35, 55),
      (38, 60), (40, 65), (35, 68)]
OC = [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
      (132, -32), (136, -35), (140, -38), (145, -38), (150, -37),
      (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
      (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
      (126, -14), (122, -17), (118, -20)]

MARKETS = [("NIKKEI 225", -4.9), ("KOSPI", -5.2), ("TAIEX", -6.4),
           ("HANG SENG", -1.9)]


def proj(lon, lat, mx0, my0, mw, mh):
    x = mx0 + (lon + 180.0) / 360.0 * mw
    y = my0 + (75.0 - lat) / 130.0 * mh
    return x, y


def draw_map(d, x0, y0, x1, y1):
    """Dark-navy world map: cream continents, ocean labels, country
    tags for the three lead stories, numbered red pins."""
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    for pts in (NA, SA, EU, AF, AS, OC):
        xy = [proj(lon, lat, x0, y0, x1 - x0, y1 - y0) for lon, lat in pts]
        d.polygon(xy, fill=LAND, outline=LAND_LN)
    lab = F(SANS_B, 8)
    d.text((x0 + 8, y0 + 8), "ATLANTIC", font=lab, fill=(120, 150, 180))
    d.text((x0 + 8, y1 - 34), "PACIFIC", font=lab, fill=(120, 150, 180))
    d.text((x1 - 58, y1 - 34), "PACIFIC", font=lab, fill=(120, 150, 180))
    d.text((x0 + 8, y1 - 20), "5  SPACE · Mercury", font=lab,
           fill=(235, 235, 215))
    for name, lon, lat, dx, dy in (
            ("INDIA", 84.9, 19.3, -14, 14), ("UKRAINE", 30.5, 50.4, 16, -18),
            ("TÜRKIYE", 30.7, 36.9, 28, 16), ("JAPAN", 139.7, 35.7, -4, 12)):
        px, py = proj(lon, lat, x0, y0, x1 - x0, y1 - y0)
        d.text((px + dx, py + dy), name, font=F(SANS_B, 7),
               fill=(90, 90, 80))
    for i, pin in enumerate(PINS):
        if pin is None:
            continue
        lon, lat, dx, dy = pin
        px, py = proj(lon, lat, x0, y0, x1 - x0, y1 - y0)
        px += dx
        py += dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        num = str(i + 1)
        tw = d.textlength(num, font=F(SANS_B, 10))
        d.text((px - tw / 2, py - 7), num, font=F(SANS_B, 10),
               fill=(255, 255, 255))


def feature_card(d, x, y, w, h, num, story, art, banner_h,
                 head_size, head_lead, deck_size, deck_lead):
    """One feature card: banner art, kicker, headline, deck + source."""
    kick, head, deck, src = story
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    art(d, x + 1, y + 1, x + w - 1, y + banner_h)
    d.line([(x, y + banner_h), (x + w, y + banner_h)], fill=INK, width=1)
    tx = x + 8
    tw_ = w - 16
    yy = y + banner_h + 6
    d.text((tx, yy), "%02d · %s" % (num, kick), font=F(SANS_B, 10), fill=RED)
    yy += 14
    hf = F(SERIF_B, head_size)
    for line in wrap(d, head, hf, tw_)[:2]:
        d.text((tx, yy), line, font=hf, fill=INK)
        yy += head_lead
    yy += 1
    if len(wrap(d, head, hf, tw_)) > 2:
        WARN.append("HEADLINE TRUNCATED #%d %r" % (num, head[:40]))
    para(d, tx, yy, deck + " " + src, F(SANS, deck_size), tw_, deck_lead,
         max_lines=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 14
    RX = W - MX  # 1010

    # ---- top label row ----
    d.text((MX, 6), "THE WORLD IN ONE DAY", font=F(SANS_B, 11), fill=RED)
    d.text((RX, 6), "FRIDAY'S NEWS · ONE PAGE · 36 STORIES · 6 CONTINENTS",
           font=F(SANS, 10), fill=GREY, anchor="ra")
    hline(d, MX, RX, 24, w=1, fill=LINE)

    # ---- giant date masthead + red strapline ----
    d.text((MX, 28), "Friday 20 November 2026",
           font=F(SERIF_B, 56), fill=INK)
    d.text((MX, 96),
           "Cyclone Akvan strikes India · Ballistic missiles hit Kyiv · "
           "COP31 deadlocked on final day · Asian AI sell-off",
           font=F(SERIF, 15), fill=RED)
    hline(d, MX, RX, 118, w=3, fill=INK)

    # ---- headline stat strip: big red numbers, short labels ----
    sy = 126
    for i, (num, lab) in enumerate(STATS):
        x = MX + i * 166
        if i:
            d.line([(x - 3, sy + 2), (x - 3, sy + 30)], fill=LINE, width=1)
        d.text((x + 2, sy), num, font=F(SERIF_B, 21), fill=RED)
        if d.textlength(lab, font=F(SANS, 9)) > 160:
            WARN.append("STAT LABEL OVERFLOW %r" % lab)
        d.text((x + 2, sy + 26), lab, font=F(SANS, 9), fill=GREY)

    # ---- coloured region chips ----
    cy = 166
    cx = MX
    for name, n, col in REGIONS:
        label = "%s %d" % (name, n)
        f = F(SANS_B, 10)
        tw = d.textlength(label, font=f)
        d.rounded_rectangle([cx, cy, cx + tw + 14, cy + 20], radius=3,
                            fill=col)
        d.text((cx + 7, cy + 4), label, font=f, fill=(255, 255, 255))
        cx += tw + 14 + 6
    d.text((RX, cy + 4), "ALL STORIES: FRI 20 NOV 2026, ANY TIME ZONE",
           font=F(SANS, 9), fill=GREY, anchor="ra")

    # ---- 13 features: 3 large + 5 + 5 small, banner art on top ----
    lw, lh, lb = 322, 212, 118
    for i in range(3):
        feature_card(d, MX + i * (lw + 5), 192, lw, lh, i + 1,
                     FEATURES[i], ART[i], lb, 19, 21, 11, 13)
    sw, sh, sb = 195, 128, 58
    for r in range(2):
        for c in range(5):
            i = 3 + r * 5 + c
            feature_card(d, MX + c * (sw + 5), 410 + r * (sh + 6),
                         sw, sh, i + 1, FEATURES[i], ART[i], sb,
                         12, 14, 9, 11)

    # ---- bottom: dark map + 3-column briefs + markets panel ----
    hline(d, MX, RX, 676, w=2)
    d.text((MX, 682), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=RED)
    d.text((322, 682), "ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES",
           font=F(SANS_B, 12), fill=RED)
    d.text((RX, 682), "BRIEFS 14–36", font=F(SANS, 10), fill=GREY,
           anchor="ra")
    draw_map(d, MX, 700, 314, 924)
    bf = F(SANS, 9)
    for j, b in enumerate(BRIEFS):
        c = j // 8
        r = j % 8
        x = 322 + c * 229
        if d.textlength(b, font=bf) > 221:
            WARN.append("BRIEF OVERFLOW #%d %r" % (j + 14, b))
        d.text((x, 700 + r * 19), b, font=bf, fill=INK)
    draw_market_bars(d, 322, 858, RX, 924, MARKETS)

    # ---- DATE CHECK strip ----
    dy0, dy1 = 932, 966
    d.rectangle([MX, dy0, RX, dy1], outline=RED, width=2)
    d.text((MX + 10, dy0 + 9), "DATE CHECK", font=F(SANS_B, 13), fill=RED)
    excl = ("First reported Thursday 19 Nov, NOT shown as Friday's news: "
            + " · ".join(EXCLUDED) + ".")
    para(d, MX + 108, dy0 + 4, excl, F(SANS, 10), RX - MX - 120, 13,
         fill=INK, max_lines=2)

    # ---- footer ----
    d.text((MX, 974),
           "Every story here happened, or was first reported, on Friday "
           "20 November 2026 in at least one time zone. Claims are "
           "attributed, not stated as fact.",
           font=F(SANS, 10), fill=GREY)
    d.text((MX, 988),
           "Sources: AP · AFP · BBC · CGIL · ICC · IMD · Reuters · "
           "UKMTO · USGS",
           font=F(SANS, 10), fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote %s (%d bytes, %dx%d)" % (out, os.path.getsize(out), W, H))
    if WARN:
        print("WARNINGS (%d):" % len(WARN))
        for wmsg in WARN:
            print("  -", wmsg)
    else:
        print("no overflow warnings")


if __name__ == "__main__":
    main()
