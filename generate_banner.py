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

Everything is drawn at 2x and downsampled with LANCZOS. PIL renders text at
the size you ask for, so supersampling is what keeps the tight tracking on
Inter Black from going crunchy at the stems.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- PRESS tokens -----------------------------------------------------------
# Canonical source: natejswenson.io/src/styles/global.css `:root`, mirrored in
# local-fitness/src/local_fitness/agent/branding.py `DEFAULT_THEME`. Kept in
# sync by hand, same as og.js -- there is no shared token package yet.
PAPER = "#F5F0E6"
INK = "#181510"
DIM = "#6E675C"
ACCENT = "#E8501F"

# --- Canvas -----------------------------------------------------------------
WIDTH, HEIGHT = 1600, 600
SCALE = 2  # supersample factor; the whole layout is multiplied by this

PAD_X, PAD_Y = 80, 56
RULE_TOP = 10       # full-bleed masthead rule (og.js: borderTop 8px at 1200w)
RULE_COLOPHON = 6
RULE_STANDFIRST = 5

FONT_DIR = Path(__file__).parent / "assets" / "fonts"
OUTPUT = Path(__file__).parent / "banner.png"

# --- Copy -------------------------------------------------------------------
# Standfirst and tagline adapted from natejswenson.io src/data/site.js and
# src/layouts/Base.astro. Em dashes removed per the voice-notes correction.
EYEBROW_LABEL = "FIELD NOTES"
EYEBROW_NO = "No. 001"
# The eyebrow separator is drawn as a small ink square, not typed as "·".
# The vendored Inter subset carries neither U+00B7 nor U+2022 -- both render
# as full-height tofu. A square reads as the same beat and is more PRESS
# anyway (structure comes from rules and squares, never rounded chrome).
SEP_SIZE = 6
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


def font(name, size):
    """Load a vendored brand face at a supersampled size."""
    return ImageFont.truetype(str(FONT_DIR / name), size * SCALE)


def px(v):
    return v * SCALE


def draw_tracked(draw, xy, text, fnt, fill, tracking=0.0):
    """Draw `text` with letter-spacing, returning the x the run ended at.

    PIL has no tracking, so each glyph is placed individually and the pen is
    advanced by the glyph's own width plus a delta. `tracking` is in em (the
    CSS unit the brand specs use), converted against the font size.

    Returns the end x so runs can be chained -- that is how the two-color
    eyebrow and the headline pivot get composed without measuring twice.
    """
    x, y = xy
    delta = tracking * fnt.size
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + delta
    return x


def tracked_width(draw, text, fnt, tracking=0.0):
    """Width of a tracked run, including the trailing letter-space (matching
    what draw_tracked actually advances)."""
    delta = tracking * fnt.size
    return sum(draw.textlength(ch, font=fnt) + delta for ch in text)


