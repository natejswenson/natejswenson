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
`float:left`. Floated images are out of normal flow, so they stack edge to
edge with none of the line-height gaps that stacked inline images get.
Measured in the browser against the real page: consecutive floats land
exactly one tile height apart, zero gap. That means the page can be cut
into pieces -- each its own <a> -- and still read as one document.

Every tile is full width, and that is forced, not a preference. GitHub
styles `img[align=left]` with `padding-right:20px` under `box-sizing:
content-box`, so a 50% tile measures `50% + 20px`. Two of them overflow
any container and wrap, which is exactly how the earlier two-column grid
broke. Full-width tiles absorb the stray 20px as transparent overflow past
the margin, where nothing shows.

So the page is a single column, which is also what the site does -- its
`.entry-list` is a numbered ledger, not a grid:

    masthead      -> natejswenson.com
    ledger 001-004 -> one repo each
    colophon x2   -> natejswenson.com, linkedin

Each piece embeds only the glyphs it actually sets, subset to woff2, since
an <img> SVG cannot fetch fonts.
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
# Every tile is W wide. See the module docstring for why partial widths are
# not an option.
W = 1200            # full design width
PAD = 64            # outer page margin
RULE_HEAVY = 10
RULE_MED = 6
RULE_LEDGER = 2     # the divider between ledger rows, per the site's entry-list

# Ledger row internals: identity stacked at the left, commentary at the right.
ROW_H = 168
COL_REPO = PAD              # numeral, repo name, stack
COL_DESC = 500              # the description block
COL_DESC_W = W - PAD - COL_DESC

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
    "repo": ("display-black", "font-size:34px;letter-spacing:-.03em"),
    "desc": ("serif-italic", "font-size:18px;font-style:italic"),
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
    # No rule here: row-001 draws the divider, and two 2px rules a few pixels
    # apart read as a printing error.
    y += 30

    aria = ("Nate Swenson. Field notes. Building in public, agent-first. "
            "Senior DevOps Engineer at GoodLeap. Shipping AI agents that "
            "automate incident analysis, debugging, and CI/CD decisions. "
            "Selected work follows.")
    return piece("masthead", W, y, b, used, aria)


def build_row(card):
    """A full-width ledger row: numeral and name at the left, the commentary
    in the middle, the stack right-aligned. Rows are separated by a hairline
    ink rule, the way the site's entry-list separates entries."""
    b, used = [], {}
    b.append(rect(PAD, 0, W - PAD * 2, RULE_LEDGER, INK))

    b.append(txt(COL_REPO, 54, card["no"], "cardno"))
    used["cardno"] = set(card["no"])
    b.append(txt(COL_REPO, 96, card["repo"], "repo"))
    used["repo"] = set(card["repo"])

    y = 52
    for line in wrap(card["desc"], FACE["serif-italic"], 18, COL_DESC_W):
        b.append(txt(COL_DESC, y, line, "desc"))
        y += 27
    used["desc"] = set(card["desc"])

    # Stack sits under the repo name, in the identity column. Right-aligning
    # it against the margin put it hard alongside the description's last
    # line, which read as a collision.
    fm = FACE["mono"]
    sx, sy = COL_REPO, 130
    for j, item in enumerate(card["stack"]):
        if j:
            b.append(rect(sx + 7, sy - 8, 5, 5, DIM))
            sx += 19
        b.append(txt(sx, sy, item, "stack"))
        sx += fm.width(item, 15)
    used["stack"] = set("".join(card["stack"]))

    aria = (f"{card['no']}. {card['repo']}. {card['desc']} "
            f"Built with {', '.join(card['stack'])}.")
    return piece(f"row-{card['no'].split('. ')[1]}", W, ROW_H, b, used, aria)


def build_colophon():
    """Two full-width rows, so both contacts get their own link target. The
    first carries the closing rule; the second sits under it."""
    paths = []

    b, used = [], {}
    b.append(rect(PAD, 0, W - PAD * 2, RULE_MED, INK))
    b.append(txt(PAD, RULE_MED + 40, COLOPHON_L, "colophon"))
    b.append(txt(W - PAD, RULE_MED + 40, URL, "tagline", "end"))
    used["colophon"] = set(COLOPHON_L)
    used["tagline"] = set(URL)
    paths.append(piece("colophon-a", W, RULE_MED + 62, b, used,
                       "Nate Swenson. Visit natejswenson.com."))

    b, used = [], {}
    b.append(txt(PAD, 26, "Shipped features, the tradeoffs, and what broke.",
                 "tagline"))
    b.append(txt(W - PAD, 26, "linkedin.com/in/natejswenson", "tagline", "end"))
    used["tagline"] = set("Shipped features, the tradeoffs, and what broke."
                          "linkedin.com/in/natejswenson")
    paths.append(piece("colophon-b", W, 26 + PAD, b, used,
                       "Building in public. Connect on LinkedIn at "
                       "linkedin.com/in/natejswenson."))
    return paths


# --- README -----------------------------------------------------------------
RAW = "https://raw.githubusercontent.com/natejswenson/natejswenson/main/assets/press"


def tile(href, name, pct, alt):
    return (f'<a href="{href}"><img align="left" width="{pct}" '
            f'src="{RAW}/{name}.svg" alt="{esc(alt)}"></a>')


def build_readme():
    """Every tile floats left at full width, so they stack with no gaps. The
    tags must stay on adjacent lines with no blank line between them, or
    markdown splits them into separate paragraphs and the float chain breaks."""
    rows = [tile(SITE, "masthead", "100%",
                 "Nate Swenson, Senior DevOps Engineer at GoodLeap. Building in "
                 "public, agent-first: shipping AI agents that automate incident "
                 "analysis, debugging, and CI/CD decisions. Selected work:")]
    for card in CARDS:
        rows.append(tile(
            card["href"], f"row-{card['no'].split('. ')[1]}", "100%",
            f"{card['no']} {card['repo']}. {card['desc']} "
            f"Built with {', '.join(card['stack'])}."))
    rows.append(tile(SITE, "colophon-a", "100%", "Nate Swenson. natejswenson.com"))
    rows.append(tile(LINKEDIN, "colophon-b", "100%",
                     "Building in public. linkedin.com/in/natejswenson"))
    return "\n".join(rows) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    built = [build_masthead()]
    built += [build_row(c) for c in CARDS]
    built += build_colophon()
    for path, size in built:
        total += size
        print(f"  {path.relative_to(ROOT)}  {size / 1024:.0f} KB")
    (ROOT / "README.md").write_text(build_readme(), encoding="utf-8")
    print(f"wrote {len(built)} tiles, {total / 1024:.0f} KB total, and README.md")


if __name__ == "__main__":
    main()
