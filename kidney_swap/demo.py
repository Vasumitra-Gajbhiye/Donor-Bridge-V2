"""The live demo for the talk: the 6-family worked example, step by step.

It shows:
  1. the six families,
  2. every possible ring between them,
  3. what Greedy and Exact choose when every final test passes (p = 1.0),
  4. what they choose when each final test only passes 60% of the time (p = 0.6).

Run:  uv run python kidney_swap/demo.py
"""

from pool import Family, Pool
from rings import find_rings, plan_value
from greedy import GreedySolver
from exact import ExactSolver


def build_example_pool():
    """Build the 6-family example from INSTRUCTIONS.md, typed in by hand."""
    families = [
        Family(1, "A", "B"),
        Family(2, "O", "B"),
        Family(3, "B", "O"),
        Family(4, "B", "O"),
        Family(5, "B", "B"),
        Family(6, "B", "AB"),
    ]

    # (i, j) means family i's donor can give a kidney to family j's patient.
    arrows = {
        (1, 4), (1, 6),
        (2, 3), (2, 4), (2, 5), (2, 6),
        (3, 1), (3, 2), (3, 4), (3, 5), (3, 6),
        (4, 1), (4, 2), (4, 6),
        (5, 3), (5, 4), (5, 6),
    }

    return Pool(families, arrows)


def print_line():
    print("-" * 60)


def print_families(pool):
    print("THE FAMILIES (each patient comes with a willing donor)")
    print_line()
    for family in pool.families:
        print(f"  Family {family.id}:  patient is {family.patient_blood:<2}  donor is {family.donor_blood}")
    print()


def print_rings(rings):
    print(f"ALL POSSIBLE RINGS ({len(rings)} of them)")
    print_line()
    for ring in rings:
        # Turn (2, 5, 3) into "2 -> 5 -> 3 -> 2" so the audience can follow the kidneys.
        steps = []
        for family_id in ring:
            steps.append(str(family_id))
        steps.append(str(ring[0]))
        # str(ring) with :<10 pads it to 10 characters, so the "means" column lines up.
        print(f"  {str(ring):<10} means   {' -> '.join(steps)}")
    print()


def print_plan(solver_name, plan, p):
    """Print one solver's plan, how many people it helps, and what it is worth on average."""
    people_helped = 0
    for ring in plan:
        people_helped = people_helped + len(ring)

    print(f"  {solver_name:<6} picks {plan}")
    print(f"         {people_helped} transplants planned, {plan_value(plan, p):.2f} expected")


def compare_solvers_at(rings, p):
    print(f"CHANCE EACH FINAL TEST PASSES: p = {p}")
    print_line()

    greedy_plan = GreedySolver().solve(rings, p)
    exact_plan = ExactSolver().solve(rings, p)

    print_plan("Greedy", greedy_plan, p)
    print_plan("Exact", exact_plan, p)
    print()
    return exact_plan


if __name__ == "__main__":
    pool = build_example_pool()
    rings = find_rings(pool, 3)

    print()
    print_families(pool)
    print_rings(rings)

    # When every test passes, Exact finds a better plan than Greedy (5 transplants vs 3).
    plan_picked_by_count = compare_solvers_at(rings, 1.0)

    # When tests can fail, big rings are risky, and the best plan changes.
    compare_solvers_at(rings, 0.6)

    print("THE PUNCHLINE")
    print_line()
    print(f"  The plan picked at p = 1.0, {plan_picked_by_count},")
    print(f"  is only worth {plan_value(plan_picked_by_count, 0.6):.2f} expected transplants at p = 0.6.")
    print("  Planning for the real chance of failure does better.")
    print()
