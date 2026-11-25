"""Rings: finding every possible kidney swap in a pool, and working out what a plan is worth.

A "ring" is a tuple of family ids, like (2, 5, 3).
It means: family 2's donor gives to family 5's patient,
          family 5's donor gives to family 3's patient,
          family 3's donor gives to family 2's patient (back to the start).

A "plan" is a list of rings that we decide to carry out, like [(1, 4), (2, 5, 3)].
"""


def ring_value(ring, p):
    """Return the expected number of transplants from one ring.

    p is the chance that one final tissue test passes.
    A ring of size k only goes ahead if all k final tests pass,
    which happens with chance p * p * ... * p (k times) = p ** k.
    If it goes ahead we get k transplants, so on average we get k * p ** k.
    """
    ring_size = len(ring)
    return ring_size * p ** ring_size


def plan_value(plan, p):
    """Return the expected number of transplants from a whole plan.

    This is just ring_value added up over every ring in the plan.
    An empty plan is worth 0.
    """
    total_value = 0
    for ring in plan:
        total_value = total_value + ring_value(ring, p)
    return total_value


def find_rings(pool, max_len):
    """Return a list of every possible ring in the pool.

    pool.families is a list of families (each one has an .id).
    pool.arrows is a set of (i, j) tuples, meaning family i's donor can give to family j's patient.
    max_len is 2 (only 2-way swaps) or 3 (2-way swaps and 3-way rings).

    All 2-way swaps come first, then all 3-way rings.
    Each ring is listed once, starting from its smallest id.
    """
    # Read the ids from the families. They are not always 1, 2, 3, ...
    ids = []
    for family in pool.families:
        ids.append(family.id)

    rings = []

    # 2-way swaps: a gives to b AND b gives to a.
    # We only keep a < b, so (1, 4) is listed but (4, 1) is not (it is the same swap).
    for a in ids:
        for b in ids:
            if a < b and (a, b) in pool.arrows and (b, a) in pool.arrows:
                rings.append((a, b))

    # 3-way rings: a gives to b, b gives to c, c gives back to a.
    # a must be the smallest id in the ring, so each ring is listed once.
    # We do NOT need b < c: (2, 5, 3) and (2, 3, 5) are different rings
    # because the arrows go in a different direction.
    if max_len >= 3:
        for a in ids:
            for b in ids:
                # Check the first arrow before the third loop, so we skip most of the work early.
                if a < b and (a, b) in pool.arrows:
                    for c in ids:
                        c_is_new = a < c and b != c
                        if c_is_new and (b, c) in pool.arrows and (c, a) in pool.arrows:
                            rings.append((a, b, c))

    return rings


if __name__ == "__main__":
    # Small demo: the 2-family swap and 3-family ring from the worked example.
    print("Value of the swap (1, 4) at p = 0.6:", ring_value((1, 4), 0.6))
    print("Value of the ring (2, 5, 3) at p = 0.6:", ring_value((2, 5, 3), 0.6))
    print("Value of the plan [(1, 4), (2, 5, 3)] at p = 0.6:", plan_value([(1, 4), (2, 5, 3)], 0.6))
    print("Value of an empty plan:", plan_value([], 0.6))
