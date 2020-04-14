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


@check50.check()
def exists():
    """Check if output.csv exists."""
    check50.exists("output.json")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.json are correct."""
    # Check if output.csv has content.
    if os.stat("output.json").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header object with the district and costs, "
                              "and an object for a battery.")

    with open("output.json") as jsonfile:
        df = pd.read_json(jsonfile)

        # Check if header object has the needed attributes.
        attributes = np.array(["district", "cost", "location", "capacity",
                               "houses"])
        attr_bools = np.isin(attributes[:2], list(df))

        if False in attr_bools:
            idxs = np.where(attr_bools == False)[0]
            error = "Did not find all attributes for the header object.\n" \
                    "    Expected to find 'district' and 'cost', but did not " \
                    "find:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{attributes[idx]}'\n"])

            raise check50.Failure(error)

        # Check if the header attributes have a values.
        notna_bools_df = df.loc[0].notna()
        if not notna_bools_df["district"] or not notna_bools_df["cost"]:
            error = "Expected the header object attributes to have a value, " \
                    "but found:\n"

            if not notna_bools_df["district"]:
                error = "".join([error, f"\t'district': \tNaN\n"])

            if not notna_bools_df["cost"]:
                error = "".join([error, f"\t'cost': \tNaN\n"])

            raise check50.Failure(error)

        # Check if the header attributes are ints.
        try:
            district = df.loc[0]["district"].astype("Int64")
        except AttributeError:
            raise check50.Failure("Expected integer value for 'district', but "
                                  f"got:\n\t'{df.loc[0]['district']}'")

        try:
            df.loc[0]["cost"].astype("Int64")
        except AttributeError:
            raise check50.Failure("Expected integer value for 'cost', but got:"
                                  f"\n\t'{df.loc[0]['cost']}'")

        # Check if district is valid number.
        if district not in [1, 2, 3]:
            raise check50.Failure("Expected 1, 2 or 3 for 'district', but got:"
                                  f"\n\t{district}")

        # Check for all batteries if the locations are in valid format.
        loc_coords = df[1:]["location"].values
        coord_bool = [False if False in list(map(str.isdigit, coord.split(",")))
                      else True for coord in loc_coords]

        if False in coord_bool:
            idxs = np.where(np.array(coord_bool) == False)[0]
            error = "Expected battery coordinates to have the format " \
                    "'<int>,<int>', but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{loc_coords[idx]}' \tfor battery "
                                        f"{idx + 1}\n"])

            raise check50.Failure(error)

        # Check for all batteries if the capacity is a float.
        caps = df[1:]["capacity"].values
        caps_error = []

        for i, cap in enumerate(caps):
            try:
                float(cap)
            except ValueError:
                caps_error.append(i)

        if caps_error:
            error = "Expected battery capacities to be floats, but found:\n"

            for idx in caps_error:
                error = "".join([error, f"\t'{caps[idx]}'        \tfor battery "
                                        f"{idx + 1}\n"])

            raise check50.Failure(error)

        # Check location and output of all houses for all batteries.
        error = "Expected all house locations to have format '<int>,<int>' " \
                "and their outputs to be floats, but found:\n"
        loc_errors = []
        out_errors = []

        for i in range(1, len(df)):
            houses = df.loc[i]["houses"]

            for j, house in enumerate(houses):
                loc_bools = list(map(str.isdigit, house["location"].split(",")))

                if False in loc_bools:
                    loc_errors.append([i, j])

                try:
                    float(house["output"])
                except ValueError:
                    out_errors.append([i, j])

        for battery, house in loc_errors:
            location = df.loc[battery]["houses"][house]["location"]
            error = "".join([error, f"\t'{location}' \t as location for house "
                                    f"{house + 1} of battery {battery}\n"])

        for battery, house in out_errors:
            output = df.loc[battery]["houses"][house]["output"]
            error = "".join([error, f"\t'{output}'        \t as output for "
                                    f"house {house + 1} of battery {battery}"
                                    f"\n"])

        if loc_errors or out_errors:
            raise check50.Failure(error)

        # Check if all cables have locations in a valid format.
        error = "Expected all cable locations to be floats, but found:\n"
        cable_errors = []

        for i in range(1, len(df)):
            houses = df.loc[i]["houses"]

            for j, house in enumerate(houses):
                cable_bools = [False if False in list(map(str.isdigit,
                                                          coord.split(",")))
                               else True for coord in house["cables"]]

                if False in cable_bools:
                    idxs = np.where(np.array(cable_bools) == False)[0]

                    for idx in idxs:
                        cable_errors.append([i, j, idx])

        if cable_errors:
            for battery, house, cable in cable_errors:
                coord = df.loc[battery]["houses"][house]["cables"][cable]
                error = "".join([error, f"\t'{coord}' \t for cable "
                                        f"{cable + 1} from house {house + 1} "
                                        f"of battery {battery}\n"])

            raise check50.Failure(error)
