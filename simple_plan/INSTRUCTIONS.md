# DonorBridge: How to code each file

Read [SimplePlan.md](../SimplePlan.md) first for the why. This file covers the how: who writes what, in what order, and how to check your work.

## Who owns what

| Person | Files | Size of the job |
| --- | --- | --- |
| **Lead** | `ilp.py`, `compare_solvers.py`, `main.py` | Medium. Also merges PRs and unblocks people. |
| **Generator** | `pool.py` | Medium |
| **Matching** | `rings.py`, `demo.py` | Medium |
| **Heuristics** | `greedy.py`, `exact.py` | Medium-large (the recursion in `exact.py` is the hardest part of the project) |
| **Simulation** | `sweep.py` | Medium-large |

All code goes in one flat folder, `kidney_swap/`. Nobody edits someone else's file. If you need a change in another file, ask its owner.

## Order of work

```text
Step 0  Lead          create kidney_swap/ and merge this plan into main   (DONE)
Step 1  Matching      ring_value + plan_value in rings.py, push straight away (everyone imports them)
Step 2  in parallel:  Generator   -> pool.py
                      Matching    -> find_rings in rings.py
                      Heuristics  -> greedy.py, then exact.py
                      Lead        -> ilp.py
                      Simulation  -> find_crossover, print_table, save_chart, then run_sweep
Step 3  Matching      demo.py           (needs pool, rings, greedy, exact)
        Lead          compare_solvers.py, then main.py   (needs everything)
Step 4  Everyone      check_all.py is green -> run main.py with 100 families -> read the chart -> deck
```

## How to check your work

Every file has a check script. Run it as often as you like:

```bash
uv run python simple_plan/checks/check_pool.py      # Generator
uv run python simple_plan/checks/check_rings.py     # Matching
uv run python simple_plan/checks/check_greedy.py    # Heuristics
uv run python simple_plan/checks/check_exact.py     # Heuristics
uv run python simple_plan/checks/check_ilp.py       # Lead
uv run python simple_plan/checks/check_sweep.py     # Simulation
uv run python simple_plan/checks/check_demo.py      # Matching
uv run python simple_plan/checks/check_lead.py      # Lead (compare_solvers.py + main.py)
uv run python simple_plan/checks/check_all.py       # everything, in order
```

- **PASS** means that part is right.
- **FAIL** comes with a sentence saying what is wrong, and often how to fix it. Fix failures from the top down.
- **SKIP** means the check needs someone else's file first. It is not your fault.

The checks don't depend on each other's code wherever possible. For example, `check_rings.py` uses its own fake pool, so Matching never waits for Generator. Your file is done when its check says "All N checks passed".

## Rules for everyone

- Use plain loops, `if`s, functions and small classes. No inheritance, no decorators, no lambdas you can't explain.
- Use long, clear names. Comment anything a classmate might not get on first read.
- Names must match this file exactly (`make_pool`, `find_rings`, `solve`, ...), because other files import them.
- End each file with a small demo you can run alone:
  ```python
  if __name__ == "__main__":
      print(can_give("O", "A"))   # try things out here
  ```
- Run with `uv run python kidney_swap/<file>.py`. Never `pip install`.
- Git: branch `simple/<role>` from `main`, commit often, and open a PR when your check passes. The Lead merges.

## The worked example (used by every check)

Six families, as (patient blood, donor blood):

| Family | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Patient | A | O | B | B | B | B |
| Donor | B | B | O | O | B | AB |

- **Arrows** (i → j means i's donor can give to j's patient): (1,4) (1,6) (2,3) (2,4) (2,5) (2,6) (3,1) (3,2) (3,4) (3,5) (3,6) (4,1) (4,2) (4,6) (5,3) (5,4) (5,6)
- **Rings:** (1,4) (2,3) (2,4) (3,5) (2,3,4) (2,5,3) (2,5,4)
- **p = 1.0:**
  - Greedy takes (2,3,4) → 3 transplants.
  - Exact takes (1,4) + (2,5,3) → 5 transplants.
- **p = 0.6:**
  - The best plan is two swaps, e.g. (1,4) + (2,3), worth 1.44.
  - The count-picked plan (1,4) + (2,5,3) is worth only 1.37.

---

## `rings.py` (Matching): do Step 1 first

### Step 1: two tiny functions (push these within the first hour)

```python
def ring_value(ring, p):
    # A ring of size k only happens if all k final tests pass: k * p^k expected transplants
    ...

def plan_value(plan, p):
    # Sum of ring_value over every ring in the plan. An empty plan is worth 0.
    ...
```

### Step 2: `find_rings(pool, max_len)`

- **Input:**
  - `pool.families`, a list of objects with `.id`
  - `pool.arrows`, a set of `(i, j)` tuples
  - `max_len`, which is 2 or 3
