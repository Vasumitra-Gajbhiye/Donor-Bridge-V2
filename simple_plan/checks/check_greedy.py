"""Checks kidney_swap/greedy.py (owner: Heuristics).

Run:  uv run python simple_plan/checks/check_greedy.py
"""

from helpers import (EXAMPLE_RINGS, check, fail, finish, get, plan_problem, plan_total,
                     reference_greedy, require, small_ring_sets)

greedy_module = require("greedy", owner="Heuristics")
example = sorted(EXAMPLE_RINGS, key=lambda r: (len(r), r))


def solve(rings, p):
    GreedySolver = get(greedy_module, "GreedySolver")
    try:
        solver = GreedySolver()
    except TypeError as error:
        fail(f"GreedySolver() failed: {error}. The class should need no arguments; "
             f"rings and p go into solve(rings, p).")
    if not hasattr(solver, "solve"):
        fail("GreedySolver has no method called 'solve'.")
    plan = solver.solve(rings, p)
    problem = plan_problem(plan, rings)
    if problem:
        fail(problem)
    return plan


def t_example_p1():
    plan = solve(list(example), 1.0)
    if plan != [(2, 3, 4)]:
        fail(f"At p = 1.0, greedy should take the most valuable ring first: (2, 3, 4), worth 3.\n"
             f"After that every other ring clashes, so the plan is [(2, 3, 4)].\nYour plan: {plan}\n"
             f"(Yes, greedy only gets 3 here while the best is 5. That is the point of the demo.)")


def t_example_p06():
    plan = solve(list(example), 0.6)
    if sorted(plan) != [(1, 4), (2, 3)]:
        fail(f"At p = 0.6 a 2-way swap is worth 0.72 and a 3-way ring only 0.648, so greedy takes 2-way "
             f"swaps first:\n(1, 4), then (2, 3); everything else clashes. Expected [(1, 4), (2, 3)], "
             f"got {plan}.\nAre you sorting by ring_value(ring, p) with the p you were given?")


def t_empty():
    plan = solve([], 0.9)
    if plan != []:
        fail(f"With no rings, solve() should return []. It returned {plan!r}.")


def t_maximal():
    for rings in small_ring_sets(40, seed=3):
        plan = solve(list(rings), 0.8)
        used = {family for ring in plan for family in ring}
        for ring in rings:
            if ring not in plan and not used & set(ring):
                fail(f"Rings: {rings}\nYour plan: {plan}\nRing {ring} shares no family with the plan, "
                     f"so greedy should have taken it.")


def t_matches_rule():
    for number, rings in enumerate(small_ring_sets(60, seed=5)):
        for p in (1.0, 0.6):
            plan = solve(list(rings), p)
            expected = reference_greedy(rings, p)
            if sorted(plan) != sorted(expected):
                fail(f"Random test {number} (p = {p})\nRings (in the order given): {rings}\n"
                     f"Expected plan: {expected} (worth {plan_total(expected, p):.3f})\n"
                     f"Your plan:     {plan} (worth {plan_total(plan, p):.3f})\n"
                     f"Rule: sort by ring_value, biggest first. When two rings have the same value, keep "
                     f"them in the order they were given\n(Python's sorted(..., reverse=True) does this). "
                     f"Then walk down the list and take each ring that shares no family with what you took.")


def t_input_untouched():
    rings = list(example)
    solve(rings, 0.8)
    if rings != example:
        fail("solve() changed the list it was given (rings.sort() sorts in place). "
             "Use sorted(rings, ...) instead, which makes a new list.")


check("6-family example, p = 1.0: plan is [(2, 3, 4)]", t_example_p1)
check("6-family example, p = 0.6: plan is [(1, 4), (2, 3)]", t_example_p06)
check("no rings -> returns []", t_empty)
check("never leaves out a ring it could still add", t_maximal)
check("60 random cases follow the greedy rule exactly", t_matches_rule)
check("does not change the input list", t_input_untouched)
finish()
