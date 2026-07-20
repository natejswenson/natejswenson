#!/usr/bin/env python3
"""Build profile.svg -- the whole README as one PRESS document, styled in CSS.

Why SVG and not HTML: GitHub's markdown sanitizer strips every `style` and
`class` attribute, escapes `<style>` blocks, and removes inline `<svg>`
entirely. Verified against the GitHub markdown API, four vectors, all
blocked. The one thing that survives is `<img src="....svg">` -- and an
external SVG keeps its own internal stylesheet, because the browser renders
it as a real document. So this is genuine CSS, just delivered through the
only door GitHub leaves open.

That buys three things over drawing to a bitmap: real cascade and selectors,
vector output that stays sharp at any zoom or DPI, and a file that is
authored rather than plotted.

Fonts must be embedded. An SVG loaded through <img> is isolated -- it cannot
fetch anything external -- so the brand faces are subset to the glyphs
actually used, converted to woff2, and inlined as data URIs. Subsetting is
what keeps that from being half a megabyte.

SVG has no text flow, so line breaking is still done here, but measured
properly against each font's real advance widths rather than guessed.
"""

import base64
import io
from pathlib import Path

from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).parent
FONT_DIR = ROOT / "assets" / "fonts"
OUTPUT = ROOT / "profile.svg"

# --- PRESS tokens -----------------------------------------------------------
# Canonical source: natejswenson.io/src/styles/global.css `:root`.
PAPER = "#F5F0E6"
INK = "#181510"
DIM = "#6E675C"
ACCENT = "#E8501F"

# --- Faces ------------------------------------------------------------------
FACES = {
    "display-black": "Inter-Black.ttf",
    "display-bold": "Inter-Bold.ttf",
    "serif-italic": "IBMPlexSerif-Italic.ttf",
    "mono": "IBMPlexMono-Regular.ttf",
}

# --- Page geometry ----------------------------------------------------------
W = 1200
PAD = 64
RULE_HEAVY = 10
RULE_MED = 6
CARD_GAP = 28
CARD_PAD = 30

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
# Two runs with a square between them. SVG collapses runs of whitespace, so
# spacing cannot carry the separation -- and the Inter/Plex subsets have no
# U+00B7 anyway. Drawn squares are the house separator throughout.
COLOPHON_R = ["natejswenson.com", "linkedin.com/in/natejswenson"]

CARDS = [
    {
        "no": "No. 001",
        "repo": "local-fitness",
        "desc": "Agent-first fitness coach. Pulls Garmin data into a local SQLite "
                "database and exposes deterministic training-load math "
                "(CTL / ATL / TSB) to Claude over MCP.",
        "stack": ["Python", "MCP", "SQLite", "Flask"],
    },
    {
        "no": "No. 002",
        "repo": "traefik-local-cli",
        "desc": "Onboards any local app to a hardened Traefik proxy at "
                "<app>.internal, driven by a bundled Claude Code skill with hard "
                "pass/fail gates.",
        "stack": ["Bash", "Claude Code", "Docker"],
    },
    {
        "no": "No. 003",
        "repo": "claude-skills",
        "desc": "Monorepo of independently-released Claude Code productivity "
                "skills: devlog, ghostwriter, resume, github-stats. Namespaced "
                "releases and path-filtered CI.",
        "stack": ["JavaScript", "Python", "Bash"],
    },
    {
        "no": "No. 004",
        "repo": "local-budget",
        "desc": "Local-first Wells Fargo spending agent. One SQLite database "
                "behind a column-level authorizer, exposed through a stdio MCP "
                "server and no-code Claude skills.",
        "stack": ["Python", "MCP", "SQLite", "Docker"],
    },
]


# --- Type measurement -------------------------------------------------------
class Face:
    """A loaded face that can measure a string the way a renderer will."""

    def __init__(self, path):
        self.path = path
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.hmtx = self.tt["hmtx"]
        self.glyphs = self.tt.getGlyphOrder()

    def advance(self, ch):
        name = self.cmap.get(ord(ch))
        if name is None:
            name = ".notdef" if ".notdef" in self.glyphs else self.glyphs[0]
        return self.hmtx[name][0] / self.upem

    def width(self, text, size, tracking=0.0):
        """Width in px, including letter-spacing. CSS letter-spacing adds after
        every glyph including the last, which is what SVG renderers do too."""
        return sum(self.advance(c) * size + tracking * size for c in text)


FACE_OBJS = {k: Face(FONT_DIR / v) for k, v in FACES.items()}


