#!/usr/bin/env python3
"""
This file uses check50 to check the output of an SmartGrid solution. It
does so by doing the following tests in this order:
    - Check if output.csv exits
    - Check if the file has valid values and is structured correctly
    - Check if houses are connected properly to their batteries, with or
      without sharing cables.
    - Check if the given costs are correct, with or without sharing cables.

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

import check50
import pandas as pd
import numpy as np
import os
import networkx as nx


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
        error = "Did not find all attributes for the header object.\n" \
                "    Expected to find 'district' and 'costs-own' or " \
                "'costs-shared',\n    but did not find:\n"
        found_error = False

        if not np.isin(["district"], list(df)):
            found_error = True
            error = "".join([error, f"\t'district'\n"])

        if not np.isin(["costs-own"], list(df)) and \
                not np.isin(["costs-shared"], list(df)):
            found_error = True
            error = "".join([error, f"\t'costs-own' or 'costs-shared'\n"])

        if found_error:
            raise check50.Failure(error)

        if np.isin(["costs-own"], list(df)):
            cost_label = "costs-own"
        else:
            cost_label = "costs-shared"

        # Check if the header attributes have a values.
        notna_bools_df = df.loc[0].notna()
        if not notna_bools_df["district"] or not notna_bools_df[cost_label]:
            error = "Expected the header object attributes to have a value, " \
                    "but found:\n"

            if not notna_bools_df["district"]:
                error = "".join([error, f"\t'district': \tNaN\n"])

            if not notna_bools_df["cost_label"]:
                error = "".join([error, f"\t'cost': \tNaN\n"])

            raise check50.Failure(error)

        # Check if the header attributes are ints.
        try:
            district = df.loc[0]["district"].astype("Int64")
        except AttributeError:
            raise check50.Failure("Expected integer value for 'district', but "
                                  f"got:\n\t'{df.loc[0]['district']}'")

        try:
            df.loc[0][cost_label].astype("Int64")
        except AttributeError:
            raise check50.Failure(f"Expected integer value for '{cost_label}', "
                                  f"but got:\n\t'{df.loc[0][cost_label]}'")

        # Check if district is valid number.
        if district not in [1, 2, 3]:
            raise check50.Failure("Expected 1, 2 or 3 for 'district', but got:"
                                  f"\n\t{district}")

        # Check attributes for every battery.
        error = f"Expected batteries to have the attributes 'location', " \
                f"'capacity' and 'houses', but did not find:\n"
        attributes = ["location", "capacity", "houses"]
        missed_label = False

        for i in range(1, len(df)):
            key_bools = [df.loc[i].notna()[a] for a in attributes]

            if False in key_bools:
                idxs = np.where(np.array(key_bools) == False)[0]
                missed_label = True

                for idx in idxs:
                    error = "".join([error, f"\t'{attributes[idx]}' \tfor "
                                            f"battery {i}\n"])

        if missed_label:
            raise check50.Failure(error)

        # Check if all houses are lists with dictionaries.
        error = f"Expected houses to be lists of dictionaries, but found " \
                f"that:\n"
        found_error = False

        for i in range(1, len(df)):
            if type(df.loc[i]["houses"]) != list:
                found_error = True
                error = "".join([error, f"\t'houses' is not a list for battery "
                                        f"{i}\n"])
            else:
                for j, house in enumerate(df.loc[i]["houses"]):
                    if type(house) != dict:
                        found_error = True
                        error = "".join([error, f"\tHouse {j + 1} \tof battery "
                                                f"{i} \tis not a dictionary\n"])

        if found_error:
            raise check50.Failure(error)

        # Check attributes for every house.
        error = f"Expected houses to have the attributes 'location', " \
                f"'output' and 'cables', but did not find:\n"
        attributes = ["location", "output", "cables"]
        missed_label = False

        for i in range(1, len(df)):
            for j, house in enumerate(df.loc[i]["houses"]):
                key_bools = [a in house for a in attributes]

                if False in key_bools:
                    idxs = np.where(np.array(key_bools) == False)[0]
                    missed_label = True

                    for idx in idxs:
                        error = "".join([error, f"\t'{attributes[idx]}' \tfor "
                                                f"house {j + 1} of battery "
                                                f"{i}\n"])

        if missed_label:
            raise check50.Failure(error)

        # Check if all cables are lists with strings.
        error = f"Expected cables to be lists of strings, but found that:\n"
        found_error = False

        for i in range(1, len(df)):
            for j, house in enumerate(df.loc[i]["houses"]):
                if type(house["cables"]) != list:
                    found_error = True
                    error = "".join([error, f"\t'cables' is not a list for "
                                            f"house {j + 1} of battery {i}\n"])
                else:
                    for k, cable in enumerate(house["cables"]):
                        if type(cable) != str:
                            found_error = True
                            error = "".join([error, f"\tCable {k + 1} \tfrom "
                                                    f"house {j + 1} \tof "
                                                    f"battery {i} \tis not a "
                                                    f"string\n"])

        if found_error:
            raise check50.Failure(error)

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

        # Check if cables connect the houses to their batteries.
        error = "Expected all houses to connect to their battery, but found " \
                "that:\n"
        found_error = False

        # Collect all cables if they are shared.
        if np.isin(["costs-shared"], list(df)):
            cables = set()
            for i in range(1, len(df)):
                for house in df.loc[i]["houses"]:
                    for cable in house["cables"]:
                        cables.add(tuple(map(int, cable.split(","))))

        # Loop over all batteries.
        for i in range(1, len(df)):
            battery_coords = tuple(map(int, df.loc[i]["location"].split(",")))

            # Check for all houses if the cables make a path to the battery.
            for j, house in enumerate(df.loc[i]["houses"]):
                house_coords = tuple(map(int, house["location"].split(",")))

                graph = nx.Graph()
                graph.add_nodes_from([0, 1])
                nodes = {battery_coords: 0, house_coords: 1}

                # Set booleans for checking if the house and battery have a
                # cable.
                battery_cable = False
                house_cable = False

                # Fetch all cables for this battery house combination if cables
                # are not shared and check if house and batteries have cables.
                if np.isin(["costs-own"], list(df)):
                    for k, n in enumerate(house["cables"]):
                        cable_coords = tuple(map(int, n.split(",")))
                        if cable_coords == battery_coords:
                            battery_cable = True
                        elif cable_coords == house_coords:
                            house_cable = True
                        else:
                            graph.add_node(k + 2)
                            nodes[cable_coords] = k + 2

                # Check if houses and battery have cables if cables are shared
                # and add cables to nodes.
                else:
                    if battery_coords in cables:
                        battery_cable = True

                    if house_coords in cables:
                        house_cable = True

                    if battery_cable and house_cable:
                        for k, cable in enumerate(cables):
                            if cable != battery_coords and \
                                    cable != house_coords:
                                graph.add_node(k + 2)
                                nodes[cable] = k + 2

                # Create edges between neighbouring nodes.
                for coord, id in nodes.items():
                    cur_pos = list(coord)

                    # Check neighbours by changing a specific axis.
                    for move in [-2, -1, 1, 2]:
                        cur_pos[abs(move) - 1] += move // abs(move)

                        if tuple(cur_pos) in nodes:
                            graph.add_edge(id, nodes[tuple(cur_pos)])

                        cur_pos[abs(move) - 1] -= move // abs(move)

                # Check if the house and battery have been connected.
                if not battery_cable:
                    error = "".join([error, f"\tBattery {i} \thas no cable "
                                            f"cable to connect to House "
                                            f"{j + 1}\n"])
                    found_error = True

                if not house_cable:
                    error = "".join([error, f"\tHouse {j + 1} \tof Battery "
                                            f"{i} \t has no outgoing"
                                            f" cable\n"])
                    found_error = True

                # Check if there is a path between the house and the battery.
                if battery_cable and house_cable and \
                        not nx.has_path(graph, 0, 1):
                    error = "".join([error, f"\tBattery {i} \tis not "
                                            f"connected to House {j + 1}"
                                            f"\n"])
                    found_error = True

        # Raise errors if there were any during connected check.
        if found_error:
            raise check50.Failure(error)

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
    with open("output.json") as jsonfile:
        df = pd.read_json(jsonfile)

        # Collect all cables.
        cables = []
        for i in range(1, len(df)):
            for house in df.loc[i]["houses"]:
                cables.extend(house["cables"])

        # Determine if cables may be shared and remove duplicates if so.
        if np.isin(["costs-shared"], list(df)):
            cables = list(set(cables))
            cost_label = "costs-shared"
        else:
            cost_label = "costs-own"

        cable_costs = 9 * len(cables)
        battery_costs = 5000 * len(df[1:])
        total_costs = cable_costs + battery_costs

        if total_costs != df.loc[0][cost_label]:
            raise check50.Failure(f"Costs in output.json is not equal to the "
                                  f"computed costs.\n    Computed costs of "
                                  f"{total_costs} is made up of:\n\t"
                                  f"{len(cables)} cables: \t{len(cables)} * 9 "
                                  f" \t= {cable_costs}\n\t{len(df[1:])} "
                                  f"batteries: \t{len(df[1:])} * 5000 \t= "
                                  f"{battery_costs}\n\tTotal costs: \t"
                                  f"{cable_costs} + {battery_costs} \t= "
                                  f"{total_costs}")
