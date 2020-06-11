#!/usr/bin/env python3
"""
This file uses check50 to check the output of an AmstelHaege solution. It
does so by doing the following tests in this order:
    - Check if output.csv exits
    - Check if the file has valid values and is structured correctly
    - Check if the structures are placed without violating a constraint
    - Check if the total networth is computed correctly

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

import check50
from shapely.geometry import Polygon, MultiPolygon
import pandas as pd
import numpy as np
import math
import os
import re


# Define common used variables.
TYPES = ["WATER", "EENGEZINSWONING", "BUNGALOW", "MAISON"]
CORNER_LABELS = [f"corner_{x}" for x in range(1, 5)]


@check50.check()
def exists():
    """Check if output.csv exists."""
    check50.exists("output.csv")
    check50.include("neighbourhoods/")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.csv are correct."""
    # Check if output.csv has content.
    if os.stat("output.csv").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header row and a row with a networth.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["structure", "corner_1", "corner_2", "corner_3",
                        "corner_4", "type"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'structure,corner_1,corner_2,corner_3,"
                                  "corner_4,type'")

        # Check footer for correct format.
        if len(df) < 1 or df["structure"].iloc[-1] != "networth":
            raise check50.Failure("Expected last row of the csv to be "
                                  "'networth,<integer>'")

        try:
            int(df['corner_1'].iloc[-1])
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'networth,<integer>'")

        # Stop checking if no objects are in the output file.
        if len(df) == 1:
            return

        # Check if all types are correct.
        type_bools = df["type"][:-1].isin(TYPES).values
        if False in type_bools:
            idxs = np.where(type_bools == False)[0]
            error = "Invalid TYPE(s) used for objects.\n    Expected " \
                    "'WATER', 'EENGEZINSWONING', 'BUNGALOW' or 'MAISON', " \
                    "but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['type'][idx]}' \ton row "
                                        f"{idx + 2}\n"])

            raise check50.Failure(error)

        # Check if all structure names are unique.
        dup_bools = np.array(df["structure"].duplicated())
        if True in dup_bools:
            idxs = np.where(dup_bools == True)[0]
            error = "Expected all structure values to be unique, but found " \
                    "duplicate:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['structure'][idx]}' \ton row "
                                        f"{idx + 2}.\n"])

            raise check50.Failure(error)

        # Check if the percentage of different houses are correct.
        perc = round(df['type'][:-1][df.type != "WATER"]
                     .value_counts(normalize=True) * 100).astype(int)
        if perc["EENGEZINSWONING"] != 60 or perc["BUNGALOW"] != 25 or \
                perc["MAISON"] != 15:
            raise check50.Failure("Percentage of different houses are "
                                  "incorrect")

        # Check if all values in the coordinate columns are of correct datatype
        # and value, except for the last row.
        pattern = r"^(\d+(?:\.\d+)?),(\d+(?:\.\d+)?)+$"

        for pos in CORNER_LABELS:
            coord_bools = np.array(list(map(lambda x:
                                            bool(re.match(pattern, x)),
                                            df[pos][:-1])))

            if False in coord_bools:
                idxs = np.where(coord_bools == False)[0]
                error = "Invalid coordinates found.\n    Expected " \
                        "coordinates with format '<int|float>,<int|float>', " \
                        "but found:\n"

                for idx in idxs:
                    error = "".join([error, f"\t'{df[pos][idx]}' \ton row "
                                            f"{idx + 2} in '{pos}' column.\n"])

                raise check50.Failure(error)

        # Check if the coordinates are in correct order for making rectangular
        # polygons.
        inv_structures = []
        correct_areas = {"WATER": 0.0, "EENGEZINSWONING": 64.0,
                         "BUNGALOW": 77.0, "MAISON": 120.0}

        for s_type, area in zip(TYPES, correct_areas.values()):
            for row in df.loc[df['type'] == s_type].values:
                p = Polygon(tuple(map(float, c.split(","))) for c in row[1:-1])

                if s_type != "WATER" and round(p.area) != area:
                    inv_structures.append([row[-1], row[0], p.area])

        if inv_structures:
            inv_structures.sort()
            error = "Invalid coordinates found.\n    Expected to form" \
                    " a rectangle with correct area, but found area of:\n"

            for s in inv_structures:
                idx = df[df["structure"] == s[1]].index.tolist()[0]
                error = "".join([error, f"\t{s[2]} instead of "
                                        f"{correct_areas[s[0]]}\t for '{s[1]}'"
                                        f" on row {idx + 2}\n"])

            raise check50.Failure(error)