def wrap(text, face, size, max_w, tracking=0.0):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if face.width(trial, size, tracking) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --- Font embedding ---------------------------------------------------------
def collect_glyphs():
    """Every character the document actually sets, per face."""
    used = {k: set() for k in FACES}
    used["display-bold"] |= set(EYEBROW + EYEBROW_NO + SECTION + COLOPHON_L)
    used["display-black"] |= set("".join(HEADLINE) + "NS")
    used["serif-italic"] |= set(STANDFIRST + "".join(COLOPHON_R))
    used["mono"] |= set(URL)
    for c in CARDS:
        used["display-bold"] |= set(c["no"])
        used["display-black"] |= set(c["repo"])
        used["serif-italic"] |= set(c["desc"])
        used["mono"] |= set("".join(c["stack"]))
    return used


def embed(name, chars):
    """Subset to `chars`, convert to woff2, return a data URI.

    Subsetting is the difference between a ~25 KB file and a ~500 KB one --
    the full four faces are 364 KB of TTF before base64 inflates them.
    """
    tt = TTFont(FONT_DIR / FACES[name])
    sub = Subsetter()
    sub.populate(text="".join(sorted(chars)))
    sub.subset(tt)
    tt.flavor = "woff2"
    buf = io.BytesIO()
    tt.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:font/woff2;base64,{b64}", len(buf.getvalue())


# --- SVG emission -----------------------------------------------------------
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def text(x, y, s, cls, anchor=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}"{a}>{esc(s)}</text>'


def rect(x, y, w, h, fill):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>'


