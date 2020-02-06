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
def check_structure():
    """Check if strucutre of output.csv is correct."""
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
                False in df["fold"][:-1].isin(list(range(-3,4))).values:
            raise check50.Failure("Invalid direction in output.csv.")

        # Check if the score in the last row is of correct value.
        if df["fold"].values[-1] > 0:
            raise check50.Failure("Score of the fold is higher than 0.")


@check50.check(check_structure)
def check_score():
    """Check if given solution produces given score."""
    hc_pos = {}

    with open("output.csv") as csvfile:
        items = list(csv.reader(csvfile))
        user_score = int(items[-1][1])
        pos_set = {(0, 0, 0)}
        pos = [0, 0, 0]
        prev_dir = 0

        # Store position of all Hs and Cs and their origin.
        for row in items[1:-1]:
            cur_dir = int(row[1])

            if row[0] == "H" or row[0] == "C":
                hc_pos[pos] = [row[0], prev_dir, cur_dir]

            # Move to next amino acid and store direction.
            prev_dir = -cur_dir

            if cur_dir == 1 or cur_dir == -1:
                pos[0] += cur_dir
            elif cur_dir == 2 or cur_dir == -2:
                pos[1] += cur_dir
            elif cur_dir == 3 or cur_dir == -3:
                pos[2] += cur_dir

            # Check if protein folds onto itself.
            if pos in pos_set:
                raise check50.Failure("Protein folds onto itself, which is "
                                      "not possible.")

            pos_set.update([tuple(pos)])

    # Loop over all Hs and Cs and compute their score to get the total score.
    score = 0
    positions = hc_pos.keys()

    for pos, [amino, prev_dir, next_dir] in hc_pos.items():
        neighbours = []

        for i in [-3, -2, -1, 1, 2, 3]:
            if i == prev_dir or i == next_dir:
                continue

            if i == -1 or i == 1:
                pos[0] += i
            elif i == -2 or i == 2:
                pos[1] += i // 2
            elif i == -3 or i == 3:
                pos[1] += i // 3

            neighbours.append(pos)

        # TODO: Itterate over neighbours and compare amino's, edit score accordingly.


    # Compare computed score with the one from the CSV.
    if score != user_score:
        raise check50.Failure("Score in output.csv is not equal to the "
                              "computed score from the output.")