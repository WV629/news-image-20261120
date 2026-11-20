#!/usr/bin/env python3
"""Render entry.png: a one-page newspaper front page summing up
Friday 20 November 2026, drawn entirely with Pillow.

Stories are the day's verified headlines, researched on 20 Nov 2026:
the Trump-Xi-Putin "peace declaration" from Shenzhen; COP31 closing
in Antalya with its fossil-fuel language stripped out; four Russian
ballistic missiles hitting Kyiv; a Houthi strike on Riyadh's tallest
tower; Meta rethinking its 2030 net-zero target; and the first US
deep-sea mining leases. Deterministic: fixed layout, fixed palette,
no network, no timestamps. Run: python3 generate.py writes
entry.png (1024x1024) next to this file.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 242, 232)
INK = (24, 24, 24)
NAVY = (18, 42, 68)
NAVY_LT = (38, 74, 110)
RED = (178, 38, 38)
GOLD = (198, 148, 52)
GREY = (108, 105, 96)
LINE = (196, 189, 172)
SKY = (186, 210, 226)
DUSK = (52, 32, 74)
TEAL = (24, 120, 116)
SAND = (232, 214, 170)

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


def kicker(d, x, y, text, fill=RED):
    d.text((x, y), text.upper(), font=font(SANS_B, 14), fill=fill)
    return y + 20


def headline(d, x, y, text, f, max_w, leading, fill=INK):
    for line in wrap(d, text, f, max_w):
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def panel(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], outline=INK, width=2)


def flag_us(d, x, y, w=34, h=22):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK)
    for i in range(7):
        if i % 2 == 0:
            d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                        fill=(178, 38, 38))
    d.rectangle([x, y, x + w * 2 // 5, y + h * 4 // 7], fill=(30, 50, 110))


def flag_cn(d, x, y, w=34, h=22):
    d.rectangle([x, y, x + w, y + h], fill=(222, 40, 40), outline=INK)
    d.text((x + 3, y + 2), "*", font=font(SANS_B, 13), fill=(255, 220, 60))


def flag_ru(d, x, y, w=34, h=22):
    d.rectangle([x, y, x + w, y + h // 3], fill=(255, 255, 255), outline=INK)
    d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(30, 80, 180))
    d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(200, 40, 40))


def birds(d, x0, y0, x1, y1, seed, count=5):
    """Small gull strokes scattered across a sky box."""
    rnd = random.Random(seed)
    for _ in range(count):
        bx = rnd.randint(x0 + 12, x1 - 24)
        by = rnd.randint(y0 + 8, y0 + (y1 - y0) // 3)
        s = rnd.randint(5, 9)
        d.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340, fill=INK)
        d.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340, fill=INK)


def starfield(d, x0, y0, x1, y1, seed, count=22, top_frac=0.45):
    """Tiny stars across the upper part of a night box."""
    rnd = random.Random(seed)
    for _ in range(count):
        sx = rnd.randint(x0 + 6, x1 - 6)
        sy = rnd.randint(y0 + 6, y0 + int((y1 - y0) * top_frac))
        d.point((sx, sy), fill=(225, 225, 205))
        if rnd.random() < 0.3:
            d.point((sx + 1, sy), fill=(225, 225, 205))


def skyline(d, x0, y0, x1, y1, seed, fill, lit=True):
    """Randomised tower blocks along the bottom of an art box."""
    rnd = random.Random(seed)
    base = y1 - 24
    cx = x0 + 8
    while cx < x1 - 8:
        bw = rnd.randint(26, 52)
        bh = rnd.randint(34, 96)
        d.rectangle([cx, base - bh, cx + bw, base], fill=fill)
        if lit:
            for wy in range(base - bh + 8, base - 6, 12):
                for wx in range(cx + 5, cx + bw - 4, 10):
                    if rnd.random() < 0.5:
                        d.rectangle([wx, wy, wx + 4, wy + 5],
                                    fill=(250, 214, 130))
        cx += bw + 4
    d.rectangle([x0, base, x1, y1], fill=(52, 74, 52))


def draw_shenzhen(d, x0, y0, x1, y1):
    """Shenzhen at dusk: sky, low sun, towers, three flags above."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    d.ellipse([x1 - 78, y0 + 14, x1 - 34, y0 + 58], fill=(250, 214, 130))
    birds(d, x0, y0, x1, y1, 2026, count=6)
    skyline(d, x0, y0, x1, y1, 1911, NAVY_LT)
    # river reflections: short gold dashes on the green strip
    for rx in range(x0 + 14, x1 - 14, 26):
        d.line([(rx, y1 - 14), (rx + 12, y1 - 14)], fill=(250, 214, 130),
               width=2)
    for i, fl in enumerate((flag_us, flag_cn, flag_ru)):
        fx = x0 + 26 + i * 62
        d.line([(fx + 17, y0 + 12), (fx + 17, y0 + 62)], fill=INK, width=3)
        fl(d, fx, y0 + 12)