- **Output:** a list of tuples. List all 2-way swaps first, then all 3-way rings (only if `max_len >= 3`).
- **Each ring is listed once, starting from its smallest id.** `(2, 5, 3)`, `(5, 3, 2)` and `(3, 2, 5)` are the same ring, so keep only `(2, 5, 3)`.
- **Direction matters.** `(2, 5, 3)` means 2→5→3→2. `(2, 3, 5)` would be 2→3→5→2, which is a different ring and might not exist.
- Get the ids from the families (`ids = [f.id for f in pool.families]`). Don't assume they are 1..n.

```python
ids = [family.id for family in pool.families]
rings = []

# 2-way swaps: a gives to b AND b gives to a
for a in ids:
    for b in ids:
        if a < b and ...:          # a < b so each swap appears once
            rings.append((a, b))

# 3-way rings: a -> b -> c -> a, with a the smallest id
if max_len >= 3:
    for a in ids:
        for b in ids:
            # Tip: test (a, b) in pool.arrows here, before the third loop. It makes it ~10x faster.
            for c in ids:
                ...
```

Common mistakes:
- Checking `a < b < c`. That loses rings like `(2, 5, 3)`. You want `a` smaller than both `b` and `c`, and `b != c`.
- Writing an arrow test backwards.

### `demo.py` (Step 3): the live demo for the talk

Build the 6-family example with `Family` and `Pool` from `pool.py`, typing the arrows in by hand. Then print, in readable sentences:

1. The families.
2. The rings from `find_rings`.
3. At p = 1.0: greedy's plan with `GreedySolver`, and the exact plan with `ExactSolver`, each with `plan_value`.
4. The same at p = 0.6.

Make the output easy to read on a projector. It must contain the words "Greedy" and "Exact" and the ring tuples.

---

## `pool.py` (Generator)

### Constants at the top

```python
BLOOD_GROUPS = ["O", "A", "B", "AB"]
INDIA_BLOOD_MIX = {"O": ..., "A": ..., "B": ..., "AB": ...}   # fractions that add up to 1.0
TISSUE_PASS_CHANCE = 0.89    # docs/original_plan.md: crossmatch is positive ~11% of the time for unrelated pairs
```

Take the blood mix from Agrawal et al. (2014), the 10,000-donor study linked in [docs/original_plan.md](../docs/original_plan.md). Write the source in a comment.

### What to write

1. **`can_give(donor, patient)`** returns True or False.
   - O gives to everyone.
   - A gives to A and AB.
   - B gives to B and AB.
   - AB gives only to AB.

   A small dict is the easiest way:
   ```python
   GIVES_TO = {"O": ["O", "A", "B", "AB"], "A": [...], ...}
   ```
2. **`class Family`** with `__init__(self, id, patient_blood, donor_blood)`, which stores all three.
3. **`class Pool`** with `__init__(self, families, arrows)`, which stores `self.families` (a list) and `self.arrows` (a set of `(i, j)`).
4. **`make_pool(n, seed)`** returns a `Pool` with exactly `n` families, ids `1..n`.

```python
def make_pool(n, seed):
    rng = random.Random(seed)    # use rng everywhere below, never plain random.xxx()
    groups = list(INDIA_BLOOD_MIX.keys())
    weights = list(INDIA_BLOOD_MIX.values())

    families = []
    while len(families) < n:
        patient = rng.choices(groups, weights)[0]
        donor = rng.choices(groups, weights)[0]
        # The family only needs a swap if its own donor CAN'T give to its own patient:
        # either the blood doesn't match, or it matches but the tissue test fails.
        ...
        families.append(Family(len(families) + 1, patient, donor))

    arrows = set()
    # for every pair of different families i, j:
    #     if i's donor can give to j's patient by blood, AND a tissue roll passes
    #     (rng.random() < TISSUE_PASS_CHANCE), add (i.id, j.id)
    ...
    return Pool(families, arrows)
```

Why tissue matters: without it, no 3-way ring can ever form, because only O donors can reach O patients.

---

## `greedy.py` (Heuristics)

```python
from rings import ring_value

class GreedySolver:
    def solve(self, rings, p):
        # 1. Sort rings by ring_value(ring, p), biggest first.
        #    Use sorted(..., reverse=True), NOT rings.sort(). sorted() leaves the input alone
        #    and keeps equal-valued rings in their original order (the check relies on that).
        # 2. Keep a set `used` of family ids already in the plan.
        # 3. Walk down the sorted list: if the ring shares no family with `used`, take it.
        # 4. Return the list of rings you took.
        ...
```

Greedy is fast but not always best. On the example at p = 1.0 it gets 3 transplants where 5 are possible. That's the demo's punchline.

## `exact.py` (Heuristics): the hand-written exact solver

