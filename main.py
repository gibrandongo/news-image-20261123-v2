# SPDX-License-Identifier: MIT
"""THE WORLD TODAY - Monday, 23 November 2026.

Draws a newspaper front page summing up 23 November 2026 world news:
a lead story (COP31 collapse in Antalya) plus 30 short labelled story
cells across six continents. All text is drawn programmatically with PIL.

Fonts are shipped inside this repository (fonts/DejaVuSans*.ttf, OFL
licensed) and loaded via a path relative to this file. No system font
paths are ever used, so the program runs in a sandbox with no system
fonts installed. No network, no clock, no randomness: two runs write
byte-identical PNGs. Writes only to MAKEFUN_OUTPUT_DIR (default
/output), never to the repository directory.
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
INK = (18, 18, 18)
PAPER = (250, 247, 238)
RED = (158, 27, 27)
BLUE = (23, 58, 110)
GREY = (90, 88, 82)
RULE = (120, 116, 106)
CELL_BG = (255, 255, 255)
TAG_COLORS = {
    "CLIMATE": (140, 40, 20),
    "MIDEAST": (120, 60, 10),
    "EUROPE": (23, 58, 110),
    "AFRICA": (90, 60, 10),
    "ASIA": (20, 100, 70),
    "AMERICAS": (90, 30, 90),
    "WORLD": (60, 60, 60),
    "SPORT": (20, 90, 120),
}

BASE = Path(__file__).resolve().parent


def load_font(name, size):
    """Load a bundled font; fall back to PIL's built-in font only if the
    bundled file is somehow missing. Never touches a system font path."""
    path = BASE / "fonts" / name
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        return ImageFont.load_default()


F_TITLE = load_font("DejaVuSans-Bold.ttf", 56)
F_DATE = load_font("DejaVuSans-Bold.ttf", 19)
F_LEAD_HEAD = load_font("DejaVuSans-Bold.ttf", 31)
F_LEAD_BODY = load_font("DejaVuSans.ttf", 17)
F_TAG = load_font("DejaVuSans-Bold.ttf", 12)
F_HEAD = load_font("DejaVuSans-Bold.ttf", 14)
F_BODY = load_font("DejaVuSans.ttf", 12)
F_FOOT = load_font("DejaVuSans.ttf", 12)

LEAD_HEAD = "COP31 COLLAPSES: NO DEAL"
LEAD_BODY = [
    "UN climate talks ended in failure after the EU and island states",
    "rejected a final text that said nothing about fossil fuels.",
    "The longest COP on record ran two days into overtime.",
]

# (tag, headline, detail) - every story first reported 22-23 Nov 2026.
STORIES = [
    ("CLIMATE", "Guterres 'deeply disappointed'", "UN chief: summit ends with no consensus."),
    ("CLIMATE", "Next climate talks: Ethiopia", "2027 round set for Ethiopia after collapse."),
    ("MIDEAST", "Tankers hit mines in Hormuz", "Two supertankers catch fire east of strait."),
    ("MIDEAST", "Houthis claim Saudi refinery hit", "Strikes claimed on oil site; 6 injured."),
    ("MIDEAST", "Iran rations electricity", "Power rationing begins as grid strains."),
    ("MIDEAST", "Israel: no new government", "Coalition talks fail to reach a deal."),
    ("EUROPE", "Warship sunk off Libya", "Russian corvette Merkury capsized."),
    ("EUROPE", "Kyiv block hit, 2 dead", "Drone strikes flats in Dymer; 11 missing."),
    ("EUROPE", "Peace talks edge closer", "US envoys see progress."),
    ("EUROPE", "West Bank vehicles torched", "Settlers burn 12 cars near Ramallah."),
    ("AFRICA", "Sudan drones hit UN site", "Strikes damage UN facility in Khartoum."),
    ("AFRICA", "Lisbon march on living costs", "Thousands protest rising prices."),
    ("AFRICA", "Amazon rescue after 11 days", "Elderly man found alive in rainforest."),
    ("ASIA", "Asia braces for market rout", "Wall St slide spurs Taiwan, Seoul measures."),
    ("ASIA", "Taiwan bans short sales", "Regulator curbs selling below flat price."),
    ("ASIA", "Bitcoin below $58,000", "Lowest since Sept 2024; weekly slide extends."),
    ("ASIA", "Lahore air worst again", "AQI 538: world's most polluted major city."),
    ("ASIA", "Factory fire: 24 dead", "Bodies recovered in Cikande, Indonesia."),
    ("ASIA", "Shuri Castle reborn", "Okinawa restores main hall, 7 years after fire."),
    ("ASIA", "MSCI warns Indonesia", "Wash-trading may cost index place."),
    ("AMERICAS", "Hegseth curbs Canada ties", "US defence memo restricts cooperation."),
    ("AMERICAS", "ICE detains father, daughter", "Pair held at Seattle airport en route to baptism."),
    ("AMERICAS", "Mexico nabs 'El Chapo Isidro'", "Cartel boss caught; 11 killed in Sinaloa."),
    ("AMERICAS", "KC Current win first title", "Mahomes-backed club takes NWSL crown."),
    ("WORLD", "128 states back robot rules", "UN push to regulate killer robots by 2028."),
    ("WORLD", "S. Korea minister quits", "Education chief resigns over AI exam cheating."),
    ("WORLD", "Myanmar slams ASEAN call", "Army-backed govt calls ruling unfair."),
    ("WORLD", "Ship ablaze off Finland", "Russian cargo vessel hit; crew evacuated."),
    ("SPORT", "Liverpool 4-0 Man Utd", "Pochettino debut ends in rout; Yoro sent off."),
    ("SPORT", "Marquez takes 8th title", "Record-tying MotoGP crown in Portugal."),
]


def wrap(draw, text, font, width):
    """Greedy word wrap using the font's real glyph widths."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_globe(draw, cx, cy, r):
    """Simple line-art globe: circle, meridians, equator."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=4)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=BLUE, width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=BLUE, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 200, 340, fill=BLUE, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 20, 160, fill=BLUE, width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN

    # --- Masthead ---
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=F_TITLE)
    d.text(((W - tw) / 2, 14), title, font=F_TITLE, fill=INK)
    d.line([x0, 86, x1, 86], fill=INK, width=3)
    date_line = "MONDAY, 23 NOVEMBER 2026  |  ONE DAY'S NEWS FROM SIX CONTINENTS"
    dw = d.textlength(date_line, font=F_DATE)
    d.text(((W - dw) / 2, 94), date_line, font=F_DATE, fill=RED)
    d.line([x0, 122, x1, 122], fill=RULE, width=1)

    # --- Lead story ---
    lead_y = 134
    lead_w = 700
    d.text((x0, lead_y), "LEAD STORY  |  ANTALYA, TURKEY", font=F_TAG, fill=RED)
    head_lines = wrap(d, LEAD_HEAD, F_LEAD_HEAD, lead_w)
    y = lead_y + 22
    for line in head_lines:
        d.text((x0, y), line, font=F_LEAD_HEAD, fill=INK)
        y += 36
    y += 4
    d.text((x0, y), "EU walks out over fossil-fuel omission; first collapse since 2009.",
           font=F_LEAD_BODY, fill=RED)
    y += 26
    for line in LEAD_BODY:
        d.text((x0, y), line, font=F_LEAD_BODY, fill=INK)
        y += 23
    # Globe art at the right of the lead.
    draw_globe(d, 880, 215, 62)
    d.text((838, 292), "NO DEAL", font=F_TAG, fill=RED)
    d.line([x0, 316, x1, 316], fill=INK, width=2)
    d.text((x0, 322), "AROUND THE WORLD  —  30 MORE STORIES", font=F_TAG, fill=INK)

    # --- Story grid: 5 rows x 6 columns, 30 cells ---
    cols, rows = 6, 5
    gap = 6
    grid_top, grid_bottom = 342, 984
    cell_w = (x1 - x0 - (cols - 1) * gap) // cols
    cell_h = (grid_bottom - grid_top - (rows - 1) * gap) // rows
    for i, (tag, head, body) in enumerate(STORIES):
        r, c = divmod(i, cols)
        cx = x0 + c * (cell_w + gap)
        cy = grid_top + r * (cell_h + gap)
        d.rectangle([cx, cy, cx + cell_w, cy + cell_h], fill=CELL_BG,
                    outline=RULE, width=1)
        d.text((cx + 7, cy + 6), tag, font=F_TAG,
               fill=TAG_COLORS.get(tag, GREY))
        head_lines = wrap(d, head, F_HEAD, cell_w - 14)
        hy = cy + 24
        for line in head_lines[:3]:
            d.text((cx + 7, hy), line, font=F_HEAD, fill=INK)
            hy += 17
        body_lines = wrap(d, body, F_BODY, cell_w - 14)
        by = hy + 3
        for line in body_lines[:2]:
            d.text((cx + 7, by), line, font=F_BODY, fill=GREY)
            by += 15

    # --- Footer ---
    d.text((x0, 994), "All stories reported 23 November 2026. Sources: AP, Reuters, AFP, BBC, Al Jazeera.",
           font=F_FOOT, fill=GREY)

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.png"
    img.save(out_path, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
