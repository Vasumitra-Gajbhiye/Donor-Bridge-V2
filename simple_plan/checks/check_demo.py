"""Checks kidney_swap/demo.py (owner: Matching).

The demo needs pool.py, rings.py, greedy.py and exact.py to work first.

Run:  uv run python simple_plan/checks/check_demo.py
"""

import os
import subprocess
import sys

from helpers import CODE_DIR, check, fail, finish, try_load

print("Checking kidney_swap/demo.py  (owner: Matching)\n")
demo_path = os.path.join(CODE_DIR, "demo.py")


def t_runs():
    if not os.path.exists(demo_path):
        fail("kidney_swap/demo.py does not exist yet. See INSTRUCTIONS.md, the section for demo.py.")
    for name in ("pool", "rings", "greedy", "exact"):
        try_load(name, "the demo")
    result = subprocess.run([sys.executable, demo_path], capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        fail(f"demo.py crashed. The end of the error:\n{result.stderr[-1500:]}")
    text = result.stdout
    needed = {
        "the 7 rings": "(2, 5, 3)",
        "greedy's plan at p = 1.0": "(2, 3, 4)",
        "the exact plan at p = 1.0": "(1, 4)",
        "the word Greedy": "Greedy",
        "the word Exact": "Exact",
    }
    for what, text_piece in needed.items():
        if text_piece not in text:
            fail(f"The demo output should show {what} (looked for '{text_piece}'). It printed:\n{text}")


check("demo.py runs and shows the rings, greedy's plan and the exact plan", t_runs)
finish()
