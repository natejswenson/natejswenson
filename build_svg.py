#!/usr/bin/env python3
"""Build the profile as tiling, individually-linked PRESS pieces.

Two constraints fight each other here.

1. GitHub's markdown sanitizer strips every `style` and `class` attribute,
   escapes `<style>` blocks, and removes inline `<svg>`. Verified against
   the GitHub markdown API. So CSS is only reachable inside an external SVG
   loaded through <img>, where the browser renders it as a real document.

2. An SVG loaded through <img> cannot carry working links. So a single
   full-page SVG is seamless but entirely unclickable.

The resolution is `align="left"`, which survives sanitization and maps to
`float:left`. Floated images are out of normal flow, so they tile edge to
edge with none of the line-height gaps that stacked inline images get.
That means the page can be sliced into pieces -- each its own <a> -- and
still read as one continuous document.

So the layout is designed as one 1200-wide page and then cut:

    masthead            1200   -> natejswenson.com
    card 001 | card 002  600x2 -> repo, repo
    card 003 | card 004  600x2 -> repo, repo
    colophon L | R       600x2 -> natejswenson.com, linkedin

Gutters and margins live *inside* the pieces, so the cuts fall on empty
paper and the seams are invisible. Each piece embeds only the glyphs it
actually sets, subset to woff2, since an <img> SVG cannot fetch fonts.
"""

import base64
import io
from pathlib import Path

from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).parent
FONT_DIR = ROOT / "assets" / "fonts"
OUT_DIR = ROOT / "assets" / "press"

# --- PRESS tokens -----------------------------------------------------------
# Canonical source: natejswenson.io/src/styles/global.css `:root`.
PAPER = "#F5F0E6"
INK = "#181510"
DIM = "#6E675C"
ACCENT = "#E8501F"

FACES = {
    "display-black": "Inter-Black.ttf",
    "display-bold": "Inter-Bold.ttf",
    "serif-italic": "IBMPlexSerif-Italic.ttf",
    "mono": "IBMPlexMono-Regular.ttf",
}

# --- Page geometry ----------------------------------------------------------
W = 1200            # full design width
HALF = W // 2       # a card column
PAD = 64            # outer page margin
GUTTER = 28         # space between the two columns
INNER = GUTTER // 2  # half-gutter, carried inside each column piece
RULE_HEAVY = 10
RULE_MED = 6
CARD_PAD = 30
ROW_GAP = 28

SITE = "https://natejswenson.com"
LINKEDIN = "https://linkedin.com/in/natejswenson"

# --- Content ----------------------------------------------------------------
EYEBROW = "FIELD NOTES"
EYEBROW_NO = "No. 001"
URL = "natejswenson.com"
HEADLINE = ["Building in public,", "agent-first."]
HEADLINE_PIVOT = "agent-first"
STANDFIRST = (
    "Senior DevOps Engineer at GoodLeap. Shipping AI agents that automate "
    "incident analysis, debugging, and CI/CD decisions."
)
SECTION = "SELECTED WORK"
COLOPHON_L = "NATE SWENSON"

CARDS = [
    {
        "no": "No. 001",
        "repo": "local-fitness",
        "href": "https://github.com/natejswenson/local-fitness",
        "desc": "Agent-first fitness coach. Pulls Garmin data into a local SQLite "
                "database and exposes deterministic training-load math "
                "(CTL / ATL / TSB) to Claude over MCP.",
        "stack": ["Python", "MCP", "SQLite", "Flask"],
    },
    {
        "no": "No. 002",
        "repo": "traefik-local-cli",
        "href": "https://github.com/natejswenson/traefik-local-cli",
        "desc": "Onboards any local app to a hardened Traefik proxy at "
                "<app>.internal, driven by a bundled Claude Code skill with hard "
                "pass/fail gates.",
        "stack": ["Bash", "Claude Code", "Docker"],
    },
    {
        "no": "No. 003",
        "repo": "claude-skills",
        "href": "https://github.com/natejswenson/claude-skills",
        "desc": "Monorepo of independently-released Claude Code productivity "
                "skills: devlog, ghostwriter, resume, github-stats. Namespaced "
                "releases and path-filtered CI.",
        "stack": ["JavaScript", "Python", "Bash"],
    },
    {
        "no": "No. 004",
        "repo": "local-budget",
        "href": "https://github.com/natejswenson/local-budget",
        "desc": "Local-first Wells Fargo spending agent. One SQLite database "
                "behind a column-level authorizer, exposed through a stdio MCP "
                "server and no-code Claude skills.",
        "stack": ["Python", "MCP", "SQLite", "Docker"],
    },
]


