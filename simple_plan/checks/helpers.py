"""Shared tools for the check scripts.

You do NOT need to edit or understand this file. Just run the check for your file, e.g.
    uv run python simple_plan/checks/check_pool.py
"""

import difflib
import importlib
import os
import random
import sys
import time
import traceback
from itertools import combinations

# Where the team's code lives: <repo>/kidney_swap
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CODE_DIR = os.environ.get("KIDNEY_SWAP_DIR", os.path.join(REPO, "kidney_swap"))
sys.path.insert(0, CODE_DIR)

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"

counts = {"passed": 0, "failed": 0, "skipped": 0}


class CheckFailed(Exception):
    pass


class Skip(Exception):
    pass


def fail(message):
    raise CheckFailed(message)


def skip(message):
    raise Skip(message)


def indent(text):
    return "\n".join("     " + line for line in str(text).splitlines())


def where_it_crashed(error):
    """Find the last line of YOUR code (inside kidney_swap/) that ran before the crash."""
    frames = traceback.extract_tb(error.__traceback__)
    yours = [f for f in frames if os.path.abspath(f.filename).startswith(os.path.abspath(CODE_DIR))]
    if not yours:
        return ""
    last = yours[-1]
    return f"\n     It happened in {os.path.basename(last.filename)}, line {last.lineno}:  {last.line}"


def check(title, test_function):
    """Run one test and print a tick, a cross or a skip with a helpful message."""
    try:
        test_function()
        counts["passed"] += 1
        print(f"{GREEN}  PASS{RESET}  {title}")
    except CheckFailed as error:
        counts["failed"] += 1
        print(f"{RED}  FAIL{RESET}  {title}")
        print(indent(error))
    except Skip as error:
        counts["skipped"] += 1
        print(f"{YELLOW}  SKIP{RESET}  {title}")
        print(indent(error))
    except Exception as error:
        counts["failed"] += 1
        print(f"{RED}  FAIL{RESET}  {title}")
        print(f"     Your code crashed: {type(error).__name__}: {error}{where_it_crashed(error)}")
        print(hint_for(error))


def hint_for(error):
    """Extra advice for crashes we have seen before."""
    text = f"{type(error).__name__}: {error}"
    if "Bad CPU type" in text or "cbc" in text.lower():
        return ("     Hint: pulp's built-in CBC solver does not run on Apple-silicon Macs. "
                "Use problem.solve(pulp.HiGHS(msg=False)) instead.")
    if "RecursionError" in text:
        return "     Hint: your recursion never stops. Check the 'start == len(rings)' base case."
    if "ZeroDivisionError" in text:
        return "     Hint: something divided by zero. When two_way is 0, set the gain to 0 instead of dividing."
    if "NoneType" in text:
        return "     Hint: a function returned None. Check every function ends with a `return` line."
    return ""


def finish():
    """Print the summary and exit with code 1 if anything failed."""
    print()
    total = counts["passed"] + counts["failed"] + counts["skipped"]
    if counts["failed"] == 0 and counts["skipped"] == 0:
        print(f"{GREEN}All {total} checks passed. Your file is done.{RESET}")
    else:
        print(f"{counts['passed']} passed, {RED}{counts['failed']} failed{RESET}, "
              f"{YELLOW}{counts['skipped']} skipped{RESET} (out of {total}).")
        print("Fix the FAIL lines from the top down: an early mistake often causes the later ones.")
    sys.exit(1 if counts["failed"] > 0 else 0)


def require(module_name, owner):
    """Import kidney_swap/<module_name>.py, or stop with a clear message."""
    path = os.path.join(CODE_DIR, module_name + ".py")
    print(f"Checking kidney_swap/{module_name}.py  (owner: {owner})\n")
    if not os.path.exists(path):
        print(f"{RED}  FAIL{RESET}  kidney_swap/{module_name}.py does not exist yet.")
        print(f"     Create it. See simple_plan/INSTRUCTIONS.md, the section for {module_name}.py.")
        sys.exit(1)
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        print(f"{RED}  FAIL{RESET}  {module_name}.py could not be loaded: it imports '{error.name}', "
              f"which does not exist yet.")
        if error.name in ("pool", "rings", "greedy", "exact", "ilp", "sweep"):
            print(f"     That file belongs to someone else. Wait until kidney_swap/{error.name}.py exists"
                  f" (see 'Order of work' in INSTRUCTIONS.md), or ask them to push it.")
        else:
            print("     If it is a library, add it with `uv add <name>` (ask the lead first).")
        sys.exit(1)
    except Exception as error:
        print(f"{RED}  FAIL{RESET}  {module_name}.py crashed while loading, before any check could run.")
        print(f"     {type(error).__name__}: {error}{where_it_crashed(error)}")
        print("     Tip: code at the bottom of the file must sit inside  if __name__ == \"__main__\":")
        sys.exit(1)


