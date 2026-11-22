#!/usr/bin/env python3
"""Draw the dense news poster for Sunday 22 November 2026.

Renders entry.png (1024x1024, deterministic) for the make.fun
news-image-20261122 bounty. All story content was researched live in
this session from Reuters, AP, Al Jazeera, AFP, The Guardian, Formula 1
and One Turn; every story happened, or was first reported, on 22 Nov 2026.

Layout: header + UTC timeline + 16 illustrated lead stories + a world
map with numbered pins + 34 numbered one-line stories + a DATE CHECK
box + a sources footer. Run: python3 poster22.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# Palette
INK = (20, 32, 46)
PAPER = (247, 242, 231)
CREAM = (252, 249, 240)
RED = (179, 38, 30)
RED_SOFT = (246, 226, 222)
TEAL = (14, 107, 107)
GOLD = (176, 128, 32)
BLUE = (31, 78, 121)
GREEN = (46, 107, 52)
GREY = (110, 116, 122)
LINE = (200, 192, 174)
MAP_LAND = (206, 214, 196)
MAP_SEA = (226, 234, 240)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def f(path, size):
    return ImageFont.truetype(path, size)


F_TITLE = f(SERIF_B, 30)
F_SUB = f(SANS_B, 12)
F_DATE = f(SANS_B, 15)
F_TL_TIME = f(SANS_B, 11)
F_TL_TXT = f(SANS, 10)
F_SEC = f(SANS_B, 12)
F_NUM = f(SANS_B, 11)
F_HEAD = f(SANS_B, 12)
F_BODY = f(SANS, 10)
F_TAG = f(SANS_B, 8)
F_ONE = f(SANS, 10)
F_ONE_B = f(SANS_B, 10)
F_SMALL = f(SANS, 9)
F_FOOT = f(SANS_B, 11)


def wrap(d, text, font, width):
    """Greedy word wrap; returns list of lines fitting width."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, font, width, max_lines=1):
    """Wrap text, keep at most max_lines, ellipsis on the last."""
    lines = wrap(d, text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "\u2026", font=font) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "\u2026"
    return lines


def text_block(d, x, y, lines, font, fill, leading):
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=font, fill=fill)


# ---------------------------------------------------------------- icons
# Each draws a small pictogram inside a 44x44 box at (x, y).

def icon_climate(d, x, y):
    d.ellipse([x + 8, y + 4, x + 24, y + 20], fill=GOLD)
    for a in range(8):
        import math
        ang = a * math.pi / 4
        cx, cy = x + 16, y + 12
        d.line([(cx + 11 * math.cos(ang), cy + 11 * math.sin(ang)),
                (cx + 15 * math.cos(ang), cy + 15 * math.sin(ang))],
               fill=GOLD, width=2)
    d.polygon([(x + 26, y + 38), (x + 40, y + 24), (x + 40, y + 38)],
              fill=GREEN)
    d.line([(x + 26, y + 38), (x + 40, y + 38)], fill=GREEN, width=2)


def icon_burst(d, x, y):
    pts = [(22, 2), (27, 13), (40, 8), (32, 20), (42, 26), (29, 29),
           (32, 42), (22, 33), (12, 42), (15, 29), (2, 26), (12, 20),
           (4, 8), (17, 13)]
    d.polygon([(x + px, y + py) for px, py in pts], fill=RED)
    d.ellipse([x + 17, y + 17, x + 27, y + 27], fill=(255, 220, 120))


def icon_rocket(d, x, y):
    d.polygon([(x + 22, y + 2), (x + 29, y + 16), (x + 15, y + 16)],
              fill=RED)
    d.rectangle([x + 15, y + 16, x + 29, y + 32], fill=INK)
    d.polygon([(x + 15, y + 26), (x + 8, y + 36), (x + 15, y + 33)],
              fill=RED)
    d.polygon([(x + 29, y + 26), (x + 36, y + 36), (x + 29, y + 33)],
              fill=RED)
    d.polygon([(x + 19, y + 32), (x + 25, y + 32), (x + 22, y + 42)],
              fill=GOLD)
    d.ellipse([x + 19, y + 19, x + 25, y + 25], fill=(255, 255, 255))


