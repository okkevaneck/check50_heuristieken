#!/usr/bin/env python3
"""
This file uses check50 to check the output of an Protein Powder solution. It
does so by doing the following tests in this order:
    - Check if output.csv exits
    - TODO: Add more tests!

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

import check50
import pandas as pd
import numpy as np
import os


@check50.check()
def exists():
    """Check if all files exists."""
    check50.include("../data")
    check50.exists("output.csv")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.csv are correct."""
    # Check if output.csv has content.
    if os.stat("output.csv").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header row and a row with a score.")

    df = pd.read_csv(open("output.csv"))

    # Check header for correct format.
    if list(df) != ["train", "stations"]:
        raise check50.Failure("Expected header of the csv to be "
                              "'train,stations'")

    # Check footer for correct format.
    if len(df) < 1 or df['train'].iloc[-1] != "score" or \
            df['stations'].iloc[-1].dtype != int:
        raise check50.Failure("Expected last row of the csv to be "
                              "'score,<integer>'")

    # Stop checking if there are no tracks are in the output file.
    if len(df) == 1:
        return

    # Check if all train names are unique.
    dup_bools = np.array(df["train"].duplicated())
    if True in dup_bools:
        idxs = np.where(dup_bools == True)[0]
        error = "Expected all train names to be unique, but found " \
                "duplicate:\n"

        for idx in idxs:
            error = "".join([error, f"\t'{df['train'][idx]}' \ton row "
                                    f"{idx}.\n"])

        raise check50.Failure(error)

    # Check if list  of stations is formated correctly and the station
    # exists in StatinosNatinoal.csv.
    existing_stations = df = pd.read_csv(open("/data/StationsNational.csv"))
    # coord_bools = np.array(list(map(lambda x: bool(re.match(pattern, x)), df[pos][:-1])))
