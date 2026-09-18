#!/usr/bin/env python3
"""Pixel-art SVG cards for the GitHub profile README: stats, contribution snake, tech stack."""

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

GLYPHS = {
    "A": ".###.#...##...#######...##...##...#",
    "B": "####.#...##...#####.#...##...#####.",
    "C": ".###.#...##....#....#....#...#.###.",
    "D": "####.#...##...##...##...##...#####.",
    "E": "######....#....####.#....#....#####",
    "F": "######....#....####.#....#....#....",
    "G": ".###.#...##....#.####...##...#.####",
    "H": "#...##...##...#######...##...##...#",
    "I": ".###...#....#....#....#....#...###.",
    "J": "..###...#....#....#.#..#.#..#..##..",
    "K": "#...##..#.#.#..##...#.#..#..#.#...#",
    "L": "#....#....#....#....#....#....#####",
    "M": "#...###.###.#.##.#.##...##...##...#",
    "N": "#...##...###..##.#.##..###...##...#",
    "O": ".###.#...##...##...##...##...#.###.",
    "P": "####.#...##...#####.#....#....#....",
    "Q": ".###.#...##...##...##.#.##..#..##.#",
    "R": "####.#...##...#####.#.#..#..#.#...#",
    "S": ".#####....#.....###.....#....#####.",
    "T": "#####..#....#....#....#....#....#..",
    "U": "#...##...##...##...##...##...#.###.",
    "V": "#...##...##...##...##...#.#.#...#..",
    "W": "#...##...##...##.#.##.#.##.#.#.#.#.",
    "X": "#...##...#.#.#...#...#.#.#...##...#",
    "Y": "#...##...#.#.#...#....#....#....#..",
    "Z": "#####....#...#...#...#...#....#####",
    "0": ".###.#...##..###.#.###..##...#.###.",
    "1": "..#...##....#....#....#....#...###.",
    "2": ".###.#...#....#...#...#...#...#####",
    "3": "####.....#....#.###.....#....#####.",
    "4": "...#...##..#.#.#..#.#####...#....#.",
    "5": "######....####.....#....##...#.###.",
    "6": ".###.#....#....####.#...##...#.###.",
    "7": "#####....#...#...#...#....#....#...",
    "8": ".###.#...##...#.###.#...##...#.###.",
    "9": ".###.#...##...#.####....#....#.###.",
    " ": "." * 35,
    ":": "..........#..............#.........",
    ".": "." * 30 + "..#..",
    ",": "." * 25 + "..#...#...",
    "-": "." * 15 + ".###." + "." * 15,
    "%": "##..###.#....#...#...#....#.###..##",
    "/": "....#...#....#...#...#....#...#....",
    "+": "......#....#..#####..#....#........",
    "·": "." * 15 + "..#.." + "." * 15,
    "'": "..#....#...........................",
    "#": ".#.#.#####.#.#..#.#.#####.#.#......",
}

SKY_TOP, SKY_BOTTOM = "#4db3fa", "#219af6"
INK, SHADOW = "#ffffff", "#0b4f8a"
GRASS, GRASS_DARK, DIRT, DIRT_DARK = "#5fcf3a", "#3a9e2a", "#7a4f35", "#5c3a26"
LEVELS = {
    "NONE": "#8fcdfb",
    "FIRST_QUARTILE": "#b4ec8a",
    "SECOND_QUARTILE": "#7ddb52",
    "THIRD_QUARTILE": "#4cb534",
    "FOURTH_QUARTILE": "#2e7f22",
}
LANG_COLORS = {
    "Python": "#3572A5", "Rust": "#dea584", "HTML": "#e34c26", "JavaScript": "#f1e05a",
    "CSS": "#663399", "TypeScript": "#3178c6", "Shell": "#89e051", "SCSS": "#c6538c",
    "C": "#555555", "Go": "#00ADD8", "Lua": "#000080",
}
LANG_IGNORE = {"Makefile", "Dockerfile", "Nix", "Just", "CMake", "Meson"}
STACK = [
    ("linux", "#222222"), ("archlinux", "#1793D1"), ("kde", "#1D99F3"), ("python", "#3776AB"),
    ("rust", "#000000"), ("javascript", "#C9A800"), ("typescript", "#3178C6"), ("html5", "#E34F26"),
    ("qt", "#41CD52"), ("cloudflare", "#F38020"), ("discord", "#5865F2"), ("git", "#F05032"),
]


def text_path(s, x, y, scale):
    parts = []
    for i, ch in enumerate(s.upper()):
        g = GLYPHS.get(ch, GLYPHS[" "])
        ox = x + i * 6 * scale
        for row in range(7):
            bits = g[row * 5:row * 5 + 5]
            for m in re.finditer(r"#+", bits):
                parts.append(f"M{ox + m.start() * scale} {y + row * scale}h{len(m.group()) * scale}v{scale}h-{len(m.group()) * scale}z")
    return "".join(parts)