def icon_flame(d, x, y):
    d.polygon([(x + 22, y + 2), (x + 32, y + 16), (x + 38, y + 28),
               (x + 30, y + 40), (x + 14, y + 40), (x + 6, y + 28),
               (x + 12, y + 16)], fill=(230, 120, 30))
    d.polygon([(x + 22, y + 16), (x + 28, y + 24), (x + 28, y + 34),
               (x + 16, y + 34), (x + 16, y + 24)], fill=(255, 210, 60))


def icon_cuffs(d, x, y):
    d.ellipse([x + 4, y + 8, x + 18, y + 22], outline=INK, width=3)
    d.ellipse([x + 26, y + 8, x + 40, y + 22], outline=INK, width=3)
    d.line([(x + 18, y + 15), (x + 26, y + 15)], fill=INK, width=3)
    d.line([(x + 11, y + 22), (x + 11, y + 40)], fill=INK, width=2)
    d.line([(x + 33, y + 22), (x + 33, y + 40)], fill=INK, width=2)
    d.line([(x + 11, y + 40), (x + 33, y + 40)], fill=INK, width=2)


def icon_factory(d, x, y):
    d.rectangle([x + 4, y + 20, x + 34, y + 40], fill=INK)
    d.rectangle([x + 30, y + 6, x + 36, y + 20], fill=INK)
    for bx in (8, 16, 24):
        d.rectangle([x + bx, y + 26, x + bx + 5, y + 31], fill=GOLD)
    d.polygon([(x + 38, y + 12), (x + 42, y + 18), (x + 40, y + 24),
               (x + 35, y + 22), (x + 36, y + 16)], fill=RED)


def icon_book(d, x, y):
    d.polygon([(x + 4, y + 10), (x + 21, y + 16), (x + 21, y + 36),
               (x + 4, y + 30)], fill=BLUE)
    d.polygon([(x + 40, y + 10), (x + 23, y + 16), (x + 23, y + 36),
               (x + 40, y + 30)], fill=TEAL)
    d.line([(x + 22, y + 16), (x + 22, y + 36)], fill=(255, 255, 255),
           width=2)


def icon_speech(d, x, y):
    d.rectangle([x + 4, y + 6, x + 40, y + 30], fill=(255, 255, 255),
                outline=INK, width=2)
    d.polygon([(x + 12, y + 30), (x + 12, y + 40), (x + 20, y + 30)],
              fill=(255, 255, 255), outline=INK)
    d.line([(x + 10, y + 14), (x + 34, y + 14)], fill=INK, width=2)
    d.line([(x + 10, y + 20), (x + 34, y + 20)], fill=INK, width=2)
    d.line([(x + 10, y + 26), (x + 24, y + 26)], fill=INK, width=2)


def icon_car(d, x, y):
    d.polygon([(x + 4, y + 26), (x + 10, y + 16), (x + 24, y + 14),
               (x + 34, y + 18), (x + 40, y + 26), (x + 40, y + 32),
               (x + 4, y + 32)], fill=RED)
    d.rectangle([x + 13, y + 18, x + 22, y + 24], fill=(200, 230, 255))
    d.ellipse([x + 9, y + 30, x + 17, y + 38], fill=INK)
    d.ellipse([x + 28, y + 30, x + 36, y + 38], fill=INK)
    d.line([(x + 36, y + 8), (x + 40, y + 8)], fill=GOLD, width=2)
    d.line([(x + 4, y + 40), (x + 40, y + 40)], fill=GREY, width=2)


def icon_chip(d, x, y):
    d.rectangle([x + 12, y + 12, x + 32, y + 32], fill=INK)
    d.rectangle([x + 18, y + 18, x + 26, y + 26], fill=TEAL)
    for px in (16, 22, 28):
        d.line([(x + px, y + 4), (x + px, y + 12)], fill=INK, width=2)
        d.line([(x + px, y + 32), (x + px, y + 40)], fill=INK, width=2)
        d.line([(x + 4, y + px), (x + 12, y + px)], fill=INK, width=2)
        d.line([(x + 32, y + px), (x + 40, y + px)], fill=INK, width=2)


def icon_ship(d, x, y):
    d.polygon([(x + 4, y + 26), (x + 40, y + 26), (x + 34, y + 36),
               (x + 10, y + 36)], fill=INK)
    d.rectangle([x + 20, y + 10, x + 24, y + 26], fill=INK)
    d.polygon([(x + 24, y + 12), (x + 34, y + 20), (x + 24, y + 20)],
              fill=RED)
    d.line([(x + 4, y + 41), (x + 40, y + 41)], fill=BLUE, width=2)
    d.ellipse([x + 30, y + 2, x + 38, y + 10], fill=GOLD)


