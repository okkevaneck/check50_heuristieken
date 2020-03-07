#!/usr/bin/env python3
"""
This file uses check50 to check the output of an RailNL solution. It
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

# Globals to specify the maximum time in minutes per track. This global is
# changed in the holland sub-folder according to the problem.
MAX_TIME = 180


@check50.check()
def exists():
    """Check if output.csv exists."""
    check50.exists("output.csv")


@check50.check(exists)
def check_file():
    """Check if the structure and values of output.csv are correct."""
    global MAX_TIME

    # Check if output.csv has content.
    if os.stat("output.csv").st_size == 0:
        raise check50.Failure("Output.csv may not be empty. Provide at least "
                              "an header row and a row with a score.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["train", "stations"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'train,stations'")

        # Check footer for correct format.
        if len(df) < 1 or df["train"].iloc[-1] != "score":
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<integer>'")

        try:
            int(df['stations'].iloc[-1])
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<integer>'")

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
        with open("data/stations.csv") as stationsfile:
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
                                                f"{row}.\n"])

            if found_error:
                raise check50.Failure(error)


@check50.check(check_file)
def check_tracks():
    """Check if the solution is valid."""

    with open("output.csv") as csvfile, \
            open("data/connections.csv") as connectionsfile:
        df = pd.read_csv(csvfile)
        connections = pd.read_csv(connectionsfile)

        # Check if the order of stations are valid.
        tracks = df["stations"][:-1].map(lambda x: x[1:-1].split(", ")).values
        tracks = [[f"{t[i]}, {t[i+1]}" for i, _ in enumerate(t[:-1])]
                  for t in tracks]
        valid_con1 = connections["station1"] + ", " + connections["station2"]
        valid_con2 = connections["station2"] + ", " + connections["station1"]

        error = "Found the following illegal connections:\n"
        found_error = False

        for row, track in enumerate(tracks):
            valid_bools1 = np.isin(track, valid_con1)
            valid_bools2 = np.isin(track, valid_con2)

            if (False, False) in zip(valid_bools1, valid_bools2):
                idxs = np.where((valid_bools1 == False) &
                                (valid_bools2 == False))[0]
                found_error = True

                for idx in idxs:
                    error = "".join([error, f"\t'{track[idx]}' \ton row "
                                            f"{row}.\n"])

        if found_error:
            raise check50.Failure(error)

        # Check if the time limit has not been exceeded.
        tracks = df["stations"][:-1].map(lambda x: x[1:-1].split(", ")).values
        tracks1 = [[f"{t[i]}, {t[i + 1]}" for i, _ in enumerate(t[:-1])]
                   for t in tracks]
        tracks2 = [[f"{t[i + 1]}, {t[i]}" for i, _ in enumerate(t[:-1])]
                   for t in tracks]
        # TODO: Get sum of time from the tracks


@check50.check(check_tracks)
def check_score():
    """Check if solution produces networth specified in output.csv."""
    pass