def text(s, x, y, scale, fill=INK, anchor="start"):
    width = text_width(s, scale)
    if anchor == "end":
        x -= width
    elif anchor == "middle":
        x -= width // 2
    shadow = text_path(s, x + scale, y + scale, scale)
    return f'<path fill="{SHADOW}" d="{shadow}"/><path fill="{fill}" d="{text_path(s, x, y, scale)}"/>'


def text_width(s, scale):
    return (len(s) * 6 - 1) * scale


def cloud(x, y, s):
    rows = ["..####..", ".######.", "########"]
    d = "".join(f"M{x + m.start() * s} {y + r * s}h{len(m.group()) * s}v{s}h-{len(m.group()) * s}z"
                for r, row in enumerate(rows) for m in re.finditer(r"#+", row))
    return f'<path fill="#ffffff" fill-opacity=".85" d="{d}"/>'


def sky(w, h, clouds, ground=True):
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges">',
        '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{SKY_TOP}"/><stop offset="1" stop-color="{SKY_BOTTOM}"/></linearGradient></defs>',
        f'<rect width="{w}" height="{h}" fill="url(#sky)"/>',
    ]
    out += [cloud(cx, cy, cs) for cx, cy, cs in clouds]
    if ground:
        g = h - 26
        teeth = "".join(f"M{x} {g - 4}h8v4h-8z" for x in range(0, w, 24))
        out.append(f'<rect y="{g}" width="{w}" height="10" fill="{GRASS}"/><path fill="{GRASS}" d="{teeth}"/>'
                   f'<rect y="{g + 10}" width="{w}" height="4" fill="{GRASS_DARK}"/>'
                   f'<rect y="{g + 14}" width="{w}" height="12" fill="{DIRT}"/>')
        dots = "".join(f"M{x} {g + 18 + (x // 16) % 2 * 4}h4v4h-4z" for x in range(6, w, 32))
        out.append(f'<path fill="{DIRT_DARK}" d="{dots}"/>')
    return out


def graphql(token, query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        sys.exit(f"GraphQL error: {body['errors']}")
    return body["data"]


def fetch(token, login):
    cal = graphql(token, """query($login: String!) { user(login: $login) { contributionsCollection {
        contributionCalendar { totalContributions weeks { contributionDays {
        date weekday contributionCount contributionLevel } } } } } }""", {"login": login})
    weeks = cal["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = cal["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    langs, cursor = {}, None
    while True:
        data = graphql(token, """query($login: String!, $after: String) { user(login: $login) {
            repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false) {
            pageInfo { hasNextPage endCursor }
            nodes { languages(first: 20) { edges { size node { name } } } } } } }""",
                       {"login": login, "after": cursor})
        repos = data["user"]["repositories"]
        for node in repos["nodes"]:
            for e in node["languages"]["edges"]:
                name = e["node"]["name"]
                if name not in LANG_IGNORE:
                    langs[name] = langs.get(name, 0) + e["size"]
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    return weeks, total, langs


def streaks(weeks):
    days = [d for w in weeks for d in w["contributionDays"]]
    today = dt.date.today().isoformat()
    days = [d for d in days if d["date"] <= today]
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            current += 1
        elif i > 0:
            break
    return current, longest


def stats_svg(login, weeks, total, langs, w):
    h, x = 336, 24
    out = sky(w, h, [(w - 250, 18, 5), (w - 110, 50, 4), (w - 360, 64, 3)])
    out.append(text(login, x, 22, 5))
    out.append(text("GITHUB · LAST 12 MONTHS", x + 2, 70, 3, "#d9efff"))

    col = 420
    lang_w = w - 3 * x - col
    current, longest = streaks(weeks)
    rows = [("CONTRIBUTIONS", str(total)), ("CURRENT STREAK", f"{current} DAYS"), ("LONGEST STREAK", f"{longest} DAYS")]
    for i, (label, value) in enumerate(rows):
        y = 112 + i * 56
        out.append(f'<rect x="{x}" y="{y}" width="{col}" height="46" fill="{SHADOW}" fill-opacity=".35"/>')
        out.append(f'<rect x="{x}" y="{y}" width="5" height="46" fill="#ffffff" fill-opacity=".6"/>')
        out.append(text(label, x + 16, y + 13, 3, "#d9efff"))
        out.append(text(value, x + col - 14, y + 13, 3, anchor="end"))

    top = sorted(langs.items(), key=lambda kv: -kv[1])
    total_size = sum(langs.values()) or 1
    shown = top[:4]
    rest = total_size - sum(sz for _, sz in shown)
    if rest > 0:
        shown.append(("Other", rest))
    lx, y = 2 * x + col, 112
    out.append(f'<rect x="{lx - 2}" y="{y - 2}" width="{lang_w + 4}" height="20" fill="{SHADOW}"/>')
    pos = lx
    for i, (name, size) in enumerate(shown):
        seg = round(lang_w * size / total_size) if i < len(shown) - 1 else lx + lang_w - pos
        out.append(f'<rect x="{pos}" y="{y}" width="{seg}" height="16" fill="{LANG_COLORS.get(name, "#cfd8e3")}"/>')
        pos += seg
    for i, (name, size) in enumerate(shown):
        ly = 144 + i * 30
        color = LANG_COLORS.get(name, "#cfd8e3")
        out.append(f'<rect x="{lx}" y="{ly}" width="21" height="21" fill="{SHADOW}"/>'
                   f'<rect x="{lx + 3}" y="{ly + 3}" width="15" height="15" fill="{color}"/>')
        out.append(text(name, lx + 32, ly, 3))
        out.append(text(f"{size * 100 / total_size:.0f}%", lx + lang_w, ly, 3, anchor="end"))
    out.append("</svg>")
    return "".join(out)


def card_width(weeks):
    return 2 * 12 + len(weeks) * 15 - 4


def snake_svg(weeks):
    step, cell, mx, my = 15, 11, 12, 16
    cols = len(weeks)
    w, h = card_width(weeks), my + 7 * step + 40
    out = sky(w, h, [(w - 140, 4, 2), (60, 2, 2)])

    length = 6
    prefix = 2 * length
    order = []
    for c in range(cols):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        order += [(c, r) for r in rows]
    last_c, last_r = order[-1]
    pts = [(-(prefix - i), 0) for i in range(prefix)] + order + [(last_c + i + 1, last_r) for i in range(length + 1)]
    total = len(pts) - 1
    span = total - length
    dur = round(span * 0.09, 2)

    def center(c, r):
        return mx + c * step + cell / 2, my + r * step + cell / 2

    d = "M" + " L".join(f"{x:g} {y:g}" for x, y in (center(c, r) for c, r in pts))
    out.append(f'<defs><path id="route" d="{d}"/></defs>')

    days = {(c, d["weekday"]): d for c, wk in enumerate(weeks) for d in wk["contributionDays"]}
    empty = LEVELS["NONE"]
    for idx, (c, r) in enumerate(order):
        day = days.get((c, r))
        if not day:
            continue
        x, y = mx + c * step, my + r * step
        color = LEVELS.get(day["contributionLevel"], empty)
        if color == empty:
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{empty}"/>')
            continue
        f = (prefix + idx - length) / span
        f2 = min(f + 0.002, 0.999)
        out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}">'
                   f'<animate attributeName="fill" values="{color};{color};{empty};{empty}" '
                   f'keyTimes="0;{f:.4f};{f2:.4f};1" dur="{dur}s" repeatCount="indefinite"/></rect>')

    for i in range(length - 1, -1, -1):
        size = step - 1 if i == 0 else step - 3
        color = "#5c3a26" if i == 0 else ("#8a5a36" if i % 2 else "#a0703f")
        a, b = (length - i) / total, (total - i) / total
        out.append(f'<rect x="{-size / 2:g}" y="{-size / 2:g}" width="{size}" height="{size}" fill="{color}">'
                   f'<animateMotion dur="{dur}s" repeatCount="indefinite" calcMode="linear" '
                   f'keyPoints="{a:.5f};{b:.5f}" keyTimes="0;1"><mpath href="#route"/></animateMotion></rect>')
    out.append("</svg>")
    return "".join(out)


