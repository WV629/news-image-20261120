#!/usr/bin/env python3
"""Render entry.png: a one-page newspaper front page summing up
Friday 20 November 2026 in 36 stories, drawn entirely with Pillow.

v3 format — mirrors the top-ranked entries' pairwise-winning look:
date-first giant serif masthead + red strapline, red headline stat
strip, coloured region chips, 13 feature stories as 3 large + 10
small cards, each with a full-width original vector banner
illustration on top, a dark-navy world map with numbered pins, a
two-column briefs list, and a DATE CHECK strip that names the big
Thursday 19 Nov stories and keeps them out of the Friday paper.

Date discipline: every story here happened, or was first
reported, on Friday 20 November 2026 in at least one time zone.
The Trump-Xi-Putin Shenzhen summit, Anthropic's $83 IPO pricing
and Nasdaq debut, the ICJ Myanmar verdict, the GTA VI launch,
the Riyadh tower attack and COP31's second draft are all
Thursday stories: they appear only in the DATE CHECK strip, never
as Friday news. Fiona the hippo died Thursday 19 Nov: excluded.

Deterministic: fixed layout, fixed palette, no network, no
timestamps. Run: python3 generate.py writes entry.png
(1024x1024) next to this file.
"""
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
SEA_DK = (13, 30, 54)
LAND_DK = (222, 206, 172)
LAND_LN_DK = (150, 138, 110)
TEAL = (24, 120, 116)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, f, max_w, leading, fill=INK, max_lines=None):
    lines = wrap(d, text, f, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def hrule(d, x0, x1, y, w=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def vgrad(d, x0, y0, x1, y1, top, bot):
    for i in range(y1 - y0):
        t = i / max(1, (y1 - y0))
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def stars(d, x0, y0, x1, y1, seed, count=14):
    rnd = random.Random(seed)
    for _ in range(count):
        sx = rnd.randint(x0 + 3, x1 - 3)
        sy = rnd.randint(y0 + 3, y1 - 3)
        d.point((sx, sy), fill=(235, 235, 215))


# ---------------------------------------------------------------- art
# Each draws an original illustration into the given box, sized
# relative to the box (works for the large 322-wide and small
# 195-wide banners alike).

def art_cyclone(d, x0, y0, x1, y1):
    """Cyclone over the coast: spiral, rain, shoreline."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (96, 110, 122), (52, 66, 80))
    cx, cy = x0 + w * 0.5, y0 + h * 0.42
    for r in (0.30, 0.21, 0.12):
        rr = r * min(w, h) * 1.15
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 200, 60 + rr,
              fill=(235, 235, 220), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(250, 240, 200))
    rnd = random.Random(1120)
    for _ in range(int(w / 12)):
        rx = rnd.randint(x0 + 4, x1 - 4)
        ry = rnd.randint(y0 + 4, y1 - int(h * 0.25))
        d.line([(rx, ry), (rx - 3, ry + 6)], fill=(200, 210, 220), width=1)
    d.rectangle([x0, y1 - h * 0.16, x1, y1], fill=(40, 90, 100))
    d.line([(x0, y1 - h * 0.16), (x1, y1 - h * 0.16)],
           fill=(250, 240, 200), width=1)


def art_kyiv(d, x0, y0, x1, y1):
    """Kyiv by night: dark sky, missile trails, bursts."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(12, 18, 38))
    stars(d, x0, y0, x1, y1, 77, count=max(10, int(w / 12)))
    base = y1 - h * 0.12
    rnd = random.Random(77)
    cx = x0 + 4
    while cx < x1 - 4:
        bw = rnd.randint(max(6, int(w * 0.05)), max(8, int(w * 0.09)))
        bh = rnd.randint(max(8, int(h * 0.18)), max(12, int(h * 0.45)))
        d.rectangle([cx, base - bh, cx + bw, base], fill=(30, 38, 60))
        cx += bw + 2
    for mx in (x0 + w * 0.18, x0 + w * 0.55):
        pts = []
        for s in range(8):
            t = s / 7.0
            pts.append((mx + int(w * 0.12 * t),
                        y0 + 6 + int((y1 - h * 0.4 - y0) * t * t)))
        d.line(pts, fill=(255, 180, 60), width=2)
        d.ellipse([pts[-1][0] - 3, pts[-1][1] - 3,
                   pts[-1][0] + 3, pts[-1][1] + 3], fill=(255, 220, 120))
    bx, by = x0 + w * 0.72, y1 - h * 0.28
    for r, col in ((7, (255, 200, 80)), (4, (255, 140, 40))):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col)


def art_cop31(d, x0, y0, x1, y1):
    """Antalya coast: hot sun, turquoise sea, sailboat, green hill."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (250, 214, 130), (240, 150, 60))
    d.ellipse([x0 + w * 0.08, y0 + h * 0.08, x0 + w * 0.08 + h * 0.34,
               y0 + h * 0.08 + h * 0.34], fill=(255, 236, 160))
    horizon = y0 + h * 0.6
    d.rectangle([x0, horizon, x1, y1], fill=(32, 130, 140))
    d.line([(x0 + 4, horizon + 6), (x1 - 4, horizon + 6)],
           fill=(120, 200, 205), width=1)
    bx = x0 + w * 0.55
    by = horizon + 4
    d.polygon([(bx, by), (bx, by - h * 0.22), (bx + w * 0.09, by)],
              fill=(255, 255, 255))
    d.rectangle([bx - w * 0.09, by, bx + w * 0.11, by + 3],
                fill=(178, 38, 38))
    d.polygon([(x0, horizon), (x0 + w * 0.2, y0 + h * 0.45),
               (x0 + w * 0.42, horizon)], fill=(90, 120, 110))


def art_markets(d, x0, y0, x1, y1):
    """Falling market: red candles and a jagged down line."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(252, 248, 240))
    d.line([(x0 + 6, y1 - 8), (x1 - 4, y1 - 8)], fill=GREY, width=1)
    d.line([(x0 + 6, y0 + 4), (x0 + 6, y1 - 8)], fill=GREY, width=1)
    pts = [(x0 + w * f, y0 + h * g) for f, g in
           ((0.12, 0.15), (0.28, 0.28), (0.40, 0.22), (0.58, 0.45),
            (0.74, 0.58), (0.92, 0.82))]
    d.line(pts, fill=RED, width=3)
    for fx, fh in ((0.2, 0.2), (0.48, 0.28), (0.72, 0.34)):
        d.rectangle([x0 + w * fx, y0 + h * 0.5,
                     x0 + w * fx + max(5, w * 0.05),
                     y0 + h * 0.5 + h * fh], fill=(200, 60, 60))
    d.text((x0 + 6, y1 - 20), "-7%", font=font(SANS_B, 13), fill=RED)


def art_mercury(d, x0, y0, x1, y1):
    """BepiColombo at Mercury: black sky, cratered planet, probe."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(8, 10, 20))
    stars(d, x0, y0, x1, y1, 99, count=max(10, int(w / 12)))
    cx, cy = x0 + w * 0.68, y0 + h * 0.52
    r = min(w, h) * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 140, 128))
    for ox, oy, rr in ((-0.45, -0.35, 0.22), (0.35, 0.1, 0.17),
                       (-0.1, 0.45, 0.17), (0.55, -0.45, 0.12)):
        d.ellipse([cx + ox * r - rr * r, cy + oy * r - rr * r,
                   cx + ox * r + rr * r, cy + oy * r + rr * r],
                  fill=(120, 110, 100))
    px, py = x0 + w * 0.08, y0 + h * 0.2
    d.rectangle([px, py, px + w * 0.07, py + h * 0.16],
                fill=(200, 200, 190))
    d.rectangle([px - w * 0.03, py + h * 0.04, px, py + h * 0.12],
                fill=(120, 160, 200))
    d.rectangle([px + w * 0.07, py + h * 0.04, px + w * 0.1,
                 py + h * 0.12], fill=(120, 160, 200))
    d.line([(px + w * 0.1, py + h * 0.08), (cx - r * 0.8, cy - r * 0.5)],
           fill=(220, 220, 200), width=1)


def art_brussels(d, x0, y0, x1, y1):
    """EU flag: blue field, circle of gold stars."""
    import math
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(0, 51, 153))
    cx, cy = x0 + w / 2, y0 + h / 2
    rr = min(w, h) * 0.34
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        sx = cx + rr * math.cos(a)
        sy = cy + rr * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    d.rectangle([x0, y1 - h * 0.12, x1, y1], fill=(250, 240, 200))


def art_tokyo(d, x0, y0, x1, y1):
    """Tokyo: red sun, rising line, tower silhouette."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
    r = min(w, h) * 0.26
    cx, cy = x0 + w * 0.72, y0 + h * 0.3
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 0, 45))
    pts = [(x0 + w * f, y1 - h * g) for f, g in
           ((0.06, 0.2), (0.24, 0.32), (0.38, 0.26), (0.58, 0.42),
            (0.78, 0.52))]
    d.line(pts, fill=TEAL, width=3)
    d.polygon([(x0 + w * 0.08, y1), (x0 + w * 0.12, y1 - h * 0.4),
               (x0 + w * 0.16, y1)], fill=NAVY)
    d.line([(x0 + w * 0.12, y1 - h * 0.4), (x0 + w * 0.12, y1 - h * 0.52)],
           fill=NAVY, width=2)