def draw_antalya(d, x0, y0, x1, y1):
    """Antalya coast: hot sun, turquoise sea, white resort blocks,
    mountains behind. The summit's final text lost its fossil-fuel
    wording, so the sun is the only thing burning here."""
    for i in range(y1 - y0):
        t = i / max(1, (y1 - y0))
        r = int(250 + (40 - 250) * t)
        g = int(214 + (150 - 214) * t)
        b = int(130 + (170 - 130) * t)
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))
    d.ellipse([x0 + 18, y0 + 10, x0 + 66, y0 + 58], fill=(255, 236, 160))
    birds(d, x0, y0, x1, y1, 1120, count=4)
    horizon = y0 + (y1 - y0) * 3 // 5
    d.rectangle([x0, horizon, x1, y1], fill=(32, 130, 140))
    for i in range(4):
        wy = horizon + 14 + i * 12
        d.line([(x0 + 10 + i * 18, wy), (x1 - 10 - i * 14, wy)],
               fill=(120, 200, 205), width=2)
    # a little sailboat crossing the bay
    bx = x0 + (x1 - x0) // 2
    by = horizon + 8
    d.polygon([(bx, by), (bx, by - 18), (bx + 14, by)], fill=(255, 255, 255))
    d.polygon([(bx - 2, by), (bx - 2, by - 12), (bx - 12, by)],
              fill=(240, 240, 235))
    d.rectangle([bx - 14, by, bx + 16, by + 4], fill=(178, 38, 38))
    # white resort blocks on the shore
    rnd = random.Random(311)
    cx = x0 + 10
    while cx < x1 - 30:
        bw = rnd.randint(30, 54)
        bh = rnd.randint(22, 44)
        d.rectangle([cx, horizon - bh, cx + bw, horizon],
                    fill=(245, 242, 234), outline=INK)
        cx += bw + 6
    # mountains behind the shore
    d.polygon([(x0, horizon), (x0 + 90, y0 + 70), (x0 + 190, horizon)],
              fill=(90, 120, 110))
    d.polygon([(x1 - 210, horizon), (x1 - 110, y0 + 56),
               (x1 - 10, horizon)], fill=(80, 108, 100))


