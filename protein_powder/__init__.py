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
import numpy as np
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
                                  "'amino,fold'")

        # Check if all values in the amino column are of correct datatype and
        # value, except for the last row.
        amino_bools = df["amino"][:-1].isin(["H", "P", "C"]).values

        if False in amino_bools:
            idxs = np.where(amino_bools == False)[0]
            error = "Invalid letter(s) used for an amino. Expected 'H', 'P' " \
                    "or 'C', but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['amino'][idx]}' \ton row "
                                        f"{idx}\n"])

            raise check50.Failure(error)

        # Check if all values in the fold column are of correct datatype and
        # value, except for the last row.
        if df["fold"].dtype != "int":
            error = "Invalid value(s) used for a fold. Expected natural " \
                    "numbers, but found:\n"

            for i, item in enumerate(df['fold']):
                try:
                    int(item)
                except ValueError:
                    error = "".join([error, f"\t'{df['fold'][i]}' \ton row "
                                            f"{i}\n"])

            raise check50.Failure(error)

        # Check if the score in the last row is of correct value.
        if df["fold"].values[-1] > 0:
            raise check50.Failure("The score for a fold should be negative.")


@check50.check(check_file)
def check_structure():
    """Check if amino placement is correct."""
    hc_pos = {}

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)
        user_score = df["fold"].iloc[-1]
        dim = df["fold"][:-1].abs().max()

        # Initialise values for origin amino.
        pos_set = {tuple(0 for _ in range(dim))}
        pos = list(0 for _ in range(dim))
        next_dir = df["fold"].iloc[1]

        if df["amino"].iloc[0] == "H" or df["amino"].iloc[0] == "C":
            hc_pos[tuple(pos)] = [df["amino"].iloc[0], 0, next_dir]

        for _, [amino, fold] in df.iloc[1:-1].iterrows():
            # Compute position of next amino. Check for division by zero.
            if next_dir:
                pos[abs(next_dir) - 1] += next_dir // abs(next_dir)

            # Set link info and remember amino if possible score maker.
            prev_dir = -next_dir
            next_dir = fold

            if amino == "H" or amino == "C":
                hc_pos[tuple(pos)] = [amino, prev_dir, next_dir]

            # Check if protein folds onto itself.
            if tuple(pos) in pos_set:
                raise check50.Failure("Protein folds onto itself, which is "
                                      "not possible.")

            pos_set.update([tuple(pos)])

    return hc_pos, user_score


def get_neighbour_aminos(pos, prev_dir, next_dir, hc_coords):
    """Get non-connected neighbour aminos of the amino at pos."""
    neighbours = []
    moves = list(range(-len(pos), len(pos)))

    for i in moves:
        # Exclude the neighbours that are linked.
        if i == prev_dir or i == next_dir:
            continue

        # Create new position of possible neighbour. Check for division by zero.
        new_pos = list(pos)

        if next_dir:
            new_pos[abs(next_dir) - 1] += next_dir // abs(next_dir)

        new_pos = tuple(new_pos)

        # Only save the position if it is an existing H or C amino.
        if new_pos in hc_coords:
            neighbours.append(new_pos)

    return neighbours


@check50.check(check_structure)
def check_score(state):
    """Check if solution produces score specified in output.csv."""
    hc_pos, user_score = state

    # Loop over all Hs and Cs and compute their score to get the total score.
    hh_score = 0
    hc_score = 0
    cc_score = 0
    hc_coords = hc_pos.keys()

    for pos, [amino, prev_dir, next_dir] in hc_pos.items():
        neighbours = get_neighbour_aminos(pos, prev_dir, next_dir, hc_coords)

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