def stack_svg(icon_dir):
    tile, gap, pad, per_row = 52, 14, 16, 6
    rows = -(-len(STACK) // per_row)
    w = pad * 2 + per_row * tile + (per_row - 1) * gap
    h = pad * 2 + rows * tile + (rows - 1) * gap
    out = sky(w, h, [], ground=False)
    for i, (slug, color) in enumerate(STACK):
        src = (icon_dir / f"{slug}.svg").read_text()
        path = re.search(r'<path d="([^"]+)"', src).group(1)
        x, y = pad + i % per_row * (tile + gap), pad + i // per_row * (tile + gap)
        out.append(f'<rect x="{x + 3}" y="{y + 3}" width="{tile}" height="{tile}" fill="{SHADOW}" fill-opacity=".45"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" fill="#ffffff"/>')
        out.append(f'<g transform="translate({x + 12} {y + 12}) scale(1.1667)" shape-rendering="geometricPrecision">'
                   f'<path fill="{color}" d="{path}"/></g>')
    out.append("</svg>")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["cards", "stack"])
    ap.add_argument("--user", default="Rockykln")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    root = Path(__file__).resolve().parent.parent
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.what == "stack":
        (out / "stack.svg").write_text(stack_svg(root / "assets" / "icons"))
        return
    tokens = [t for t in (os.environ.get("GH_TOKEN"), os.environ.get("FALLBACK_TOKEN")) if t]
    if not tokens:
        sys.exit("GH_TOKEN missing")
    for i, token in enumerate(tokens):
        try:
            weeks, total, langs = fetch(token, args.user)
            break
        except urllib.error.HTTPError as e:
            if e.code != 401 or i == len(tokens) - 1:
                raise
            print("GH_TOKEN rejected, using FALLBACK_TOKEN", file=sys.stderr)
    (out / "stats.svg").write_text(stats_svg(args.user, weeks, total, langs, card_width(weeks)))
    (out / "snake.svg").write_text(snake_svg(weeks))


if __name__ == "__main__":
    main()
