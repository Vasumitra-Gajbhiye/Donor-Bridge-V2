"""The exact solver: always finds the best plan, but is slow on big pools.

For each ring we try two options, skip it or take it, and keep
whichever one ends up worth more. Recursion does the bookkeeping.
It also uses a bound (branch and bound) so it can skip trying to take
a ring when that clearly can't beat skipping it.
It is still only meant for small pools (about 15 families or less).
Its main job is to prove the ILP is right.
"""

from rings import ring_value


class ExactSolver:
    def solve(self, rings, p):
        """Return the list of rings with the highest total ring_value at this p."""
        self.rings = rings
        self.p = p
        best_value, best_plan = self.best_from(0, [])
        return best_plan

    def most_we_could_add(self, start, used):
        """A guess at the most rings[start:] could add, that is never too low.

        Every family can only be in one ring. If a family sits in a ring of
        size k, it gets an equal share of that ring's value: ring_value / k.
        So the most a free family can add is its biggest share over the
        rings left that don't clash with `used`. We add that up over all families.
        """
        best_share_of_family = {}
        for ring in self.rings[start:]:
            ring_clashes = False
            for family in ring:
                if family in used:
                    ring_clashes = True
            if not ring_clashes:
                share = ring_value(ring, self.p) / len(ring)
                for family in ring:
                    if family not in best_share_of_family or share > best_share_of_family[family]:
                        best_share_of_family[family] = share

        total = 0
        for family in best_share_of_family:
            total = total + best_share_of_family[family]
        return total

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

        # The bound: if even the most taking could be worth can't beat
        # skipping, don't bother trying it
        most_take_could_be_worth = ring_value(ring, self.p) + self.most_we_could_add(start + 1, used_after_taking)
        if most_take_could_be_worth <= skip_value:
            return skip_value, skip_plan

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