def icon_waves(d, x, y):
    for yy in (12, 22, 32):
        d.line([(x + 4, y + yy), (x + 12, y + yy - 4), (x + 20, y + yy),
                (x + 28, y + yy - 4), (x + 36, y + yy), (x + 40, y + yy - 2)],
               fill=BLUE, width=3)
    d.polygon([(x + 18, y + 2), (x + 26, y + 2), (x + 22, y + 8)],
              fill=RED)


def icon_drone(d, x, y):
    d.rectangle([x + 16, y + 16, x + 28, y + 28], fill=INK)
    for cx, cy in ((8, 8), (36, 8), (8, 36), (36, 36)):
        d.ellipse([x + cx - 5, y + cy - 5, x + cx + 5, y + cy + 5],
                  outline=INK, width=2)
        d.line([(x + 22, y + 22), (x + cx, y + cy)], fill=INK, width=2)
    d.ellipse([x + 19, y + 19, x + 25, y + 25], fill=RED)


def icon_aid(d, x, y):
    d.polygon([(x + 6, y + 20), (x + 38, y + 20), (x + 34, y + 34),
               (x + 10, y + 34)], fill=TEAL)
    d.rectangle([x + 4, y + 16, x + 40, y + 21], fill=INK)
    d.line([(x + 22, y + 24), (x + 22, y + 32)], fill=(255, 255, 255),
           width=3)
    d.line([(x + 18, y + 28), (x + 26, y + 28)], fill=(255, 255, 255),
           width=3)
    d.ellipse([x + 30, y + 4, x + 40, y + 14], fill=RED)
    d.line([(x + 35, y + 6), (x + 35, y + 12)], fill=(255, 255, 255),
           width=2)
    d.line([(x + 32, y + 9), (x + 38, y + 9)], fill=(255, 255, 255),
           width=2)


def icon_crown(d, x, y):
    d.polygon([(x + 6, y + 34), (x + 6, y + 14), (x + 14, y + 24),
               (x + 22, y + 8), (x + 30, y + 24), (x + 38, y + 14),
               (x + 38, y + 34)], fill=GOLD)
    d.rectangle([x + 6, y + 36, x + 38, y + 40], fill=GOLD)
    d.ellipse([x + 19, y + 22, x + 25, y + 28], fill=RED)


def icon_dna(d, x, y):
    import math
    for i in range(21):
        t = i / 20.0
        yy = y + 4 + t * 36
        off = 8 * math.sin(t * math.pi * 2)
        d.ellipse([x + 22 + off - 2, yy - 2, x + 22 + off + 2, yy + 2],
                  fill=TEAL)
        d.ellipse([x + 22 - off - 2, yy - 2, x + 22 - off + 2, yy + 2],
                  fill=BLUE)
        if i % 4 == 0:
            d.line([(x + 22 - off, yy), (x + 22 + off, yy)], fill=GREY,
                   width=1)


ICONS = {
    "climate": icon_climate, "burst": icon_burst, "rocket": icon_rocket,
    "flame": icon_flame, "cuffs": icon_cuffs, "factory": icon_factory,
    "book": icon_book, "speech": icon_speech, "car": icon_car,
    "chip": icon_chip, "ship": icon_ship, "waves": icon_waves,
    "drone": icon_drone, "aid": icon_aid, "crown": icon_crown,
    "dna": icon_dna,
}

