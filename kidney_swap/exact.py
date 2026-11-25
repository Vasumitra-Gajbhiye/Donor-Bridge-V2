"""The exact solver: always finds the best plan, but is slow.

For each ring we try two options, skip it or take it, and keep
whichever one ends up worth more. Recursion does the bookkeeping.
It tries a lot of combinations so it is only for small pools
(about 15 families or less). Its main job is to prove the ILP is right.
"""

from rings import ring_value


class ExactSolver:
    def solve(self, rings, p):
        """Return the list of rings with the highest total ring_value at this p."""
        self.rings = rings
        self.p = p
        best_value, best_plan = self.best_from(0, [])
        return best_plan

    def best_from(self, start, used):
        """Best (value, plan) using only rings[start:], given families in `used` are taken."""

        # No rings left, so nothing more to add
        if start == len(self.rings):
            return 0, []

        # Option 1: skip this ring
        skip_value, skip_plan = self.best_from(start + 1, used)

        ring = self.rings[start]

        # If any family in this ring is already used we can't take it,
        # so skipping is the only option
        for family in ring:
            if family in used:
                return skip_value, skip_plan

        # Option 2: take this ring.
        # Make a new list for the used families, don't change `used` itself
        # because the skip option above still needs the old one.
        used_after_taking = used + list(ring)
        rest_value, rest_plan = self.best_from(start + 1, used_after_taking)
        take_value = ring_value(ring, self.p) + rest_value
        take_plan = [ring] + rest_plan

        # Keep whichever option is worth more
        if take_value > skip_value:
            return take_value, take_plan
        else:
            return skip_value, skip_plan


if __name__ == "__main__":
    # The 6 family example rings
    example_rings = [(1, 4), (2, 3), (2, 4), (3, 5), (2, 3, 4), (2, 5, 3), (2, 5, 4)]
    solver = ExactSolver()
    print("p = 1.0:", solver.solve(example_rings, 1.0))   # should be [(1, 4), (2, 5, 3)]
    print("p = 0.6:", solver.solve(example_rings, 0.6))   # worth 1.44, e.g. [(1, 4), (2, 3)]