def get(module, name):
    """Fetch module.name, or fail with a 'did you mean' hint."""
    if hasattr(module, name):
        return getattr(module, name)
    file_name = module.__name__ + ".py"
    close = difflib.get_close_matches(name, dir(module), n=1)
    hint = f" Did you mean '{close[0]}'? Rename it to '{name}'." if close else ""
    fail(f"{file_name} has nothing called '{name}'.{hint}\n"
         f"Names must match INSTRUCTIONS.md exactly, because other people's files use them.")


def try_load(module_name, what_for):
    """Load someone else's module for a check that needs it, or SKIP the check politely."""
    if not os.path.exists(os.path.join(CODE_DIR, module_name + ".py")):
        skip(f"Can't check {what_for} yet: kidney_swap/{module_name}.py does not exist.")
    try:
        return importlib.import_module(module_name)
    except Exception as error:
        skip(f"Can't check {what_for} yet: {module_name}.py fails to load ({type(error).__name__}: {error}).")


def timed(function, *args):
    start = time.time()
    result = function(*args)
    return result, time.time() - start


# ---------------------------------------------------------------------------------------------
# Reference data, written independently of the team's code
# ---------------------------------------------------------------------------------------------

BLOOD_GROUPS = ["O", "A", "B", "AB"]
GIVES_TO = {"O": ["O", "A", "B", "AB"], "A": ["A", "AB"], "B": ["B", "AB"], "AB": ["AB"]}


def blood_ok(donor_blood, patient_blood):
    return patient_blood in GIVES_TO[donor_blood]


class FakeFamily:
    def __init__(self, id, patient_blood, donor_blood):
        self.id = id
        self.patient_blood = patient_blood
        self.donor_blood = donor_blood


class FakePool:
    def __init__(self, families, arrows):
        self.families = families
        self.arrows = arrows


def example_pool():
    """The 6-family worked example from SimplePlan / INSTRUCTIONS.md."""
    families = [FakeFamily(1, "A", "B"), FakeFamily(2, "O", "B"), FakeFamily(3, "B", "O"),
                FakeFamily(4, "B", "O"), FakeFamily(5, "B", "B"), FakeFamily(6, "B", "AB")]
    arrows = {(1, 4), (1, 6), (2, 3), (2, 4), (2, 5), (2, 6), (3, 1), (3, 2), (3, 4), (3, 5),
              (3, 6), (4, 1), (4, 2), (4, 6), (5, 3), (5, 4), (5, 6)}
    return FakePool(families, arrows)


EXAMPLE_RINGS = [(1, 4), (2, 3), (2, 4), (3, 5), (2, 3, 4), (2, 5, 3), (2, 5, 4)]


def random_fake_pool(n, arrow_chance, seed):
    """A pool with random arrows (no blood rules), for cross-checking."""
    rng = random.Random(seed)
    families = [FakeFamily(i, "O", "O") for i in range(1, n + 1)]
    arrows = set()
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j and rng.random() < arrow_chance:
                arrows.add((i, j))
    return FakePool(families, arrows)


def reference_rings(pool, max_len):
    """Every ring, found with networkx (a completely different method from nested loops)."""
    import networkx as nx
    graph = nx.DiGraph()
    graph.add_nodes_from(f.id for f in pool.families)
    graph.add_edges_from(pool.arrows)
    found = set()
    for cycle in nx.simple_cycles(graph, length_bound=max_len):
        if len(cycle) >= 2:
            start = cycle.index(min(cycle))
            found.add(tuple(cycle[start:] + cycle[:start]))
    return found


def value(ring, p):
    return len(ring) * p ** len(ring)


def plan_total(plan, p):
    return sum(value(ring, p) for ring in plan)


def brute_force_best(rings, p):
    """Try every combination of rings. Slow, but certainly right for small inputs."""
    best = 0.0
    for size in range(1, len(rings) + 1):
        for combo in combinations(rings, size):
            families = [f for ring in combo for f in ring]
            if len(families) == len(set(families)):
                best = max(best, plan_total(combo, p))
    return best


def reference_greedy(rings, p):
    """Stable sort by value (ties keep input order), then take every ring that doesn't clash."""
    taken, used = [], set()
    for ring in sorted(rings, key=lambda r: value(r, p), reverse=True):
        if not used & set(ring):
            taken.append(ring)
            used |= set(ring)
    return taken


