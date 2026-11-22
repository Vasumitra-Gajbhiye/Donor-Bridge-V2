"""Checks kidney_swap/compare_solvers.py and kidney_swap/main.py (owner: Lead).

These two files glue everyone's work together, so this check only makes sense once
check_pool, check_rings, check_exact, check_ilp and check_sweep pass.

Run:  uv run python simple_plan/checks/check_lead.py
"""

import contextlib
import io
import os
import tempfile

os.environ["MPLBACKEND"] = "Agg"

from helpers import check, fail, finish, get, require, skip, try_load

compare_module = require("compare_solvers", owner="Lead")


def need_everyone():
    for name in ("pool", "rings", "exact", "ilp", "sweep"):
        try_load(name, "the glue code")


def t_compare():
    need_everyone()
    compare = get(compare_module, "compare")
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        mismatches = compare(10, 10)
    if mismatches is None:
        fail("compare(n_pools, n_families) returned None. Return the number of pools where the two "
             "solvers disagreed.")
    if mismatches != 0:
        fail(f"ExactSolver and IlpSolver disagreed on {mismatches} of 10 pools. One of them is wrong.\n"
             f"Run check_exact.py and check_ilp.py to see which.\nWhat compare printed:\n{printed.getvalue()}")
    if printed.getvalue().strip() == "":
        fail("compare() printed nothing. Print one line per pool and a final summary, so it can be shown "
             "on a slide.")


def t_main():
    need_everyone()
    main_path = os.path.join(os.path.dirname(compare_module.__file__), "main.py")
    if not os.path.exists(main_path):
        skip("kidney_swap/main.py does not exist yet.")
    import main as main_module
    main_function = get(main_module, "main")
    folder = tempfile.mkdtemp()
    old_folder = os.getcwd()
    os.chdir(folder)
    printed = io.StringIO()
    try:
        with contextlib.redirect_stdout(printed):
            main_function(12, 2)
    finally:
        os.chdir(old_folder)
    text = printed.getvalue()
    if "ANSWER" not in text:
        fail(f"main(12, 2) should end by printing a line that starts with 'ANSWER'. It printed:\n{text}")
    if not os.path.exists(os.path.join(folder, "results", "sweep.png")):
        fail("main() should save the chart to results/sweep.png (create the folder with "
             "os.makedirs('results', exist_ok=True)).")


check("compare(10, 10): ExactSolver and IlpSolver agree on every pool", t_compare)
check("main(12, 2) prints an ANSWER line and saves results/sweep.png", t_main)
finish()