def draw_kyiv(d, x0, y0, x1, y1):
    """Kyiv by night: dark sky, lit towers, four missile trails
    arcing down with bright heads, one burst over the rooftops."""
    d.rectangle([x0, y0, x1, y1], fill=(12, 18, 38))
    starfield(d, x0, y0, x1, y1, 1120, count=26)
    skyline(d, x0, y0, x1, y1, 77, (30, 38, 60))
    # two searchlight beams sweeping up from the rooftops
    for sx, lean in ((x0 + 70, -30), (x1 - 90, 26)):
        d.polygon([(sx, y1 - 24), (sx + 8, y1 - 24),
                   (sx + lean + 26, y0 + 10), (sx + lean + 10, y0 + 10)],
                  fill=(255, 240, 180))
    # missile trails: four arcs from the top edge
    for i, mx in enumerate((x0 + 52, x0 + 130, x0 + 210, x0 + 288)):
        top = y0 + 8 + i * 6
        bot = y1 - 62 - i * 10
        pts = []
        for s in range(11):
            t = s / 10.0
            px = mx + int(26 * t)
            py = int(top + (bot - top) * t * t)
            pts.append((px, py))
        d.line(pts, fill=(255, 180, 60), width=3)
        d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5,
                   pts[-1][0] + 5, pts[-1][1] + 5], fill=(255, 220, 120))
    # burst over the rooftops
    bx, by = x0 + 190, y1 - 66
    for r, col in ((16, (255, 200, 80)), (10, (255, 140, 40)),
                   (5, (255, 240, 180))):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col)


def draw_riyadh(d, x0, y0, x1, y1):
    """Riyadh's tallest tower at dusk, smoke curling from its crown
    after the strike, the city glowing below."""
    for i in range(y1 - y0):
        t = i / max(1, (y1 - y0))
        r = int(232 + (40 - 232) * t)
        g = int(170 + (60 - 170) * t)
        b = int(120 + (110 - 120) * t)
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))
    # crescent moon low over the desert city: a pale disc with a
    # bite taken out of it in the local sky colour
    mx, my = x1 - 52, y0 + 26
    mt = (my - y0) / max(1, (y1 - y0))
    sky_here = (int(232 + (40 - 232) * mt), int(170 + (60 - 170) * mt),
                int(120 + (110 - 120) * mt))
    d.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=(250, 240, 200))
    d.ellipse([mx - 8, my - 16, mx + 16, my + 12], fill=sky_here)
    starfield(d, x0, y0, x1, y1, 777, count=10, top_frac=0.3)
    cx = (x0 + x1) // 2
    base = y1 - 22
    # low city blocks first, so the tower stands in front of them
    skyline(d, x0, y0 + 60, x1, y1, 55, (44, 52, 72))
    d.rectangle([x0, base, x1, y1], fill=(40, 34, 30))
    # the tower: a tall pale slab with a slanted crown, bright
    # enough to stand out against the dark blocks behind it
    d.polygon([(cx - 34, base), (cx - 30, y0 + 34), (cx + 26, y0 + 22),
               (cx + 30, base)], fill=(150, 168, 198), outline=INK)
    for wy in range(y0 + 48, base - 8, 14):
        d.line([(cx - 30, wy), (cx + 28, wy)], fill=(250, 214, 130), width=2)
    # smoke curling from the crown
    for r, gy in ((20, 26), (15, 44), (11, 60)):
        d.ellipse([cx - r, y0 + gy - r, cx + r, y0 + gy + r],
                  fill=(96, 92, 86))
    d.polygon([(cx - 14, y0 + 62), (cx + 12, y0 + 62),
               (cx + 4, y0 + 42), (cx - 4, y0 + 42)], fill=(240, 140, 30))


