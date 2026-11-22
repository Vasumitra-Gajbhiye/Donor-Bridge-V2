"""Runs every check, in the order the files should be built.

Run:  uv run python simple_plan/checks/check_all.py
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKS = ["check_rings.py", "check_pool.py", "check_greedy.py", "check_exact.py", "check_ilp.py",
          "check_sweep.py", "check_demo.py", "check_lead.py"]

results = []
for name in CHECKS:
    print("=" * 70, flush=True)
    finished = subprocess.run([sys.executable, os.path.join(HERE, name)])
    results.append((name, finished.returncode == 0))
    print()

print("=" * 70)
print("Summary")
for name, passed in results:
    print(f"  {'ok  ' if passed else 'FAIL'}  {name}")
sys.exit(0 if all(passed for _, passed in results) else 1)
