#!/usr/bin/env python3
"""Pixel-art SVG cards for the GitHub profile README: stats, contribution snake, projects, tech stack."""

import argparse
import datetime as dt
import json
import os
import random
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
PROJECTS = ["refrain", "podctl", "clientctl"]
STACK = [
    ("linux", "#222222"), ("archlinux", "#1793D1"), ("cachyos", "#17B978"), ("kde", "#1D99F3"),
    ("bluetooth", "#0082FC"), ("podman", "#892CA0"), ("git", "#F05032"), ("githubactions", "#2088FF"),
    ("python", "#3776AB"), ("rust", "#000000"), ("typescript", "#3178C6"), ("javascript", "#C9A800"),
    ("html5", "#E34F26"), ("qt", "#41CD52"), ("cloudflare", "#F38020"), ("discord", "#5865F2"),
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


def bird(x, y, s, w, dur, begin, flap=0.55, fill="#08477c"):
    up = ["##...##", ".##.##.", "...#..."]
    down = ["...#...", ".##.##.", "##...##"]

    def shape(rows):
        return "".join(f"M{x + m.start() * s} {y + r * s}h{len(m.group()) * s}v{s}h-{len(m.group()) * s}z"
                       for r, row in enumerate(rows) for m in re.finditer(r"#+", row))

    frames = "".join(
        f'<path fill="{fill}" fill-opacity=".8" opacity="{o1}" d="{shape(rows)}">'
        f'<animate attributeName="opacity" values="{o1};{o1};{o2};{o2}" keyTimes="0;.49;.5;1" '
        f'dur="{flap}s" repeatCount="indefinite"/></path>'
        for rows, o1, o2 in ((up, 1, 0), (down, 0, 1)))
    span = w - x + 60
    drift = f"0 0;{span * 0.35:.0f} -18;{span * 0.7:.0f} 6;{span} -12"
    return (f'<g>{frames}<animateTransform attributeName="transform" type="translate" '
            f'values="{drift}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>')


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
    out.append(bird(int(w * 0.42), 30, 5, w, 22, 0))
    out.append(bird(int(w * 0.55), 58, 4, w, 28, 7, 0.7))
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


def projects(token, login, names):
    out = []
    for name in names:
        data = graphql(token, """query($login: String!, $name: String!) { repository(owner: $login, name: $name) {
            name description stargazerCount pushedAt
            primaryLanguage { name } latestRelease { tagName } } }""", {"login": login, "name": name})
        repo = data["repository"]
        if repo:
            out.append(repo)
    return out


def star(x, y, s, fill):
    rows = ["..#..", ".###.", "#####", ".###.", "#.#.#"]
    d = "".join(f"M{x + m.start() * s} {y + r * s}h{len(m.group()) * s}v{s}h-{len(m.group()) * s}z"
                for r, row in enumerate(rows) for m in re.finditer(r"#+", row))
    return f'<path fill="{fill}" d="{d}"/>'


def since(iso):
    days = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(iso)).days
    if days < 1:
        return "TODAY"
    if days < 14:
        return f"{days}D AGO"
    if days < 60:
        return f"{days // 7}W AGO"
    return f"{days // 30}MO AGO"


def projects_svg(repos, w):
    h, x, row_h = 296, 24, 56
    out = sky(w, h, [(w - 220, 22, 5), (w - 90, 58, 3)])
    out.append(bird(int(w * 0.40), 26, 5, w, 24, 2))
    out.append(bird(int(w * 0.58), 54, 4, w, 30, 9, 0.7))
    out.append(text("PROJECTS", x, 22, 5))
    out.append(text("RELEASES AND ACTIVITY", x + 2, 70, 3, "#d9efff"))

    cells = [(r["name"], (r["primaryLanguage"] or {}).get("name", ""),
              (r["latestRelease"] or {}).get("tagName", "").upper(), since(r["pushedAt"]),
              str(r["stargazerCount"])) for r in repos]
    gap = text_width("·", 3) + 22
    name_col = max(text_width(c[0], 3) for c in cells) + 28
    lang_col = max(text_width(c[1].upper(), 3) for c in cells) + gap
    ver_col = max(text_width(c[2], 3) for c in cells) + gap
    for i, (name, lang, ver, age, stars) in enumerate(cells):
        y = 112 + i * row_h
        color = LANG_COLORS.get(lang, "#cfd8e3")
        cx = x + 24
        out.append(f'<rect x="{x}" y="{y}" width="{w - 2 * x}" height="46" fill="{SHADOW}" fill-opacity=".35"/>')
        out.append(f'<rect x="{x}" y="{y}" width="11" height="46" fill="{SHADOW}"/>')
        out.append(f'<rect x="{x + 3}" y="{y + 3}" width="5" height="40" fill="{color}"/>')
        out.append(text(name, cx, y + 13, 3))
        out.append(text(lang.upper(), cx + name_col, y + 13, 3, "#d9efff"))
        out.append(text("·", cx + name_col + lang_col - gap + 11, y + 13, 3, "#8fc9f5"))
        out.append(text(ver, cx + name_col + lang_col, y + 13, 3, "#d9efff"))
        out.append(text("·", cx + name_col + lang_col + ver_col - gap + 11, y + 13, 3, "#8fc9f5"))
        out.append(text(age, cx + name_col + lang_col + ver_col, y + 13, 3, "#d9efff"))
        right = w - x - 14
        out.append(text(stars, right, y + 13, 3, anchor="end"))
        out.append(star(right - text_width(stars, 3) - 26, y + 13, 3, "#ffe066"))
    out.append("</svg>")
    return "".join(out)


