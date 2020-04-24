#!/usr/bin/env python3
"""
This file uses check50 to check the output of an SmartGrid solution. It
does so by doing the following tests in this order:
    - Check if output.csv exits
    - Check if the file has valid values and is structured correctly
    - TODO: Add more tests!

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
    """Check if the structure and values of output.json are correct."""
    # Check if output.json has content.
    if os.stat("output.csv").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header row and a row with the used chip and "
                              "costs.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["net", "wires"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'net,wires'")

        # Check footer for correct format.
        if len(df) < 1 or df["net"].iloc[-1][:5] != "chip_":
            raise check50.Failure("Expected last row of the csv to be "
                                  "'chip_<int>,<int>'")

        try:
            int(df["net"].iloc[-1][5:])
            int(df["wires"].iloc[-1])
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'chip_<int>,<int>'")

        # Stop checking if no objects are in the output file.
        if len(df) == 1:
            return

        # Check if all connections are of correct types.
        pattern = r"^\(\d+,\d+\)$"
        net_bools = np.array(list(map(lambda x: bool(re.match(pattern, x)),
                                      df["net"][:-1])))

        if False in net_bools:
            idxs = np.where(net_bools == False)[0]
            error = "Invalid coordinates for nets found.\n    Expected " \
                    "coordinates with format '(<int>,<int>)', but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['net'][idx]}' \ton row "
                                        f"{idx + 2}\n"])

            raise check50.Failure(error)

        # Check if all the wires are of correct types.
        pattern = r"^\d+,\d+$"
        coords = [x[2:-2].split("),(") for x in df["wires"][:-1]]
        wire_bools = [list(map(lambda x: bool(re.match(pattern, x)), c))
                      for c in coords]
        wire_bools = [(i, "".join(["(", coords[i][j], ")"]))
                      for i, bools in enumerate(wire_bools)
                      for j, b in enumerate(bools) if not b]

        if wire_bools:
            error = "Invalid coordinates for wires found.\n    Expected " \
                    "coordinates with format '(<int>,<int>)', but found:\n"

            for idx, coord in wire_bools:
                error = "".join([error, f"\t'{coord}' \ton row "
                                        f"{idx + 2}\n"])

            raise check50.Failure(error)


@check50.check(check_file)
def check_structure():
    """Check if the structured solution of output.json is correct."""
    pass


@check50.check(check_structure)
def check_cost():
    """Check if solution costs as much as specified in output.json."""
    pass