def draw_datacentre(d, x0, y0, x1, y1):
    """A data-centre hall: rows of server racks, blinking lights,
    and one big power bolt — the appetite behind Meta's rethink."""
    d.rectangle([x0, y0, x1, y1], fill=(14, 22, 34))
    d.text((x0 + 14, y0 + 6), "AI  ·  POWER HUNGRY",
           font=font(SANS_B, 20), fill=(150, 200, 230))
    rnd = random.Random(2030)
    top = y0 + 40
    bot = y1 - 10
    for rx in range(4):
        rx0 = x0 + 12 + rx * ((x1 - x0 - 24) // 4)
        rx1 = rx0 + (x1 - x0 - 24) // 4 - 10
        d.rectangle([rx0, top, rx1, bot], fill=(28, 40, 58), outline=INK)
        for ry in range(top + 8, bot - 6, 16):
            for lx in range(rx0 + 6, rx1 - 6, 12):
                col = (60, 220, 130) if rnd.random() < 0.6 else (240, 90, 60)
                d.rectangle([lx, ry, lx + 5, ry + 5], fill=col)
    # lightning bolt over the racks, kept inside the art box
    bx = (x0 + x1) // 2
    bt = top + 2
    d.polygon([(bx + 6, bt), (bx - 9, bt + 22), (bx - 1, bt + 22),
               (bx - 6, bt + 42), (bx + 11, bt + 18), (bx + 2, bt + 18)],
              fill=(250, 214, 80))
    # cable trays running along the floor between the racks
    for cx0 in range(x0 + 12, x1 - 12, 40):
        d.line([(cx0, bot - 2), (cx0 + 18, bot - 2)], fill=(90, 110, 130),
               width=2)
        d.line([(cx0 + 9, bot - 2), (cx0 + 9, bot - 8)], fill=(90, 110, 130),
               width=2)


def draw_seabed(d, x0, y0, x1, y1):
    """The ocean in section: a mining ship on the surface, a cable
    dropping to the seabed, nodules on the floor."""
    for i in range(y1 - y0):
        t = i / max(1, (y1 - y0))
        r = int(40 + (8 - 40) * t)
        g = int(120 + (30 - 120) * t)
        b = int(160 + (60 - 160) * t)
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))
    sea = y0 + (y1 - y0) * 2 // 5
    d.rectangle([x0, sea, x1, y1], fill=(16, 60, 96))
    # ship on the surface, all of it inside the art box
    sx = x0 + 30
    d.rectangle([sx, sea - 10, sx + 120, sea], fill=(30, 40, 56))
    d.rectangle([sx + 20, sea - 22, sx + 70, sea - 10],
                fill=(240, 240, 235))
    d.line([(sx + 90, sea - 22), (sx + 90, sea - 32)], fill=INK, width=3)
    # cable down to the seabed
    cx = sx + 90
    d.line([(cx, sea), (cx + 40, y1 - 30)], fill=(200, 200, 190), width=3)
    d.rectangle([cx + 28, y1 - 44, cx + 56, y1 - 28], fill=(240, 140, 30))
    # seabed with nodules
    d.rectangle([x0, y1 - 26, x1, y1], fill=(90, 76, 60))
    rnd = random.Random(99)
    for _ in range(18):
        nx = rnd.randint(x0 + 8, x1 - 8)
        d.ellipse([nx, y1 - 30, nx + 10, y1 - 22], fill=(60, 52, 44))
    # bubbles rising
    for bx, by, br in ((cx - 60, sea + 30, 4), (cx - 40, sea + 55, 3),
                       (cx + 90, sea + 40, 5), (cx + 120, sea + 70, 3)):
        d.ellipse([bx - br, by - br, bx + br, by + br],
                  outline=(180, 220, 235), width=2)
    # small fish silhouettes drifting through the water column
    rnd = random.Random(2026)
    for _ in range(6):
        fx = rnd.randint(x0 + 16, x1 - 40)
        fy = rnd.randint(sea + 10, y1 - 32)
        fl = rnd.randint(10, 18)
        d.polygon([(fx, fy), (fx + fl, fy - 4), (fx + fl, fy + 4)],
                  fill=(140, 170, 190))
        d.polygon([(fx + fl, fy - 4), (fx + fl + 6, fy),
                   (fx + fl, fy + 4)], fill=(140, 170, 190))


