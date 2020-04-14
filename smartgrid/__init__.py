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
from collections import Counter


@check50.check()
def exists():
    """Check if output.csv exists."""
    check50.exists("output.json")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.json are correct."""
    # Check if output.json has content.
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


@check50.check(check_file)
def check_structure():
    """Check if the structured solution of output.json is correct."""
    with open("output.json") as jsonfile:
        df = pd.read_json(jsonfile)

        # Check if the houses and batteries do not overlap.
        battery_locs = df[1:]["location"].to_list()
        house_locs = np.array([[battery, house["location"]]
                       for battery, houses in enumerate(df[1:]["houses"])
                       for house in houses])

        # Check for overlap between batteries.
        dup_bools =  pd.DataFrame(battery_locs).duplicated(keep=False).values

        if True in dup_bools:
            idxs = np.where(dup_bools == True)[0]
            error = "Expected no overlap between batteries, but found " \
                    "duplicate locations:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{battery_locs[idx]}' \tfrom "
                                        f"battery {idx + 1}\n"])
            raise check50.Failure(error)

        # Check for overlap between houses.
        dup_bools = pd.DataFrame(house_locs[:,1]).duplicated(keep=False).values

        if True in dup_bools:
            idxs = np.where(dup_bools == True)[0]
            error = "Expected no overlap between houses, but found duplicate" \
                    "locations:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{house_locs[idx][1]}' \tfrom "
                                        f"house {idx + 1} of battery "
                                        f"{int(house_locs[idx][0]) + 1}\n"])
            raise check50.Failure(error)

        # Check for overlap between batteries and houses.
        battery_df = pd.DataFrame(battery_locs)
        house_df = pd.DataFrame(house_locs[:,1])
        battery_overlap = battery_df[0].isin(house_df[0])
        house_overlap = house_df[0].isin(battery_df[0])

        if True in battery_overlap.values or True in house_overlap.values:
            battery_idxs = np.where(battery_overlap == True)[0]
            house_idxs = np.where(house_overlap == True)[0]
            error = "Expected no overlap between batteries and houses, but " \
                    "found duplicate locations:\n"

            for idx in battery_idxs:
                error = "".join([error, f"\t'{battery_locs[idx]}' \tfrom "
                                        f"battery {idx + 1}\n"])

            for idx in house_idxs:
                error = "".join([error, f"\t'{house_locs[idx][1]}' \tfrom "
                                        f"house {idx + 1} of battery "
                                        f"{int(house_locs[idx][0]) + 1}\n"])

            raise check50.Failure(error)

        # Check if cables do connect house with battery.
        for i in range(1, len(df)):
            dest_x, dest_y = list(map(int, df.loc[i]["location"].split(",")))
            houses = df.loc[i]["houses"]

            for j, house in enumerate(houses):
                cur_x, cur_y = list(map(int, house["location"].split(",")))

                # Check if first cable is same as the house location.
                if house["cables"][0] != house["location"]:
                    raise check50.Failure(f"Expected first cable to connect to"
                                          f"the house, but found:\n\t"
                                          f"'{house['cables'][0]}' instead of "
                                          f"'{house['location']}'")

                for cable in house["cables"][1:]:
                    new_x, new_y = list(map(int, cable.split(",")))

                    # Raise error if step size is bigger than 1. `!=` is a xor.
                    if not ((abs(cur_x - new_x) == 1 and cur_y - new_y == 0) !=
                            (cur_x - new_x == 0 and abs(cur_y - new_y) == 1)):
                        raise check50.Failure(f"Expected the cables to follow "
                                              f"each other up, but found the "
                                              f"gap:\n\t'{cur_x},{cur_y}' "
                                              f"-> '{new_x},{new_y}' \tfor "
                                              f"house {j + 1} of battery "
                                              f"{i + 1}")

                    cur_x += new_x - cur_x
                    cur_y += new_y - cur_y

                # Check if last cable is same as the battery.
                if cur_x != dest_x or cur_y != dest_y:
                    raise check50.Failure(f"Expected last cable to connect to "
                                          f"the battery, but found:\n\t"
                                          f"'{cur_x},{cur_y}' instead of "
                                          f"'{df.loc[i]['location']}'")

        # Check if capacities are not exceeded.
        for i in range(1, len(df)):
            capacity = df.loc[i]["capacity"]
            output = sum([house["output"] for house in df.loc[i]["houses"]])

            if capacity - output < 0:
                raise check50.Failure(f"Capacity of battery {i} was exceeded."
                                      f"\n\tCapacity: \t{capacity}\n"
                                      f"\tTotal usage: \t{output}")


@check50.check(check_structure)
def check_cost():
    """Check if solution costs as much as specified in output.json."""
    # TODO: Implement.
    pass
