#!/usr/bin/env python3
"""
This file uses check50 to check the output of an AmstelHaege solution. It
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
                                  "'<country>,<integer>'")

        # Stop checking if there are no countries in the output file.
        if len(df) == 1:
            return

        # Check if specified IDs are unique.
        dup_bools = np.array(df["id"].duplicated())
        if True in dup_bools:
            idxs = np.where(dup_bools == True)[0]
            error = "Expected all ids to be unique, but found duplicate(s):\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['id'][idx]}' \ton row "
                                        f"{idx + 2}.\n"])

            raise check50.Failure(error)

        # Check if IDs are the same as in the source file.
        with open(f"data/gen_students_data/{country}/{country}_regions.csv")\
                as sourcefile:
            source_df = pd.read_csv(sourcefile)
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

            # Check if neighbours don't have the same send type.
            neighbours = [n.split(",")
                          for n in source_df["neighbours"].tolist()]
            neighbours = [list(map(int, x)) for x in [n for n in neighbours]]
            print(neighbours)

