"""The sweep: run the experiment for many values of p and find where 3-way rings stop being worth it."""

import matplotlib.pyplot as plt
# from rings import find_rings, plan_value    # turn this on when rings.py is on this branch (needed by run_sweep)


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