#!/usr/bin/env python3
"""Render the Selected work cards as PRESS artifacts.

GitHub sanitizes all CSS out of README markdown -- no style attributes, no
<style> block -- so a markdown table renders in GitHub's own chrome: white
canvas, blue links, gray code pills. The only way to put the brand on this
section is to draw it. Each card is wrapped in a link in README.md, so the
cards stay clickable.

THE ACCENT LAW on a card: the ledger numeral is the single orange element.
The law permits a numeral "only if it's a real number" -- No. 001 is one.
The repo name is the headline and stays ink; there is no stamp here (the
banner carries it for the page).
"""

from pathlib import Path

from PIL import ImageDraw

import press

# Height is sized to the longest description (3 wrapped lines) and held
# uniform across all four so the 2x2 grid stays aligned. Shorter cards carry
# a little extra whitespace under the description, which is the PRESS
# preference anyway -- structure comes from rules and whitespace.
WIDTH, HEIGHT = 880, 350
PAD = 44
RULE_TOP = 6

OUT_DIR = Path(__file__).parent / "assets" / "cards"

# Order is the ledger order. Description doubles as the README alt text, so
# it has to read as a sentence on its own -- for screen readers and for
# GitHub search, which cannot see into a PNG.
CARDS = [
    {
        "no": "No. 001",
        "repo": "local-fitness",
        "desc": "Agent-first fitness coach. Pulls Garmin data into a local SQLite "
                "database and exposes deterministic training-load math (CTL / ATL / "
                "TSB) to Claude over MCP.",
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


def render_card(card):
    canvas = press.new_canvas(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(canvas)

    f_no = press.font(press.DISPLAY_BOLD, 22)
    f_repo = press.font(press.DISPLAY_BLACK, 44)
    f_desc = press.font(press.SERIF_ITALIC, 23)
    f_stack = press.font(press.MONO, 18)

    left = press.px(PAD)
    right = press.px(WIDTH - PAD)
    usable = right - left

    # Card top rule -- each card is its own small poster.
    draw.rectangle([0, 0, press.px(WIDTH), press.px(RULE_TOP)], fill=press.INK)

    y = press.px(PAD + RULE_TOP)

    # Ledger numeral: the one accent on this artifact.
    press.draw_tracked(draw, (left, y), card["no"], f_no, press.ACCENT, tracking=0.14)

    # Repo name, ink, tight tracking.
    y += press.px(42)
    press.draw_tracked(draw, (left, y), card["repo"], f_repo, press.INK, tracking=-0.03)

    # Description, serif italic -- the commentary voice.
    y += press.px(64)
    for line in press.wrap(draw, card["desc"], f_desc, usable):
        draw.text((left, y), line, font=f_desc, fill=press.INK)
        y += f_desc.size * 1.45

    # Stack, mono dim, pinned to the bottom with square separators. Mono is
    # the data voice; the stack is data, not prose.
    stack_y = press.px(HEIGHT - PAD) - f_stack.size
    x = left
    for i, item in enumerate(card["stack"]):
        if i:
            x = press.draw_sep_square(draw, x + press.px(9), stack_y, f_stack,
                                      size=5, fill=press.DIM)
            x += press.px(9)
        draw.text((x, stack_y), item, font=f_stack, fill=press.DIM)
        x += draw.textlength(item, font=f_stack)

    return canvas


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for card in CARDS:
        path = OUT_DIR / f"card-{card['no'].split('. ')[1]}.png"
        img = press.finish(render_card(card), WIDTH, HEIGHT, path)
        print(f"wrote {path.relative_to(Path(__file__).parent)}  "
              f"{img.width}x{img.height}  {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
