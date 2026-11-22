"""Checks that our hand-written ExactSolver and the IlpSolver always agree.

This is the "correctness evidence" slide: on many random pools, two completely different
methods find plans with the same value. If they ever disagree, one of them has a bug.

We compare the VALUE of the plans, not the plans themselves: two different plans
can both be the best (e.g. (1, 4) + (2, 3) and (1, 4) + (3, 5) are both worth 1.44 at p = 0.6).
"""

from pool import make_pool
from rings import find_rings, plan_value
from exact import ExactSolver
from ilp import IlpSolver

P_VALUES_TO_TEST = [1.0, 0.7]

# Two values closer than this count as equal. Decimal numbers on a computer are not exact,
# so 1.44 and 1.4400000000000002 should not count as a mismatch.
TOLERANCE = 1e-9


def compare(n_pools, n_families):
    """Compare both solvers on n_pools random pools. Returns the number of pools where they disagree.

    Keep n_families small (about 10): ExactSolver tries every combination, so it gets very slow.
    """
    exact_solver = ExactSolver()
    ilp_solver = IlpSolver()
    mismatches = 0

    print(f"Comparing ExactSolver and IlpSolver on {n_pools} random pools of {n_families} families")
    print()

    for seed in range(n_pools):
        pool = make_pool(n_families, seed)
        rings = find_rings(pool, 3)

        pool_agrees = True
        line = f"Pool {seed:3d} ({len(rings):3d} rings):"

        for p in P_VALUES_TO_TEST:
            # Give each solver its own copy of the list, so neither can affect the other.
            exact_value = plan_value(exact_solver.solve(list(rings), p), p)
            ilp_value = plan_value(ilp_solver.solve(list(rings), p), p)

            line = line + f"   p={p:.1f}  exact {exact_value:6.3f}  ilp {ilp_value:6.3f}"
            if abs(exact_value - ilp_value) > TOLERANCE:
                pool_agrees = False

        if pool_agrees:
            line = line + "   agree"
        else:
            line = line + "   MISMATCH"
            mismatches = mismatches + 1
        print(line)

    print()
    if mismatches == 0:
        print(f"Summary: the two solvers agree on all {n_pools} pools.")
    else:
        print(f"Summary: the two solvers DISAGREE on {mismatches} of {n_pools} pools.")
    return mismatches


if __name__ == "__main__":
    compare(100, 10)
