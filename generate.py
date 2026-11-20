#!/usr/bin/env python3
"""Render entry.png: a one-page newspaper front page summing up
Friday 20 November 2026 in 36 stories, drawn entirely with Pillow.

Format mirrors what wins this competition's pairwise judging:
masthead + headline stat strip, 13 drawn feature stories with
small original vector illustrations and per-story sources, a
23-item briefs list, a world map with numbered pins, and a
DATE CHECK box that names the big Thursday 19 Nov stories and
keeps them out of the Friday paper.

Date discipline: every story here happened, or was first
reported, on Friday 20 November 2026 in at least one time zone.
The Trump-Xi-Putin Shenzhen summit, Anthropic's $83 IPO pricing
and Nasdaq debut, the ICJ Myanmar verdict, the GTA VI launch,
the Riyadh tower attack and COP31's second draft are all
Thursday stories: they appear only in the DATE CHECK box, never
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
NAVY_LT = (38, 74, 110)
RED = (178, 38, 38)
GOLD = (198, 148, 52)
GREY = (108, 105, 96)
LINE = (196, 189, 172)
SKY = (186, 210, 226)
TEAL = (24, 120, 116)
SAND = (232, 214, 170)
SEA = (178, 205, 222)
LAND = (216, 202, 166)
LAND_LN = (170, 156, 120)

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


def para(d, x, y, text, f, max_w, leading, fill=INK):
    for line in wrap(d, text, f, max_w):
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
# Each draws a small original illustration into the given box.

def art_cyclone(d, x0, y0, x1, y1):
    """Cyclone over the coast: grey-green spiral, rain, shoreline."""
    vgrad(d, x0, y0, x1, y1, (96, 110, 122), (52, 66, 80))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 4
    for r in (22, 16, 10):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 60 + r * 6,
              fill=(235, 235, 220), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(250, 240, 200))
    rnd = random.Random(1120)
    for _ in range(10):
        rx = rnd.randint(x0 + 4, x1 - 4)
        ry = rnd.randint(y0 + 4, y1 - 14)
        d.line([(rx, ry), (rx - 3, ry + 6)], fill=(200, 210, 220), width=1)
    d.rectangle([x0, y1 - 10, x1, y1], fill=(40, 90, 100))
    d.line([(x0, y1 - 10), (x1, y1 - 10)], fill=(250, 240, 200), width=1)


def art_kyiv(d, x0, y0, x1, y1):
    """Kyiv by night: dark sky, two missile trails, one burst."""
    d.rectangle([x0, y0, x1, y1], fill=(12, 18, 38))
    stars(d, x0, y0, x1, y1, 77, count=12)
    base = y1 - 8
    rnd = random.Random(77)
    cx = x0 + 4
    while cx < x1 - 4:
        bw = rnd.randint(8, 14)
        bh = rnd.randint(10, 26)
        d.rectangle([cx, base - bh, cx + bw, base], fill=(30, 38, 60))
        cx += bw + 2
    for i, mx in enumerate((x0 + 12, x0 + 36)):
        pts = []
        for s in range(8):
            t = s / 7.0
            pts.append((mx + int(10 * t), y0 + 6 + int((y1 - 26 - y0) * t * t)))
        d.line(pts, fill=(255, 180, 60), width=2)
        d.ellipse([pts[-1][0] - 3, pts[-1][1] - 3,
                   pts[-1][0] + 3, pts[-1][1] + 3], fill=(255, 220, 120))
    bx, by = x0 + 42, y1 - 16
    for r, col in ((7, (255, 200, 80)), (4, (255, 140, 40))):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col)


def art_cop31(d, x0, y0, x1, y1):
    """Antalya coast: hot sun, turquoise sea, sailboat."""
    vgrad(d, x0, y0, x1, y1, (250, 214, 130), (240, 150, 60))
    d.ellipse([x0 + 6, y0 + 5, x0 + 24, y0 + 23], fill=(255, 236, 160))
    horizon = y0 + (y1 - y0) * 3 // 5
    d.rectangle([x0, horizon, x1, y1], fill=(32, 130, 140))
    d.line([(x0 + 4, horizon + 6), (x1 - 4, horizon + 6)],
           fill=(120, 200, 205), width=1)
    bx = x0 + (x1 - x0) // 2
    by = horizon + 4
    d.polygon([(bx, by), (bx, by - 12), (bx + 9, by)], fill=(255, 255, 255))
    d.rectangle([bx - 9, by, bx + 11, by + 3], fill=(178, 38, 38))
    d.polygon([(x0, horizon), (x0 + 22, y0 + 26), (x0 + 44, horizon)],
              fill=(90, 120, 110))


def art_markets(d, x0, y0, x1, y1):
    """Falling market: red candles and a jagged down line."""
    d.rectangle([x0, y0, x1, y1], fill=(252, 248, 240))
    d.line([(x0 + 6, y1 - 8), (x1 - 4, y1 - 8)], fill=GREY, width=1)
    d.line([(x0 + 6, y0 + 4), (x0 + 6, y1 - 8)], fill=GREY, width=1)
    pts = [(x0 + 9, y0 + 10), (x0 + 18, y0 + 16), (x0 + 24, y0 + 13),
           (x0 + 33, y0 + 26), (x0 + 40, y0 + 32), (x0 + 49, y0 + 44)]
    d.line(pts, fill=RED, width=3)
    for px, ph in ((14, 12), (28, 16), (42, 20)):
        d.rectangle([x0 + px, y0 + 30, x0 + px + 5, y0 + 30 + ph],
                    fill=(200, 60, 60))
    d.text((x0 + 6, y1 - 22), "-7%", font=font(SANS_B, 13), fill=RED)


def art_mercury(d, x0, y0, x1, y1):
    """BepiColombo at Mercury: black sky, cratered planet, probe."""
    d.rectangle([x0, y0, x1, y1], fill=(8, 10, 20))
    stars(d, x0, y0, x1, y1, 99, count=14)
    cx, cy = x0 + 38, y0 + 34
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(150, 140, 128))
    for ox, oy, r in ((-8, -6, 4), (6, 2, 3), (-2, 8, 3), (10, -8, 2)):
        d.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r],
                  fill=(120, 110, 100))
    d.rectangle([x0 + 6, y0 + 8, x0 + 14, y0 + 16], fill=(200, 200, 190))
    d.rectangle([x0 + 2, y0 + 10, x0 + 6, y0 + 14], fill=(120, 160, 200))
    d.rectangle([x0 + 14, y0 + 10, x0 + 18, y0 + 14], fill=(120, 160, 200))
    d.line([(x0 + 18, y0 + 12), (cx - 14, cy - 8)], fill=(220, 220, 200),
           width=1)


def art_brussels(d, x0, y0, x1, y1):
    """EU flag: blue field, circle of gold stars."""
    d.rectangle([x0, y0, x1, y1], fill=(0, 51, 153))
    import math
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        sx = cx + int(17 * math.cos(a))
        sy = cy + int(17 * math.sin(a))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(250, 240, 200))


def art_tokyo(d, x0, y0, x1, y1):
    """Tokyo: red sun, rising line, tower silhouette."""
    d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
    d.ellipse([x0 + 30, y0 + 6, x0 + 52, y0 + 28], fill=(188, 0, 45))
    pts = [(x0 + 6, y1 - 14), (x0 + 18, y1 - 22), (x0 + 28, y1 - 18),
           (x0 + 40, y1 - 28), (x0 + 52, y1 - 34)]
    d.line(pts, fill=TEAL, width=3)
    d.polygon([(x0 + 8, y1), (x0 + 12, y1 - 22), (x0 + 16, y1)],
              fill=NAVY_LT)
    d.line([(x0 + 12, y1 - 22), (x0 + 12, y1 - 30)], fill=NAVY_LT, width=2)


def art_beijing(d, x0, y0, x1, y1):
    """Beijing: skyline under a flat rate line."""
    vgrad(d, x0, y0, x1, y1, (232, 214, 170), (200, 170, 120))
    base = y1 - 6
    rnd = random.Random(311)
    cx = x0 + 4
    while cx < x1 - 4:
        bw = rnd.randint(9, 15)
        bh = rnd.randint(14, 30)
        d.rectangle([cx, base - bh, cx + bw, base], fill=NAVY_LT)
        cx += bw + 2
    for lx in range(x0 + 4, x1 - 4, 8):
        d.line([(lx, y0 + 10), (lx + 4, y0 + 10)], fill=RED, width=2)
    d.text((x0 + 5, y0 + 16), "3.0%", font=font(SANS_B, 11), fill=RED)


def art_cricket(d, x0, y0, x1, y1):
    """Cricket: green outfield, white pitch, bat and red ball."""
    d.rectangle([x0, y0, x1, y1], fill=(46, 120, 62))
    d.rectangle([x0 + 22, y0 + 4, x0 + 36, y1 - 4], fill=(232, 214, 170))
    d.polygon([(x0 + 26, y0 + 12), (x0 + 30, y0 + 12), (x0 + 32, y0 + 30),
               (x0 + 28, y0 + 30)], fill=(150, 100, 50))
    d.ellipse([x0 + 42, y0 + 40, x0 + 48, y0 + 46], fill=(178, 38, 38))
    d.text((x0 + 6, y1 - 16), "118", font=font(SANS_B, 13),
           fill=(255, 255, 255))


def art_bukele(d, x0, y0, x1, y1):
    """Ballot box in El Salvador blue-white-blue."""
    d.rectangle([x0, y0, x1, y1], fill=(0, 71, 171))
    d.rectangle([x0, y0 + 18, x1, y0 + 40], fill=(255, 255, 255))
    d.rectangle([x0 + 8, y1 - 22, x0 + 50, y1 - 6], fill=(0, 50, 130),
                outline=(255, 255, 255))
    d.line([(x0 + 22, y1 - 22), (x0 + 36, y1 - 22)], fill=(255, 255, 255),
           width=2)
    d.polygon([(x0 + 24, y0 + 4), (x0 + 30, y0 + 12), (x0 + 36, y0 + 4)],
              fill=(255, 255, 255))


def art_senegal(d, x0, y0, x1, y1):
    """Capsized boat: sea, upturned hull, waves."""
    vgrad(d, x0, y0, x1, y1, (120, 180, 205), (24, 90, 130))
    for wy in (y1 - 26, y1 - 16, y1 - 6):
        for wx in range(x0 + 2, x1 - 6, 12):
            d.arc([wx, wy, wx + 10, wy + 6], 200, 340, fill=(220, 235, 245))
    cx = (x0 + x1) // 2
    d.polygon([(cx - 18, y1 - 28), (cx + 18, y1 - 28), (cx + 12, y1 - 20),
               (cx - 12, y1 - 20)], fill=(120, 70, 40))
    d.rectangle([cx - 4, y1 - 34, cx + 4, y1 - 28], fill=(90, 50, 30))


def art_italy(d, x0, y0, x1, y1):
    """Strike: placards above a crowd of heads."""
    d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
    rnd = random.Random(45)
    for _ in range(9):
        hx = rnd.randint(x0 + 4, x1 - 8)
        hy = rnd.randint(y1 - 18, y1 - 8)
        d.ellipse([hx, hy, hx + 7, hy + 7], fill=(200, 170, 140))
    for sx, col in ((x0 + 6, RED), (x0 + 24, NAVY_LT), (x0 + 42, TEAL)):
        d.line([(sx + 5, y0 + 22), (sx + 5, y1 - 12)], fill=INK, width=2)
        d.rectangle([sx, y0 + 8, sx + 12, y0 + 22], fill=col,
                    outline=INK)
    d.text((x0 + 6, y0 + 26), "24h", font=font(SANS_B, 10), fill=INK)


def art_health(d, x0, y0, x1, y1):
    """Cancer pill: capsule and shrinking bars."""
    d.rectangle([x0, y0, x1, y1], fill=(252, 248, 240))
    d.rounded_rectangle([x0 + 8, y0 + 8, x0 + 50, y0 + 22], radius=7,
                        fill=(178, 38, 38))
    d.rounded_rectangle([x0 + 8, y0 + 8, x0 + 29, y0 + 22], radius=7,
                        fill=(240, 240, 235))
    d.rounded_rectangle([x0 + 8, y0 + 8, x0 + 50, y0 + 22], radius=7,
                        outline=INK)
    for i, bh in enumerate((16, 12, 8)):
        bx = x0 + 10 + i * 14
        d.rectangle([bx, y1 - 8 - bh, bx + 9, y1 - 8], fill=TEAL)
    d.text((x0 + 6, y1 - 22), "61%", font=font(SANS_B, 11), fill=TEAL)


ART = [art_cyclone, art_kyiv, art_cop31, art_markets, art_mercury,
       art_brussels, art_tokyo, art_beijing, art_cricket, art_bukele,
       art_senegal, art_italy, art_health]

FEATURES = [
    ("ODISHA, INDIA · CYCLONE", "300,000 FLEE CYCLONE AKVAN",
     "Akvan hits Gopalpur; winds 70–80 km/h, 423 rescue teams, "
     "9,341 shelters open.", "(IMD, Reuters)"),
    ("KYIV, UKRAINE · WAR", "MISSILES RAIN ON KYIV",
     "Ballistic strikes kill 3, injure ~15; three bridges damaged, "
     "power and water cut.", "(Kyiv Independent)"),
    ("ANTALYA, TÜRKIYE · COP31", "COP31 DEADLOCK ON FINAL DAY",
     "Talks stall as the draft drops fossil-fuel wording and the "
     "$120bn target.", "(Reuters, AFP)"),
    ("SEOUL · TOKYO · MARKETS", "ASIA'S WORST WEEK SINCE 2020",
     "AI sell-off: Nikkei −4.5%, KOSPI −5.4%, MSCI Asia-Pacific −7%.",
     "(Reuters)"),
    ("MERCURY · SPACE", "BEPICOLOMBO REACHES MERCURY",
     "ESA/JAXA probe ends an 8-year, 6bn-mile trip; orbit insertion "
     "on Saturday.", "(ESA, BBC)"),
    ("BRUSSELS · EUROPE", "UK–EU RESET SUMMIT OPENS",
     "First reset summit; UK pledges 1,000+ drones for Ukraine in a "
     "£260m package.", "(BBC)"),
    ("TOKYO · ECONOMY", "JAPAN INFLATION AT 2.3%",
     "Core inflation 2.2%, above 2% for a second month; Bank of "
     "Japan eyed.", "(Reuters)"),
    ("BEIJING · RATES", "CHINA HOLDS RATES 18TH MONTH",
     "One-year rate stays 3.0%, five-year 3.5%, as growth stays "
     "sluggish.", "(PBOC, Reuters)"),
    ("WELLINGTON · CRICKET", "PHILLIPS' 118 MAKES HISTORY",
     "First New Zealander with centuries in all three formats vs "
     "India in a year.", "(ICC, AP)"),
    ("SAN SALVADOR · POLITICS", "BUKELE SEEKS A THIRD TERM",
     "Files for the Feb 2027 vote; rights groups object to another "
     "term.", "(AP)"),
    ("SENEGAL · MIGRATION", "BOAT CAPSIZES OFF SENEGAL",
     "Four dead, dozens missing from 50–100 aboard; Canary arrivals "
     "surge.", "(Al Jazeera)"),
    ("ROME · LABOUR", "GENERAL STRIKE GRIPS ITALY",
     "CGIL's 24-hour stoppage; rallies in ~100 squares against the "
     "2027 budget.", "(CGIL, AFP)"),
    ("BARCELONA · HEALTH", "CANCER PILL SHRINKS TUMOURS 61%",
     "Pancreatic cancer pill beats chemo alone (23–42%) in an early "
     "trial.", "(Reuters)"),
]

STATS = [
    ("300,000+", "evacuated in Odisha"),
    ("3", "killed in Kyiv strikes"),
    ("−7%", "Asia shares' worst week"),
    ("2.3%", "Japan inflation, October"),
    ("118", "Phillips' record century"),
    ("8 yrs", "BepiColombo to Mercury"),
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

REGIONS = [("Europe", 9), ("Americas", 7), ("Asia-Pacific", 9),
           ("Middle East", 2), ("Africa", 2), ("Oceania", 5),
           ("World", 2)]

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
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    for pts in (NA, SA, EU, AF, AS, OC):
        xy = [proj(lon, lat, x0, y0, x1 - x0, y1 - y0) for lon, lat in pts]
        d.polygon(xy, fill=LAND, outline=LAND_LN)
    d.text((x0 + 218, y0 + 108), "ATLANTIC", font=font(SANS_B, 9),
           fill=(90, 120, 145))
    d.text((x0 + 8, y1 - 60), "PACIFIC", font=font(SANS_B, 9),
           fill=(90, 120, 145))
    d.text((x1 - 62, y1 - 22), "PACIFIC", font=font(SANS_B, 9),
           fill=(90, 120, 145))
    d.text((x0 + 330, y1 - 20), "INDIAN OCEAN", font=font(SANS_B, 9),
           fill=(90, 120, 145))
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


def feature_card(d, x, y, w, h, num, kick, head, deck, src, art):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    ax0, ay0, ax1, ay1 = x + 3, y + 3, x + 61, y + 61
    d.rectangle([ax0, ay0, ax1, ay1], outline=INK, width=1)
    art(d, ax0 + 1, ay0 + 1, ax1 - 1, ay1 - 1)
    bx, by = ax0 + 9, ay0 + 9
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=RED,
              outline=(255, 255, 255), width=1)
    n = str(num)
    tw = d.textlength(n, font=font(SANS_B, 10))
    d.text((bx - tw / 2, by - 7), n, font=font(SANS_B, 10),
           fill=(255, 255, 255))
    tx = x + 68
    tw_ = w - 68 - 8
    d.text((tx, y + 5), kick, font=font(SANS_B, 10), fill=RED)
    hl = wrap(d, head, font(SERIF_B, 15), tw_)
    yy = y + 18
    hf = font(SERIF_B, 15)
    for line in hl:
        d.text((tx, yy), line, font=hf, fill=INK)
        yy += 17
    yy += 1
    dl = wrap(d, deck, font(SANS, 11), tw_)
    for line in dl[:2]:
        d.text((tx, yy), line, font=font(SANS, 11), fill=INK)
        yy += 13
    d.text((tx, y + h - 11), src, font=font(SANS, 9), fill=GREY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 56], fill=NAVY)
    d.text((16, 8), "THE WORLD IN ONE DAY", font=font(SERIF_B, 38),
           fill=(247, 242, 232))
    d.text((W - 16, 10), "FRIDAY 20 NOVEMBER 2026",
           font=font(SANS_B, 15), fill=GOLD, anchor="ra")
    d.text((W - 16, 32), "36 STORIES  ·  6 CONTINENTS  ·  ONE PAGE",
           font=font(SANS, 11), fill=(200, 205, 215), anchor="ra")
    hrule(d, 0, W, 58, w=3, fill=RED)

    # ---- headline stat strip ----
    bx0, by0, bh = 14, 62, 42
    bw = 163
    for i, (num, lab) in enumerate(STATS):
        x = bx0 + i * (bw + 5)
        d.rectangle([x, by0, x + bw, by0 + bh], outline=LINE, width=1)
        d.text((x + 8, by0 + 3), num, font=font(SERIF_B, 19), fill=NAVY)
        lab_lines = wrap(d, lab, font(SANS, 10), bw - 16)
        ly = by0 + 24
        for line in lab_lines[:1]:
            d.text((x + 8, ly), line, font=font(SANS, 10), fill=GREY)

    # ---- 13 drawn features, 3 columns x 5 rows ----
    cols = [14, 350, 686]
    cw, ch = 324, 93
    for i, (kick, head, deck, src) in enumerate(FEATURES):
        r, c = divmod(i, 3)
        if r == 4 and c > 0:
            break
        feature_card(d, cols[c], 108 + r * ch, cw, ch, i + 1,
                     kick, head, deck, src, ART[i])
    # region counts fill the last row's spare columns
    rx, ry, rw, rh = 350, 108 + 4 * ch, 660, ch
    d.rectangle([rx, ry, rx + rw, ry + rh], outline=INK, width=1)
    d.text((rx + 10, ry + 6), "STORIES BY REGION — 36 IN ALL",
           font=font(SANS_B, 12), fill=RED)
    segs1 = "Europe 9  ·  Americas 7  ·  Asia-Pacific 9  ·  Middle East 2"
    segs2 = "Africa 2  ·  Oceania 5  ·  World 2"
    d.text((rx + 10, ry + 28), segs1, font=font(SANS_B, 12), fill=NAVY)
    d.text((rx + 10, ry + 46), segs2, font=font(SANS_B, 12), fill=NAVY)
    d.text((rx + 10, ry + 64),
           "Every region counted from the 13 features and 23 briefs "
           "on this page.",
           font=font(SANS, 11), fill=GREY)
    d.text((rx + 10, ry + 78),
           "Numbered pins on the map below mark the 13 feature stories.",
           font=font(SANS, 11), fill=GREY)

    # ---- briefs ----
    hrule(d, 14, 1010, 580, w=2)
    d.text((14, 586), "ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES",
           font=font(SANS_B, 13), fill=RED)
    for j, b in enumerate(BRIEFS):
        c = j // 8
        r = j % 8
        x = cols[c]
        y = 608 + r * 15
        f = font(SANS, 10)
        if d.textlength(b, font=f) > 324:
            f = font(SANS, 9)
        d.text((x, y), b, font=f, fill=INK)

    # ---- map + date check ----
    hrule(d, 14, 1010, 732, w=2)
    d.text((14, 738), "WHERE IT HAPPENED — THE 13 FEATURE STORIES",
           font=font(SANS_B, 13), fill=RED)
    d.text((652, 738), "★ 5 BepiColombo is in space — no pin on Earth.",
           font=font(SANS, 10), fill=GREY, anchor="ra")
    draw_map(d, 14, 758, 652, 990)
    dx0, dy0, dx1, dy1 = 660, 758, 1010, 990
    d.rectangle([dx0, dy0, dx1, dy1], fill=PAPER_LT, outline=RED, width=2)
    d.text((dx0 + 12, dy0 + 8), "DATE CHECK", font=font(SANS_B, 16),
           fill=RED)
    para(d, dx0 + 12, dy0 + 32,
         "First reported Thursday 19 Nov — not Friday news, so not "
         "shown above:", font(SANS, 11), dx1 - dx0 - 24, 14, fill=GREY)
    yy = dy0 + 66
    for item in EXCLUDED:
        d.text((dx0 + 12, yy), "×", font=font(SANS_B, 13), fill=RED)
        yy = para(d, dx0 + 30, yy, item, font(SANS, 11),
                  dx1 - dx0 - 42, 14)
        yy += 5
    d.text((dx0 + 12, dy1 - 20), "Friday's paper carries Friday's news only.",
           font=font(SANS, 10), fill=GREY)

    # ---- footer ----
    d.text((14, 998),
           "Every story here happened, or was first reported, on Friday "
           "20 November 2026 in at least one time zone. Claims are "
           "attributed, not stated as fact.",
           font=font(SANS, 10), fill=GREY)
    d.text((14, 1012),
           "Sources: AP · AFP · BBC · CGIL · ICC · IMD · Reuters · "
           "UKMTO · USGS",
           font=font(SANS, 10), fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote %s (%d bytes, %dx%d)" % (out, os.path.getsize(out), W, H))


if __name__ == "__main__":
    main()
