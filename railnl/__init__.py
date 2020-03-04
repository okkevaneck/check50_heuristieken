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

# Globals to specify the connections csv and maximum time in minutes, changed
# according to the specified problem. Default is for the whole Netherlands.
CONNECTIONS_CSV = "data/ConnectionsNational.csv"
STATIONS_CSV = "data/StationsNational.csv"
MAX_TIME = 180


@check50.check()
def exists():
    """Check if all files exists."""
    check50.include("data")
    check50.exists("output.csv")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.csv are correct."""
    global CONNECTIONS_CSV, STATIONS_CSV, MAX_TIME

    # Check if output.csv has content.
    if os.stat("output.csv").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header row and a row with a score.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["train", "stations", "problem"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'train,stations,problem'")

        # Check footer for correct format.
        if len(df) < 1 or df["train"].iloc[-1] != "score" or \
                df["problem"].iloc[-1] not in ["NL", "NZH"]:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<integer>,<NL | NZH>'")

        try:
            int(df['stations'].iloc[-1])
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<integer>,<NL | NZH>'")

        # Change globals if output has specified North- and South-Holland.
        if df["problem"].iloc[-1] == "NZH":
            CONNECTIONS_CSV = "data/ConnectionsHolland.csv"
            STATIONS_CSV = "data/StationsHolland.csv"
            MAX_TIME = 120

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

        # Check if list  of stations is formatted correctly and the station
        # exists in the specified station csv file.
        with open(STATIONS_CSV) as stationsfile:
            existing_stations = pd.read_csv(stationsfile)["station"]
            loaded_stations = df["stations"][:-1].map(lambda x: x[1:-1]
                                                      .split(", ")).values

            error = "Found the following non-existing stations:\n"
            found_error = False

            for row, stations in enumerate(loaded_stations):
                exist_bools = np.isin(stations, existing_stations)
                if False in exist_bools:
                    idxs = np.where(exist_bools == False)[0]
                    found_error = True

                    for idx in idxs:
                        error = "".join([error, f"\t'{stations[idx]}' \ton row "
                                                f"{idx}.\n"])

            if found_error:
                raise check50.Failure(error)


@check50.check(check_file)
def check_tracks():
    """Check if the solution is valid."""

    with open("output.csv") as csvfile,\
         open(CONNECTIONS_CSV) as connectionsfile:
        df = pd.read_csv(csvfile)
        connections = pd.read_csv(connectionsfile)

        # Check if the order of stations are valid.
        # TODO: Implement

        # Check if the time limit has not been exceeded.
        # TODO: Implement

        #