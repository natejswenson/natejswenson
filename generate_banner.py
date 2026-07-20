#!/usr/bin/env python3
"""Render the PRESS masthead banner for the GitHub profile README.

This is a PIL port of the site's OG card renderer
(natejswenson.io/src/lib/og.js `renderCard`), retargeted from the 1200x630
social card to a 1600x600 README hero. Same skeleton, same tokens: flat
paper canvas, ink rules for structure, and ONE signature accent.

THE ACCENT LAW: orange is a signature, not a color scheme. This artifact
spends it in exactly three places -- the stamp, the `No. 001` numeral, and
the two-word headline pivot. The pivot is named explicitly below; never
auto-orange a word.

Shared tokens and drawing helpers live in press.py.
"""

from pathlib import Path

from PIL import Image, ImageDraw

import press

WIDTH, HEIGHT = 1600, 600

PAD_X, PAD_Y = 80, 56
RULE_TOP = 10       # full-bleed masthead rule (og.js: borderTop 8px at 1200w)
RULE_COLOPHON = 6
RULE_STANDFIRST = 5

OUTPUT = Path(__file__).parent / "banner.png"

# --- Copy -------------------------------------------------------------------
# Standfirst and tagline adapted from natejswenson.io src/data/site.js and
# src/layouts/Base.astro. Em dashes removed per the voice-notes correction.
EYEBROW_LABEL = "FIELD NOTES"
EYEBROW_NO = "No. 001"
MASTHEAD_URL = "natejswenson.com"
HEADLINE = "Building in public,\nagent-first."
HEADLINE_PIVOT = "agent-first"
STANDFIRST = (
    "Senior DevOps Engineer at GoodLeap. Shipping AI agents that automate\n"
    "incident analysis, debugging, and CI/CD decisions."
)
COLOPHON_LEFT = "NATE SWENSON"
COLOPHON_RIGHT = "Shipped features, the tradeoffs, and what broke."
STAMP = "NS"


def draw_stamp(canvas, xy, size, fnt):
    """The NS stamp: square, accent border, accent monogram, rotated -4deg.

    Rendered on its own transparent layer because PIL cannot rotate in place.
    `expand=True` grows the layer to fit the rotated corners, so the paste is
    re-centered on the original box.
    """
    s = press.px(size)
    border = press.px(3)
    pad = s // 2  # headroom so the rotated corners are not clipped
    layer = Image.new("RGBA", (s + pad * 2, s + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([pad, pad, pad + s, pad + s], outline=press.ACCENT, width=border)

    # Optically center the monogram using its ink extents, not the font
    # metrics -- Inter Black's line box has asymmetric bearings.
    bbox = ld.textbbox((0, 0), STAMP, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    ld.text(
        (pad + (s - tw) / 2 - bbox[0], pad + (s - th) / 2 - bbox[1]),
        STAMP, font=fnt, fill=press.ACCENT,
    )

    rotated = layer.rotate(-4, expand=True, resample=Image.BICUBIC)
    x, y = press.px(xy[0]), press.px(xy[1])
    ox = x - (rotated.width - s) // 2
    oy = y - (rotated.height - s) // 2
    canvas.alpha_composite(rotated, (int(ox - pad), int(oy - pad)))


def render():
    canvas = press.new_canvas(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(canvas)

    f_stamp = press.font(press.DISPLAY_BLACK, 28)
    f_eyebrow = press.font(press.DISPLAY_BOLD, 24)
    f_mono = press.font(press.MONO, 22)
    f_headline = press.font(press.DISPLAY_BLACK, 84)
    f_serif = press.font(press.SERIF_ITALIC, 28)
    f_colophon = press.font(press.DISPLAY_BOLD, 22)
    f_tagline = press.font(press.SERIF_ITALIC, 24)

    # --- Full-bleed top rule ------------------------------------------------
    draw.rectangle([0, 0, press.px(WIDTH), press.px(RULE_TOP)], fill=press.INK)

    left = press.px(PAD_X)
    right = press.px(WIDTH - PAD_X)
    y = press.px(PAD_Y + RULE_TOP)

    # --- Masthead: stamp + eyebrow, url right -------------------------------
    stamp_size = 64
    draw_stamp(canvas, (PAD_X, PAD_Y + RULE_TOP), stamp_size, f_stamp)

    eyebrow_x = left + press.px(stamp_size + 20)
    # Vertically center the eyebrow against the stamp square.
    eyebrow_y = y + press.px(stamp_size) / 2 - f_eyebrow.size * 0.72
    end = press.draw_tracked(
        draw, (eyebrow_x, eyebrow_y), EYEBROW_LABEL,
        f_eyebrow, press.INK, tracking=0.16,
    )
    gap = press.px(14)
    end = press.draw_sep_square(draw, end + gap, eyebrow_y, f_eyebrow, size=6)
    press.draw_tracked(
        draw, (end + gap, eyebrow_y), EYEBROW_NO,
        f_eyebrow, press.ACCENT, tracking=0.16,
    )

    url_w = draw.textlength(MASTHEAD_URL, font=f_mono)
    draw.text(
        (right - url_w, y + press.px(stamp_size) / 2 - f_mono.size * 0.72),
        MASTHEAD_URL, font=f_mono, fill=press.DIM,
    )

    # --- Headline -----------------------------------------------------------
    # Tight tracking (-0.03em) and a 1.02 line box, per og.js.
    y += press.px(stamp_size) + press.px(58)
    line_h = f_headline.size * 1.02
    for line in HEADLINE.split("\n"):
        if HEADLINE_PIVOT in line:
            before, after = line.split(HEADLINE_PIVOT, 1)
            x = press.draw_tracked(draw, (left, y), before, f_headline,
                                   press.INK, tracking=-0.03)
            x = press.draw_tracked(draw, (x, y), HEADLINE_PIVOT, f_headline,
                                   press.ACCENT, tracking=-0.03)
            press.draw_tracked(draw, (x, y), after, f_headline,
                               press.INK, tracking=-0.03)
        else:
            press.draw_tracked(draw, (left, y), line, f_headline,
                               press.INK, tracking=-0.03)
        y += line_h

    # --- Standfirst: accent left rule, serif italic --------------------------
    y += press.px(30)
    sf_lines = STANDFIRST.split("\n")
    sf_h = f_serif.size * 1.4 * len(sf_lines)
    draw.rectangle([left, y, left + press.px(RULE_STANDFIRST), y + sf_h],
                   fill=press.ACCENT)
    sf_x = left + press.px(RULE_STANDFIRST + 18)
    sf_y = y
    for line in sf_lines:
        draw.text((sf_x, sf_y), line, font=f_serif, fill=press.INK)
        sf_y += f_serif.size * 1.4

    # --- Colophon: ink rule pinned to the bottom -----------------------------
    col_rule_y = press.px(HEIGHT - PAD_Y) - press.px(46)
    draw.rectangle([left, col_rule_y, right, col_rule_y + press.px(RULE_COLOPHON)],
                   fill=press.INK)
    col_y = col_rule_y + press.px(RULE_COLOPHON + 20)
    press.draw_tracked(draw, (left, col_y), COLOPHON_LEFT, f_colophon,
                       press.INK, tracking=0.14)
    tag_w = draw.textlength(COLOPHON_RIGHT, font=f_tagline)
    draw.text((right - tag_w, col_y), COLOPHON_RIGHT, font=f_tagline, fill=press.DIM)

    return canvas


def main():
    img = press.finish(render(), WIDTH, HEIGHT, OUTPUT)
    print(f"wrote {OUTPUT.name}  {img.width}x{img.height}  "
          f"{OUTPUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