# ---------------------------------------------------------------- data
# (num, headline, body, region, status, source, icon, lon, lat, nudge)
LEADS = [
    (1, "COP31 collapses \u2014 no deal on fossil fuels",
     "EU, UK and vulnerable states reject the Antalya draft; the summit ends two days late with no agreement.",
     "CLIMATE", "CONFIRMED", "Guardian / Al Jazeera", "climate", 30.7, 36.9, (0, 0)),
    (2, "Russian drone hits block near Kyiv",
     "Five-storey building in Dymer struck; 2 killed, 14 people missing under the rubble.",
     "EUROPE", "CONFIRMED", "Reuters", "burst", 30.0, 50.8, (-8, -9)),
    (3, "Iran strikes Bahrain site; 2 hurt",
     "Projectiles hit an industrial site; Gulf states condemn. Iran claims a US drone downed.",
     "MIDDLE EAST", "CONFIRMED", "Reuters / AFP", "rocket", 50.6, 26.2, (0, 0)),
    (4, "Settlers torch vehicles in West Bank",
     "Four villages attacked overnight; Eisenkot calls it \u201cJewish terrorism\u201d; inquiry opened.",
     "MIDDLE EAST", "CONFIRMED", "Reuters / AP", "flame", 35.2, 31.9, (7, 7)),
    (5, "Mexico captures \u201cEl Chapo Isidro\u201d",
     "Cartel boss taken in a Sinaloa raid; 11 killed, four of them soldiers. FBI most-wanted fugitive.",
     "N. AMERICA", "CONFIRMED", "AP / Al Jazeera", "cuffs", -108.5, 25.6, (0, 0)),
    (6, "Candy factory fire in Indonesia",
     "Blaze at a factory in Banten; 3 dead, 36 missing as rescuers search the ruins.",
     "ASIA", "CONFIRMED", "AP / Reuters", "factory", 106.0, -6.0, (0, 0)),
    (7, "Seoul minister quits over AI cheating",
     "Education minister resigns days before college entrance exams after an AI cheating scandal.",
     "ASIA", "CONFIRMED", "Reuters", "book", 127.0, 37.5, (0, 0)),
    (8, "US spy chief: Putin \u201cnot a friend\u201d",
     "DNI Jay Clayton contradicts Trump, days after the president called Putin a friend.",
     "N. AMERICA", "CONFIRMED", "Reuters", "speech", -77.0, 38.9, (0, 0)),
    (9, "Verstappen wins wild Las Vegas GP",
     "35 lead changes on the Strip; Norris 2nd, Piastri 3rd after late Mercedes drama.",
     "SPORT", "CONFIRMED", "Formula 1", "car", -115.1, 36.2, (-4, -3)),
    (10, "UN AI weapons talks end with no rules",
     "A week of Geneva talks on killer robots closes with no mandate for binding rules.",
     "WORLD", "CONFIRMED", "AP", "chip", 6.1, 46.2, (0, 0)),
    (11, "Blast aboard Russian ship in Benghazi",
     "Explosion at the naval base; Libya\u2019s eastern government suspects a drone attack.",
     "AFRICA", "REPORTED", "Reuters", "ship", 20.1, 32.1, (0, 0)),
    (12, "Russian ship still burns in Baltic",
     "Sanctioned Sparta II ablaze after a drone hit; an air alert sounds in Kaliningrad.",
     "EUROPE", "CONFIRMED", "AP / Reuters", "waves", 26.0, 59.8, (-16, -14)),
    (13, "Drones hit Khartoum, damage UN site",
     "Sudan\u2019s air defences intercept drones over the capital; explosions heard in districts.",
     "AFRICA", "CONFIRMED", "Reuters", "drone", 32.5, 15.6, (-6, 6)),
    (14, "Hamas seeks urgent mediators\u2019 talks",
     "After a strike kills three Gaza soup kitchen workers, Hamas calls for a meeting.",
     "MIDDLE EAST", "CONFIRMED", "AP", "aid", 34.5, 31.5, (24, 20)),
    (15, "Princess Kate in remission from cancer",
     "In a new documentary she reflects on life after her cancer diagnosis.",
     "EUROPE", "CONFIRMED", "AP", "crown", -0.1, 51.5, (-12, -8)),
    (16, "One-off CRISPR jab cuts cholesterol 52%",
     "A single gene-editing therapy halves bad cholesterol, trial results show.",
     "HEALTH", "CONFIRMED", "One Turn", "dna", -95.0, 39.0, (0, 0)),
]

TIMELINE = [
    ("~02:00", "India declare 720/9; Pant 128"),
    ("~05:00", "Verstappen wins Las Vegas GP"),
    ("~08:00", "Drone hits Dymer block; 14 missing"),
    ("14:20", "COP31 collapses; EU rejects draft"),
    ("14:42", "Indonesia factory fire; 3 dead"),
    ("15:44", "Eisenkot condemns settler arson"),
    ("~16:00", "Spy chief: Putin \u201cnot a friend\u201d"),
]

