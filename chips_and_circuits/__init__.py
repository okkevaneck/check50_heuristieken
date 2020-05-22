#!/usr/bin/env python3
"""
This file uses check50 to check the output of an Chips & Circuits solution. It
does so by doing the following tests in this order:
    - Check if output.csv exits
    - Check if the file has valid values and is structured correctly
    - Check if all connections from the designated netlist have been made.
    - Check if coordinates of the nets are in the wire lists
    - Check if the wires do not overlap
    - Check if the wires actually connect the designated nets
    - Check if the length in output.csv is equal to the computed wire length

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

import check50
import pandas as pd
import numpy as np
import os
import re
import networkx as nx


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
                              "wire length.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["net", "wires"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'net,wires'")

        # Check footer for correct format.
        if len(df) < 1 or df["net"].iloc[-1][:5] != "chip_" or \
                df["net"].iloc[-1][6:11] != "_net_":

            raise check50.Failure("Expected last row of the csv to be "
                                  "'chip_<int>_net_<int>,<int>'")

        try:
            int(df["wires"].iloc[-1])
            chip_id = int(df["net"].iloc[-1][5:6])
            net_id = int(df["net"].iloc[-1][11:])

            # Check if chip in footer is either 1 or 2.
            if chip_id not in [0, 1, 2]:
                raise check50.Failure(f"Expected chip number to be 0, 1 or 2, "
                                      f"but found:\n\tchip_{chip_id} \ton row "
                                      f"{len(df) + 1}")

            if net_id not in list(range(1,10)):
                raise check50.Failure(f"Expected netlist number to be 1 till 9,"
                                      f" but found:\n\tnet_{net_id} \ton row "
                                      f"{len(df) + 1}")
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'chip_<int>_net_<int>,<int>'")

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
        chip_id = int(df["net"].iloc[-1][5:6])
        net_id = int(df["net"].iloc[-1][11:])

        # Create dict with coordinates of the print nets.
        print_pos_3d = {}

        with open(f"data/chip_{chip_id}/print_{chip_id}.csv") as printfile:
            print_df = pd.read_csv(printfile)

            for id, x, y in print_df.values:
                print_pos_3d[id] = (x, y, 0)

        # Check if all connections from netlist are specified.
        with open(f"data/chip_{chip_id}/netlist_{net_id}.csv") as netlistfile:
            netlist_df = pd.read_csv(netlistfile)
            netlist_list = [tuple(n) for n in netlist_df.values.tolist()]
            nets = [tuple(map(int, p[1:-1].split(",")))
                    for p in df["net"][:-1].values.tolist()]

            # Add flipped values as well.
            for p in df["net"][:-1].values.tolist():
                nets.append(tuple(map(int, p[1:-1].split(",")[::-1])))

            net_errors = []

            # Check if all required connections are made.
            for nl in netlist_list:
                if nl not in nets:
                    net_errors.append(nl)

            if net_errors:
                error = "Expected all connections from the netlist to be in " \
                        "the output, but did not find:\n"

                for nl in net_errors:
                    error = "".join([error, f"\t'({nl[0]},{nl[1]})' or "
                                            f"'({nl[1]},{nl[0]})'\n"])

                raise check50.Failure(error)

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
                                        f"{coord_3d[2]})' \tor '({coord_3d[0]},"
                                        f"{coord_3d[1]})' \tfor net {net} \ton "
                                        f"row {idx + 2}\n"])

            raise check50.Failure(error)

        # Check if the wire lists do connect their designated nets.
        connect_errors = []

        for i, wires in enumerate(wire_coords_3d):
            net_1, net_2 = df["net"].iloc[i][1:-1].split(",")
            net_1_coord = print_pos_3d[int(net_1)]
            net_2_coord = print_pos_3d[int(net_2)]

            # Create a new graph and add nodes for origin and destination.
            graph = nx.Graph()
            graph.add_nodes_from([0, 1])
            nodes = {net_1_coord: 0, net_2_coord: 1}

            # Add nodes for all the wires.
            for j, coord in enumerate(wires):
                if coord != net_1_coord and coord != net_2_coord:
                    graph.add_node(j + 2)
                    nodes[coord] = j + 2

            # Create edges between neighbouring nodes.
            for coord, id in nodes.items():
                cur_pos = list(coord)

                # Check neighbours by changing a specific axis.
                for move in [-3, -2, -1, 1, 2, 3]:
                    cur_pos[abs(move) - 1] += move // abs(move)

                    if tuple(cur_pos) in nodes:
                        graph.add_edge(id, nodes[tuple(cur_pos)])

                    cur_pos[abs(move) - 1] -= move // abs(move)

            # Check if a path has been created between origin and destination.
            if not nx.has_path(graph, 0, 1):
                connect_errors.append([i, net_1, net_2])

        if connect_errors:
            error = "Expected wires to connect designated nets, but found " \
                    "that:\n"

            for row, net_1, net_2 in connect_errors:
                error = "".join([error, f"\tNet {net_1} \tand net {net_2} \t"
                                        f"were not connected with wires from "
                                        f"row {row + 2}\n"])

            raise check50.Failure(error)

        # Check if there are wires which surpass the maximum height of 7.
        invalid_height = [[(w, i + 1) for w in wires if w[2] > 7]
                          for i, wires in enumerate(wire_coords_3d)]

        error = "Wires cannot go higher than the 7th layer, but found:\n"
        error_found = False

        for height in invalid_height:
            if height:
                error_found = True
                for wire, row in height:
                    error = "".join([error, f"\tWire {wire} \ton row {row}\n"])

        if error_found:
            raise check50.Failure(error)

        # Check if all coordinates fall within the dimensions of the base layer.
        with open(f"data/chip_{chip_id}/print_{chip_id}.csv") as printfile:
            print_df = pd.read_csv(printfile)
            x_min = print_df["x"].min()
            x_max = print_df["x"].max()
            y_min = print_df["y"].min()
            y_max = print_df["y"].max()

        error = "All wires have to be placed within the dimensions of the " \
                "base layer, but found:\n"
        error_found = False

        for i, wires in enumerate(wire_coords):
            for wire in wires:
                if wire[0] > x_max + 1 or wire[0] < x_min - 1 or \
                        wire[1] > y_max + 1 or wire[1] < y_min - 1:
                    error_found = True
                    error = "".join([error, f"\tWire {wire} \ton row {i}\n"])

        if error_found:
            raise check50.Failure(error)


@check50.check(check_structure)
def check_cost():
    """Check if solution costs as much as specified in output.csv."""
    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)
        chip_id = int(df["net"].iloc[-1][5:6])

        # Create dict with coordinates of the print nets.
        print_pos_3d = {}

        with open(f"data/chip_{chip_id}/print_{chip_id}.csv") as printfile:
            print_df = pd.read_csv(printfile)

            for id, x, y in print_df.values:
                print_pos_3d[id] = (x, y, 0)

        # Create lists with all coordinates in 3D.
        wire_coords = [x[2:-2].split("),(") for x in df["wires"][:-1]]
        wire_coords = [[tuple(int(c) for c in coord.split(","))
                        for coord in coords] for coords in wire_coords]
        wire_coords_3d = [[c if len(c) == 3 else (c[0], c[1], 0)
                           for c in coords] for coords in wire_coords]

        # Check if any of the intermediate wires overlap. Only begin and end may
        # overlap since this is the net itself.
        wire_coords_3d_flatten = {}
        wire_errors = []

        for i, wires in enumerate(wire_coords_3d):
            net_1, net_2 = df["net"].iloc[i][1:-1].split(",")
            net_1_coord = print_pos_3d[int(net_1)]
            net_2_coord = print_pos_3d[int(net_2)]

            for c in wires:
                if c != net_1_coord and c != net_2_coord:
                    if c in wire_coords_3d_flatten:
                        wire_errors.append([c, wire_coords_3d_flatten[c], i])
                    else:
                        wire_coords_3d_flatten[c] = i

        intersections = len(wire_errors)

        # Compute the total number of wires used.
        wire_lengths = []

        for i, wires in enumerate(wire_coords):
            net_1, net_2 = df["net"].iloc[i][1:-1].split(",")
            wire_lengths.append([net_1, net_2, len(wires) - 1])

        wire_count = sum([x[2] for x in wire_lengths])

        # Check if the total costs are equal to the ones in output.csv.
        total_costs = wire_count + 300 * intersections

        if total_costs != int(df["wires"].iloc[-1]):
            error = f"Length in output.csv is not equal to the computed " \
                    f"length.\n    Computed wire length of {total_costs} is " \
                    f"made up of:\n"

            for net_1, net_2, length in wire_lengths:
                error = "".join([error, f"\t{length} \twires between net "
                                        f"{net_1} \tand net {net_2}\n"])
            error = "".join([error, f"\t{300  * intersections} \textra costs "
                                    f"for 300 * {intersections} "
                                    f"intersections\n"])

            raise check50.Failure(error)
