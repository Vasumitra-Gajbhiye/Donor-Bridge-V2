"""Checks kidney_swap/rings.py (owner: Matching).

Run:  uv run python simple_plan/checks/check_rings.py
"""

from helpers import (EXAMPLE_RINGS, FakePool, check, example_pool, fail, finish, get,
                     random_fake_pool, reference_rings, require, timed)

rings_module = require("rings", owner="Matching")


def t_ring_value():
    ring_value = get(rings_module, "ring_value")
    cases = [((1, 2), 1.0, 2.0), ((1, 2, 3), 1.0, 3.0), ((1, 2), 0.5, 0.5), ((1, 2, 3), 0.5, 0.375),
             ((4, 9), 0.8, 1.28), ((2, 5, 3), 0.6, 0.648)]
    for ring, p, expected in cases:
        got = ring_value(ring, p)
        if got is None:
            fail("ring_value returned None. Did you forget `return`?")
        if abs(got - expected) > 1e-9:
            fail(f"ring_value({ring}, {p}) returned {got}, should be {expected}.\n"
                 f"Formula: len(ring) * p ** len(ring)  (size times p to the power of size).")


def t_plan_value():
    plan_value = get(rings_module, "plan_value")
    if plan_value([], 0.7) != 0:
        fail(f"plan_value([], 0.7) should be 0 (no rings, no transplants). It returned {plan_value([], 0.7)!r}.")
    got = plan_value([(1, 4), (2, 5, 3)], 0.6)
    if abs(got - 1.368) > 1e-9:
        fail(f"plan_value([(1, 4), (2, 5, 3)], 0.6) returned {got}, should be 0.72 + 0.648 = 1.368.\n"
             f"It is the sum of ring_value(ring, p) over every ring in the plan.")


def call_find_rings(pool, max_len):
    find_rings = get(rings_module, "find_rings")
    result = find_rings(pool, max_len)
    if result is None:
        fail("find_rings returned None. Did you forget `return rings`?")
    if not isinstance(result, list):
        fail(f"find_rings should return a list, but returned a {type(result).__name__}.")
    for ring in result:
        if not isinstance(ring, tuple):
            fail(f"Every ring must be a tuple like (2, 5, 3). Found {ring!r} ({type(ring).__name__}).")
    return result


def explain_difference(got, expected):
    missing = sorted(expected - set(got), key=lambda r: (len(r), r))
    extra = sorted(set(got) - expected, key=lambda r: (len(r), r))
    lines = []
    if missing:
        lines.append(f"Missing rings: {missing}")
    if extra:
        lines.append(f"Rings that should not be there: {extra}")
        if any(ring[0] != min(ring) for ring in extra):
            lines.append("Some rings don't start with their smallest id. (3, 5, 2) and (2, 3, 5) are the "
                         "same ring, so only keep the version that starts with the smallest id.")
    duplicates = sorted({ring for ring in got if got.count(ring) > 1})
    if duplicates:
        lines.append(f"Rings listed more than once: {duplicates}. Each ring must appear once.")
    return "\n".join(lines)


def t_example():
    got = call_find_rings(example_pool(), 3)
    expected = set(EXAMPLE_RINGS)
    if sorted(got) != sorted(expected):
        fail("On the 6-family example the 7 rings are:\n"
             f"{EXAMPLE_RINGS}\nYou returned {len(got)}: {got}\n" + explain_difference(got, expected))


def t_max_len_2():
    got = call_find_rings(example_pool(), 2)
    expected = {ring for ring in EXAMPLE_RINGS if len(ring) == 2}
    if sorted(got) != sorted(expected):
        fail(f"find_rings(pool, 2) must return only the 2-way swaps: {sorted(expected)}.\n"
             f"You returned {got}.\nOnly look for 3-way rings when max_len >= 3.")


def t_order():
    got = call_find_rings(example_pool(), 3)
    sizes = [len(ring) for ring in got]
    if sizes != sorted(sizes):
        fail(f"Put all 2-way swaps first, then all 3-way rings. Your order: {got}")


def t_empty_pools():
    got = call_find_rings(FakePool([], set()), 3)
    if got != []:
        fail(f"A pool with no families should give []. You returned {got}.")
    no_arrows = random_fake_pool(5, 0.0, seed=1)
    got = call_find_rings(no_arrows, 3)
    if got != []:
        fail(f"A pool with no arrows should give []. You returned {got}.")


def t_random():
    for seed in range(8):
        pool = random_fake_pool(15, 0.25, seed)
        got = call_find_rings(pool, 3)
        expected = reference_rings(pool, 3)
        if sorted(got) != sorted(expected) or len(got) != len(set(got)):
            fail(f"Random pool (seed {seed}, 15 families) gives a different answer from the "
                 f"networkx library.\nArrows: {sorted(pool.arrows)}\n" + explain_difference(got, expected))


def t_ids_not_positions():
    pool = example_pool()
    for family in pool.families:
        family.id = family.id * 10
    pool.arrows = {(i * 10, j * 10) for (i, j) in pool.arrows}
    got = call_find_rings(pool, 3)
    expected = {tuple(f * 10 for f in ring) for ring in EXAMPLE_RINGS}
    if sorted(got) != sorted(expected):
        fail("With ids 10, 20, ..., 60 instead of 1..6 the rings are wrong.\n"
             "Read the ids from the families ([f.id for f in pool.families]); "
             "don't assume they are 1..n or list positions.\n" + explain_difference(got, expected))


def t_speed():
    pool = random_fake_pool(100, 0.3, seed=0)
    _, seconds = timed(call_find_rings, pool, 3)
    if seconds > 10:
        fail(f"find_rings on 100 families took {seconds:.1f} s. It should take a few seconds at most.\n"
             f"Tip: put the cheap tests first, e.g. `if a < b and (a, b) in pool.arrows:` before the "
             f"third loop, so you skip most of the work early.")


check("ring_value(ring, p) = size * p ** size", t_ring_value)
check("plan_value(plan, p) adds up ring_value", t_plan_value)
check("6-family example: exactly the 7 right rings", t_example)
check("max_len = 2 gives only the 2-way swaps", t_max_len_2)
check("2-way swaps come before 3-way rings", t_order)
check("empty pool and pool with no arrows give []", t_empty_pools)
check("8 random pools match the networkx library", t_random)
check("works when ids are not 1..n", t_ids_not_positions)
check("100 families finishes in reasonable time", t_speed)
finish()