def story(d, x0, y0, x1, y1, art, kick, head, deck, head_size=27):
    panel(d, x0, y0, x1, y1)
    ah = int((y1 - y0) * 0.42)
    art(d, x0 + 2, y0 + 2, x1 - 2, y0 + ah)
    tx = x0 + 12
    y = kicker(d, tx, y0 + ah + 10, kick)
    y = headline(d, tx, y, head, font(SERIF_B, head_size),
                 x1 - tx - 10, head_size + 6)
    para(d, tx, y + 4, deck, font(SANS, 15), x1 - tx - 12, 19)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.text((16, 12), "THE WORLD IN ONE PAGE",
           font=font(SERIF_B, 46), fill=(247, 242, 232))
    d.text((16, 72), "FRIDAY  20  NOVEMBER  2026",
           font=font(SANS_B, 17), fill=GOLD)
    d.text((W - 16, 72), "ONE DAY  ·  SIX STORIES  ·  ONE PAGE",
           font=font(SANS_B, 15), fill=(200, 205, 215), anchor="ra")
    hrule(d, 0, W, 110, w=3, fill=RED)

    # ---- lead: the peace declaration ----
    story(d, 16, 122, 600, 440, draw_shenzhen,
          "Shenzhen  ·  The trilateral", "THE PEACE DECLARATION",
          "Trump, Xi and Putin issue a four-point declaration after "
          "their first-ever three-way talks: UN reform, more oil, "
          "nuclear-risk dialogue. Europe answers with a call for a "
          "winter energy ceasefire.", head_size=30)

    # ---- COP31 ----
    story(d, 616, 122, 1008, 440, draw_antalya, "Antalya  ·  COP31",
          "NO FOSSIL-FUEL DEAL AT COP31",
          "COP31 closes today in Antalya, its final draft stripped "
          "of the fossil-fuel phase-out and the $120bn adaptation "
          "target.", head_size=30)

    # ---- row two ----
    story(d, 16, 456, 504, 712, draw_kyiv, "Ukraine  ·  Kyiv",
          "FOUR MISSILES HIT KYIV",
          "Russia fires four ballistic missiles at Kyiv, and Putin "
          "vows to hit back hard after the Crimean Bridge was struck "
          "a third time this week.", head_size=26)
    story(d, 520, 456, 1008, 712, draw_riyadh, "Middle East  ·  Riyadh",
          "RIYADH TOWER STRUCK",
          "A Houthi strike hits Riyadh's tallest skyscraper, home "
          "of the Saudi wealth fund, and a tanker hits a mine near "
          "the Strait of Hormuz.", head_size=26)

    # ---- row three ----
    story(d, 16, 728, 504, 932, draw_datacentre, "Tech  ·  AI power",
          "META RETHINKS NET ZERO",
          "Meta says it is \u201creevaluating\u201d its 2030 net-zero "
          "target as its AI buildout swallows ever more power.",
          head_size=26)
    story(d, 520, 728, 1008, 932, draw_seabed, "Oceans  ·  Mining",
          "AMERICA SELLS THE SEABED",
          "The US auctions its first-ever deep-sea mining leases, "
          "despite a court ruling against the sale.",
          head_size=26)

    # ---- briefs strip ----
    hrule(d, 16, 1008, 948, w=2)
    d.text((16, 958), "IN BRIEF", font=font(SANS_B, 14), fill=RED)
    briefs = ("Somalia expels the UAE ambassador  ·  Fiona the hippo "
              "dies at Cincinnati Zoo  ·  Trump says he will meet Kim "
              "Jong-un  ·  Israel ends its Gaza ground operation")
    para(d, 16, 980, briefs, font(SANS, 12), 992, 16, fill=(70, 68, 62))

    # ---- footer ----
    d.text((16, 1008), "All stories first reported Friday 20 November 2026",
           font=font(SANS, 12), fill=GREY)
    d.text((1008, 1008), "Sources: AP · BBC · NYT · Reuters",
           font=font(SANS, 12), fill=GREY, anchor="ra")

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote %s (%d bytes, %dx%d)" % (out, os.path.getsize(out), W, H))


if __name__ == "__main__":
    main()