@check50.check(check_file)
def check_placement():
    """Check if all objects are placed correctly."""
    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Create Polygons from the coordinates and check if they overlap.
        ps_water = {}
        ps_houses = {}
        overlap = []

        for row in df[:-1].values:
            p = Polygon(tuple(map(float, c.split(","))) for c in row[1:-1])

            if p.within(MultiPolygon(list(ps_water.values()))):
                overlap.append([row[0], "Water"])

            if p.within(MultiPolygon(list(ps_houses.values()))):
                overlap.append([row[0], "House"])

            if row[-1] == "WATER":
                ps_water[row[0]] = p
            else:
                ps_houses[row[0]] = p

        if overlap:
            error = "Structures may not overlap, but found:\n"

            for s in overlap:
                idx = df[df["structure"] == s[0]].index.tolist()[0]
                error = "".join([error, f"\t{s[1]} was overlapped by '{s[0]}' "
                                        f"   \ton row {idx + 2}\n"])

            raise check50.Failure(error)

        # Check if the area of the total map is 180x160.
        polys = list(ps_water.values())
        polys.extend(list(ps_houses.values()))
        bounds = MultiPolygon(polys).bounds
        x_dim = bounds[2] - bounds[0]
        y_dim = bounds[3] - bounds[1]

        if x_dim > 180.0 or y_dim > 160.0:
            raise check50.Failure(f"The area has a dimension of "
                                  f"'{x_dim}x{y_dim}' and thus exceeds "
                                  f"180x160.")

        free_space = {}
        house_polys = list(ps_houses.values()) # TODO: Add one big rectangle poly with hole in the middle for the map.
        min_extra_meters = [0, 2, 3, 6]
        invalid_houses = np.array([[0, 0, 0]], ndmin=2)

        # Check if the minimal extra meters for houses are correct.
        for s, p in ps_houses.items():
            other_houses = list(house_polys)
            other_houses.remove(p)
            free_space[s] = math.floor(p.distance(MultiPolygon(other_houses)))
            s_type = df[df["structure"] == s]["type"].values[0]
            req_space = min_extra_meters[TYPES.index(s_type)]

            if req_space > free_space[s]:
                invalid_houses = np.append(invalid_houses,
                                           [[s, free_space[s], req_space]],
                                           axis=0)

        if invalid_houses[1:].size:
            error = "Structures with less than minimal free meters found:\n"

            for s, space, req_space in invalid_houses[1:]:
                idx = df[df["structure"] == s].index.tolist()[0]
                error = "".join([error, f"\t'{s}' \t has {space} free meters "
                                        f"instead of {req_space} on row "
                                        f"{idx + 2}\n"])

            raise check50.Failure(error)


@check50.check(check_placement)
def check_score():
    """Check if solution produces networth specified in output.csv."""
    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Create a Polygon for each house.
        ps_houses = {}

        for row in df.iloc[:-1].loc[df.type != "WATER"].values:
            p = Polygon(tuple(map(float, c.split(","))) for c in row[1:-1])
            ps_houses[row[0]] = p

        # Compute the free meters per house.
        free_space = {}
        house_polys = list(ps_houses.values())

        for s, p in ps_houses.items():
            other_houses = list(house_polys)
            other_houses.remove(p)
            free_space[s] = math.floor(p.distance(MultiPolygon(other_houses)))

        # Fetch structures per type and compute networths to make up the total
        # networth.
        base_worths = [2850, 3990, 6100]
        perc_incr = [3, 4, 6]
        networths = [0, 0, 0]

        for i, type in enumerate(TYPES[1:]):
            structures = df[df.type == type]["structure"].values
            networths[i] += base_worths[i] * 100 * len(structures)

            for s in structures:
                networths[i] += perc_incr[i] * free_space[s] \
                                * base_worths[i]

        if sum(networths) != int(df["corner_1"].iloc[-1]):
            raise check50.Failure("Networth in output.csv is not equal to the "
                                  "computed networth from the output.\n    "
                                  f"Computed networth of {sum(networths):,} "
                                  "is made up of:\n"
                                  f"\t{networths[0]:,} \tfrom '{TYPES[1]}'\n"
                                  f"\t{networths[1]:,} \tfrom '{TYPES[2]}'\n"
                                  f"\t{networths[2]:,} \tfrom '{TYPES[3]}'\n")
