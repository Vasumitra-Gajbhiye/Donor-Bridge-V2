"""The sweep: run the experiment for many values of p and find where 3-way rings stop being worth it."""

import matplotlib.pyplot as plt

from rings import find_rings, plan_value


def find_crossover(rows, threshold=5.0):
    """Return the p where the 3-way gain first drops below threshold (in percent).

    rows are ordered from p = 1.0 downwards. Each row is a dict with at least
    "p" and "gain_by_expected".
    Returns None if the gain never drops below the threshold.
    """
    for index in range(len(rows)):
        row = rows[index]

        if row["gain_by_expected"] < threshold:
            # This is the first row where the gain is too small.

            # If it is the very first row, there is no earlier row to draw a line from.
            if index == 0:
                return row["p"]

            # Otherwise the crossover is between the row before and this row.
            row_before = rows[index - 1]
            p_before = row_before["p"]                    # higher p, gain was still big enough
            gain_before = row_before["gain_by_expected"]
            p_after = row["p"]                            # lower p, gain is too small
            gain_after = row["gain_by_expected"]

            # Draw a straight line between the two points and find where it hits the threshold.
            fraction_of_the_way = (threshold - gain_after) / (gain_before - gain_after)
            crossover_p = p_after + (p_before - p_after) * fraction_of_the_way
            return crossover_p

    # No row was below the threshold.
    return None


def print_table(rows):
    """Print one line per row: p, the three averages, and the two gains (in percent)."""
    # Header line, so every column has a label.
    print("   p    two_way   3way_by_count   3way_by_expected   gain_by_count   gain_by_expected")

    for row in rows:
        # The numbers after the colon set the width and the decimals, so the columns line up.
        print(f"{row['p']:4.1f}   "
              f"{row['two_way']:8.2f}   "
              f"{row['three_by_count']:13.2f}   "
              f"{row['three_by_expected']:16.2f}   "
              f"{row['gain_by_count']:12.1f}%   "
              f"{row['gain_by_expected']:15.1f}%")


def save_chart(rows, path):
    """Draw the three lines (average transplants against p) and save the picture to path."""
    # Pull one list out of the rows for each line on the chart.
    p_values = []
    two_way_values = []
    three_by_count_values = []
    three_by_expected_values = []
    for row in rows:
        p_values.append(row["p"])
        two_way_values.append(row["two_way"])
        three_by_count_values.append(row["three_by_count"])
        three_by_expected_values.append(row["three_by_expected"])

    plt.plot(p_values, two_way_values, marker="o", label="2-way swaps only")
    plt.plot(p_values, three_by_count_values, marker="o", label="3-way rings, picked by count")
    plt.plot(p_values, three_by_expected_values, marker="o", label="3-way rings, picked by expected value")

    plt.xlabel("p (chance that one final test passes)")
    plt.ylabel("Average expected transplants per pool")
    plt.title("Are 3-way kidney rings worth it?")
    plt.legend()

    plt.savefig(path)
    plt.close()


def run_sweep(pools, p_values, solver):
    """Run the experiment for every p in p_values and return one row (a dict) per p.

    Each row has: p, two_way, three_by_count, three_by_expected, gain_by_count, gain_by_expected.
    The three totals are averages over all the pools. The gains are in percent.
    """
    # Running totals, one number per p. We add each pool's score to these.
    two_way_totals = {}
    three_by_count_totals = {}
    three_by_expected_totals = {}
    for p in p_values:
        two_way_totals[p] = 0.0
        three_by_count_totals[p] = 0.0
        three_by_expected_totals[p] = 0.0

    for pool in pools:
        # Find every ring once per pool. The rings do not depend on p.
        rings = find_rings(pool, 3)

        # Keep only the 2-way swaps, for the "2-way only" policy.
        two_way_rings = []
        for ring in rings:
            if len(ring) == 2:
                two_way_rings.append(ring)

        # The count plan is PICKED as if p were 1.0 (raw count), so it is the same for every p.
        # It is still SCORED with the real p below.
        count_plan = solver.solve(rings, 1.0)

        for p in p_values:
            two_way_plan = solver.solve(two_way_rings, p)
            expected_plan = solver.solve(rings, p)

            two_way_totals[p] = two_way_totals[p] + plan_value(two_way_plan, p)
            three_by_count_totals[p] = three_by_count_totals[p] + plan_value(count_plan, p)
            three_by_expected_totals[p] = three_by_expected_totals[p] + plan_value(expected_plan, p)

    # Turn the totals into averages and gains, one row per p, in the same order as p_values.
    number_of_pools = len(pools)
    rows = []
    for p in p_values:
        two_way = two_way_totals[p] / number_of_pools
        three_by_count = three_by_count_totals[p] / number_of_pools
        three_by_expected = three_by_expected_totals[p] / number_of_pools

        # Gain = how much more the 3-way plan gets than 2-way only, as a percent of 2-way only.
        # If 2-way only gets nothing we cannot divide by it, so the gain is 0.
        if two_way == 0:
            gain_by_count = 0
            gain_by_expected = 0
        else:
            gain_by_count = (three_by_count - two_way) / two_way * 100
            gain_by_expected = (three_by_expected - two_way) / two_way * 100

        row = {
            "p": p,
            "two_way": two_way,
            "three_by_count": three_by_count,
            "three_by_expected": three_by_expected,
            "gain_by_count": gain_by_count,
            "gain_by_expected": gain_by_expected,
        }
        rows.append(row)

    return rows


if __name__ == "__main__":
    # Try find_crossover on two made-up rows.
    fake_crossover_rows = [
        {"p": 0.8, "gain_by_expected": 9.3},
        {"p": 0.7, "gain_by_expected": 3.5},
    ]
    print(find_crossover(fake_crossover_rows))    # expect about 0.726

    # Try print_table on made-up rows with every column.
    fake_table_rows = [
        {"p": 0.8, "two_way": 33.28, "three_by_count": 34.33, "three_by_expected": 36.38,
         "gain_by_count": 3.2, "gain_by_expected": 9.3},
        {"p": 0.7, "two_way": 25.48, "three_by_count": 23.99, "three_by_expected": 26.37,
         "gain_by_count": -5.8, "gain_by_expected": 3.5},
    ]
    print_table(fake_table_rows)