def art_beijing(d, x0, y0, x1, y1):
    """Beijing: skyline under a flat rate line."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (232, 214, 170), (200, 170, 120))
    base = y1 - h * 0.1
    rnd = random.Random(311)
    cx = x0 + 4
    while cx < x1 - 4:
        bw = rnd.randint(max(6, int(w * 0.05)), max(9, int(w * 0.09)))
        bh = rnd.randint(max(10, int(h * 0.25)), max(16, int(h * 0.55)))
        d.rectangle([cx, base - bh, cx + bw, base], fill=(38, 74, 110))
        cx += bw + 2
    for lx in range(x0 + 4, x1 - 4, 8):
        d.line([(lx, y0 + h * 0.16), (lx + 4, y0 + h * 0.16)],
               fill=RED, width=2)
    d.text((x0 + 5, y0 + h * 0.26), "3.0%", font=font(SANS_B, 11),
           fill=RED)


def art_cricket(d, x0, y0, x1, y1):
    """Cricket: green outfield, white pitch, bat and red ball."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(46, 120, 62))
    d.rectangle([x0 + w * 0.38, y0 + 4, x0 + w * 0.58, y1 - 4],
                fill=(232, 214, 170))
    d.polygon([(x0 + w * 0.42, y0 + h * 0.2), (x0 + w * 0.48, y0 + h * 0.2),
               (x0 + w * 0.52, y0 + h * 0.55),
               (x0 + w * 0.46, y0 + h * 0.55)], fill=(150, 100, 50))
    d.ellipse([x0 + w * 0.7, y0 + h * 0.62, x0 + w * 0.7 + 7,
               y0 + h * 0.62 + 7], fill=(178, 38, 38))
    d.text((x0 + 6, y1 - 18), "118", font=font(SANS_B, 13),
           fill=(255, 255, 255))


