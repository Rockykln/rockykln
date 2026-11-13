#!/usr/bin/env python3
"""Redraws the badges in dist/ from live GitHub numbers. Touches nothing else."""

import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import badges
import profile_tests

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = [
    ("locsim", "LocSim", "#F05138", "swift"),
    ("refrain", "Refrain", "#3776AB", "python"),
    ("podctl", "podctl", "#dea584", "rust"),
    ("nettools", "nettools", "#3178C6", "typescript"),
    ("clientctl", "clientctl", "#3776AB", "python"),
]
QUERY = """query($name: String!) { repository(owner: "Rockykln", name: $name) {
    stargazerCount latestRelease { tagName } } }"""


def ask(token, name):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"name": name}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-badges"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        sys.exit(f"GraphQL error: {body['errors']}")
    return body["data"]["repository"]


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("FALLBACK_TOKEN")
    if not token:
        sys.exit("GH_TOKEN missing")
    rows = []
    for slug, label, color, logo in PROJECTS:
        repo = ask(token, slug)
        tag = (repo["latestRelease"] or {}).get("tagName")
        message = tag if tag else "in development"
        rows.append((slug, label, f"{message} · ★{repo['stargazerCount']}", color, logo))
    out = ROOT / "dist"
    out.mkdir(parents=True, exist_ok=True)
    for slug, label, message, color, logo in rows:
        (out / f"badge-{slug}.svg").write_text(
            badges.badge(label, message, color, ROOT / "assets/icons", logo))
    ok, count, _ = profile_tests.run()
    (out / "badge-tests.svg").write_text(badges.badge(
        "profile tests", f"{count} passed" if ok else "failing",
        "#4c1" if ok else "#e05d44", ROOT / "assets/icons", "githubactions"))
    print(f"{len(rows) + 1} badges written to {out}")


if __name__ == "__main__":
    main()