def draw_stamp(canvas, xy, size, fnt):
    """The NS stamp: square, accent border, accent monogram, rotated -4deg.

    Rendered on its own transparent layer because PIL cannot rotate in place.
    `expand=True` grows the layer to fit the rotated corners, so the paste is
    re-centered on the original box.
    """
    s = px(size)
    border = px(3)
    pad = s // 2  # headroom so the rotated corners are not clipped
    layer = Image.new("RGBA", (s + pad * 2, s + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([pad, pad, pad + s, pad + s], outline=ACCENT, width=border)

    # Optically center the monogram in the square using its ink extents, not
    # the font metrics -- Inter Black's line box has asymmetric bearings.
    bbox = ld.textbbox((0, 0), STAMP, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    ld.text(
        (pad + (s - tw) / 2 - bbox[0], pad + (s - th) / 2 - bbox[1]),
        STAMP, font=fnt, fill=ACCENT,
    )

    rotated = layer.rotate(-4, expand=True, resample=Image.BICUBIC)
    x, y = px(xy[0]), px(xy[1])
    ox = x - (rotated.width - s) // 2 - pad + pad
    oy = y - (rotated.height - s) // 2 - pad + pad
    canvas.alpha_composite(rotated, (int(ox - pad), int(oy - pad)))


def render():
    canvas = Image.new("RGBA", (px(WIDTH), px(HEIGHT)), PAPER)
    draw = ImageDraw.Draw(canvas)

    f_stamp = font("Inter-Black.ttf", 28)
    f_eyebrow = font("Inter-Bold.ttf", 24)
    f_mono = font("IBMPlexMono-Regular.ttf", 22)
    f_headline = font("Inter-Black.ttf", 84)
    f_serif = font("IBMPlexSerif-Italic.ttf", 28)
    f_colophon = font("Inter-Bold.ttf", 22)
    f_tagline = font("IBMPlexSerif-Italic.ttf", 24)

    # --- Full-bleed top rule ------------------------------------------------
    draw.rectangle([0, 0, px(WIDTH), px(RULE_TOP)], fill=INK)

    left = px(PAD_X)
    right = px(WIDTH - PAD_X)
    y = px(PAD_Y + RULE_TOP)

    # --- Masthead: stamp + eyebrow, url right -------------------------------
    stamp_size = 64
    draw_stamp(canvas, (PAD_X, PAD_Y + RULE_TOP), stamp_size, f_stamp)

    eyebrow_x = left + px(stamp_size + 20)
    # Vertically center the eyebrow against the stamp square.
    eyebrow_y = y + px(stamp_size) / 2 - f_eyebrow.size * 0.72
    end = draw_tracked(
        draw, (eyebrow_x, eyebrow_y), EYEBROW_LABEL,
        f_eyebrow, INK, tracking=0.16,
    )
    # Separator square, optically centered on the eyebrow's cap height.
    gap = px(14)
    sep = px(SEP_SIZE)
    sep_y = eyebrow_y + f_eyebrow.size * 0.72 - sep / 2
    draw.rectangle([end + gap, sep_y, end + gap + sep, sep_y + sep], fill=INK)
    draw_tracked(
        draw, (end + gap * 2 + sep, eyebrow_y), EYEBROW_NO,
        f_eyebrow, ACCENT, tracking=0.16,
    )

    url_w = draw.textlength(MASTHEAD_URL, font=f_mono)
    draw.text(
        (right - url_w, y + px(stamp_size) / 2 - f_mono.size * 0.72),
        MASTHEAD_URL, font=f_mono, fill=DIM,
    )

    # --- Headline -----------------------------------------------------------
    # Tight tracking (-0.03em) and a 1.02 line box, per og.js.
    y += px(stamp_size) + px(58)
    line_h = f_headline.size * 1.02
    for line in HEADLINE.split("\n"):
        if HEADLINE_PIVOT in line:
            before, after = line.split(HEADLINE_PIVOT, 1)
            x = draw_tracked(draw, (left, y), before, f_headline, INK, tracking=-0.03)
            x = draw_tracked(draw, (x, y), HEADLINE_PIVOT, f_headline, ACCENT, tracking=-0.03)
            draw_tracked(draw, (x, y), after, f_headline, INK, tracking=-0.03)
        else:
            draw_tracked(draw, (left, y), line, f_headline, INK, tracking=-0.03)
        y += line_h

    # --- Standfirst: accent left rule, serif italic --------------------------
    y += px(30)
    sf_lines = STANDFIRST.split("\n")
    sf_h = f_serif.size * 1.4 * len(sf_lines)
    draw.rectangle([left, y, left + px(RULE_STANDFIRST), y + sf_h], fill=ACCENT)
    sf_x = left + px(RULE_STANDFIRST + 18)
    sf_y = y
    for line in sf_lines:
        draw.text((sf_x, sf_y), line, font=f_serif, fill=INK)
        sf_y += f_serif.size * 1.4

    # --- Colophon: ink rule pinned to the bottom -----------------------------
    col_rule_y = px(HEIGHT - PAD_Y) - px(46)
    draw.rectangle([left, col_rule_y, right, col_rule_y + px(RULE_COLOPHON)], fill=INK)
    col_y = col_rule_y + px(RULE_COLOPHON + 20)
    draw_tracked(draw, (left, col_y), COLOPHON_LEFT, f_colophon, INK, tracking=0.14)
    tag_w = draw.textlength(COLOPHON_RIGHT, font=f_tagline)
    draw.text((right - tag_w, col_y), COLOPHON_RIGHT, font=f_tagline, fill=DIM)

    return canvas.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)


def main():
    img = render()
    img.save(OUTPUT, optimize=True)
    print(f"wrote {OUTPUT.name}  {img.width}x{img.height}  "
          f"{OUTPUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