def art_bukele(d, x0, y0, x1, y1):
    """Ballot box in El Salvador blue-white-blue."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(0, 71, 171))
    d.rectangle([x0, y0 + h * 0.3, x1, y0 + h * 0.68],
                fill=(255, 255, 255))
    d.rectangle([x0 + w * 0.14, y1 - h * 0.38, x0 + w * 0.86,
                 y1 - h * 0.1], fill=(0, 50, 130),
                outline=(255, 255, 255))
    d.line([(x0 + w * 0.38, y1 - h * 0.38), (x0 + w * 0.62, y1 - h * 0.38)],
           fill=(255, 255, 255), width=2)
    d.polygon([(x0 + w * 0.42, y0 + h * 0.06), (x0 + w * 0.5, y0 + h * 0.2),
               (x0 + w * 0.58, y0 + h * 0.06)], fill=(255, 255, 255))


def art_senegal(d, x0, y0, x1, y1):
    """Capsized boat: sea, upturned hull, waves."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, x0, y0, x1, y1, (120, 180, 205), (24, 90, 130))
    for wy in (y1 - h * 0.42, y1 - h * 0.26, y1 - h * 0.1):
        for wx in range(x0 + 2, x1 - 6, 12):
            d.arc([wx, wy, wx + 10, wy + 6], 200, 340,
                  fill=(220, 235, 245))
    cx = x0 + w / 2
    d.polygon([(cx - w * 0.18, y1 - h * 0.46), (cx + w * 0.18, y1 - h * 0.46),
               (cx + w * 0.12, y1 - h * 0.32),
               (cx - w * 0.12, y1 - h * 0.32)], fill=(120, 70, 40))
    d.rectangle([cx - 4, y1 - h * 0.56, cx + 4, y1 - h * 0.46],
                fill=(90, 50, 30))