def plan_problem(plan, rings):
    """Return a sentence describing what is wrong with a plan, or None if it is a valid plan."""
    if plan is None:
        return "solve() returned None. Did you forget the `return` line?"
    if not isinstance(plan, list):
        return f"solve() must return a list of rings, but it returned a {type(plan).__name__}."
    seen = set()
    for ring in plan:
        if not isinstance(ring, tuple):
            return f"Every ring in the plan must be a tuple, but found {ring!r} ({type(ring).__name__})."
        if ring not in rings:
            return f"The plan contains {ring}, which was not in the rings you were given."
        for family in ring:
            if family in seen:
                return (f"Family {family} is used twice in the plan {plan}. "
                        f"A family can only be in one ring.")
            seen.add(family)
    return None


def small_ring_sets(how_many, seed):
    """Random small ring lists (at most 14 rings, so brute force stays fast)."""
    rng = random.Random(seed)
    sets = []
    while len(sets) < how_many:
        pool = random_fake_pool(rng.randint(3, 8), rng.uniform(0.2, 0.6), rng.randint(0, 10**6))
        rings = sorted(reference_rings(pool, 3), key=lambda r: (len(r), r))
        if 1 <= len(rings) <= 14:
            sets.append(rings)
    return sets


def solver_checks(solver_class, file_name):
    """The checks shared by exact.py and ilp.py (both must find the true best plan)."""
    example = sorted(EXAMPLE_RINGS, key=lambda r: (len(r), r))

    def make_solver():
        try:
            return solver_class()
        except TypeError as error:
            fail(f"Could not create the solver with {solver_class.__name__}(): {error}\n"
                 f"The class should need no arguments to create. Put rings and p in solve(rings, p).")

    def t_has_solve():
        solver = make_solver()
        if not hasattr(solver, "solve"):
            fail(f"{solver_class.__name__} has no method called 'solve'.")

    def t_example_p1():
        plan = make_solver().solve(list(example), 1.0)
        problem = plan_problem(plan, example)
        if problem:
            fail(problem)
        if set(plan) != {(1, 4), (2, 5, 3)}:
            fail(f"On the 6-family example at p = 1.0 the best plan is [(1, 4), (2, 5, 3)] "
                 f"(5 transplants).\nYour plan: {plan} ({plan_total(plan, 1.0):g} transplants).")

    def t_example_p06():
        plan = make_solver().solve(list(example), 0.6)
        problem = plan_problem(plan, example)
        if problem:
            fail(problem)
        got = plan_total(plan, 0.6)
        if abs(got - 1.44) > 1e-6:
            fail(f"On the 6-family example at p = 0.6 the best expected value is 1.44, "
                 f"from two 2-way swaps like [(1, 4), (2, 3)].\nYour plan {plan} is worth {got:.3f}.\n"
                 f"Are you using ring_value(ring, p) with the p you were given?")

    def t_empty():
        plan = make_solver().solve([], 0.9)
        if plan != []:
            fail(f"With no rings, solve() should return [] (an empty list). It returned {plan!r}.")

    def t_random():
        for number, rings in enumerate(small_ring_sets(40, seed=7)):
            for p in (1.0, 0.6):
                plan = make_solver().solve(list(rings), p)
                problem = plan_problem(plan, rings)
                if problem:
                    fail(f"Random test {number} (p = {p}), rings = {rings}\n{problem}")
                best = brute_force_best(rings, p)
                got = plan_total(plan, p)
                if abs(got - best) > 1e-6:
                    fail(f"Random test {number} (p = {p}) is not optimal.\nRings: {rings}\n"
                         f"Your plan: {plan}, worth {got:.4f}\nThe best possible is worth {best:.4f}.")

    def t_input_untouched():
        rings = list(example)
        make_solver().solve(rings, 0.8)
        if rings != example:
            fail("solve() changed the list of rings it was given. Work on a copy "
                 "(e.g. sorted(rings) or list(rings)) so other solvers get the same input.")

    check(f"{solver_class.__name__} can be created and has a solve() method", t_has_solve)
    check("6-family example, p = 1.0: finds [(1, 4), (2, 5, 3)]", t_example_p1)
    check("6-family example, p = 0.6: finds a plan worth 1.44", t_example_p06)
    check("no rings -> returns []", t_empty)
    check("40 random small cases: always as good as trying every combination", t_random)
    check("does not change the input list", t_input_untouched)