REST = [
    (17, "Trump: hard to work with Schumer if he leads the Senate \u2014 Reuters"),
    (18, "Trump confirms the FBI\u2019s crime database was hacked \u2014 AP"),
    (19, "Israel and US agree joint plans for a possible Iran escalation \u2014 Israeli media"),
    (20, "Saudi air defences intercept missile allegedly aimed at Makkah \u2014 Dunya"),
    (21, "Yemeni army: 149 Houthis killed or wounded in 816 attacks in a day \u2014 CLAIM"),
    (22, "Qatar, Germany urge Iran to drop Houthi backing, open up on nukes \u2014 Dunya"),
    (23, "Iran begins rationing electricity as Gulf tensions bite \u2014 One Turn"),
    (24, "Saudi Arabia triples the oil it stores in Japan \u2014 One Turn"),
    (25, "China\u2019s exchanges ease margin trading to prop up stocks \u2014 Reuters"),
    (26, "Tata Steel nears deal for majority stake in APL Apollo Tubes \u2014 Reuters"),
    (27, "US Army to detonate 68 barrels of toxic lead azide in Iowa, defying court \u2014 Reuters"),
    (28, "Okinawa celebrates Shuri Castle hall restored, 7 years after fire \u2014 AP"),
    (29, "US immigration officers make arrests at Seattle airport, delay flight \u2014 AP"),
    (30, "Washington governor demands ICE abolished after masked agents detain two \u2014 Yeni Safak"),
    (31, "Thousands march in Lisbon as living costs fuel anger \u2014 Dunya"),
    (32, "Turkey takes control of its last major independent news channel \u2014 One Turn"),
    (33, "Eisenkot invites Netanyahu\u2019s Likud to coalition talks \u2014 Reuters"),
    (34, "Australia criticises US budget office over AUKUS comments \u2014 Dunya"),
    (35, "Trump briefs Japan\u2019s Takaichi on summits with Xi and Putin \u2014 Yeni Safak"),
    (36, "Taiwan warns Canada\u2019s Carney that deeper China ties carry risks \u2014 Manila Times"),
    (37, "Nvidia faces a US accounting probe amid market turmoil \u2014 Manila Times"),
    (38, "Nigeria opens bids for 40 oil and gas blocks; troops rout bandits in Kogi \u2014 Phoenix"),
    (39, "Meloni shocked as Italian ex-police chief is found dead \u2014 AP"),
    (40, "Specially bred mosquitoes can fend off dengue, new evidence says \u2014 AP"),
    (41, "Tear gas may harm reproductive health, concerns rise in France \u2014 AP"),
    (42, "India declare 720/9 in Wellington, a record in NZ; Pant 128; NZ 119/2 \u2014 ANI"),
    (43, "Kansas City Current win their first NWSL Championship \u2014 One Turn"),
    (44, "England beat New Zealand at Twickenham \u2014 One Turn"),
    (45, "Leeds win at Chelsea for first time since 1999; Hull beat Brighton 2\u20130 \u2014 One Turn"),
    (46, "Lara Colturi wins Albania\u2019s first Alpine skiing World Cup \u2014 One Turn"),
    (47, "Haugan wins Gurgl slalom as Braathen\u2019s streak ends \u2014 Reuters"),
    (48, "Canadian women sweep the 500m podium in Seoul \u2014 One Turn"),
    (49, "Cavalry FC win the Canadian Premier League title \u2014 One Turn"),
    (50, "Earth gains a new mini-moon, asteroid 2026 QQ8 \u2014 One Turn"),
]

LEFT_OUT = ("LEFT OUT \u2014 broke on earlier days: ICJ Myanmar ruling 19 Nov \u00b7 "
            "S&P sell-off 20 Nov \u00b7 Riemann claim 20 Nov \u00b7 Kryvyi Rih strike 20 Nov \u00b7 "
            "Trump\u2013Xi AI accord 20 Nov \u00b7 BepiColombo orbit 21 Nov \u00b7 400-drone barrage "
            "21 Nov \u00b7 Hormuz tankers 21 Nov \u00b7 Bayelsa boat 21 Nov \u00b7 "
            "UK\u2013EU deals 21 Nov \u00b7 EU\u2013Indonesia deal 21 Nov")
