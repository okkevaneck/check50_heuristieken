#!/usr/bin/env python3
"""
This file uses check50 to check if their is an output.csv file, if it is
structured according to the specifications from the case, and if it produces
the score given in the last row.

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

import check50
import pandas as pd
import csv


@check50.check()
def exists():
    """Check if output.csv exists."""
    check50.exists("output.csv")


@check50.check(exists)
def check_file():
    """Check if strucutre and values of output.csv is correct."""
    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["amino", "fold"]:
            raise check50.Failure("Expected header of csv to be "
                                  "['amino, fold']")

        # Check if all values in the amino column are of correct datatype and
        # value, except for the last row.
        if df["amino"].dtype != "object" or \
                False in df["amino"][:-1].isin(["H", "P", "C"]).values:
            raise check50.Failure("Invalid letter used for an amino.")

        # Check if all values in the fold column are of correct datatype and
        # value, except for the last row.
        if df["fold"].dtype != "int" or \
                False in df["fold"][:-1].isin(list(range(-3, 4))).values:
            raise check50.Failure("Invalid direction in output.csv.")

        # Check if the score in the last row is of correct value.
        if df["fold"].values[-1] > 0:
            raise check50.Failure("Score of the fold is higher than 0.")


@check50.check(check_file)
def check_structure():
    """Check if amino placement is correct."""
    hc_pos = {}

    with open("output.csv") as csvfile:
        items = list(csv.reader(csvfile))
        user_score = int(items[-1][1])

        # Initialise values for origin amino.
        pos_set = {(0, 0, 0)}
        pos = [0, 0, 0]
        next_dir = int(items[1][1])

        for row in items[2:-1]:
            # Compute position of next amino.
            if next_dir == 1 or next_dir == -1:
                pos[0] += next_dir
            elif next_dir == 2 or next_dir == -2:
                pos[1] += next_dir // 2
            elif next_dir == 3 or next_dir == -3:
                pos[2] += next_dir // 3

            # Set link info and remember amino if possible score maker.
            prev_dir = -next_dir
            next_dir = int(row[1])

            if row[0] == "H" or row[0] == "C":
                hc_pos[tuple(pos)] = [row[0], prev_dir, next_dir]

            # Check if protein folds onto itself.
            if tuple(pos) in pos_set:
                raise check50.Failure("Protein folds onto itself, which is "
                                      "not possible.")

            pos_set.update([tuple(pos)])

    return hc_pos, user_score


def get_neighbour_aminos(pos, prev_dir, next_dir, positions):
    """Get non-connected neighbour aminos of the amino at pos."""
    neighbours = []

    for i in [-3, -2, -1, 1, 2, 3]:
        if i == prev_dir or i == next_dir:
            continue

        new_pos = list(pos)

        if i == -1 or i == 1:
            new_pos[0] += i
        elif i == -2 or i == 2:
            new_pos[1] += i // 2
        elif i == -3 or i == 3:
            new_pos[2] += i // 3

        new_pos = tuple(new_pos)

        if new_pos in positions:
            neighbours.append(new_pos)

    return neighbours


@check50.check(check_structure)
def check_score(state):
    """Check if given solution produces given score."""
    hc_pos, user_score = state

    # Loop over all Hs and Cs and compute their score to get the total score.
    hh_score = 0
    hc_score = 0
    cc_score = 0
    positions = hc_pos.keys()

    for pos, [amino, prev_dir, next_dir] in hc_pos.items():
        neighbours = get_neighbour_aminos(pos, prev_dir, next_dir, positions)

        # Iterate over neighbour aminos and check if it scored points.
        for n in neighbours:
            if amino == "H" and hc_pos[n][0] == "H":
                hh_score -= 1
            elif amino != hc_pos[n][0]:
                hc_score -= 1
            else:
                cc_score -= 5

    hh_score //= 2
    hc_score //= 2
    cc_score //= 2

    # Compare computed score with the one from the CSV.
    if hh_score + hc_score + cc_score != user_score:
        raise check50.Failure("Score in output.csv is not equal to the "
                              "computed score from the output.\n    Computed "
                              f"score {hh_score + hc_score + cc_score} is "
                              f"made up of:\n\tHH-bonds: {hh_score}\n\t"
                              f"HC-bonds: {hc_score}\n\tCC-bonds: {cc_score}")
