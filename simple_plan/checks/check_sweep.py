"""Checks kidney_swap/sweep.py (owner: Simulation).

Run:  uv run python simple_plan/checks/check_sweep.py
"""

import contextlib
import io
import os
import tempfile

os.environ["MPLBACKEND"] = "Agg"  # draw charts without opening a window

from helpers import (EXAMPLE_RINGS, FakePool, brute_force_best, check, example_pool, fail, finish,
                     get, plan_total, require, skip, try_load)

sweep_module = require("sweep", owner="Simulation")

KEYS = ["p", "two_way", "three_by_count", "three_by_expected", "gain_by_count", "gain_by_expected"]

# The prototype numbers from docs/original_plan.md, as rows.
PROTOTYPE_ROWS = [
    {"p": 1.0, "two_way": 52.00, "three_by_count": 63.00, "three_by_expected": 63.00, "gain_by_count": 21.2, "gain_by_expected": 21.2},
    {"p": 0.9, "two_way": 42.12, "three_by_count": 47.24, "three_by_expected": 48.50, "gain_by_count": 12.2, "gain_by_expected": 15.1},
    {"p": 0.8, "two_way": 33.28, "three_by_count": 34.33, "three_by_expected": 36.38, "gain_by_count": 3.2, "gain_by_expected": 9.3},
    {"p": 0.7, "two_way": 25.48, "three_by_count": 23.99, "three_by_expected": 26.37, "gain_by_count": -5.8, "gain_by_expected": 3.5},
    {"p": 0.6, "two_way": 18.72, "three_by_count": 15.94, "three_by_expected": 18.98, "gain_by_count": -14.9, "gain_by_expected": 1.4},
    {"p": 0.5, "two_way": 13.00, "three_by_count": 9.90, "three_by_expected": 13.14, "gain_by_count": -23.8, "gain_by_expected": 1.1},
]


class ReferenceSolver:
    """A correct (slow) solver, so this check does not depend on anyone else's solver."""

    def solve(self, rings, p):
        best_value = brute_force_best(rings, p)
        from itertools import combinations
        for size in range(len(rings), -1, -1):
            for combo in combinations(rings, size):
                families = [f for ring in combo for f in ring]
                if len(families) == len(set(families)) and abs(plan_total(combo, p) - best_value) < 1e-9:
                    return list(combo)
        return []


def t_crossover():
    find_crossover = get(sweep_module, "find_crossover")
    got = find_crossover(PROTOTYPE_ROWS)
    if got is None:
        fail("find_crossover returned None, but gain_by_expected does drop below 5% (between p = 0.8 and 0.7).")
    if abs(got - 0.7259) > 0.002:
        fail(f"On the prototype rows, gain_by_expected is 9.3% at p = 0.8 and 3.5% at p = 0.7.\n"
             f"Drawing a straight line between them, it hits 5% at p = 0.7 + 0.1 * (5 - 3.5) / (9.3 - 3.5) "
             f"= 0.726.\nYou returned {got}.")


def t_crossover_edges():
    find_crossover = get(sweep_module, "find_crossover")
    always_high = [dict(row, gain_by_expected=20.0) for row in PROTOTYPE_ROWS]
    got = find_crossover(always_high)
    if got is not None:
        fail(f"If the gain never drops below 5%, find_crossover should return None. It returned {got}.")
    starts_low = [dict(row, gain_by_expected=1.0) for row in PROTOTYPE_ROWS]
    got = find_crossover(starts_low)
    if got != 1.0:
        fail(f"If the gain is already below 5% at the first row (p = 1.0), return that p (1.0). Got {got}.")


def t_print_table():
    print_table = get(sweep_module, "print_table")
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        print_table(PROTOTYPE_ROWS)
    text = printed.getvalue()
    for needed in ("0.7", "52", "26.37"):
        if needed not in text:
            fail(f"print_table should print one line per row with p and the numbers. "
                 f"'{needed}' is missing from what it printed:\n{text}")


def t_chart():
    save_chart = get(sweep_module, "save_chart")
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "sweep.png")
    save_chart(PROTOTYPE_ROWS, path)
    if not os.path.exists(path):
        fail(f"save_chart(rows, path) did not create a file at the path it was given ({path}).\n"
             f"Use plt.savefig(path) and don't change the path.")
    if os.path.getsize(path) < 5000:
        fail("The chart file is almost empty. Did you plot the three lines before saving?")


