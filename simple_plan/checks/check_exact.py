"""Checks kidney_swap/exact.py (owner: Heuristics).

Run:  uv run python simple_plan/checks/check_exact.py
"""

from helpers import check, fail, finish, get, random_fake_pool, reference_rings, require, solver_checks, timed

exact_module = require("exact", owner="Heuristics")


def t_has_class():
    get(exact_module, "ExactSolver")


def t_speed():
    pool = random_fake_pool(12, 0.3, seed=2)
    rings = sorted(reference_rings(pool, 3), key=lambda r: (len(r), r))
    _, seconds = timed(exact_module.ExactSolver().solve, rings, 0.8)
    if seconds > 10:
        fail(f"{len(rings)} rings took {seconds:.1f} s. Skip a ring as soon as it clashes with the families "
             f"already used, instead of exploring it.")


check("exact.py has a class called ExactSolver", t_has_class)
if hasattr(exact_module, "ExactSolver"):
    solver_checks(exact_module.ExactSolver, "exact.py")
    check("a 12-family pool solves in reasonable time", t_speed)
finish()
