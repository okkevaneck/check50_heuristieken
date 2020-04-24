#!/usr/bin/env python3
"""
This file uses check50 to check the output of an Chips & Circuits solution. It
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
    # Check if output.csv has content.
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
                                  "'chip_[1|2],<int>'")

        try:
            int(df["wires"].iloc[-1])
            chip_id = int(df["net"].iloc[-1][5:])

            # Check if chip in footer is either 1 or 2.
            if chip_id not in [1, 2]:
                raise check50.Failure(f"Expected chip number to be 1 or 2, but "
                                      f"found:\n\tchip_{chip_id} \ton row "
                                      f"{len(df) + 1}")
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'chip_[1|2],<int>'")

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
        pattern = r"^\d+,\d+(,\d+)?$"
        coords = [x[2:-2].split("),(") for x in df["wires"][:-1]]
        wire_bools = [list(map(lambda x: bool(re.match(pattern, x)), c))
                      for c in coords]
        wire_bools = [(i, "".join(["(", coords[i][j], ")"]))
                      for i, bools in enumerate(wire_bools)
                      for j, b in enumerate(bools) if not b]

        if wire_bools:
            error = "Invalid coordinates for wires found.\n    Expected " \
                    "coordinates with format '(<int>,<int>[,<int>])', but " \
                    "found:\n"

            for idx, coord in wire_bools:
                error = "".join([error, f"\t'{coord}' \ton row "
                                        f"{idx + 2}\n"])

            raise check50.Failure(error)


@check50.check(check_file)
def check_structure():
    """Check if the structured solution of output.csv is correct."""
    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)
        chip_id = int(df["net"].iloc[-1][5:])

        # Create dict with coordinates of the print nets.
        print_pos_3d = {}

        with open(f"data/chip_{chip_id}/print_{chip_id}.csv") as printfile:
        # with open("print.csv") as printfile: # TODO: Remove and use above.
            print_df = pd.read_csv(printfile)

            for id, x, y in print_df.values:
                print_pos_3d[id] = (x, y, 0)

        # Create lists with all coordinates in 3D.
        wire_coords = [x[2:-2].split("),(") for x in df["wires"][:-1]]
        wire_coords = [[tuple(int(c) for c in coord.split(","))
                        for coord in coords] for coords in wire_coords]
        wire_coords_3d = [[c if len(c) == 3 else (c[0], c[1], 0)
                           for c in coords] for coords in wire_coords]

        # Check if the coordinates of the nets in the print are also in the list
        # with wires.
        net_errors = []

        for i, wires in enumerate(wire_coords_3d):
            net_1, net_2 = df["net"].iloc[i][1:-1].split(",")

            if print_pos_3d[int(net_1)] not in wires:
                net_errors.append([i, net_1, print_pos_3d[int(net_1)]])

            if print_pos_3d[int(net_2)] not in wires:
                net_errors.append([i, net_2, print_pos_3d[int(net_2)]])

        if net_errors:
            error = "Expected to find all coordinates of nets in the wire " \
                    "lists, but did not find:\n"

            for idx, net, coord_3d in net_errors:
                error = "".join([error, f"\t'({coord_3d[0]},{coord_3d[1]},"
                                        f"{coord_3d[2]})' or '({coord_3d[0]},"
                                        f"{coord_3d[1]})' \tfor net {net} \ton "
                                        f"row {idx + 2}\n"])

            raise check50.Failure(error)

        # Check if any of the intermediate wires overlap. Only begin and end may
        # overlap since this is the net itself.
        # TODO: Implement

        # Check if the paths do connect the nets.
        # TODO: Implement


@check50.check(check_structure)
def check_cost():
    """Check if solution costs as much as specified in output.csv."""
    pass

    # TODO: Count number of wires and check if that number equals the costs in
    #       output.csv