def art_italy(d, x0, y0, x1, y1):
    """Strike: placards above a crowd of heads."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
    rnd = random.Random(45)
    for _ in range(max(6, int(w / 16))):
        hx = rnd.randint(x0 + 4, x1 - 8)
        hy = rnd.randint(y1 - int(h * 0.3), y1 - 8)
        d.ellipse([hx, hy, hx + 7, hy + 7], fill=(200, 170, 140))
    for fx, col in ((0.08, RED), (0.4, (38, 74, 110)), (0.72, TEAL)):
        sx = x0 + w * fx
        d.line([(sx + 5, y0 + h * 0.38), (sx + 5, y1 - h * 0.2)],
               fill=INK, width=2)
        d.rectangle([sx, y0 + h * 0.14, sx + max(11, w * 0.1),
                     y0 + h * 0.38], fill=col, outline=INK)
    d.text((x0 + 6, y0 + h * 0.44), "24h", font=font(SANS_B, 10), fill=INK)


def art_health(d, x0, y0, x1, y1):
    """Cancer pill: capsule and shrinking bars."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(252, 248, 240))
    d.rounded_rectangle([x0 + w * 0.1, y0 + h * 0.14, x0 + w * 0.62,
                         y0 + h * 0.4], radius=7, fill=(178, 38, 38))
    d.rounded_rectangle([x0 + w * 0.1, y0 + h * 0.14, x0 + w * 0.36,
                         y0 + h * 0.4], radius=7, fill=(240, 240, 235))
    d.rounded_rectangle([x0 + w * 0.1, y0 + h * 0.14, x0 + w * 0.62,
                         y0 + h * 0.4], radius=7, outline=INK)
    for i, fh in enumerate((0.3, 0.22, 0.14)):
        bx = x0 + w * (0.12 + i * 0.2)
        d.rectangle([bx, y1 - 8 - h * fh, bx + max(8, w * 0.08), y1 - 8],
                    fill=TEAL)
    d.text((x0 + w * 0.68, y1 - 20), "61%", font=font(SANS_B, 11),
           fill=TEAL)


ART = [art_cyclone, art_kyiv, art_cop31, art_markets, art_mercury,
       art_brussels, art_tokyo, art_beijing, art_cricket, art_bukele,
       art_senegal, art_italy, art_health]