def card_width(weeks):
    return 2 * 12 + len(weeks) * 15 - 4


def snake_svg(weeks):
    step, cell, mx, my = 15, 11, 12, 16
    cols = len(weeks)
    w, h = card_width(weeks), my + 7 * step + 40
    out = sky(w, h, [])

    length = 6
    prefix = 2 * length
    order = []
    for c in range(cols):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        order += [(c, r) for r in rows]

    days = {(c, d["weekday"]): d for c, wk in enumerate(weeks) for d in wk["contributionDays"]}
    empty = LEVELS["NONE"]
    route = [(c, r) for c, r in order
             if LEVELS.get((days.get((c, r)) or {}).get("contributionLevel"), empty) != empty]
    first_r = route[0][1] if route else 0
    last_c, last_r = route[-1] if route else (cols - 1, 0)
    pts = ([(-(prefix - i), first_r) for i in range(prefix)] + route
           + [(last_c + i + 1, last_r) for i in range(length + 1)])

    def center(c, r):
        return mx + c * step + cell / 2, my + r * step + cell / 2

    xy = [center(c, r) for c, r in pts]
    cum = [0.0]
    for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
        cum.append(cum[-1] + ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    route_len = cum[-1]
    dur = round((route_len - cum[prefix]) / 36, 2)

    d = "M" + " L".join(f"{x:g} {y:g}" for x, y in xy)
    out.append(f'<defs><path id="route" d="{d}"/></defs>')

    eaten = {cr: i for i, cr in enumerate(route)}
    for c, r in order:
        day = days.get((c, r))
        if not day:
            continue
        x, y = mx + c * step, my + r * step
        color = LEVELS.get(day["contributionLevel"], empty)
        if (c, r) not in eaten:
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{empty}"/>')
            continue
        head0 = cum[prefix] / route_len
        f = (cum[prefix + eaten[(c, r)]] / route_len - head0) / (1 - head0)
        f2 = min(f + 0.002, 0.999)
        f3 = min(f2 + 0.004, 0.9995)
        out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}">'
                   f'<animate attributeName="fill" values="{color};{color};#ffffff;{empty};{empty}" '
                   f'keyTimes="0;{f:.4f};{f2:.4f};{f3:.4f};1" dur="{dur}s" repeatCount="indefinite"/></rect>')

    head0 = cum[prefix] / route_len

    def at_cell(idx):
        idx = min(idx, len(route) - 1)
        return (cum[prefix + idx] / route_len - head0) / (1 - head0)

    grow_every = max(2, round(len(route) * 0.15))
    start_len = random.randint(3, 5)
    max_len = min(12, start_len + len(route) // grow_every)
    for i in range(max_len - 1, -1, -1):
        small = 10 if i else 12
        full = step - 3 if i else step - 1
        color = "#4a2f1e" if i == 0 else ("#7d5130" if i % 2 else "#9a6a3c")
        back = i * step / route_len
        a, b = head0 - back, 1 - back
        grow = (f'<animate attributeName="{{}}" values="{{}}" dur="{dur}s" repeatCount="indefinite"/>')
        body = (f'<rect fill="{color}" rx="3" shape-rendering="geometricPrecision">'
                + grow.format("width", f"{small};{full}") + grow.format("height", f"{small};{full}")
                + grow.format("x", f"{-small / 2:g};{-full / 2:g}") + grow.format("y", f"{-small / 2:g};{-full / 2:g}")
                + "</rect>")
        if i == 0:
            for sign in (-1, 1):
                ex = f"{sign * small / 4 - small / 8:g};{sign * full / 4 - full / 8:g}"
                body += ('<rect fill="#ffffff">'
                         + grow.format("width", f"{small / 4:g};{full / 4:g}")
                         + grow.format("height", f"{small / 4:g};{full / 4:g}")
                         + grow.format("x", ex)
                         + grow.format("y", f"{-small / 2.5:g};{-full / 2.5:g}") + "</rect>")
        seg = (f'<g>{body}<animateMotion dur="{dur}s" repeatCount="indefinite" calcMode="linear" '
               f'keyPoints="{a:.5f};{b:.5f}" keyTimes="0;1"><mpath href="#route"/></animateMotion></g>')
        if i >= start_len:
            t = max(at_cell((i - start_len + 1) * grow_every), 0.0001)
            seg = (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1" '
                   f'keyTimes="0;{t:.4f};{min(t + 0.002, 0.999):.4f};1" dur="{dur}s" '
                   f'repeatCount="indefinite"/>{seg}</g>')
        out.append(seg)
    out.append("</svg>")
    return "".join(out)


def stack_svg(icon_dir):
    tile, gap, pad, per_row = 52, 14, 16, 8
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
            repos = projects(token, args.user, PROJECTS)
            break
        except urllib.error.HTTPError as e:
            if e.code != 401 or i == len(tokens) - 1:
                raise
            print("GH_TOKEN rejected, using FALLBACK_TOKEN", file=sys.stderr)
    (out / "stats.svg").write_text(stats_svg(args.user, weeks, total, langs, card_width(weeks)))
    (out / "snake.svg").write_text(snake_svg(weeks))
    (out / "projects.svg").write_text(projects_svg(repos, card_width(weeks)))


if __name__ == "__main__":
    main()