NOT_YET = ("NOT YET: Spain election 29 Nov \u00b7 Senate leadership vote 1 Dec \u00b7 "
           "BepiColombo orbiters separate 9\u201310 Dec \u00b7 India\u2013NZ final day 23 Nov \u00b7 "
           "Iowa detonation due by 24 Nov")

FOOT_NOTE = ("Every story here happened, or was first reported, on Sunday 22 November 2026; "
             "claims are attributed.")
FOOT_SRC = ("Sources: Reuters \u00b7 AP \u00b7 Al Jazeera \u00b7 AFP \u00b7 The Guardian \u00b7 "
            "Formula 1 \u00b7 ANI \u00b7 One Turn \u00b7 Dunya News \u00b7 Yeni Safak \u00b7 "
            "Manila Times \u00b7 Phoenix")

# Stylised continents, pixel polygons inside the map band (x 8..1016).
LAND = [
    [(140, 618), (200, 612), (280, 614), (330, 625), (320, 645), (290, 660),
     (250, 672), (210, 665), (170, 655), (130, 640), (120, 628)],       # N America
    [(360, 606), (385, 606), (388, 618), (365, 620), (358, 612)],        # Greenland
    [(330, 668), (380, 665), (400, 680), (380, 700), (350, 705), (330, 690)],  # S America
    [(500, 612), (560, 608), (580, 618), (560, 630), (520, 632), (500, 622)],  # Europe
    [(510, 640), (580, 638), (600, 655), (580, 680), (550, 700), (525, 685),
     (510, 660)],                                                          # Africa
    [(590, 608), (850, 605), (900, 620), (880, 650), (820, 665), (760, 660),
     (700, 645), (620, 640), (590, 625)],                                 # Asia
    [(820, 672), (880, 670), (890, 682), (850, 690), (825, 685)],         # Australia
    [(503, 610), (512, 610), (512, 618), (503, 618)],                     # Britain
    [(872, 618), (880, 618), (880, 626), (872, 626)],                     # Japan
]


def lonlat_to_xy(lon, lat, mx0=8, my0=600, mw=1008, mh=112):
    x = mx0 + (lon + 180.0) / 360.0 * mw
    y = my0 + (75.0 - lat) / 130.0 * mh
    return x, y

# ---------------------------------------------------------------- sections

def draw_header(d):
    d.rectangle([0, 0, W, 60], fill=INK)
    d.text((12, 6), "THE WORLD IN ONE DAY", font=F_TITLE, fill=(248, 243, 230))
    d.text((12, 40), "50 STORIES  \u00b7  7 REGIONS  \u00b7  14 FIELDS  \u00b7  ALL FROM THIS ONE DAY",
           font=F_SUB, fill=(212, 172, 84))
    d.rectangle([W - 268, 0, W, 60], fill=RED)
    d.text((W - 256, 8), "SUNDAY", font=F_DATE, fill=(255, 255, 255))
    d.text((W - 256, 30), "22 NOVEMBER 2026", font=F_DATE, fill=(255, 255, 255))


def draw_timeline(d):
    y0 = 60
    d.rectangle([0, y0, W, y0 + 46], fill=CREAM)
    d.line([(0, y0 + 46), (W, y0 + 46)], fill=LINE, width=1)
    d.text((12, y0 + 4), "THE DAY IN UTC", font=F_SEC, fill=RED)
    slot = (W - 170) / len(TIMELINE)
    for i, (tm, txt) in enumerate(TIMELINE):
        sx = 170 + i * slot
        d.text((sx, y0 + 4), tm, font=F_TL_TIME, fill=RED)
        lines = fit(d, txt, F_TL_TXT, slot - 8, max_lines=2)
        text_block(d, sx, y0 + 20, lines, F_TL_TXT, INK, 12)