# --- Type measurement -------------------------------------------------------
class Face:
    """A loaded face that measures strings the way the renderer will."""

    def __init__(self, path):
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.hmtx = self.tt["hmtx"]
        self.order = self.tt.getGlyphOrder()

    def advance(self, ch):
        name = self.cmap.get(ord(ch)) or self.order[0]
        return self.hmtx[name][0] / self.upem

    def width(self, s, size, tracking=0.0):
        return sum(self.advance(c) * size + tracking * size for c in s)


FACE = {k: Face(FONT_DIR / v) for k, v in FACES.items()}


def wrap(s, face, size, max_w):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if face.width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --- Fonts ------------------------------------------------------------------
_SUBSET_CACHE = {}


def subset_uri(face_name, chars):
    key = (face_name, "".join(sorted(chars)))
    if key in _SUBSET_CACHE:
        return _SUBSET_CACHE[key]
    tt = TTFont(FONT_DIR / FACES[face_name])
    sub = Subsetter()
    sub.populate(text="".join(sorted(chars)))
    sub.subset(tt)
    tt.flavor = "woff2"
    buf = io.BytesIO()
    tt.save(buf)
    uri = f"data:font/woff2;base64,{base64.b64encode(buf.getvalue()).decode()}"
    _SUBSET_CACHE[key] = uri
    return uri


# --- SVG emission -----------------------------------------------------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, cls, anchor=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}"{a}>{esc(s)}</text>'


def rect(x, y, w, h, fill):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" fill="{fill}"/>')


STYLES = {
    "stamp": ("display-black", f"font-size:24px;fill:{ACCENT}"),
    "eyebrow": ("display-bold", "font-size:22px;letter-spacing:.16em"),
    "url": ("mono", f"font-size:20px;fill:{DIM}"),
    "headline": ("display-black", "font-size:68px;letter-spacing:-.03em"),
    "standfirst": ("serif-italic", "font-size:22px;font-style:italic"),
    "section": ("display-bold", "font-size:20px;letter-spacing:.16em"),
    "cardno": ("display-bold", f"font-size:18px;letter-spacing:.14em;fill:{ACCENT}"),
    "repo": ("display-black", "font-size:32px;letter-spacing:-.03em"),
    "desc": ("serif-italic", "font-size:17px;font-style:italic"),
    "stack": ("mono", f"font-size:15px;fill:{DIM}"),
    "colophon": ("display-bold", "font-size:19px;letter-spacing:.14em"),
    "tagline": ("serif-italic", f"font-size:19px;font-style:italic;fill:{DIM}"),
}


def piece(name, w, h, body, used, aria):
    """Emit one tile. `used` maps style class -> characters set in it, so each
    piece embeds only the faces and glyphs it actually needs."""
    needed = {}
    for cls, chars in used.items():
        face_name = STYLES[cls][0]
        needed.setdefault(face_name, set()).update(chars)

    css = "".join(
        f"@font-face{{font-family:'{f}';src:url({subset_uri(f, ch)}) format('woff2');}}"
        for f, ch in sorted(needed.items())
    )
    css += f"text{{fill:{INK}}}.accent{{fill:{ACCENT}}}"
    # Only the classes this tile actually sets. Keying off `needed` instead
    # would emit every class sharing a face, which quietly inflates the
    # accent count and ships dead rules.
    for cls in used:
        face_name, decl = STYLES[cls]
        css += f".{cls}{{font-family:'{face_name}';{decl}}}"

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h:.0f}" '
        f'viewBox="0 0 {w} {h:.0f}" role="img" aria-label="{esc(aria)}">'
        f"<style>{css}</style>"
        f'<rect width="{w}" height="{h:.0f}" fill="{PAPER}"/>'
        + "".join(body) + "</svg>"
    )
    path = OUT_DIR / f"{name}.svg"
    path.write_text(svg, encoding="utf-8")
    return path, len(svg)


