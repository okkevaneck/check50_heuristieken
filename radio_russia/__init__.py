#!/usr/bin/env python3
"""
This file uses check50 to check the output of an AmstelHaege solution. It
does so by doing the following tests in this order:
    - Check if output.csv exits
    - Check if the file has valid values and is structured correctly
    - Check if the given configuration has no neighbouring regions with the
        same send type.
    - Check if the given schema is correct for assignment 2.
    - Check if the given schema is correct for the advanced assignment.

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
    check50.exists("output.csv")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.csv are correct."""
    # Check if output.csv has content.
    if os.stat("output.csv").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header row and a row with the country and a"
                              " score.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["id", "type"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'id,type'")

        # Check footer for correct format.
        countries = ["china", "russia", "ukraine", "usa"]
        country = df['id'].iloc[-1]
        score_is_int = True

        try:
            int(df['type'].iloc[-1])
        except ValueError:
            score_is_int = False

        if len(df) < 1 or country not in countries or not score_is_int:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'<country>,<schema>', for example:\n"
                                  "\t'ukraine,1'")

        # Stop checking if there are no countries in the output file.
        if len(df) == 1:
            return

        # Check if specified ids are unique.
        dup_bools = np.array(df["id"].duplicated())
        if True in dup_bools:
            idxs = np.where(dup_bools == True)[0]
            error = "Expected all ids to be unique, but found duplicate(s):\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['id'][idx]}' \ton row "
                                        f"{idx + 2}.\n"])

            raise check50.Failure(error)

        # Check if the values of the ids are all present.
        with open(f"data/gen_students_data/{country}/{country}_regions.csv")\
                as sourcefile:
            source_df = pd.read_csv(sourcefile)

            # Check if ids are in the source file.
            id_bools = df["id"][:-1].isin(source_df["id"].values.astype(str))\
                .values

            if False in id_bools:
                idxs = np.where(id_bools == False)[0]
                error = "Invalid id(s) used. Expected to find ids in source " \
                        "file, but found:\n"

                for idx in idxs:
                    error = "".join([error, f"\t'{df['id'][idx]}' \ton row "
                                            f"{idx + 2}\n"])

                raise check50.Failure(error)

            # Check if ids from the source file are not in output.csv.
            id_bools = source_df["id"].astype(str).isin(df["id"][:-1].values) \
                .values

            if False in id_bools:
                idxs = np.where(id_bools == False)[0]
                error = "Expected to find all id(s) from the source file in " \
                        "output.csv, but did not find:\n"

                for idx in idxs:
                    error = "".join([error, f"\t'{source_df['id'][idx]}'\n"])

                raise check50.Failure(error)

        # Check if used send types are A till G.
        type_bools = df["type"][:-1].isin(["A", "B", "C", "D", "E", "F", "G"])\
            .values
        if False in type_bools:
            idxs = np.where(type_bools == False)[0]
            error = "Invalid letter(s) used as send types. Expected 'A' till "\
                    "'G', but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['type'][idx]}' \ton row "
                                        f"{idx + 2}\n"])

            raise check50.Failure(error)


@check50.check(check_file)
def check_configuration():
    """Check if the given configuration is valid."""
    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)
        country = df['id'].iloc[-1]

        with open(f"data/gen_students_data/{country}/{country}_regions.csv")\
                as sourcefile:
            source_df = pd.read_csv(sourcefile)

            # Create a list of neighbours for all ids and a list of used types.
            neighbours = [n.split(",")
                          for n in source_df["neighbours"].tolist()]
            neighbours = [list(map(int, x)) for x in [n for n in neighbours]]
            types = df["type"][:-1].tolist()

            # Check if neighbours don't have the same send type.
            invalid = []

            for i, [id, type] in enumerate(df[:-1].values):
                for n in neighbours[int(id)]:
                    if type == types[n]:
                        invalid.append([i, n])

            if invalid:
                error = "Found the following neighbouring regions with the " \
                        "same send type:\n"

                for i, j in invalid:
                    error = "".join([error, f"\t'{df['id'][i]}' \tand "
                                            f"'{df['id'][j]}' \thave the same "
                                            f"type '{df['type'][i]}'\n"])

                raise check50.Failure(error)


@check50.check(check_configuration)
def check_cost_assignment():
    """Check if the cost schema specified in output.csv is for assignment 2."""
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    schema_1 = np.array([12, 26, 27, 30, 37, 39, 41])
    schema_2 = np.array([19, 20, 21, 23, 36, 37, 38])
    schema_3 = np.array([16, 17, 31, 33, 36, 56, 57])
    schema_4 = np.array([3, 34, 36, 39, 41, 43, 58])

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)
        types = df["type"][:-1].tolist()
        occurrences = np.array([], dtype=int)

        # Compute occurrences for all letters.
        for l in letters:
            occurrences = np.append(occurrences, types.count(l))

        # Compute costs for assignment 2.
        schema_1_costs = np.multiply(schema_1, occurrences)
        schema_2_costs = np.multiply(schema_2, occurrences)
        schema_3_costs = np.multiply(schema_3, occurrences)
        schema_4_costs = np.multiply(schema_4, occurrences)
        schema_costs_assign = [sum(schema_1_costs), sum(schema_2_costs),
                               sum(schema_3_costs), sum(schema_4_costs)]
        min_schema = schema_costs_assign.index(min(schema_costs_assign)) + 1

        # Check if the given scheme is correct for assignment 2 or advanced.
        if int(df["type"].iloc[-1]) != min_schema:
            error = "Specified schema in output.csv is not the one with " \
                    "minimal costs.\n    The computed costs per schema with " \
                    "the current configuration are:\n"

            for i, cost in enumerate(schema_costs_assign):
                error = "".join([error, f"\tSchema {i + 1}: {cost}\n"])

            error = "".join([error, f"    Therefore, schema {min_schema} is "
                                    "the cheapest."])

            raise check50.Failure(error)


@check50.check(check_configuration)
def check_cost_advanced():
    """Check if the cost schema specified in output.csv is for the advanced
    assignment."""
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    schema_1 = np.array([12, 26, 27, 30, 37, 39, 41])
    schema_2 = np.array([19, 20, 21, 23, 36, 37, 38])
    schema_3 = np.array([16, 17, 31, 33, 36, 56, 57])
    schema_4 = np.array([3, 34, 36, 39, 41, 43, 58])

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)
        types = df["type"][:-1].tolist()
        occurrences = np.array([], dtype=int)

        # Compute occurrences for all letters.
        for l in letters:
            occurrences = np.append(occurrences, types.count(l))

        # Compute costs for advanced assignment.
        schema_costs_advanced = [0, 0, 0, 0]

        for i, s in enumerate([schema_1, schema_2, schema_3, schema_4]):
            for j, _ in enumerate(letters):
                costs = s[j]

                for _ in range(occurrences[j]):
                    schema_costs_advanced[i] += costs
                    costs *= 0.9

        min_schema = schema_costs_advanced.index(min(schema_costs_advanced)) + 1

        # Check if the given scheme is correct for assignment 2 or advanced.
        if int(df["type"].iloc[-1]) != min_schema:
            error = "Specified schema in output.csv is not the one with " \
                    "minimal costs.\n    The computed costs per schema with " \
                    "the current configuration are:\n"

            for i, cost in enumerate(schema_costs_advanced):
                error = "".join([error, f"\tSchema {i + 1}: {cost:.3f}\n"])

            error = "".join([error, f"    Therefore, schema {min_schema} is "
                                    "the cheapest."])

            raise check50.Failure(error)
