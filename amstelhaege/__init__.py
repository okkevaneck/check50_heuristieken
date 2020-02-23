#!/usr/bin/env python3
"""
This file uses check50 to check the output of an AmstelHaege solution. It
does so by doing the following tests in this order:
    - Check if output.csv exits
    - Check if the file has valid values and is structured correctly
    - TODO: INSERT OTHER TESTS

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

import check50
import pandas as pd
import numpy as np
import os
import re


@check50.check()
def exists():
    """Check if output.csv exists."""
    check50.exists("output.csv")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.csv is correct."""
    # Check if output.csv has content.
    if os.stat("output.csv").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header row and a row with a score.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["structure", "bottom_left_xy", "top_right_xy", "type"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'structure,bottom_left_xy,top_right_xy,"
                                  "type'")

        # Check footer for correct format.
        if len(df) < 1 or df['structure'].iloc[-1] != "score":
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<integer>'")

        try:
            int(df['bottom_left_xy'].iloc[-1])
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<integer>'")

        # Stop checking if no objects are in the output file.
        if len(df) == 1:
            return

        # Check if all values in the coordinate columns are of correct datatype
        # and value, except for the last row.
        pattern = "([0-9]|[1-9][0-9]*),([0-9]|[1-9][0-9]*)"

        for pos in ["bottom_left_xy", "top_right_xy"]:
            coord_bools = list(map(lambda x: bool(re.match(pattern, x)),
                                   df["bottom_left_xy"][:-1]))
            if False in coord_bools:
                idxs = np.where(coord_bools == False)[0]
                error = "Invalid position(s) found for the objects. Expected" \
                        " coordinates with format '<integer>,<integer>', but" \
                        " found:\n"

                for idx in idxs:
                    error = "".join([error, f"\t'{df[pos][idx]}' \ton row "
                                            f"{idx} in '{pos}' column.\n"])

                raise check50.Failure(error)

        # Check if all types are correct.
        type_bools = df["type"][:-1].isin(["WATER", "EENGEZINSWONING",
                                           "BUNGALOW", "MAISON"]).values
        if False in type_bools:
            idxs = np.where(type_bools == False)[0]
            error = "Invalid TYPE(s) used for objects. Expected 'WATER', " \
                    "'EENGEZINSWONING', 'BUNGALOW' or 'MAISON', but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['type'][idx]}' \ton row "
                                        f"{idx}\n"])

            raise check50.Failure(error)

        # Check if all structure names are unique.
        dup_bools = np.array(df["structure"].duplicated())
        if True in dup_bools:
            idxs = np.where(dup_bools == True)[0]
            error = "Expected all structure values to be unique, but found " \
                    "duplicate:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['structure'][idx]}' \ton row "
                                        f"{idx}.\n"])

            raise check50.Failure(error)

        # Check if the percentage of different houses are correct.
        perc = round(df['type'][:-1][df.type != "WATER"]
                     .value_counts(normalize=True) * 100).astype(int)
        if perc["EENGEZINSWONING"] != 60 or perc["BUNGALOW"] != 25 or \
                perc["MAISON"] != 15:
            raise check50.Failure("Percentage of different houses are "
                                  "incorrect")



@check50.check(check_file)
def check_placement():
    """Check if all objects are placed correctly."""
    pass

    # TODO: implement the following checks:
    #   - Are all houses on the 160 x 180 grid?
    #       - Keep rotation in mind.
    #   - Are no houses placed on water?
    #   - Are the vrijstand of the houses at least: (also checks if houses are placed onto each other)
    #       - 2m for EENGEZINSWONING
    #       - 3m for BUNGALOW
    #       - 6m for MAISON


@check50.check(check_placement)
def check_score():
    """Check if solution produces score specified in output.csv."""
    pass
