#!/usr/bin/env python3
"""Classic flat README badges, rendered here instead of fetched from a badge service."""

import re
from pathlib import Path

H, PAD, LOGO = 20, 6, 14
GREY = "#555555"

# DejaVu Sans 11px advance widths, measured once so the workflow needs no font and no Pillow.
CHAR_W = {' ': 3.5, '!': 4.41, '"': 5.06, '#': 9.22, '$': 7.0, '%': 10.45, '&': 8.58, "'": 3.03, '(': 4.3, ')': 4.3, '*': 5.5, '+': 9.22, ',': 3.5, '-': 3.97, '.': 3.5, '/': 3.7, '0': 7.0, '1': 7.0, '2': 7.0, '3': 7.0, '4': 7.0, '5': 7.0, '6': 7.0, '7': 7.0, '8': 7.0, '9': 7.0, ':': 3.7, ';': 3.7, '<': 9.22, '=': 9.22, '>': 9.22, '?': 5.84, '@': 11.0, 'A': 7.53, 'B': 7.55, 'C': 7.69, 'D': 8.47, 'E': 6.95, 'F': 6.33, 'G': 8.53, 'H': 8.27, 'I': 3.25, 'J': 3.25, 'K': 7.22, 'L': 6.12, 'M': 9.48, 'N': 8.23, 'O': 8.66, 'P': 6.64, 'Q': 8.66, 'R': 7.64, 'S': 6.98, 'T': 6.72, 'U': 8.05, 'V': 7.53, 'W': 10.88, 'X': 7.53, 'Y': 6.72, 'Z': 7.53, '[': 4.3, '\\': 3.7, ']': 4.3, '^': 9.22, '_': 5.5, '`': 5.5, 'a': 6.73, 'b': 6.98, 'c': 6.05, 'd': 6.98, 'e': 6.77, 'f': 3.88, 'g': 6.98, 'h': 6.97, 'i': 3.06, 'j': 3.06, 'k': 6.38, 'l': 3.06, 'm': 10.72, 'n': 6.97, 'o': 6.73, 'p': 6.98, 'q': 6.98, 'r': 4.52, 's': 5.73, 't': 4.31, 'u': 6.97, 'v': 6.52, 'w': 9.0, 'x': 6.52, 'y': 6.52, 'z': 5.78, '{': 7.0, '|': 3.7, '}': 7.0, '~': 9.22, '·': 3.5, '—': 11.0}
FALLBACK_W = 6.4


def width(text):
    return sum(CHAR_W.get(c, FALLBACK_W) for c in text)


def logo_path(icon_dir, slug):
    f = Path(icon_dir) / f"{slug}.svg"
    if not f.exists():
        return None
    return re.search(r'<path d="([^"]+)"', f.read_text()).group(1)


def badge(label, message, color, icon_dir=None, logo=None):
    path = logo_path(icon_dir, logo) if (icon_dir and logo) else None
    lw = width(label) + 2 * PAD + (LOGO + 3 if path else 0)
    mw = width(message) + 2 * PAD
    w = round(lw + mw)
    lw, mw = round(lw), w - round(lw)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" '
           f'role="img" aria-label="{label}: {message}">',
           f'<title>{label}: {message}</title>',
           '<linearGradient id="s" x2="0" y2="100%">'
           '<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
           '<stop offset="1" stop-opacity=".1"/></linearGradient>',
           f'<clipPath id="r"><rect width="{w}" height="{H}" rx="3" fill="#fff"/></clipPath>',
           f'<g clip-path="url(#r)"><rect width="{lw}" height="{H}" fill="{GREY}"/>'
           f'<rect x="{lw}" width="{mw}" height="{H}" fill="{color}"/>'
           f'<rect width="{w}" height="{H}" fill="url(#s)"/></g>',
           '<g fill="#fff" text-anchor="start" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">']
    tx = PAD
    if path:
        out.append(f'<g transform="translate({PAD} 3) scale({LOGO / 24:.4f})" opacity=".95">'
                   f'<path fill="#fff" d="{path}"/></g>')
        tx += LOGO + 3
    for text, x in ((label, tx), (message, lw + PAD)):
        out.append(f'<text x="{x}" y="15" fill="#010101" fill-opacity=".3">{text}</text>'
                   f'<text x="{x}" y="14">{text}</text>')
    out.append("</g></svg>")
    return "".join(out)


def write_all(out, projects, tests_ok, test_count, icon_dir=None):
    out.mkdir(parents=True, exist_ok=True)
    for slug, label, message, color, logo in projects:
        (out / f"badge-{slug}.svg").write_text(badge(label, message, color, icon_dir, logo))
    (out / "badge-tests.svg").write_text(
        badge("profile tests", f"{test_count} passed" if tests_ok else "failing",
              "#4c1" if tests_ok else "#e05d44", icon_dir, "githubactions"))
    return len(projects) + 1
