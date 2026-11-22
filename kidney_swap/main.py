"""The main experiment: should India allow 3-way kidney swaps, and up to what p?

p is the chance that one transplant's final tests pass. For each p we compare:
  - two_way:           only 2-way swaps allowed
  - three_by_count:    3-way rings allowed, plan picked by raw count (as if p were 1.0)
  - three_by_expected: 3-way rings allowed, plan picked by expected transplants at the real p
and find the p below which 3-way rings stop being worth it (gain under 5%).
"""

import os

from pool import make_pool
from ilp import IlpSolver
from sweep import run_sweep, print_table, find_crossover, save_chart

P_VALUES = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
CHART_PATH = "results/sweep.png"


def main(n_families, n_pools):
    # 1. Make the random pools. Seed 0, 1, 2, ... so every run gives the same pools.
    print(f"Making {n_pools} pools of {n_families} families each...")
    pools = []
    for seed in range(n_pools):
        pools.append(make_pool(n_families, seed))

    # 2. Run the sweep: for every p, the average transplants under each policy.
    print("Running the sweep (this can take a minute)...")
    print()
    rows = run_sweep(pools, P_VALUES, IlpSolver())

    # 3. Show the results as a table.
    print_table(rows)
    print()

    # 4. The headline answer.
    crossover = find_crossover(rows)
    if crossover is None:
        print(f"ANSWER: 3-way rings add at least 5% more expected transplants at every p we tried "
              f"(down to p = {P_VALUES[-1]}).")
    else:
        print(f"ANSWER: 3-way rings are worth it (5% or more extra expected transplants) "
              f"only while p is above about {crossover:.2f}.")

    # 5. Save the chart.
    os.makedirs("results", exist_ok=True)
    save_chart(rows, CHART_PATH)
    print(f"Chart saved to {CHART_PATH}")


if __name__ == "__main__":
    main(100, 20)      # about a minute
