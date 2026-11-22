"""The ILP solver: picks the best set of rings by handing the problem to a solver library.

ILP means "integer linear programming". We describe the problem as:
  - one yes/no choice per ring (take it or not),
  - a score to make as big as possible (the total value of the rings we take),
  - rules that must hold (each family can be in at most one ring we take),
and the library (pulp, using the HiGHS solver) finds the best answer for us.

It gives the same answer as ExactSolver in exact.py, but is much faster,
so it is the one we use for big pools of 100 families.
"""

import pulp

from rings import ring_value


class IlpSolver:
    def solve(self, rings, p):
        """Return the list of rings (a plan) with the highest total ring_value at this p."""

        # With no rings there is nothing to choose, and pulp does not like empty problems.
        if len(rings) == 0:
            return []

        problem = pulp.LpProblem("pick_rings", pulp.LpMaximize)

        # One yes/no variable per ring: 1 means "take ring k", 0 means "skip ring k".
        ring_is_taken = []
        for k in range(len(rings)):
            variable = pulp.LpVariable(f"ring_{k}", cat="Binary")
            ring_is_taken.append(variable)

        # The score to maximise: the total value of the rings we take.
        score_parts = []
        for k in range(len(rings)):
            score_parts.append(ring_value(rings[k], p) * ring_is_taken[k])
        problem += pulp.lpSum(score_parts)

        # Collect, for every family, the variables of all the rings that contain it.
        # Example: family 2 is in (2, 3), (2, 4) and (2, 5, 3), so its list has those three variables.
        rings_of_family = {}
        for k in range(len(rings)):
            for family_id in rings[k]:
                if family_id not in rings_of_family:
                    rings_of_family[family_id] = []
                rings_of_family[family_id].append(ring_is_taken[k])

        # One rule per family: at most one of the rings containing it can be taken.
        # (We add each rule once, after the dict is built, which keeps this fast.)
        for family_id in rings_of_family:
            problem += pulp.lpSum(rings_of_family[family_id]) <= 1

        # Solve with HiGHS. pulp's default (CBC) does not run on Apple-silicon Macs.
        # msg=False stops the solver from printing pages of output.
        problem.solve(pulp.HiGHS(msg=False))

        # Read the answer back: a variable worth 1 means the ring was taken.
        # We compare with 0.5 rather than == 1 because the solver may return 0.9999999.
        plan = []
        for k in range(len(rings)):
            if ring_is_taken[k].value() > 0.5:
                plan.append(rings[k])
        return plan


if __name__ == "__main__":
    # The 6-family worked example from INSTRUCTIONS.md
    example_rings = [(1, 4), (2, 3), (2, 4), (3, 5), (2, 3, 4), (2, 5, 3), (2, 5, 4)]
    solver = IlpSolver()

    plan_at_1 = solver.solve(example_rings, 1.0)
    print("p = 1.0 ->", plan_at_1)      # expect (1, 4) + (2, 5, 3): 5 transplants

    plan_at_06 = solver.solve(example_rings, 0.6)
    print("p = 0.6 ->", plan_at_06)     # expect two 2-way swaps, worth 1.44
