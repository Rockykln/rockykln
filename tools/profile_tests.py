#!/usr/bin/env python3
"""Takes the Rust block out of README.md, compiles it and runs its tests."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRATE = ROOT / "profile"


def extract(readme):
    block = re.search(r"```rust\n(.*?)```", readme.read_text(), re.S)
    if not block:
        sys.exit("no rust block in README.md")
    return block.group(1)


def run():
    (CRATE / "src").mkdir(parents=True, exist_ok=True)
    (CRATE / "src/lib.rs").write_text(extract(ROOT / "README.md"))
    test = subprocess.run(["cargo", "test", "--quiet"], cwd=CRATE, capture_output=True, text=True)
    output = test.stdout + test.stderr
    result = next((l for l in output.splitlines() if l.startswith("test result:")), "")
    count = result.split()[3] if result else "0"
    return test.returncode == 0, count, output


if __name__ == "__main__":
    ok, count, output = run()
    print(output.strip())
    sys.exit(0 if ok else 1)
