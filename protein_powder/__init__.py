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
    """Checks if output.csv exists."""
    check50.exists("output.csv")


@check50.check(exists)
def check_structure():
    """Checks if strucutre of output.csv is correct."""
    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["amino", "fold"]:
            raise check50.Failure("Expected header of csv to be 'amino, fold'")

        # Check if all values in the amino column are of correct datatype and
        # value, except for the last row.
        if df["amino"].dtype != "object" or \
                False in df["amino"][:-1].isin(["H", "P", "C"]).values:
            raise check50.Failure("Invalid value in 'amino' column.")

        # Check if all values in the fold column are of correct datatype and
        # value, except for the last row.
        if df["fold"].dtype != "int" or \
                False in df["fold"][:-1].isin([0, -1, 1, -2, 2, -3, 3]).values:
            raise check50.Failure("Invalid value in 'fold' column.")

        # Check if the score in the last row is of correct value.
        if df["fold"].values[-1] > 0:
            raise check50.Failure("Score of the fold is higher than 0.")


@check50.check(check_structure)
def check_score():
    """Checks if given solution produces given score."""
    hc_pos = {}

    with open("output.csv") as csvfile:
        items = list(csv.reader(csvfile))
        user_score = items[-1][1]
        pos = [0, 0, 0]
        prev_dir = 0

        # Store position of all Hs and Cs and their origin.
        for row in items[1:-1]:
            if row[0] == "H" or row[0] == "C":
                hc_pos[tuple(pos)] = [row[0], prev_dir]

            # Move to next amino acid and store direction.
            prev_dir = -row[1]

            if dir == 1 or dir == -1:
                pos[0] += 1
            elif dir == 2 or dir == -2:
                pos[1] += dir
            elif dir == 3 or dir == -3:
                pos[2] += dir

    # Loop over all Hs and Cs and compute their score to get the total score.
    score = 0

    for amino in hc_pos.items():
        pass

    # Compare computed score with the one from the CSV.
    if score != user_score:
        raise check50.Failure(f"Computed score {score} does not equal given "
                              f"score {user_score}")