def build():
    body = []
    fb = FACE_OBJS["display-bold"]
    fbl = FACE_OBJS["display-black"]
    fs = FACE_OBJS["serif-italic"]

    # ---- Masthead ----------------------------------------------------------
    body.append(rect(0, 0, W, RULE_HEAVY, INK))
    y = RULE_HEAVY + PAD

    # Stamp: rotated square with the monogram. A transform, not a raster trick.
    st = 56
    body.append(
        f'<g transform="rotate(-4 {PAD + st / 2:.1f} {y + st / 2:.1f})">'
        f'<rect x="{PAD}" y="{y:.1f}" width="{st}" height="{st}" '
        f'fill="none" stroke="{ACCENT}" stroke-width="3"/>'
        f'{text(PAD + st / 2, y + st / 2 + 9, "NS", "stamp", "middle")}</g>'
    )

    # Eyebrow, vertically centered on the stamp.
    ey = y + st / 2 + 7
    ex = PAD + st + 20
    body.append(text(ex, ey, EYEBROW, "eyebrow"))
    sep_x = ex + fb.width(EYEBROW, 22, 0.16) + 8
    body.append(rect(sep_x, ey - 11, 6, 6, INK))
    body.append(text(sep_x + 20, ey, EYEBROW_NO, "eyebrow accent"))
    body.append(text(W - PAD, ey, URL, "url", "end"))

    # Headline. The pivot is a <tspan>, so the accent is one span in one run --
    # no manual pen positioning, the renderer handles the advance.
    y += st + 74
    for line in HEADLINE:
        if HEADLINE_PIVOT in line:
            before, after = line.split(HEADLINE_PIVOT, 1)
            inner = (f"{esc(before)}<tspan class='accent'>{esc(HEADLINE_PIVOT)}</tspan>"
                     f"{esc(after)}")
            body.append(f'<text x="{PAD}" y="{y:.1f}" class="headline">{inner}</text>')
        else:
            body.append(text(PAD, y, line, "headline"))
        y += 72

    # Standfirst behind its accent rule.
    y += 4
    sf_lines = wrap(STANDFIRST, fs, 22, W - PAD * 2 - 400)
    sf_h = len(sf_lines) * 32
    body.append(rect(PAD, y - 22, 5, sf_h, ACCENT))
    for line in sf_lines:
        body.append(text(PAD + 23, y, line, "standfirst"))
        y += 32

    # ---- Section label -----------------------------------------------------
    y += 44
    body.append(text(PAD, y, SECTION, "section"))
    y += 16
    body.append(rect(PAD, y, W - PAD * 2, 2, INK))
    y += 34

    # ---- Card grid ---------------------------------------------------------
    cw = (W - PAD * 2 - CARD_GAP) / 2
    inner_w = cw - CARD_PAD * 2

    # Uniform height across all four, sized to the tallest description, so the
    # grid stays aligned. Whitespace under a short card is the PRESS default.
    max_lines = max(len(wrap(c["desc"], fs, 17, inner_w)) for c in CARDS)
    ch = CARD_PAD + 22 + 40 + max_lines * 25 + 34 + CARD_PAD

    for i, card in enumerate(CARDS):
        cx = PAD + (i % 2) * (cw + CARD_GAP)
        cy = y + (i // 2) * (ch + CARD_GAP)
        body.append(rect(cx, cy, cw, RULE_MED, INK))
        ty = cy + RULE_MED + CARD_PAD + 6
        # The ledger numeral is this card's single accent.
        body.append(text(cx + CARD_PAD, ty, card["no"], "cardno accent"))
        ty += 40
        body.append(text(cx + CARD_PAD, ty, card["repo"], "repo"))
        ty += 34
        for line in wrap(card["desc"], fs, 17, inner_w):
            body.append(text(cx + CARD_PAD, ty, line, "desc"))
            ty += 25
        # Stack pinned to the card's baseline.
        sy = cy + ch - CARD_PAD
        sx = cx + CARD_PAD
        fm = FACE_OBJS["mono"]
        for j, item in enumerate(card["stack"]):
            if j:
                body.append(rect(sx + 7, sy - 8, 5, 5, DIM))
                sx += 19
            body.append(text(sx, sy, item, "stack"))
            sx += fm.width(item, 15)

    y += ch * 2 + CARD_GAP

    # ---- Colophon ----------------------------------------------------------
    y += 40
    body.append(rect(PAD, y, W - PAD * 2, RULE_MED, INK))
    y += RULE_MED + 30
    body.append(text(PAD, y, COLOPHON_L, "colophon"))
    # Lay the two right-hand runs out from a computed left edge so the pair
    # ends flush with the margin.
    gap, sq = 12, 5
    widths = [fs.width(s, 19) for s in COLOPHON_R]
    cx = W - PAD - (sum(widths) + gap * 2 + sq)
    for j, s in enumerate(COLOPHON_R):
        if j:
            body.append(rect(cx + gap - 3, y - 7, sq, sq, DIM))
            cx += gap * 2 - 6 + sq
        body.append(text(cx, y, s, "tagline"))
        cx += widths[j]
    height = y + PAD

    # ---- Stylesheet --------------------------------------------------------
    used = collect_glyphs()
    faces_css, total = [], 0
    for name, chars in used.items():
        uri, size = embed(name, chars)
        total += size
        faces_css.append(
            f"@font-face{{font-family:'{name}';src:url({uri}) format('woff2');}}"
        )

    css = "".join(faces_css) + f"""
.bg{{fill:{PAPER}}}
text{{fill:{INK}}}
.accent{{fill:{ACCENT}}}
.stamp{{font-family:'display-black';font-size:24px;fill:{ACCENT}}}
.eyebrow{{font-family:'display-bold';font-size:22px;letter-spacing:.16em}}
.url{{font-family:'mono';font-size:20px;fill:{DIM}}}
.headline{{font-family:'display-black';font-size:68px;letter-spacing:-.03em}}
.standfirst{{font-family:'serif-italic';font-size:22px;font-style:italic}}
.section{{font-family:'display-bold';font-size:20px;letter-spacing:.16em}}
.cardno{{font-family:'display-bold';font-size:18px;letter-spacing:.14em}}
.repo{{font-family:'display-black';font-size:32px;letter-spacing:-.03em}}
.desc{{font-family:'serif-italic';font-size:17px;font-style:italic}}
.stack{{font-family:'mono';font-size:15px;fill:{DIM}}}
.colophon{{font-family:'display-bold';font-size:19px;letter-spacing:.14em}}
.tagline{{font-family:'serif-italic';font-size:19px;font-style:italic;fill:{DIM}}}
"""

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height:.0f}" '
        f'viewBox="0 0 {W} {height:.0f}" role="img" '
        f'aria-label="Nate Swenson, Senior DevOps Engineer at GoodLeap. '
        f'Selected work: local-fitness, traefik-local-cli, claude-skills, local-budget.">'
        f"<style>{css}</style>"
        f'<rect class="bg" width="{W}" height="{height:.0f}"/>'
        + "".join(body)
        + "</svg>"
    )
    return svg, height, total


def main():
    svg, height, font_bytes = build()
    OUTPUT.write_text(svg, encoding="utf-8")
    kb = OUTPUT.stat().st_size / 1024
    print(f"wrote {OUTPUT.name}  {W}x{height:.0f}  {kb:.0f} KB "
          f"(subset fonts: {font_bytes / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
