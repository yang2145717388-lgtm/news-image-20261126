#!/usr/bin/env python3
"""Draw a newspaper front page summing up the world news of
Thursday, 26 November 2026, as a single 1024x1024 image.

Deterministic: stdlib + Pillow only, no network, no clock, no files
read. Writes the poster to $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png) and prints its size and sha256.
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
PAPER = (247, 241, 227)
INK = (20, 20, 20)
RED = (176, 42, 32)
NAVY = (29, 53, 87)
GREY = (90, 84, 72)
ORANGE = (214, 96, 24)
FLAME = (232, 148, 32)
SMOKE = (70, 66, 60)
SEA = (46, 92, 122)
SKY = (233, 214, 178)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


SERIF = "DejaVuSerif-Bold.ttf"
SERIF_REG = "DejaVuSerif.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, width, fill=INK, spacing=4):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, fnt, width)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def rule(draw, x0, y, x1, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_refinery(draw, x0, y0, x1, y1):
    """A small drawn scene: refinery towers, flame and smoke above a
    tanker at sea in the Strait of Hormuz."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY, outline=INK, width=2)
    horizon = y0 + int((y1 - y0) * 0.58)
    draw.rectangle([x0, horizon, x1, y1 - 20], fill=SEA)
    # sun
    cx = x0 + 46
    cy = y0 + 34
    draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(226, 170, 60))
    # refinery towers on the left shore
    base = horizon
    draw.rectangle([x0 + 84, base - 50, x0 + 110, base], fill=INK)
    draw.rectangle([x0 + 118, base - 70, x0 + 140, base], fill=INK)
    draw.rectangle([x0 + 148, base - 40, x0 + 178, base], fill=INK)
    draw.rectangle([x0 + 186, base - 56, x0 + 204, base], fill=INK)
    draw.rectangle([x0 + 84, base - 78, x0 + 204, base - 70], fill=INK)
    # distillation column with a tall flame
    draw.rectangle([x0 + 220, base - 80, x0 + 244, base], fill=INK)
    draw.polygon(
        [(x0 + 220, base - 80), (x0 + 244, base - 80), (x0 + 232, base - 118)],
        fill=FLAME,
    )
    draw.polygon(
        [(x0 + 225, base - 80), (x0 + 239, base - 80), (x0 + 232, base - 104)],
        fill=ORANGE,
    )
    # smoke drifting right from the flame
    for sx, sy, r in [(256, 26, 10), (274, 20, 13), (292, 26, 10)]:
        draw.ellipse(
            [x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r], fill=SMOKE
        )
    # tanker on the sea, clear of the caption strip
    tx0 = x0 + 84
    ty = horizon + 12
    draw.polygon(
        [(tx0, ty), (tx0 + 190, ty), (tx0 + 172, ty + 20), (tx0 + 16, ty + 20)],
        fill=(196, 52, 40),
    )
    draw.rectangle([tx0 + 26, ty - 18, tx0 + 70, ty], fill=(196, 52, 40))
    draw.rectangle([tx0 + 86, ty - 12, tx0 + 134, ty], fill=(196, 52, 40))
    draw.rectangle([tx0 + 142, ty - 26, tx0 + 152, ty], fill=INK)
    # small flame on the tanker deck
    draw.polygon(
        [(tx0 + 98, ty - 12), (tx0 + 109, ty - 12), (tx0 + 103, ty - 28)],
        fill=FLAME,
    )
    # wake lines beside the tanker
    for wy in (ty + 26, ty + 32):
        draw.line([(tx0 - 8, wy), (tx0 + 60, wy)], fill=(247, 241, 227), width=2)
    # caption strip along the bottom of the panel
    draw.rectangle([x0, y1 - 20, x1, y1], fill=NAVY)
    draw.text(
        (x0 + 10, y1 - 17),
        "RAS TANURA AND THE STRAIT OF HORMUZ",
        font=font(SANS_B, 11),
        fill=(247, 241, 227),
    )


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # double outer frame
    d.rectangle([26, 26, 998, 998], outline=INK, width=3)
    d.rectangle([33, 33, 991, 991], outline=INK, width=1)

    # top line: date left, tag right
    f_top = font(SANS_B, 17)
    d.text((44, 48), "THURSDAY, 26 NOVEMBER 2026", font=f_top, fill=INK)
    tag = "THE DAY IN ONE IMAGE"
    d.text((980 - d.textlength(tag, font=f_top), 48), tag, font=f_top, fill=INK)

    # masthead
    f_mast = font(SERIF, 60)
    mast = "THE WORLD IN ONE PAGE"
    d.text(
        ((W - d.textlength(mast, font=f_mast)) / 2, 74),
        mast,
        font=f_mast,
        fill=INK,
    )
    rule(d, 44, 146, 980, width=4)
    rule(d, 44, 152, 980, width=1)

    # ---- lead story ----
    y = 164
    d.text((44, y), "OIL SHOCK  •  THE MIDDLE EAST", font=font(SANS_B, 18), fill=RED)
    y = 190
    f_head = font(SERIF, 40)
    headline = (
        "Houthis hit Saudi Arabia's\nbiggest refinery as mines\nstrike tankers in Hormuz"
    )
    for line in headline.split("\n"):
        d.text((44, y), line, font=f_head, fill=INK)
        y += 48
    y += 2
    f_deck = font(SERIF_REG, 19)
    y = text_block(
        d,
        44,
        y,
        "Brent jumps as Ras Tanura burns and shipping through the "
        "strait stalls. The Houthis claim the strike; Iran says its "
        "mines hit two tankers. OPEC+ meets on Sunday.",
        f_deck,
        936,
        spacing=3,
    )

    # lead body (left) + illustration (right)
    y_body = y + 6
    f_body = font(SERIF_REG, 16)
    text_block(
        d,
        44,
        y_body,
        "Yemen's Houthis said on Wednesday they attacked Ras Tanura, "
        "the kingdom's largest refinery and a main crude export "
        "terminal, and Riyadh's financial district. Satellite images "
        "showed black smoke over the plant; the Saudi-led coalition "
        "said it shot down four drones and did not confirm a hit.\n"
        "In the Strait of Hormuz, Iran said two tankers struck mines "
        "and caught fire. Brent settled up 3.5% on Wednesday.",
        f_body,
        540,
        spacing=3,
    )
    draw_refinery(d, 612, y_body, 980, y_body + 148)

    rule(d, 44, 566, 980, width=2)

    # ---- middle row: two columns ----
    y = 578
    f_label = font(SANS_B, 16)
    f_h2 = font(SERIF, 24)
    f_small = font(SERIF_REG, 15)
    col_w = 452
    d.text((44, y), "MARKETS", font=f_label, fill=RED)
    y2 = text_block(
        d, 44, y + 26, "Asia bounces after Wall Street slide", f_h2, col_w, spacing=2
    )
    text_block(
        d,
        44,
        y2 + 4,
        "Nikkei +1.6%, Kospi +1.9% as Asia steadies. The Nasdaq fell "
        "2% on Wednesday, near bear territory; Nvidia lost 3.9% as "
        "S&P put its rating on watch. US growth was revised up to "
        "4.3%; Wall Street is shut Thursday for Thanksgiving.",
        f_small,
        col_w,
        spacing=2,
    )
    d.text((528, y), "TARIFFS", font=f_label, fill=RED)
    y2 = text_block(
        d, 528, y + 26, "US proposes new duties on 14 partners", f_h2, col_w, spacing=2
    )
    text_block(
        d,
        528,
        y2 + 4,
        "Washington's Section 301 findings target 'excess capacity': "
        "China faces 20% on top of earlier duties, with the EU, "
        "Japan and Korea also named. India says settle it inside "
        "trade talks. A hearing comes first; duties could land in "
        "January.",
        f_small,
        col_w,
        spacing=2,
    )
    d.line([(512, 578), (512, 738)], fill=GREY, width=1)

    rule(d, 44, 750, 980, width=2)

    # ---- third row: three columns ----
    y = 762
    col3 = 296
    xs = [44, 364, 684]
    heads = [
        ("UKRAINE", "Kyiv: five Russian jets hit at Savasleyka",
         "Three MiG-31 Kinzhal carriers and two Su-34 bombers were "
         "damaged in strikes on Nov 24-25, 300 km east of Moscow, "
         "Kyiv says."),
        ("EGYPT", "Tanker fire kills 31 on Cairo ring road",
         "A fuel tanker overturned on the Ring Road in Giza on "
         "Wednesday evening, engulfing cars in flames. At least 31 "
         "dead, 21 hurt."),
        ("COLOMBIA", "Cartagena siege ends: all hostages freed",
         "Police stormed a supermarket after gunmen held about 20 "
         "people for 17 hours after a failed armoured-car robbery. "
         "All were freed."),
    ]
    for x, (label, head, body) in zip(xs, heads):
        d.text((x, y), label, font=f_label, fill=RED)
        y2 = text_block(d, x, y + 26, head, font(SERIF, 20), col3, spacing=2)
        text_block(d, x, y2 + 4, body, font(SERIF_REG, 14), col3, spacing=2)
    d.line([(348, 762), (348, 900)], fill=GREY, width=1)
    d.line([(668, 762), (668, 900)], fill=GREY, width=1)

    rule(d, 44, 906, 980, width=2)

    # ---- markets ticker band ----
    d.rectangle([44, 914, 980, 946], fill=NAVY)
    f_tick = font(SANS_B, 15)
    tick = "NIKKEI +1.6%    KOSPI +1.9%    BRENT $94.71    WTI $84.03    GOLD $3,566    DOLLAR 103.71    US 10-YR 4.85%"
    d.text(
        ((W - d.textlength(tick, font=f_tick)) / 2, 922),
        tick,
        font=f_tick,
        fill=(247, 241, 227),
    )

    # ---- briefs ----
    d.text((44, 954), "IN BRIEF  —  ", font=font(SANS_B, 12), fill=RED)
    brief = (
        "Norway's top court voids disputed oil licences  •  Ramaphosa wins reprieve from Farmgate probe  •  "
        "North Korea orders Switzerland to shut its Pyongyang office  •  California warns of king-tide floods  •  "
        "Gukesh meets Sindarov for the chess crown"
    )
    bx = 44 + d.textlength("IN BRIEF  —  ", font=font(SANS_B, 12))
    text_block(d, int(bx), 954, brief, font(SERIF_REG, 12), 980 - int(bx), spacing=1)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    data = open(path, "rb").read()
    if len(data) > 1024 * 1024:
        print("entry.png exceeds 1 MiB: %d bytes" % len(data), file=sys.stderr)
        sys.exit(1)
    print("wrote %s (%d bytes, %s, sha256 %s)"
          % (path, len(data), img.size, hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