def need_find_rings():
    rings_module = try_load("rings", "run_sweep")
    find_rings = getattr(rings_module, "find_rings", None)
    try:
        ok = find_rings is not None and sorted(find_rings(example_pool(), 3)) == sorted(EXAMPLE_RINGS)
    except Exception:
        ok = False
    if not ok:
        skip("Can't check run_sweep yet: rings.py's find_rings isn't working. "
             "It will be checked once check_rings.py passes.")


def run(pools, p_values):
    run_sweep = get(sweep_module, "run_sweep")
    rows = run_sweep(pools, p_values, ReferenceSolver())
    if rows is None:
        fail("run_sweep returned None. Did you forget `return rows`?")
    if not isinstance(rows, list) or len(rows) != len(p_values):
        fail(f"run_sweep should return a list with one row per p value ({len(p_values)} rows).")
    for row in rows:
        missing = [key for key in KEYS if key not in row]
        if missing:
            fail(f"Each row must be a dict with keys {KEYS}. Missing: {missing}.")
    return rows


def t_run_example():
    need_find_rings()
    rows = run([example_pool()], [1.0, 0.8, 0.6])
    expected = [
        (1.0, 4.00, 5.000, 5.00, 25.0, 25.0),
        (0.8, 2.56, 2.816, 2.816, 10.0, 10.0),
        (0.6, 1.44, 1.368, 1.44, -5.0, 0.0),
    ]
    for row, (p, two, count, best, gain_count, gain_best) in zip(rows, expected):
        if abs(row["p"] - p) > 1e-9:
            fail(f"Rows must be in the same order as p_values. Expected p = {p}, got {row['p']}.")
        if abs(row["two_way"] - two) > 1e-6:
            fail(f"At p = {p}, two_way should be {two} (best plan using only 2-way swaps, scored at p). "
                 f"Got {row['two_way']}.\nDid you remove the 3-way rings before solving?")
        if abs(row["three_by_count"] - count) > 1e-6:
            hint = ""
            if abs(row["three_by_count"] - 5.0) < 1e-6:
                hint = ("\nYou scored the count plan with p = 1.0. Pick it with p = 1.0, but score it "
                        "with the real p: plan_value(plan, p).")
            fail(f"At p = {p}, three_by_count should be {count}: the plan picked by count "
                 f"(solve(rings, 1.0)) is [(1, 4), (2, 5, 3)],\nscored at the real p. Got "
                 f"{row['three_by_count']}.{hint}")
        if abs(row["three_by_expected"] - best) > 1e-6:
            fail(f"At p = {p}, three_by_expected should be {best} (solve(rings, p), scored at p). "
                 f"Got {row['three_by_expected']}.")
        if abs(row["gain_by_count"] - gain_count) > 1e-6 or abs(row["gain_by_expected"] - gain_best) > 1e-6:
            fail(f"At p = {p}, the gains should be {gain_count}% (by count) and {gain_best}% (by expected).\n"
                 f"Got {row['gain_by_count']} and {row['gain_by_expected']}.\n"
                 f"Formula: (three - two_way) / two_way * 100, as a percent.")


def t_run_average():
    need_find_rings()
    empty = FakePool(example_pool().families, set())
    rows = run([example_pool(), empty], [1.0])
    if abs(rows[0]["two_way"] - 2.0) > 1e-6 or abs(rows[0]["three_by_expected"] - 2.5) > 1e-6:
        fail(f"With two pools (the example, and one with no arrows) at p = 1.0, the averages should be "
             f"two_way = (4 + 0) / 2 = 2.0\nand three_by_expected = (5 + 0) / 2 = 2.5. "
             f"Got {rows[0]['two_way']} and {rows[0]['three_by_expected']}.\n"
             f"Add up each pool's score, then divide by the number of pools.")


def t_run_no_arrows():
    need_find_rings()
    empty = FakePool(example_pool().families, set())
    rows = run([empty], [1.0, 0.5])
    if rows[0]["gain_by_expected"] != 0:
        fail("When two_way is 0 the gain can't be divided out. Set the gain to 0 in that case.")


check("find_crossover gives 0.726 on the prototype numbers", t_crossover)
check("find_crossover: None if never below 5%, first p if already below", t_crossover_edges)
check("print_table prints the numbers", t_print_table)
check("save_chart writes a PNG to the given path", t_chart)
check("run_sweep on the 6-family example matches the worked example", t_run_example)
check("run_sweep averages over pools", t_run_average)
check("run_sweep doesn't crash on a pool with no arrows", t_run_no_arrows)
finish()