# --- Pieces -----------------------------------------------------------------
def build_masthead():
    b, used = [], {}
    fb, fs = FACE["display-bold"], FACE["serif-italic"]

    b.append(rect(0, 0, W, RULE_HEAVY, INK))
    y = RULE_HEAVY + PAD

    st = 56
    b.append(
        f'<g transform="rotate(-4 {PAD + st / 2:.1f} {y + st / 2:.1f})">'
        f'<rect x="{PAD}" y="{y:.1f}" width="{st}" height="{st}" fill="none" '
        f'stroke="{ACCENT}" stroke-width="3"/>'
        f'{txt(PAD + st / 2, y + st / 2 + 9, "NS", "stamp", "middle")}</g>'
    )
    used["stamp"] = set("NS")

    ey = y + st / 2 + 7
    ex = PAD + st + 20
    b.append(txt(ex, ey, EYEBROW, "eyebrow"))
    sx = ex + fb.width(EYEBROW, 22, 0.16) + 8
    b.append(rect(sx, ey - 11, 6, 6, INK))
    b.append(txt(sx + 20, ey, EYEBROW_NO, "eyebrow accent"))
    b.append(txt(W - PAD, ey, URL, "url", "end"))
    used["eyebrow"] = set(EYEBROW + EYEBROW_NO)
    used["url"] = set(URL)

    y += st + 74
    for line in HEADLINE:
        if HEADLINE_PIVOT in line:
            before, after = line.split(HEADLINE_PIVOT, 1)
            b.append(
                f'<text x="{PAD}" y="{y:.1f}" class="headline">{esc(before)}'
                f'<tspan class="accent">{esc(HEADLINE_PIVOT)}</tspan>'
                f'{esc(after)}</text>'
            )
        else:
            b.append(txt(PAD, y, line, "headline"))
        y += 72
    used["headline"] = set("".join(HEADLINE))

    y += 4
    lines = wrap(STANDFIRST, fs, 22, W - PAD * 2 - 400)
    b.append(rect(PAD, y - 22, 5, len(lines) * 32, ACCENT))
    for line in lines:
        b.append(txt(PAD + 23, y, line, "standfirst"))
        y += 32
    used["standfirst"] = set(STANDFIRST)

    y += 44
    b.append(txt(PAD, y, SECTION, "section"))
    used["section"] = set(SECTION)
    y += 16
    b.append(rect(PAD, y, W - PAD * 2, 2, INK))
    y += 34

    aria = ("Nate Swenson. Field notes. Building in public, agent-first. "
            "Senior DevOps Engineer at GoodLeap. Shipping AI agents that "
            "automate incident analysis, debugging, and CI/CD decisions. "
            "Selected work follows.")
    return piece("masthead", W, y, b, used, aria)


def card_height():
    """Uniform across all four so the grid aligns, sized to the tallest
    description plus the row gap that follows it."""
    inner = HALF - PAD - INNER - CARD_PAD * 2
    longest = max(len(wrap(c["desc"], FACE["serif-italic"], 17, inner)) for c in CARDS)
    return RULE_MED + CARD_PAD + 28 + 34 + longest * 25 + 40 + CARD_PAD + ROW_GAP


