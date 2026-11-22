# DonorBridge: Simple Plan

## The one question
**At what final-test success rate (p) do 3-way swaps stop being worth it?** (Worth it = at least 5% more transplants than 2-way only.)

The whole project is one command that prints a table of results for p from 1.0 down to 0.5, prints the answer, and saves one chart. Anything that does not help with that is deferred.

## How it works (5 steps)
1. **Make a pool** of fake families: each has a patient blood group and a donor blood group. A family joins the pool only if its own donor cannot give to its own patient, either by blood group or because a random tissue test failed.
2. **Draw arrows.** Family i points to family j if i's donor can give to j's patient (blood compatible, and a random tissue test passes). Tissue has to be in the model: with blood groups alone, no 3-way ring can ever form.
3. **Find rings.** List every 2-family swap and 3-family ring (plain nested loops).
4. **Pick the best rings,** with no family used twice. A ring's value is its size (counting) or `size * p ** size` (expected, failure-aware).
5. **Sweep p.** For each p, compare 2-only, 3-way picked by count, and 3-way picked by expected value. Find where the 3-way gain drops below 5%.

## Files
All code lives in one flat folder, `kidney_swap/`. Each file has one owner and is under about 100 lines. How to code each one, and in what order, is in [simple_plan/INSTRUCTIONS.md](simple_plan/INSTRUCTIONS.md).

| File | Contains | Owner |
| --- | --- | --- |
| `pool.py` | `Family` and `Pool` classes, `can_give(donor, patient)`, `make_pool(n, seed)`, and the constants `BLOOD_GROUPS`, `INDIA_BLOOD_MIX`, `TISSUE_PASS_CHANCE` | Generator |
| `rings.py` | `ring_value(ring, p)`, `plan_value(plan, p)` and `find_rings(pool, max_len)` (nested loops). A ring is a tuple of family ids. | Matching |
| `demo.py` | The 6-family worked example, printed step by step for the talk | Matching |
| `greedy.py` | `GreedySolver.solve(rings, p)`: sort by value, take each ring that does not clash | Heuristics |
| `exact.py` | `ExactSolver.solve(rings, p)`: recursive "take this ring or skip it", for small pools | Heuristics |
| `ilp.py` | `IlpSolver.solve(rings, p)`: about 25 lines with `pulp` (HiGHS backend), used for the real runs | Lead |
| `compare_solvers.py` | `compare(n_pools, n_families)`: proves the exact solver and the ILP agree on random pools | Lead |
| `sweep.py` | `run_sweep`, `find_crossover`, `print_table`, `save_chart` | Simulation |
| `main.py` | `uv run python kidney_swap/main.py` runs everything, prints the answer, saves `results/sweep.png` | Lead |

Every solver has the same method, `solve(rings, p)`, which returns the chosen rings.

Each file has a check script in `simple_plan/checks/` that says what's wrong in plain English. `uv run python simple_plan/checks/check_all.py` runs them all.

## Rules for the code
- Plain functions and small classes only: `Family`, `Pool`, and one class per solver. No base classes, no abstract classes, no decorators, no type tricks.
- Readable beats tidy. Long names, comments in plain English, and repeated code are fine.
- A beginner who has done Python up to OOP must be able to read every file top to bottom. If a line needs explaining, add a comment or rewrite it.
- Libraries: `random`, `matplotlib`, and `pulp` (ILP only, with `pulp.HiGHS`; the default CBC solver doesn't run on Apple-silicon Macs). All are already installed. Use `uv run`.
- Each file ends with a small `if __name__ == "__main__":` block that runs a tiny example, so you can see it work alone.
- Fix the assumptions once: rings up to 3 families, every test passes with the same probability p, and only blood group plus one fixed random tissue-pass chance decide compatibility.

## Order of work (no dates, each step finishes before the next)
1. **Setup (Lead):** create `kidney_swap/` and merge this plan into `main`. (Done.)
2. **Unblock (Matching):** push `ring_value` and `plan_value` first, because every solver imports them.
3. **Build in parallel:**
   - Generator: `pool.py`
   - Matching: `find_rings`
   - Heuristics: `greedy.py`, then `exact.py`
   - Lead: `ilp.py`
   - Simulation: `sweep.py`

   Each person's check uses fake data where it can, so nobody waits.
4. **Glue:** Matching writes `demo.py`. The Lead writes `compare_solvers.py`, then `main.py`.
5. **Results and story (all):**
   - `check_all.py` is green.
   - Run `main.py` with 100 families × 20 pools (about a minute) and read the chart.
   - Build the deck: the problem, the 5 steps, the chart, p*, and the limits (all patients simulated, no clinical rules).

## Done means
- `uv run python simple_plan/checks/check_all.py` passes.
- `uv run python kidney_swap/main.py` prints the table and p*, and saves the chart.
- Everyone can explain their own file out loud.

## Deferred (not now)
`kep_solver` and Glasgow checks, 2-way matching, branch and bound, local search, 4-rings, the fairness and gender experiments, regional pools, India-vs-US charts, runtime charts, the night-before re-solve simulation, altruist chains, the web viewer, the integration-test gates and stub-skip system, per-task AI logs, and the four extra team playbooks. The original, bigger plan is kept for reference in [docs/original_plan.md](docs/original_plan.md).

## Open choices
- Keep the AI usage log? Keep one short `AI_LOG.md` if the course rubric needs it.
