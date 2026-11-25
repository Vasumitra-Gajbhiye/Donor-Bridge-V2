"""The exact solver: always finds the best plan, but is slow on big pools.

For each ring we try two options, take it or skip it, and remember the
best plan we have seen. It uses branch and bound to go faster: at each
step it works out the most the current plan could still grow to, and if
that can't beat the best plan found so far it stops going down that path.
It is still only meant for small pools (about 15 families or less).
Its main job is to prove the ILP is right.
"""

from rings import ring_value


class ExactSolver:
    def solve(self, rings, p):
        """Return the list of rings with the highest total ring_value at this p."""
        self.rings = rings
        self.p = p

        # The best plan seen so far. Starts as the empty plan, worth 0.
        self.best_value = 0
        self.best_plan = []

        self.search(0, [], [], 0)
        return self.best_plan

    def clashes(self, ring, used):
        """True if any family in this ring is already in `used`."""
        for family in ring:
            if family in used:
                return True
        return False

    def search(self, start, used, plan_so_far, value_so_far):
        """Try every way to add rings[start:] to plan_so_far, and remember the best one.

        used is the list of families already in plan_so_far,
        value_so_far is what plan_so_far is worth.
        """

        # Is the plan we have right now the best one yet?
        if value_so_far > self.best_value:
            self.best_value = value_so_far
            self.best_plan = plan_so_far

        # No rings left, so nothing more to add
        if start == len(self.rings):
            return

        # The bound: a guess at the most we could still add, that is never too low.
        # Every family can only be in one ring. If a family sits in a ring of
        # size k, it gets an equal share of that ring's value: ring_value / k.
        # So the most a free family can add is its biggest share over the
        # remaining rings that don't clash. Add that up over all free families.
        best_share_of_family = {}
        for later_ring in self.rings[start:]:
            if not self.clashes(later_ring, used):
                share = ring_value(later_ring, self.p) / len(later_ring)
                for family in later_ring:
                    if family not in best_share_of_family or share > best_share_of_family[family]:
                        best_share_of_family[family] = share

        most_we_could_still_add = 0
        for family in best_share_of_family:
            most_we_could_still_add = most_we_could_still_add + best_share_of_family[family]

        # If even that can't beat the best plan so far, stop going down this path.
        if value_so_far + most_we_could_still_add <= self.best_value:
            return

        ring = self.rings[start]

        # Option 1: take this ring, if it doesn't clash.
        # We try taking first because it finds good plans early, which makes
        # the bound cut off more paths later.
        # used + list(ring) makes a new list so `used` itself doesn't change
        # (option 2 below still needs the old one). Same for the plan.
        if not self.clashes(ring, used):
            self.search(start + 1,
                        used + list(ring),
                        plan_so_far + [ring],
                        value_so_far + ring_value(ring, self.p))

        # Option 2: skip this ring
        self.search(start + 1, used, plan_so_far, value_so_far)


if __name__ == "__main__":
    # The 6 family example rings
    example_rings = [(1, 4), (2, 3), (2, 4), (3, 5), (2, 3, 4), (2, 5, 3), (2, 5, 4)]
    solver = ExactSolver()
    print("p = 1.0:", solver.solve(example_rings, 1.0))   # should be [(1, 4), (2, 5, 3)]
    print("p = 0.6:", solver.solve(example_rings, 0.6))   # worth 1.44, e.g. [(1, 4), (2, 3)]