def build_card(idx, card):
    """Left column carries the page margin on its left and a half-gutter on
    its right; the right column mirrors it. The cut lands on empty paper."""
    left_col = idx % 2 == 0
    x0 = PAD if left_col else INNER
    x1 = HALF - INNER if left_col else HALF - PAD
    cw = x1 - x0
    inner = cw - CARD_PAD * 2
    h = card_height()

    b, used = [], {}
    b.append(rect(x0, 0, cw, RULE_MED, INK))
    y = RULE_MED + CARD_PAD + 22

    b.append(txt(x0 + CARD_PAD, y, card["no"], "cardno"))
    used["cardno"] = set(card["no"])
    y += 34
    b.append(txt(x0 + CARD_PAD, y, card["repo"], "repo"))
    used["repo"] = set(card["repo"])
    y += 34
    for line in wrap(card["desc"], FACE["serif-italic"], 17, inner):
        b.append(txt(x0 + CARD_PAD, y, line, "desc"))
        y += 25
    used["desc"] = set(card["desc"])

    sy = h - ROW_GAP - CARD_PAD
    sx = x0 + CARD_PAD
    fm = FACE["mono"]
    for j, item in enumerate(card["stack"]):
        if j:
            b.append(rect(sx + 7, sy - 8, 5, 5, DIM))
            sx += 19
        b.append(txt(sx, sy, item, "stack"))
        sx += fm.width(item, 15)
    used["stack"] = set("".join(card["stack"]))

    aria = (f"{card['no']}. {card['repo']}. {card['desc']} "
            f"Built with {', '.join(card['stack'])}.")
    return piece(f"card-{card['no'].split('. ')[1]}", HALF, h, b, used, aria)


def build_colophon():
    """Two halves whose top rules meet at the cut to read as one rule."""
    h = RULE_MED + 30 + 28
    paths = []

    b, used = [], {}
    b.append(rect(PAD, 0, HALF - PAD, RULE_MED, INK))
    b.append(txt(PAD, RULE_MED + 30, COLOPHON_L, "colophon"))
    used["colophon"] = set(COLOPHON_L)
    paths.append(piece("colophon-l", HALF, h, b, used,
                       "Nate Swenson. Visit natejswenson.com."))

    b, used = [], {}
    b.append(rect(0, 0, HALF - PAD, RULE_MED, INK))
    b.append(txt(HALF - PAD, RULE_MED + 30, "linkedin.com/in/natejswenson",
                 "tagline", "end"))
    used["tagline"] = set("linkedin.com/in/natejswenson")
    paths.append(piece("colophon-r", HALF, h, b, used,
                       "Connect on LinkedIn at linkedin.com/in/natejswenson."))
    return paths


# --- README -----------------------------------------------------------------
RAW = "https://raw.githubusercontent.com/natejswenson/natejswenson/main/assets/press"


def tile(href, name, pct, alt):
    return (f'<a href="{href}"><img align="left" width="{pct}" '
            f'src="{RAW}/{name}.svg" alt="{esc(alt)}"></a>')


def build_readme():
    """Every tile floats left, so they butt together with no gaps. The tags
    must stay on adjacent lines with no blank line between them, or markdown
    splits them into separate paragraphs and the float chain breaks."""
    rows = [tile(SITE, "masthead", "100%",
                 "Nate Swenson, Senior DevOps Engineer at GoodLeap. Building in "
                 "public, agent-first: shipping AI agents that automate incident "
                 "analysis, debugging, and CI/CD decisions. Selected work:")]
    for card in CARDS:
        rows.append(tile(
            card["href"], f"card-{card['no'].split('. ')[1]}", "50%",
            f"{card['no']} {card['repo']}. {card['desc']} "
            f"Built with {', '.join(card['stack'])}."))
    rows.append(tile(SITE, "colophon-l", "50%", "Nate Swenson. natejswenson.com"))
    rows.append(tile(LINKEDIN, "colophon-r", "50%", "linkedin.com/in/natejswenson"))
    return "\n".join(rows) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    built = [build_masthead()]
    built += [build_card(i, c) for i, c in enumerate(CARDS)]
    built += build_colophon()
    for path, size in built:
        total += size
        print(f"  {path.relative_to(ROOT)}  {size / 1024:.0f} KB")
    (ROOT / "README.md").write_text(build_readme(), encoding="utf-8")
    print(f"wrote {len(built)} tiles, {total / 1024:.0f} KB total, and README.md")


if __name__ == "__main__":
    main()