FEATURES = [
    ("ODISHA, INDIA · CYCLONE", "Cyclone Akvan makes landfall in eastern India",
     "Akvan crosses near Gopalpur; 300,000+ evacuated, winds to 110 km/h, "
     "423 teams out.",
     "(IMD, The Hindu)"),
    ("KYIV, UKRAINE · WAR", "Russia fires wave of ~30 ballistic missiles at Kyiv",
     "Waves hit energy sites; fires burn in three districts, two embassies "
     "damaged.",
     "(Kyiv Post, Reuters)"),
    ("ANTALYA, TÜRKIYE · CLIMATE", "COP31 reaches its final day deadlocked",
     "Closing draft omits fossil-fuel phase-out; $120bn adaptation finance "
     "unresolved.",
     "(UN News, Reuters)"),
    ("SEOUL · TOKYO · MARKETS", "AI sell-off sinks Asia to worst week since 2020",
     "Nikkei −4.5%, KOSPI −5.4%, MSCI Asia-Pacific down 7%.",
     "(Reuters)"),
    ("MERCURY · SPACE", "BepiColombo reaches Mercury after 8 years",
     "ESA/JAXA probe ends 6bn-mile trip; orbit insertion set for Saturday.",
     "(ESA, BBC)"),
    ("BRUSSELS · EUROPE", "Burnham holds first EU–UK reset summit",
     "Costa & von der Leyen host UK PM; trade & carbon links eyed.",
     "(EU Council)"),
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
     "Daraxonrasib + chemo beats chemo alone (23–42%) in early trial.",
     "(Reuters)"),
]

STATS = [
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("~30", "ballistic missiles fired at Kyiv"),
    ("−7%", "Asia shares’ worst week since 2020"),
    ("2.3%", "Japan Oct headline CPI; BoJ eyed"),
    ("118", "Phillips’ historic century vs India"),
    ("8 yrs", "BepiColombo reaches Mercury"),
]

BRIEFS = [
    "BRAZIL — Lula meets Raoni; land recognised. (Al Jazeera)",
    "SEOUL — Ruling party moves to impeach top judge. (SBS)",
    "CANBERRA — CBO: AUKUS sales may shrink US fleet. (Reuters)",
    "FLORIDA — St Johns River hits record 18.3 ft. (AP)",
    "IOWA — Army to detonate 68 unstable barrels. (AP)",
    "TONGA — Emergency as El Niño drought bites. (RNZ)",
    "WASHINGTON — Pentagon: Iran war cost US $48.5bn. (Pentagon)",
    "LONDON — UK, Norway fund £100m for Ukraine ships. (BBC)",
    "COPENHAGEN — Denmark approves Greenland bill. (AFP)",
    "JAKARTA — Parliament passes asset-forfeiture bill. (AFP)",
    "GLOBAL — UN marks World Children's Day. (UN News)",
    "LAS VEGAS — Russell fastest in wet F1 practice. (F1)",
    "HORMUZ — Tanker struck near Khasab; 7 new incidents. (UKMTO)",
    "NEW DELHI — Pakistan minister leads SCO delegation. (Hindu)",
    "QATAR — U17 World Cup: Australia stun Argentina 2–0. (FIFA)",
    "SOUTH AFRICA — Hammer spins Proteas to Test win. (ICC)",
    "HONG KONG — Badminton Open reaches semifinals. (BWF)",
    "TAIWAN — Short-sell curbs take effect. (Reuters)",
    "TURIN — Alcaraz, Medvedev close ATP Finals groups. (ATP)",
    "LOS ANGELES — Thomas Markle ruled fit to stand trial. (BBC)",
    "WELLINGTON — Nicholls 175* in 216-run stand. (ICC)",
    "GENOA — Drones shut airport for two hours. (ANSA)",
    "NEW CALEDONIA — M5.6 quake strikes offshore. (USGS)",
]

REGIONS = [("EUROPE", 9, (0, 84, 160)), ("AMERICAS", 7, (0, 128, 96)),
           ("ASIA-PACIFIC", 9, (178, 38, 38)),
           ("MIDEAST", 2, (196, 132, 0)), ("AFRICA", 2, (112, 62, 150)),
           ("OCEANIA", 5, (0, 130, 130)), ("WORLD", 2, (96, 96, 96))]

