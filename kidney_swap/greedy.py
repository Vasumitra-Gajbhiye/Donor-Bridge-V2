"""The greedy solver: a quick way to pick rings that is not always the best.

It sorts the rings by how much each one is worth, biggest first,
then walks down the list and takes every ring that does not share
a family with a ring it already took.
"""

from rings import ring_value


class GreedySolver:
    def solve(self, rings, p):
        """Return the list of rings greedy picks at this p."""

        # Small helper so sorted() knows what to sort by.
        # It sits inside solve() so it can use p.
        def value_of_ring(ring):
            return ring_value(ring, p)

        # sorted() makes a new list, so the rings we were given stay as they are.
        # Rings with the same value keep the order they came in.
        rings_best_first = sorted(rings, key=value_of_ring, reverse=True)

        plan = []
        used_families = set()

        for ring in rings_best_first:
            # Check if any family in this ring is already in the plan
            ring_clashes = False
            for family in ring:
                if family in used_families:
                    ring_clashes = True

            if not ring_clashes:
                plan.append(ring)
                for family in ring:
                    used_families.add(family)

        return plan


if __name__ == "__main__":
    # The 6 family example rings
    example_rings = [(1, 4), (2, 3), (2, 4), (3, 5), (2, 3, 4), (2, 5, 3), (2, 5, 4)]
    solver = GreedySolver()
    print("p = 1.0:", solver.solve(example_rings, 1.0))   # should be [(2, 3, 4)]
    print("p = 0.6:", solver.solve(example_rings, 0.6))   # should be [(1, 4), (2, 3)]
