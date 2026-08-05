#!/usr/bin/env python3
"""Render an animated `ansible-playbook` run as a self-playing SVG.

Lines reveal one at a time, hold, then the whole thing loops. Animation is
pure SMIL so it plays inside a GitHub README via a plain <img>.
"""

from datetime import date
from html import escape
from pathlib import Path

HERE = Path(__file__).parent

# --- the only things worth editing -----------------------------------------
THESIS_DUE = date(2027, 3, 1)
ECTS_DONE, ECTS_TOTAL = 60, 90
COLS = 66                      # terminal width the run is "printed" at
# ---------------------------------------------------------------------------

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SIZE = 14
CW = SIZE * 0.6
LH = 22
PAD = 24
CHROME = 40
MARGIN = 30

REVEAL = 0.24      # seconds between lines
HOLD = 3.4         # seconds the finished frame stays up

THEMES = {
    "dark": {
        "grad": ("#12343b", "#1b4b4f", "#2c5364"), "win": "#22262e",
        "plain": "#abb2bf", "bright": "#e6edf3", "dim": "#525c6b",
        "ok": "#98c379", "changed": "#e5c07b", "failed": "#e06c75",
    },
    "light": {
        "grad": ("#dfe9f3", "#c9dfd4", "#b8d8c7"), "win": "#fbfbfb",
        "plain": "#383a42", "bright": "#1b1c1f", "dim": "#a8adb7",
        "ok": "#3f8a3f", "changed": "#9a6b00", "failed": "#c8392e",
    },
}


def banner(label):
    """`TASK [x] ****` padded out the way ansible pads it."""
    head = f"{label} "
    return [(head, "bright"), ("*" * max(3, COLS - len(head)), "dim")]


def result(status, host, detail):
    tokens = [(f"{status}: ", status), (f"[{host}]", "plain")]
    if detail:
        tokens.append((f" => {detail}", "plain"))
    return tokens


def build():
    days = (THESIS_DUE - date.today()).days
    lines = []
    add = lines.append

    add(banner("PLAY [dmitrijs sizovs]"))
    add([])

    add(banner("TASK [Learn devops]"))
    for item in ("intern", "devops engineer i", "devops engineer ii"):
        add(result("ok", "swisscom", f"(item={item})"))
    add([])

    add(banner("TASK [Connect nemo hpc to galaxy eu via pulsar]"))
    add(result("changed", "usegalaxy.eu", "nobody had done this one before"))
    add([])

    add(banner("TASK [Upstream a pulsar bugfix]"))
    add(result("changed", "usegalaxy.eu", "(pr=galaxyproject/pulsar#460)"))
    add([])

    add(banner("TASK [Hand ansible roles to usegalaxy]"))
    for item in ("pulsar-relay-role", "pulsar-nemo-login-role"):
        add(result("changed", "usegalaxy.eu", f"(item={item})"))
    add([])

    add(banner("TASK [Run computer vision at the edge]"))
    add(result("ok", "free time", "novuss-vision"))
    add([])

    add(banner("TASK [Collect ects]"))
    add(result("changed", "freiburg.de", f"{ECTS_DONE}/{ECTS_TOTAL}"))
    add([])

    add(banner("TASK [Submit thesis]"))
    add([("FAILED - RETRYING: Submit thesis ", "failed"),
         (f"({days} retries left)", "failed")])
    add([])

    add(banner("PLAY RECAP"))
    for host, ok, changed in (("swisscom", 3, 0), ("usegalaxy.eu", 0, 4),
                              ("freiburg.de", 1, 1)):
        add([(f"{host:<13}: ", "plain"),
             (f"ok={ok}", "ok"), ("  ", "plain"),
             (f"changed={changed}", "changed"), ("  ", "plain"),
             ("unreachable=0  ", "plain"), ("failed=0", "ok")])
    return lines


def render(theme_name, lines):
    t = THEMES[theme_name]
    widest = max((sum(len(x) for x, _ in ln) for ln in lines), default=COLS)
    win_w = round(PAD * 2 + widest * CW)
    win_h = CHROME + PAD + len(lines) * LH
    w, h = win_w + MARGIN * 2, win_h + MARGIN * 2

    # timeline: only non-empty lines consume a reveal slot
    times, clock = [], 0.15
    for ln in lines:
        times.append(clock)
        if ln:
            clock += REVEAL
    total = clock + HOLD

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        *(f'<stop offset="{o}%" stop-color="{c}"/>'
          for o, c in zip((0, 55, 100), t["grad"])),
        "</linearGradient>",
        '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">',
        '<feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000" flood-opacity="0.34"/>',
        "</filter>",
        "</defs>",
        f'<rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>',
        f'<rect x="{MARGIN}" y="{MARGIN}" width="{win_w}" height="{win_h}" rx="11" '
        f'fill="{t["win"]}" filter="url(#sh)"/>',
    ]
    for i, colour in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{MARGIN + PAD + i * 20}" cy="{MARGIN + 20}" r="6" fill="{colour}"/>')
    out.append(
        f'<text x="{MARGIN + win_w / 2}" y="{MARGIN + 25}" fill="{t["dim"]}" '
        f'font-size="11.5" text-anchor="middle">ansible-playbook about.yml</text>'
    )

    for row, (tokens, start) in enumerate(zip(lines, times)):
        if not tokens:
            continue
        y = MARGIN + CHROME + PAD / 2 + row * LH + SIZE
        spans, col = [], 0
        for text, role in tokens:
            x = MARGIN + PAD + col * CW
            spans.append(
                f'<tspan x="{x:.1f}" fill="{t[role]}">{escape(text)}</tspan>'
            )
            col += len(text)

        # hold at 0 until this line's turn, snap on, hold, clear for the loop
        a = start / total
        b = min(a + 0.004, 0.95)
        anim = (
            f'<animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="0;{a:.4f};{b:.4f};0.965;1" '
            f'dur="{total:.2f}s" repeatCount="indefinite"/>'
        )
        out.append(
            f'<text y="{y:.1f}" font-size="{SIZE}" opacity="0" xml:space="preserve">'
            + "".join(spans) + anim + "</text>"
        )

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    lines = build()
    for name in THEMES:
        path = HERE / f"run-{name}.svg"
        path.write_text(render(name, lines) + "\n")
        print(f"wrote {path.name} ({path.stat().st_size:,} bytes)")
    print(f"thesis countdown: {(THESIS_DUE - date.today()).days} days")