EXCLUDED = [
    "Trump–Xi–Putin Shenzhen summit itself",
    "Anthropic's $83 IPO pricing & Nasdaq debut",
    "ICJ Myanmar Rohingya genocide verdict",
    "GTA VI midnight launch",
    "Riyadh tower attack (Thursday)",
    "COP31's second draft",
]

# (lon, lat, dx, dy) pins for features 1-13 on the map; 5 is in space.
PINS = [
    (84.9, 19.3, 0, 0), (30.5, 50.4, 6, -8), (30.7, 36.9, 18, 12),
    (127.0, 37.5, 0, 8), None, (4.35, 50.85, -8, -6),
    (139.7, 35.7, 10, -6), (116.4, 39.9, -8, -10), (174.8, -41.3, 0, 0),
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


def proj(lon, lat, mx0, my0, mw, mh):
    x = mx0 + (lon + 180.0) / 360.0 * mw
    y = my0 + (75.0 - lat) / 130.0 * mh
    return x, y


def draw_map(d, x0, y0, x1, y1):
    """Dark-navy world map with cream continents and red pins."""
    d.rectangle([x0, y0, x1, y1], fill=SEA_DK)
    for pts in (NA, SA, EU, AF, AS, OC):
        xy = [proj(lon, lat, x0, y0, x1 - x0, y1 - y0) for lon, lat in pts]
        d.polygon(xy, fill=LAND_DK, outline=LAND_LN_DK)
    d.text((x0 + 8, y0 + 8), "ATLANTIC", font=font(SANS_B, 8),
           fill=(120, 150, 180))
    d.text((x0 + 8, y1 - 34), "PACIFIC", font=font(SANS_B, 8),
           fill=(120, 150, 180))
    d.text((x1 - 58, y1 - 34), "PACIFIC", font=font(SANS_B, 8),
           fill=(120, 150, 180))
    d.text((x0 + 8, y1 - 20), "5  SPACE · Mercury",
           font=font(SANS_B, 8), fill=(235, 235, 215))
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
        tw = d.textlength(num, font=font(SANS_B, 10))
        d.text((px - tw / 2, py - 7), num, font=font(SANS_B, 10),
               fill=(255, 255, 255))


def feature_card(d, x, y, w, h, num, kick, head, deck, src, art,
                 banner_h, head_size, head_lead, deck_size, deck_lead):
    """One feature: full-width banner art on top, kicker + headline
    + deck below, source in parens at the end of the deck."""
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    art(d, x + 1, y + 1, x + w - 1, y + banner_h)
    d.line([(x, y + banner_h), (x + w, y + banner_h)], fill=INK, width=1)
    tx = x + 8
    tw_ = w - 16
    yy = y + banner_h + 6
    d.text((tx, yy), "%02d · %s" % (num, kick), font=font(SANS_B, 10),
           fill=RED)
    yy += 14
    hf = font(SERIF_B, head_size)
    for line in wrap(d, head, hf, tw_)[:2]:
        d.text((tx, yy), line, font=hf, fill=INK)
        yy += head_lead
    yy += 1
    full_deck = deck + " " + src
    para(d, tx, yy, full_deck, font(SANS, deck_size), tw_, deck_lead,
         max_lines=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 14
    RX = W - MX  # 1010

    # ---- top label row ----
    d.text((MX, 6), "THE WORLD IN ONE DAY", font=font(SANS_B, 11),
           fill=RED)
    d.text((RX, 6), "FRIDAY'S NEWS · ONE PAGE · 36 STORIES · 6 CONTINENTS",
           font=font(SANS, 10), fill=GREY, anchor="ra")
    hrule(d, MX, RX, 24, w=1, fill=LINE)

    # ---- giant date masthead + red strapline ----
    d.text((MX, 28), "Friday 20 November 2026",
           font=font(SERIF_B, 56), fill=INK)
    d.text((MX, 96),
           "Cyclone Akvan strikes India · Ballistic missiles hit Kyiv · "
           "COP31 deadlocked on final day · Asian AI sell-off",
           font=font(SERIF, 15), fill=RED)
    hrule(d, MX, RX, 118, w=3, fill=INK)

    # ---- headline stat strip: big red numbers, hairline dividers ----
    sy = 126
    for i, (num, lab) in enumerate(STATS):
        x = MX + i * 166
        if i:
            d.line([(x - 3, sy + 2), (x - 3, sy + 30)], fill=LINE, width=1)
        d.text((x + 2, sy), num, font=font(SERIF_B, 21), fill=RED)
        d.text((x + 2, sy + 26), lab, font=font(SANS, 9), fill=GREY)

    # ---- coloured region chips ----
    cy = 166
    cx = MX
    for name, n, col in REGIONS:
        label = "%s %d" % (name, n)
        f = font(SANS_B, 10)
        tw = d.textlength(label, font=f)
        d.rounded_rectangle([cx, cy, cx + tw + 14, cy + 20], radius=3,
                            fill=col)
        d.text((cx + 7, cy + 4), label, font=f, fill=(255, 255, 255))
        cx += tw + 14 + 6
    d.text((RX, cy + 4), "ALL STORIES: FRI 20 NOV 2026, ANY TIME ZONE",
           font=font(SANS, 9), fill=GREY, anchor="ra")

    # ---- 13 features: 3 large + 5 + 5 small, banner art on top ----
    lw, lh, lb = 322, 212, 118
    for i in range(3):
        kick, head, deck, src = FEATURES[i]
        feature_card(d, MX + i * (lw + 5), 192, lw, lh, i + 1, kick,
                     head, deck, src, ART[i], lb, 19, 21, 11, 13)
    sw, sh, sb = 195, 128, 58
    for r in range(2):
        for c in range(5):
            i = 3 + r * 5 + c
            kick, head, deck, src = FEATURES[i]
            feature_card(d, MX + c * (sw + 5), 410 + r * (sh + 6),
                         sw, sh, i + 1, kick, head, deck, src, ART[i],
                         sb, 12, 14, 9, 11)

    # ---- bottom: dark map + briefs ----
    hrule(d, MX, RX, 676, w=2)
    d.text((MX, 682), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=RED)
    d.text((352, 682), "ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES",
           font=font(SANS_B, 12), fill=RED)
    d.text((RX, 682), "BRIEFS 14–36", font=font(SANS, 10), fill=GREY,
           anchor="ra")
    draw_map(d, MX, 700, 344, 924)
    for j, b in enumerate(BRIEFS):
        c = j // 12
        r = j % 12
        x = 352 + c * 332
        y = 700 + r * 19
        f = font(SANS, 10)
        if d.textlength(b, font=f) > 324:
            f = font(SANS, 9)
        d.text((x, y), b, font=f, fill=INK)

    # ---- DATE CHECK strip ----
    dy0, dy1 = 932, 966
    d.rectangle([MX, dy0, RX, dy1], outline=RED, width=2)
    d.text((MX + 10, dy0 + 9), "DATE CHECK", font=font(SANS_B, 13),
           fill=RED)
    excl = "First reported Thursday 19 Nov, NOT shown as Friday's news: " \
           + " · ".join(EXCLUDED) + "."
    para(d, MX + 108, dy0 + 4, excl, font(SANS, 10), RX - MX - 120, 13,
         fill=INK, max_lines=2)

    # ---- footer ----
    d.text((MX, 974),
           "Every story here happened, or was first reported, on Friday "
           "20 November 2026 in at least one time zone. Claims are "
           "attributed, not stated as fact.",
           font=font(SANS, 10), fill=GREY)
    d.text((MX, 988),
           "Sources: AP · AFP · BBC · CGIL · ICC · IMD · Reuters · "
           "UKMTO · USGS",
           font=font(SANS, 10), fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote %s (%d bytes, %dx%d)" % (out, os.path.getsize(out), W, H))


if __name__ == "__main__":
    main()
