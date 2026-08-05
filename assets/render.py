#!/usr/bin/env python3
"""Render about.yml as a Carbon-style code card (SVG), light and dark."""

import re
from html import escape
from pathlib import Path

HERE = Path(__file__).parent
SRC = (HERE / "about.yml").read_text().rstrip("\n").split("\n")

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SIZE = 15
CW = SIZE * 0.6         # monospace advance width
LH = 25                 # line height
PAD = 26                # padding inside the window
CHROME = 42             # title-bar height
MARGIN = 34             # backdrop padding around the window

THEMES = {
    "dark": {
        "grad": ("#12343b", "#1b4b4f", "#2c5364"),
        "win": "#282c34", "text": "#abb2bf", "key": "#e06c75",
        "module": "#61afef", "val": "#d19a66", "str": "#98c379",
        "comment": "#5c6370", "punct": "#7f848e",
    },
    "light": {
        "grad": ("#dfe9f3", "#c9dfd4", "#b8d8c7"),
        "win": "#fafafa", "text": "#383a42", "key": "#a626a4",
        "module": "#4078f2", "val": "#986801", "str": "#50a14f",
        "comment": "#a0a1a7", "punct": "#696c77",
    },
}

KEYLINE = re.compile(r"^([A-Za-z0-9_.'\- ]+?):(\s*)(.*)$")


def tokenize(line):
    """-> list of (text, role). Roles map onto theme colours."""
    indent = len(line) - len(line.lstrip(" "))
    out = [(" " * indent, "text")]
    rest = line[indent:]

    if rest.startswith("#"):
        return out + [(rest, "comment")]

    if rest.startswith("- "):
        out.append(("- ", "punct"))
        rest = rest[2:]

    match = KEYLINE.match(rest)
    if not match:
        return out + [(rest, "text")]

    key, gap, value = match.groups()
    out.append((key, "module" if "." in key else "key"))
    out.append((":", "punct"))
    out.append((gap, "text"))

    if not value:
        return out
    if value.startswith('"'):
        out.append((value, "str"))
    elif value.startswith("["):
        out.append(("[", "punct"))
        items = value[1:-1].split(", ")
        for i, item in enumerate(items):
            if i:
                out.append((", ", "punct"))
            out.append((item, "val"))
        out.append(("]", "punct"))
    else:
        out.append((value, "val"))
    return out


def render(theme_name):
    t = THEMES[theme_name]
    width_chars = max(len(line) for line in SRC)
    win_w = round(PAD * 2 + width_chars * CW)
    win_h = CHROME + PAD + len(SRC) * LH
    w, h = win_w + MARGIN * 2, win_h + MARGIN * 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        f'<stop offset="0%" stop-color="{t["grad"][0]}"/>',
        f'<stop offset="55%" stop-color="{t["grad"][1]}"/>',
        f'<stop offset="100%" stop-color="{t["grad"][2]}"/>',
        "</linearGradient>",
        '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">',
        '<feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000" flood-opacity="0.34"/>',
        "</filter>",
        "</defs>",
        f'<rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>',
        f'<rect x="{MARGIN}" y="{MARGIN}" width="{win_w}" height="{win_h}" rx="11" '
        f'fill="{t["win"]}" filter="url(#sh)"/>',
    ]

    # traffic lights
    for i, colour in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        cx = MARGIN + PAD + i * 20
        parts.append(f'<circle cx="{cx}" cy="{MARGIN + 21}" r="6" fill="{colour}"/>')

    parts.append(
        f'<text x="{MARGIN + win_w / 2}" y="{MARGIN + 26}" fill="{t["comment"]}" '
        f'font-size="12" text-anchor="middle">about.yml</text>'
    )

    # code
    for row, line in enumerate(SRC):
        y = MARGIN + CHROME + PAD / 2 + row * LH + SIZE
        spans = []
        col = 0
        for text, role in tokenize(line):
            if text:
                x = MARGIN + PAD + col * CW
                style = ' font-style="italic"' if role == "comment" else ""
                spans.append(
                    f'<tspan x="{x:.1f}" fill="{t[role]}"{style}>{escape(text)}</tspan>'
                )
                col += len(text)
        if spans:
            parts.append(
                f'<text y="{y:.1f}" font-size="{SIZE}" xml:space="preserve">'
                + "".join(spans)
                + "</text>"
            )

    parts.append("</svg>")
    return "\n".join(parts)


for name in THEMES:
    out = HERE / f"about-{name}.svg"
    out.write_text(render(name) + "\n")
    print(f"wrote {out.name}  ({out.stat().st_size:,} bytes)")
