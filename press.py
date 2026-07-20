"""Shared PRESS primitives for every image this repo renders.

Tokens and drawing helpers live here so the banner and the Selected work
cards cannot drift apart. This is the same hand-sync problem og.js calls
out in natejswenson.io -- at least within this repo it is solved once.

Canonical token source: natejswenson.io/src/styles/global.css `:root`,
mirrored in local-fitness/src/local_fitness/agent/branding.py.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- Tokens -----------------------------------------------------------------
PAPER = "#F5F0E6"
INK = "#181510"
DIM = "#6E675C"
ACCENT = "#E8501F"

# Everything is drawn at SCALE and downsampled with LANCZOS. PIL rasterizes
# text at the size requested, so supersampling is what keeps Inter Black's
# tight tracking from going crunchy at the stems.
SCALE = 2

FONT_DIR = Path(__file__).parent / "assets" / "fonts"

DISPLAY_BLACK = "Inter-Black.ttf"
DISPLAY_BOLD = "Inter-Bold.ttf"
SERIF_ITALIC = "IBMPlexSerif-Italic.ttf"
MONO = "IBMPlexMono-Regular.ttf"


def px(v):
    """Nominal layout units -> supersampled device pixels."""
    return v * SCALE


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size * SCALE)


def draw_tracked(draw, xy, text, fnt, fill, tracking=0.0):
    """Draw `text` with letter-spacing, returning the x the run ended at.

    PIL has no tracking, so glyphs are placed one at a time and the pen is
    advanced by the glyph width plus a delta. `tracking` is in em -- the unit
    the brand specs use -- and is resolved against the font size.

    The return value is what lets multi-color runs (the eyebrow, the headline
    pivot) be composed without measuring the same text twice.
    """
    x, y = xy
    delta = tracking * fnt.size
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + delta
    return x


def tracked_width(draw, text, fnt, tracking=0.0):
    """Width of a tracked run, including the trailing letter-space, matching
    what draw_tracked actually advances."""
    delta = tracking * fnt.size
    return sum(draw.textlength(ch, font=fnt) + delta for ch in text)


def draw_sep_square(draw, x, baseline_y, fnt, size=6, fill=INK):
    """A small square separator, optically centered on the run's cap height.

    Used everywhere a `·` would normally go: the vendored Inter subsets carry
    neither U+00B7 nor U+2022, so both render as full-height tofu. A square is
    more PRESS anyway -- structure comes from rules and squares, never rounded
    chrome. Returns the x just past the square.
    """
    s = px(size)
    y = baseline_y + fnt.size * 0.72 - s / 2
    draw.rectangle([x, y, x + s, y + s], fill=fill)
    return x + s


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap to a pixel width. PIL has no line breaking."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def new_canvas(width, height):
    """A flat paper canvas at supersampled size. Never gradiented or textured."""
    return Image.new("RGBA", (px(width), px(height)), PAPER)


def finish(canvas, width, height, path):
    """Downsample to nominal size and write."""
    img = canvas.convert("RGB").resize((width, height), Image.LANCZOS)
    img.save(path, optimize=True)
    return img