The idea: for each ring in turn, either **skip it** or **take it** (only if it doesn't clash). Try both, keep the better one. The recursion does the bookkeeping.

```python
from rings import ring_value

class ExactSolver:
    def solve(self, rings, p):
        self.rings = rings
        self.p = p
        best_value, best_plan = self.best_from(0, [])
        return best_plan

    def best_from(self, start, used):
        """Best (value, plan) using only rings[start:], given families in `used` are taken."""
        if start == len(self.rings):
            return 0, []                       # no rings left: nothing to add

        # Option 1: skip this ring
        skip_value, skip_plan = self.best_from(start + 1, used)

        ring = self.rings[start]
        # If the ring clashes with `used`, skipping is the only option -> return it
        ...
        # Option 2: take this ring -> recurse with its families added to `used`,
        #           then add ring_value(ring, self.p) to that value and put ring in front of that plan
        ...
        # Return whichever option is worth more
        ...
```

This tries a huge number of combinations, so it's only for small pools (up to about 15 families). That's fine: its job is to prove the ILP is right.

Extra credit: add a bound ("even if I took every remaining ring, could I beat the best so far? If not, stop"). That turns it into branch and bound. Only do this once the check passes.

---

## `ilp.py` (Lead)

The same problem, handed to a solver library. It is fast enough for 100 families (about 0.25 s per solve).

```python
import pulp
from rings import ring_value

class IlpSolver:
    def solve(self, rings, p):
        if len(rings) == 0:
            return []
        problem = pulp.LpProblem("pick_rings", pulp.LpMaximize)
        # one yes/no variable per ring
        x = [pulp.LpVariable(f"ring_{k}", cat="Binary") for k in range(len(rings))]
        # objective: total value of the chosen rings
        problem += pulp.lpSum(...)
        # one rule per family: at most one chosen ring contains it
        # (build a dict family -> list of that family's ring variables first, then add each rule once)
        ...
        problem.solve(pulp.HiGHS(msg=False))   # NOT the default CBC: it doesn't run on Apple-silicon Macs
        return [rings[k] for k in range(len(rings)) if x[k].value() > 0.5]
```

## `compare_solvers.py` (Lead)

`compare(n_pools, n_families)` does the following:

- For each seed `0..n_pools-1`:
  - Make a pool and find its rings.
  - Solve with both `ExactSolver` and `IlpSolver` at p = 1.0 and p = 0.7.
  - Compare `plan_value`. Print one line per pool.
- Print a summary and **return the number of mismatches**.

This is the correctness evidence slide: "on 100 random pools, our hand-written solver and the ILP agree".

## `main.py` (Lead)

```python
def main(n_families, n_pools):
    # 1. pools = [make_pool(n_families, seed) for seed in range(n_pools)]
    # 2. rows = run_sweep(pools, [1.0, 0.9, 0.8, 0.7, 0.6, 0.5], IlpSolver())
    # 3. print_table(rows)
    # 4. print("ANSWER: ...") using find_crossover(rows)
    # 5. os.makedirs("results", exist_ok=True); save_chart(rows, "results/sweep.png")
    ...

if __name__ == "__main__":
    main(100, 20)      # about a minute
```

---

## `sweep.py` (Simulation)

Four functions. Do the first three before `find_rings` exists, then `run_sweep`.

### `find_crossover(rows, threshold=5.0)`

Rows are ordered from p = 1.0 downwards.
- Find the first row whose `gain_by_expected` is below `threshold`.
- If it's the very first row, return its `p`.
- If no row is below, return `None`.
- Otherwise draw a straight line between that row and the one before it, and return the p where the line hits the threshold. With 9.3% at p = 0.8 and 3.5% at p = 0.7:
  ```text
  0.7 + 0.1 * (5 - 3.5) / (9.3 - 3.5) = 0.726
  ```

### `print_table(rows)`

Print one line per row, with p, the three totals and the gains. Use f-strings like `f"{row['p']:.1f}"` to line things up.

### `save_chart(rows, path)`

Draw three lines with `matplotlib.pyplot`: `two_way`, `three_by_count` and `three_by_expected` against `p`. Add axis labels, a legend and a title. Then call `plt.savefig(path)` and `plt.close()`.

### `run_sweep(pools, p_values, solver)`

Returns one row (a dict) per p, in the same order as `p_values`:

```python
{"p": 0.8, "two_way": ..., "three_by_count": ..., "three_by_expected": ...,
 "gain_by_count": ..., "gain_by_expected": ...}      # gains in percent
```

```python
from rings import find_rings, plan_value

# for each pool:
#     rings = find_rings(pool, 3)                        # once per pool
#     two_way_rings = only the rings of length 2
#     count_plan = solver.solve(rings, 1.0)              # picked by count: once per pool, same for every p
#     for each p:
#         add plan_value(solver.solve(two_way_rings, p), p)  to the two_way total for p
#         add plan_value(count_plan, p)                      to the three_by_count total for p
#         add plan_value(solver.solve(rings, p), p)          to the three_by_expected total for p
# then divide each total by len(pools), and compute
#     gain = (three - two_way) / two_way * 100     (use 0 when two_way is 0)
```

The key idea of the project:
- The count plan is **picked** with p = 1.0 (raw count) but **scored** with the real p.
- The expected plan is picked and scored with the real p.
- The gap between these two lines is the headline.
