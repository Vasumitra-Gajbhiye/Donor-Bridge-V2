"""Checks kidney_swap/ilp.py (owner: Lead).

Run:  uv run python simple_plan/checks/check_ilp.py
"""

from helpers import (check, fail, finish, get, plan_problem, random_fake_pool, reference_rings,
                     require, solver_checks, timed)

ilp_module = require("ilp", owner="Lead")


def t_has_class():
    get(ilp_module, "IlpSolver")


def t_big_pool():
    pool = random_fake_pool(60, 0.15, seed=4)
    rings = sorted(reference_rings(pool, 3), key=lambda r: (len(r), r))
    plan, seconds = timed(ilp_module.IlpSolver().solve, rings, 0.8)
    problem = plan_problem(plan, rings)
    if problem:
        fail(problem)
    if seconds > 20:
        fail(f"{len(rings)} rings took {seconds:.1f} s. Make sure the solver is told not to print "
             f"(PULP_CBC_CMD(msg=False)) and that you build each family's rule once, not once per ring.")


check("ilp.py has a class called IlpSolver", t_has_class)
if hasattr(ilp_module, "IlpSolver"):
    solver_checks(ilp_module.IlpSolver, "ilp.py")
    check("a 60-family pool solves in reasonable time", t_big_pool)
finish()
