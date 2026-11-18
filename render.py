#!/usr/bin/env python3
"""THE WORLD IN A DAY - a one-page newspaper of Tuesday 17 November 2026.

Draws a clean, airy broadsheet front page with Pillow: one big lead story,
a dot-grid world map with markers, a day-in-numbers box, and a numbered
digest of complete stories grouped by continent (the three biggest digest
stories are set larger, as features). Rendered at 2048x2048 and downscaled
to 1024x1024. Fully deterministic: no randomness, no clocks, no network.
The layout is measured first and balanced across three columns; if the
page overflows, the lowest-priority stories are dropped - the type is
never shrunk below its floor sizes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
SS = 2048                      # render size (supersampled), final is 1024
FINAL = 1024
MARGIN = 76
CW = SS - 2 * MARGIN           # content width = 1896

PAPER = (251, 247, 238)
INK = (26, 22, 17)
RED = (158, 27, 36)
NAVY = (30, 46, 74)
GREY = (104, 94, 82)
DOT = (62, 74, 99)
GOLD = (232, 179, 75)
WHITE = (255, 255, 255)
LABEL_BLUE = (206, 213, 226)

FDIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


def F_serif(size):
    return font("NotoSerif-Regular.ttf", size)


def F_serif_b(size):
    return font("NotoSerif-Bold.ttf", size)


def F_disp_b(size):
    return font("NotoSerifDisplay-Bold.ttf", size)


def F_sans(size):
    return font("NotoSans-Regular.ttf", size)


def F_sans_b(size):
    return font("NotoSans-Bold.ttf", size)


# ---------------------------------------------------------------- text utils
def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, leading, fill=INK):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def shrink_to_fit(draw, text, name, size, width, floor=10):
    while size > floor:
        f = font(name, size)
        if draw.textlength(text, font=f) <= width:
            return f
        size -= 2
    return font(name, size)


# ---------------------------------------------------------------- story data
# Every summary written from the day's wire reporting; see sources.txt.
LEAD = {
    "id": "kerch",
    "kicker": "EUROPE · THE LEAD",
    "headline": "UKRAINE BLOWS A SPAN FROM THE KERCH BRIDGE",
    "body": ("A Ukrainian drone and missile strike brought down the main road arch of the "
             "19-kilometre Kerch Bridge, Russia's supply artery into occupied Crimea. Kyiv "
             "called it stage seven of an operation weeks in the making: drones hit the road "
             "deck, Neptune and Flamingo missiles the railway."),
}

# Digest groups in reading order. kind: "feature" (set larger) or "story".
# drop: lower = dropped earlier if the page overflows (None = protected).
GROUPS = [
    ("EUROPE", [
        {"id": "cop31", "kind": "feature", "kicker": "EUROPE · CLIMATE",
         "headline": "COP31 DRAFT: OUT WITH FOSSIL FUELS, $120BN TO ADAPT",
         "body": ("The Antalya draft deal calls for a faster phase-out of fossil fuels "
                  "and a tripling of adaptation finance to $120 billion a year by 2035.")},
        {"id": "kyiv", "kind": "story", "drop": 22,
         "headline": "RUSSIA HITS KYIV'S BRIDGES",
         "body": "Russian strikes on the capital's bridges cut power, heat and water across districts of Kyiv."},
        {"id": "drones", "kind": "story", "drop": 16,
         "headline": "MOSCOW: 1,400 UKRAINIAN DRONES DOWNED",
         "body": "Russia's Defence Ministry claimed its air defences intercepted more than 1,400 Ukrainian drones in a day."},
        {"id": "rwanda", "kind": "story", "drop": 15,
         "headline": "FIVE EU STATES AGREE RWANDA RETURN HUB",
         "body": "Germany, Denmark, Austria, Greece and the Netherlands will fund a hub in Rwanda for rejected asylum seekers."},
        {"id": "france", "kind": "story", "drop": 11,
         "headline": "FRANCE STRIKES AGAIN OVER PAY",
         "body": "Unions staged a second nationwide strike in a month, pressing the government for higher wages."},
        {"id": "geneva", "kind": "story", "drop": 12,
         "headline": "128 STATES DEBATE A KILLER-ROBOT BAN",
         "body": "Delegates in Geneva opened talks on a treaty to ban lethal autonomous weapons and keep humans in control."},
    ]),
    ("ASIA", [
        {"id": "shenzhen", "kind": "feature", "kicker": "ASIA · DIPLOMACY",
         "headline": "THREE PRESIDENTS, ONE TABLE IN SHENZHEN",
         "body": ("Trump flew into Shenzhen for APEC, where on Thursday he sits down "
                  "with Xi Jinping and Vladimir Putin - a first three-way meeting "
                  "in years.")},
        {"id": "bahrain", "kind": "story", "drop": 21,
         "headline": "IRANIAN DRONES TARGET US RADAR IN BAHRAIN",
         "body": "Iran's Guards fired drones at a US radar at Bahrain's Sheikh Isa base; Bahrain intercepted them, no casualties. US officials say Tehran may be drafting a 'dirty bomb' plan."},
        {"id": "japan", "kind": "story", "drop": 14,
         "headline": "JAPAN JETS ANSWER RUSSIAN INCURSION",
         "body": "Tokyo scrambled fighters and protested 'strongly' after two suspected Russian aircraft violated its airspace."},
        {"id": "hormuz", "kind": "story", "drop": 18,
         "headline": "TANKERS MINED IN THE STRAIT OF HORMUZ",
         "body": "Tankers were struck by naval mines in the strait as a third US aircraft carrier joined the Gulf force."},
        {"id": "singapore", "kind": "story", "drop": 6,
         "headline": "SINGAPORE BIDS FOR TRUSTED CHIP ACCESS",
         "body": "Singapore asked Washington for trusted access to advanced AI processors after fresh US export curbs."},
        {"id": "jericho", "kind": "story", "drop": 17,
         "headline": "SETTLERS KILL WOMAN, 72, IN JERICHO",
         "body": "Palestinian officials said settlers who seized homes in Jericho killed a 72-year-old woman overnight."},
        {"id": "akvan", "kind": "story", "drop": 4,
         "headline": "CYCLONE AKVAN STALLS OFF INDIA",
         "body": "The storm stalled over the Bay of Bengal, set for Andhra Pradesh on Friday; a bus plunge in Uttarakhand killed six."},
        {"id": "yemen", "kind": "story", "drop": 3,
         "headline": "HOUTHIS PUSH YEMEN'S ARMY BACK TO ADEN",
         "body": "Government forces quit the Red Sea coast to defend Aden as the Iran-backed Houthis advanced."},
        {"id": "tual", "kind": "story", "drop": None,
         "headline": "M6.6 QUAKE RATTLES THE BANDA SEA",
         "body": "USGS put the Banda Sea quake at magnitude 6.6, 148 km from Tual, Indonesia; green alert, no tsunami threat."},
    ]),
    ("NORTH AMERICA", [
        {"id": "measles", "kind": "feature", "kicker": "NORTH AMERICA · HEALTH",
         "headline": "AMERICA LOSES ITS MEASLES-FREE STATUS",
         "body": ("PAHO revoked the US elimination status held since 2000 after a year "
                  "of continuous spread. The CDC counts 5,412 cases in 2026, the most "
                  "since 1991.")},
        {"id": "pentagon", "kind": "story", "drop": 19,
         "headline": "PENTAGON FAILS ITS AUDIT - AGAIN",
         "body": "Auditors failed the Pentagon for a ninth straight year, unable to verify $4.9 trillion in assets."},
        {"id": "vulcan", "kind": "story", "drop": 20,
         "headline": "VULCAN FAILURE LOSES 40 AMAZON SATELLITES",
         "body": "ULA's Vulcan failed on return to flight, its first total loss in 20 years; early data blames the first stage."},
        {"id": "whitehouse", "kind": "story", "drop": 2,
         "headline": "WHITE HOUSE VETS TESTIMONY TO CONGRESS",
         "body": "A White House memo orders agencies to approve in advance any employee testimony to Congress."},
        {"id": "carney", "kind": "story", "drop": 13,
         "headline": "XI AND CARNEY AGREE TARIFF CUTS",
         "body": "China and Canada agreed further tariff cuts and deeper ties as Xi met Mark Carney on the APEC margins."},
    ]),
    ("AFRICA", [
        {"id": "sudan", "kind": "story", "drop": None,
         "headline": "UN: 1,390 CIVILIANS KILLED IN SUDAN",
         "body": "The UN human-rights office counted at least 1,390 civilians killed in Sudan's war in the first half of 2026."},
        {"id": "sahara", "kind": "story", "drop": 8,
         "headline": "UN BEGINS LEAVING WESTERN SAHARA",
         "body": "The first MINURSO peacekeepers departed Laayoune as the mission's mandate withdrawal got under way."},
        {"id": "afdb", "kind": "story", "drop": 9,
         "headline": "AFDB SIGNS RECORD ¥86.6BN JICA LOAN",
         "body": "The African Development Bank's loan from Japan's JICA is the largest ever for its concessional fund."},
        {"id": "barrick", "kind": "story", "drop": 10,
         "headline": "BARRICK SENDS CONGO MINE STAFF HOME",
         "body": "Barrick furloughed some personnel at its DR Congo mines over Ebola concerns, Reuters reported."},
    ]),
    ("SOUTH AMERICA", [
        {"id": "pope", "kind": "story", "drop": None,
         "headline": "ROSARY FROM CROWD HITS POPE IN LIMA",
         "body": "A rosary thrown by a well-wisher struck Pope Leo below the eye at his Lima farewell Mass; unhurt, he carried on."},
        {"id": "brazil", "kind": "story", "drop": 7,
         "headline": "BRAZIL'S FOSSIL ROADMAP WELCOMED",
         "body": "The COP31 draft welcomed Brazil's voluntary roadmap for moving beyond fossil fuels."},
    ]),
    ("OCEANIA", [
        {"id": "rlwc", "kind": "story", "drop": None,
         "headline": "KANGAROOS TAKE FOURTH STRAIGHT CROWN",
         "body": "Australia beat New Zealand 32-12 for a fourth straight Rugby League World Cup; the Jillaroos won 34-10."},
        {"id": "nz", "kind": "story", "drop": 5,
         "headline": "NEW ZEALAND AS 'SEVENTH STATE'?",
         "body": "An opinion piece urging NZ to join Australia reignited a 125-year-old debate; 40,000 weighed in, most against."},
        {"id": "gaza", "kind": "story", "drop": 1,
         "headline": "FOUR NATIONS URGE OPEN GAZA CROSSINGS",
         "body": "London, Canberra, Ottawa and Rome urged Israel to open Gaza's crossings, calling conditions catastrophic."},
    ]),
]

NUMBERS = [
    ("5,412", "US measles cases in 2026"),
    ("$120bn", "adaptation aid, COP31 draft"),
    ("19 km", "the Kerch Bridge arch"),
    ("1,390", "Sudan civilians killed in H1"),
]

TICKER = ("KERCH ARCH DOWN +++ SHENZHEN TRILATERAL SET FOR THURSDAY +++ US MEASLES STATUS "
          "REVOKED +++ VULCAN LOSES 40 SATELLITES +++ FRANCE STRIKES +++ M6.6 OFF TUAL +++ "
          "KANGAROOS 32-12 +++")

SOURCES = ("Sources: Reuters · AP · ISW · USGS · PAHO · CDC · UN OHCHR · Just Security · "
           "GeekWire · The Watchers - the reporting of Tuesday 17 November 2026 · Drawn "
           "entirely by program: no photographs, no AI imagery")

# Map markers: (story id, longitude, latitude)
MARKER_SPOTS = [
    ("kerch", 36.6, 45.2),
    ("cop31", 30.7, 36.9),
    ("shenzhen", 114.1, 22.5),
    ("bahrain", 50.6, 26.2),
    ("measles", -98.0, 39.5),
    ("tual", 131.4, -6.0),
]
MARKER_NAMES = {"kerch": "Kerch", "cop31": "Antalya", "shenzhen": "Shenzhen",
                "bahrain": "Bahrain", "measles": "USA", "tual": "Tual"}

# ---------------------------------------------------------------- world map
# Stylised dot-grid world: land spans per grid row. Grid is 120 x 54 cells,
# longitude -168..+192 across, latitude +84..-56 down (equirectangular).
MAP_COLS, MAP_ROWS = 120, 54
LAND = {
    4: [(38, 44)],
    5: [(1, 10), (14, 30), (36, 45), (70, 95)],
    6: [(0, 11), (13, 33), (35, 46), (68, 105)],
    7: [(1, 10), (12, 36), (36, 44), (66, 110)],
    8: [(11, 38), (37, 42), (58, 64), (66, 112)],
    9: [(12, 39), (54, 56), (58, 65), (67, 113)],
    10: [(13, 40), (54, 56), (57, 66), (68, 112)],
    11: [(14, 40), (56, 68), (70, 114)],
    12: [(15, 39), (56, 69), (71, 115)],
    13: [(15, 38), (55, 66), (67, 72), (74, 116)],
    14: [(16, 37), (55, 60), (61, 68), (70, 76), (78, 116)],
    15: [(16, 36), (55, 60), (63, 66), (69, 78), (80, 116), (103, 105)],
    16: [(17, 34), (65, 72), (73, 80), (82, 115), (104, 106)],
    17: [(19, 31), (72, 79), (81, 90), (92, 114), (100, 101), (105, 106)],
    18: [(21, 29), (71, 78), (79, 88), (89, 110)],
    19: [(24, 28), (54, 68), (72, 77), (83, 89), (91, 108)],
    20: [(26, 29), (52, 70), (73, 76), (84, 88), (90, 106)],
    21: [(29, 35), (51, 71), (84, 87), (92, 100), (101, 107), (103, 104)],
    22: [(30, 37), (51, 72), (85, 86), (93, 99), (103, 104)],
    23: [(31, 39), (51, 72), (95, 97), (103, 104)],
    24: [(32, 40), (52, 73), (88, 93), (96, 101), (105, 109)],
    25: [(32, 40), (52, 73), (104, 112)],
    26: [(31, 39), (53, 74)],
    27: [(31, 38), (53, 74)],
    28: [(30, 37), (54, 73)],
    29: [(30, 36), (55, 72)],
    30: [(29, 35), (56, 71)],
    31: [(29, 34), (57, 70)],
    32: [(28, 33), (58, 69)],
    33: [(28, 32), (58, 68)],
    34: [(28, 31), (59, 67)],
    35: [(28, 30), (59, 67), (71, 72)],
    36: [(27, 30), (59, 66), (71, 72)],
    37: [(27, 29), (60, 66), (71, 72), (96, 104)],
    38: [(27, 29), (60, 65), (71, 71), (95, 106)],
    39: [(27, 28), (60, 65), (95, 107)],
    40: [(27, 28), (60, 64), (96, 107)],
    41: [(27, 28), (61, 64), (97, 107)],
    42: [(27, 28), (61, 63), (98, 106)],
    43: [(27, 28), (61, 63), (99, 105)],
    44: [(27, 27), (62, 62), (100, 104)],
    45: [(101, 103), (112, 113)],
    46: [(111, 112)],
    47: [(110, 111)],
}


def lonlat_to_cell(lon, lat):
    cx = (lon + 168.0) / 360.0 * MAP_COLS
    cy = (84.0 - lat) / 140.0 * MAP_ROWS
    return cx, cy


def draw_map(draw, x, y, w, h, markers):
    cw = w / MAP_COLS
    ch = h / MAP_ROWS
    r = min(cw, ch) * 0.30
    for row, spans in LAND.items():
        cy = y + (row + 0.5) * ch
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = x + (c + 0.5) * cw
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DOT)
    mf = F_sans_b(24)
    for num, lon, lat in markers:
        cx, cy = lonlat_to_cell(lon, lat)
        px, py = x + cx * cw, y + cy * ch
        rad = 18
        draw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=RED)
        t = str(num)
        tw = draw.textlength(t, font=mf)
        draw.text((px - tw / 2, py - 13), t, font=mf, fill=WHITE)


# ---------------------------------------------------------------- digest layout
COL_GAP = 30
COL_W = (CW - 2 * COL_GAP) // 3          # 612
GUT = 48                                  # number gutter inside a column
HDR_H = 30                                # continent header block
FEAT = {"kick": 30, "hlh": 39, "blh": 29, "gap": 12}
STOR = {"hlh": 29, "blh": 24, "gap": 7}
BLOCK_GAP = 6


def item_height(draw, item):
    tw = COL_W - GUT
    if item["kind"] == "feature":
        hl = wrap(draw, item["headline"], F_serif_b(32), tw)
        bl = wrap(draw, item["body"], F_serif(23), tw)
        return FEAT["kick"] + len(hl) * FEAT["hlh"] + 4 + len(bl) * FEAT["blh"] + FEAT["gap"]
    hl = wrap(draw, item["headline"], F_serif_b(24), tw)
    bl = wrap(draw, item["body"], F_serif(20), tw)
    return len(hl) * STOR["hlh"] + 2 + len(bl) * STOR["blh"] + STOR["gap"]


def block_height(draw, block):
    return HDR_H + sum(item_height(draw, it) for it in block[1])


def pack_columns(draw, limit):
    """Balance groups over 3 columns; drop low-priority stories until fit.
    Returns (columns, dropped_ids); columns = [[(header, [items]), ...]]."""
    groups = [(name, list(items)) for name, items in GROUPS]
    dropped = []

    def blocks_for(groups):
        blocks = []
        for name, items in groups:
            if name == "ASIA" and block_height(draw, (name, items)) > limit:
                best = None
                for k in range(2, len(items) - 1):
                    a = (name, items[:k])
                    b = (name + " (CONT.)", items[k:])
                    m = max(block_height(draw, a), block_height(draw, b))
                    if best is None or m < best[0]:
                        best = (m, a, b)
                blocks.extend([best[1], best[2]])
            else:
                blocks.append((name, items))
        return blocks

    def assign(blocks):
        cols = [[], [], []]
        heights = [0, 0, 0]
        for b in blocks:
            i = heights.index(min(heights))
            cols[i].append(b)
            heights[i] += block_height(draw, b) + BLOCK_GAP
        return cols, heights

    while True:
        cols, heights = assign(blocks_for(groups))
        if max(heights) <= limit:
            return cols, dropped
        cands = []
        for gi, (name, items) in enumerate(groups):
            for ii, it in enumerate(items):
                if it.get("drop") is not None:
                    cands.append((it["drop"], gi, ii))
        if not cands:
            return cols, dropped
        cands.sort()
        _, gi, ii = cands[0]
        dropped.append(groups[gi][1][ii]["id"])
        del groups[gi][1][ii]


# ---------------------------------------------------------------- build
# Lead-zone geometry shared by the measurer and the builder.
LEAD_W = 1090
RIGHT_W = CW - 1134
MAP_H = 250
NUMBERS_H = 132


def caption_text(numbers):
    parts = []
    for sid, _, _ in sorted(MARKER_SPOTS, key=lambda s: numbers.get(s[0], 99)):
        if sid in numbers:
            parts.append(f"{numbers[sid]} {MARKER_NAMES[sid]}")
    return "Markers: " + " · ".join(parts)


def measure_top(scratch):
    """(digest_top, zone_top) measured on a scratch draw; mirrors build."""
    y = 36 + 38                                   # eyebrow
    mast = shrink_to_fit(scratch, "THE WORLD IN A DAY",
                         "NotoSerifDisplay-Black.ttf", 120, CW)
    bbox = scratch.textbbox((0, 0), "THE WORLD IN A DAY", font=mast)
    y += (bbox[3] - bbox[1]) + 14 + 28            # masthead + rules
    y += 82 + 20                                  # date band
    zone_top = y
    lead_h = 44
    lead_h += len(wrap(scratch, LEAD["headline"], F_serif_b(74), LEAD_W)) * 90 + 10
    lead_h += len(wrap(scratch, LEAD["body"], F_serif(32), LEAD_W)) * 43
    cap = caption_text({sid: 88 for sid, _, _ in MARKER_SPOTS})
    cap_lines = len(wrap(scratch, cap, F_sans(20), RIGHT_W))
    right_h = MAP_H + 12 + 30 + cap_lines * 25 + 10 + NUMBERS_H
    zone_h = max(lead_h, right_h) + 16
    y = zone_top + zone_h + 22 + 40               # gap + digest header
    return y, zone_top


def build_image():
    scratch = ImageDraw.Draw(Image.new("RGB", (64, 64), PAPER))
    digest_top, _ = measure_top(scratch)
    digest_limit = (SS - 140) - digest_top
    cols, dropped = pack_columns(scratch, digest_limit)

    numbers = {"kerch": 1}
    n = 2
    for col in cols:
        for _, items in col:
            for it in items:
                numbers[it["id"]] = n
                n += 1
    total = n - 1
    markers = [(numbers[sid], lon, lat) for sid, lon, lat in MARKER_SPOTS
               if sid in numbers]

    img = Image.new("RGB", (SS, SS), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, SS - MARGIN
    y = 36

    # --- eyebrow row
    eb = F_sans_b(25)
    d.text((x0, y), "THE COMPLETE ONE-PAGE NEWSPAPER OF A SINGLE DAY", font=eb, fill=GREY)
    right = "GLOBAL EDITION · ONE IMAGE"
    d.text((x1 - d.textlength(right, font=eb), y), right, font=eb, fill=GREY)
    y += 38

    # --- masthead (anchored on the glyph box: nothing is clipped)
    mast = shrink_to_fit(d, "THE WORLD IN A DAY", "NotoSerifDisplay-Black.ttf", 120, CW)
    bbox = d.textbbox((0, 0), "THE WORLD IN A DAY", font=mast)
    d.text((SS // 2, y - bbox[1]), "THE WORLD IN A DAY", font=mast, fill=INK, anchor="ma")
    y += (bbox[3] - bbox[1]) + 14
    d.rectangle([x0, y, x1, y + 7], fill=INK)
    d.rectangle([x0, y + 11, x1, y + 13], fill=INK)
    y += 28

    # --- red date band
    d.rectangle([x0, y, x1, y + 82], fill=RED)
    bf = F_sans_b(46)
    d.text((x0 + 26, y + 15), "TUESDAY 17 NOVEMBER 2026", font=bf, fill=WHITE)
    bfr = F_sans_b(32)
    rtxt = f"{total} STORIES · 6 CONTINENTS · ONE PAGE"
    d.text((x1 - 26 - d.textlength(rtxt, font=bfr), y + 23), rtxt, font=bfr, fill=WHITE)
    y += 82 + 20

    # --- lead zone: lead story left, map + numbers right
    zone_top = y
    right_x = x0 + 1134
    kf = F_sans_b(27)
    d.text((x0, y), "STORY 1 · " + LEAD["kicker"], font=kf, fill=RED)
    y += 44
    hf = F_serif_b(74)
    lines = wrap(d, LEAD["headline"], hf, LEAD_W)
    y = draw_lines(d, x0, y, lines, hf, 90)
    y += 10
    bf2 = F_serif(32)
    lines = wrap(d, LEAD["body"], bf2, LEAD_W)
    y = draw_lines(d, x0, y, lines, bf2, 43)

    d.rectangle([right_x, zone_top, right_x + RIGHT_W, zone_top + MAP_H],
                outline=INK, width=2)
    draw_map(d, right_x + 14, zone_top + 12, RIGHT_W - 28, MAP_H - 24, markers)
    cap_y = zone_top + MAP_H + 12
    d.text((right_x, cap_y), "THE DAY ON ONE MAP", font=F_sans_b(24), fill=INK)
    cap_lines = wrap(d, caption_text(numbers), F_sans(20), RIGHT_W)
    draw_lines(d, right_x, cap_y + 30, cap_lines, F_sans(20), 25, fill=GREY)

    nb_y = cap_y + 30 + len(cap_lines) * 25 + 10
    d.rectangle([right_x, nb_y, right_x + RIGHT_W, nb_y + NUMBERS_H], fill=NAVY)
    d.text((right_x + 22, nb_y + 10), "THE DAY IN NUMBERS", font=F_sans_b(24), fill=GOLD)
    nf, lf = F_disp_b(38), F_sans(19)
    cell_w = (RIGHT_W - 44) // 2
    for i, (num, lab) in enumerate(NUMBERS):
        cx = right_x + 22 + (i % 2) * cell_w
        cy = nb_y + 44 + (i // 2) * 42
        d.text((cx, cy), num, font=nf, fill=WHITE)
        nw = d.textlength(num, font=nf)
        lab_lines = wrap(d, lab, lf, cell_w - nw - 14)
        ly = cy + 5
        for ln in lab_lines[:2]:
            d.text((cx + nw + 12, ly), ln, font=lf, fill=LABEL_BLUE)
            ly += 23

    # advance to the measured digest header position
    y = digest_top - 40
    dh = F_sans_b(29)
    d.text((x0, y), "THE FULL DAY IN STORIES - THE DIGEST", font=dh, fill=INK)
    rtxt = f"NUMBERED 1-{total} · GROUPED BY CONTINENT"
    d.text((x1 - d.textlength(rtxt, font=dh), y), rtxt, font=dh, fill=GREY)
    y = digest_top

    # --- digest columns
    dg_g = F_sans_b(24)
    fh, fb = F_serif_b(32), F_serif(23)
    sh, sb = F_serif_b(24), F_serif(20)
    fk = F_sans_b(21)
    for ci, col in enumerate(cols):
        cx = x0 + ci * (COL_W + COL_GAP)
        cy = y
        for header, items in col:
            d.text((cx, cy), header, font=dg_g, fill=RED)
            cy += HDR_H
            for it in items:
                num = numbers[it["id"]]
                if it["kind"] == "feature":
                    d.text((cx, cy), it["kicker"], font=fk, fill=RED)
                    cy += FEAT["kick"]
                    d.text((cx, cy), f"{num}.", font=fh, fill=RED)
                    hl = wrap(d, it["headline"], fh, COL_W - GUT)
                    cy = draw_lines(d, cx + GUT, cy, hl, fh, FEAT["hlh"])
                    cy += 4
                    bl = wrap(d, it["body"], fb, COL_W - GUT)
                    cy = draw_lines(d, cx + GUT, cy, bl, fb, FEAT["blh"])
                    cy += FEAT["gap"]
                else:
                    d.text((cx, cy), f"{num}.", font=sh, fill=RED)
                    hl = wrap(d, it["headline"], sh, COL_W - GUT)
                    cy = draw_lines(d, cx + GUT, cy, hl, sh, STOR["hlh"])
                    cy += 2
                    bl = wrap(d, it["body"], sb, COL_W - GUT)
                    cy = draw_lines(d, cx + GUT, cy, bl, sb, STOR["blh"])
                    cy += STOR["gap"]
            cy += BLOCK_GAP

    # --- ticker
    tick_y = SS - 118
    d.rectangle([x0, tick_y, x1, tick_y + 52], fill=INK)
    tf = shrink_to_fit(d, TICKER, "NotoSans-Bold.ttf", 24, CW - 40, floor=14)
    tw = d.textlength(TICKER, font=tf)
    d.text(((SS - tw) / 2, tick_y + 13), TICKER, font=tf, fill=WHITE)

    # --- sources
    sf = shrink_to_fit(d, SOURCES, "NotoSans-Regular.ttf", 21, CW, floor=12)
    tw = d.textlength(SOURCES, font=sf)
    d.text(((SS - tw) / 2, tick_y + 68), SOURCES, font=sf, fill=GREY)

    global LAST_BUILD
    LAST_BUILD = {"stories": total, "dropped": dropped}
    return img.resize((FINAL, FINAL), Image.LANCZOS)


LAST_BUILD = {}


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build_image()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print(f"wrote {path} ({os.path.getsize(path)} bytes)")
    print(f"stories on page: {LAST_BUILD.get('stories')}, dropped: {LAST_BUILD.get('dropped')}")


if __name__ == "__main__":
    main()