def draw_leads(d):
    y0, row_h, cols = 106, 117, 4
    cw = (W - 16) / cols
    for idx, lead in enumerate(LEADS):
        (num, head, body, region, status, src, kind, lon, lat, nudge) = lead
        r, c = divmod(idx, cols)
        x0 = 8 + c * cw
        yy = y0 + r * row_h
        if c:
            d.line([(x0, yy + 4), (x0, yy + row_h - 4)], fill=LINE, width=1)
        if r:
            d.line([(x0 + 4, yy), (x0 + cw - 4, yy)], fill=LINE, width=1)
        # number badge
        cx, cy = x0 + 14, yy + 13
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=RED)
        d.text((cx - 5, cy - 8), str(num), font=F_NUM, fill=(255, 255, 255))
        # headline, two lines
        hl = fit(d, head, F_HEAD, cw - 34, max_lines=2)
        text_block(d, x0 + 30, yy + 3, hl, F_HEAD, INK, 14)
        # icon box + body
        d.rectangle([x0 + 6, yy + 52, x0 + 50, yy + 96], fill=CREAM,
                    outline=LINE, width=1)
        ICONS[kind](d, x0 + 6, yy + 52)
        bl = fit(d, body, F_BODY, cw - 62, max_lines=3)
        text_block(d, x0 + 56, yy + 52, bl, F_BODY, INK, 12)
        # tag line
        tag = "%s \u00b7 %s \u00b7 %s" % (region, status, src)
        tl = fit(d, tag, F_TAG, cw - 12, max_lines=1)
        d.text((x0 + 6, yy + 102), tl[0], font=F_TAG, fill=TEAL)


def draw_map(d):
    y0 = 574
    d.rectangle([0, y0, W, y0 + 132], fill=MAP_SEA)
    d.text((12, y0 + 3), "WHERE IT HAPPENED \u2014 NUMBERED PINS MATCH THE LEAD STORIES",
           font=F_SEC, fill=INK)
    d.line([(0, y0 + 132), (W, y0 + 132)], fill=LINE, width=1)
    for poly in LAND:
        d.polygon(poly, fill=MAP_LAND, outline=(150, 160, 140))
    for lead in LEADS:
        (num, head, body, region, status, src, kind, lon, lat, nudge) = lead
        px, py = lonlat_to_xy(lon, lat)
        qx, qy = px + nudge[0], py + nudge[1]
        if nudge != (0, 0):
            d.line([(px, py), (qx, qy)], fill=GREY, width=1)
        d.ellipse([qx - 9, qy - 9, qx + 9, qy + 9], fill=RED,
                  outline=(255, 255, 255), width=2)
        tw = d.textlength(str(num), font=F_NUM)
        d.text((qx - tw / 2, qy - 8), str(num), font=F_NUM,
               fill=(255, 255, 255))


def draw_rest(d):
    y0 = 706
    d.text((12, y0 + 2), "THE REST OF THE DAY \u2014 STORIES 17\u201350",
           font=F_SEC, fill=INK)
    d.line([(0, y0 + 20), (W, y0 + 20)], fill=LINE, width=1)
    col_w = (W - 32) / 2
    for i, (num, txt) in enumerate(REST):
        col, row = divmod(i, 17)
        x0 = 12 + col * (col_w + 8)
        yy = y0 + 26 + row * 11
        d.text((x0, yy), "%d." % num, font=F_ONE_B, fill=RED)
        lines = fit(d, txt, F_ONE, col_w - 26, max_lines=1)
        d.text((x0 + 26, yy), lines[0], font=F_ONE, fill=INK)


def draw_datecheck(d):
    y0 = 912
    d.rectangle([0, y0, W, y0 + 64], fill=RED_SOFT)
    d.text((12, y0 + 3), "DATE CHECK \u2014 WHAT WE LEFT OUT, AND WHY",
           font=F_SEC, fill=RED)
    half = (W - 24) / 2
    lines = fit(d, LEFT_OUT, F_SMALL, half, max_lines=3)
    text_block(d, 12, y0 + 20, lines, F_SMALL, INK, 11)
    lines2 = fit(d, NOT_YET, F_SMALL, half, max_lines=3)
    text_block(d, 12 + half + 8, y0 + 20, lines2, F_SMALL, INK, 11)


def draw_footer(d):
    y0 = 976
    d.rectangle([0, y0, W, H], fill=INK)
    d.text((12, y0 + 5), FOOT_NOTE, font=F_FOOT, fill=(248, 243, 230))
    d.text((12, y0 + 26), FOOT_SRC, font=F_SMALL, fill=(190, 196, 204))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_timeline(d)
    draw_leads(d)
    draw_map(d)
    draw_rest(d)
    draw_datecheck(d)
    draw_footer(d)
    return img


if __name__ == "__main__":
    poster = build()
    poster.save(OUT, format="PNG")
    print("wrote", OUT, poster.size,
          os.path.getsize(OUT), "bytes")
