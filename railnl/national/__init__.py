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
import re

# Global to specify the maximum time in minutes per track. This global is
# changed in the holland sub-folder according to the problem.
MAX_TIME = 180


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
                              "an header row and a row with a score.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(open("output.csv"), dtype=str, keep_default_na=False)

        # Check header for correct format.
        if list(df) != ["train", "stations"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'train,stations'")

        # Check footer for correct format.
        if len(df) < 1 or df["train"].iloc[-1] != "score":
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<int | float>'")

        try:
            float(df['stations'].iloc[-1])
        except ValueError:
            raise check50.Failure("Expected last row of the csv to be "
                                  "'score,<int | float>'")

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
                                        f"{idx + 1}.\n"])

            raise check50.Failure(error)

        # Check if the stations are correctly formatted.
        pattern = r"^\[.*\]+$"
        stations_bools = np.array(list(map(lambda x:
                                           bool(re.match(pattern, x)),
                                           df["stations"][:-1])))

        if False in stations_bools:
            idxs = np.where(stations_bools == False)[0]
            error = "Invalid formated list of stations found.\n    " \
                    "Expected stations with format '[<station1>, <station2>, " \
                    "..]' but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['stations'][idx]}' \ton "
                                        f"row {idx + 1} \n"])

            raise check50.Failure(error)

        # Check if all stations in output.csv are specified in stations.csv.
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
                                                f"{row + 1}.\n"])

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
        valid_cons = connections.iloc[:,:-1].values.tolist()
        output_cons = []
        errors = []

        for i, track in enumerate(tracks):
            output_cons.append([])

            for j, t in enumerate(track[:-1]):
                if [t, track[j + 1]] in valid_cons:
                    output_cons[i].append([t, track[j + 1]])
                elif [track[j + 1], t] in valid_cons:
                    output_cons[i].append([track[j + 1], t])
                else:
                    errors.append([i, f"{t}, {track[j + 1]}"])

        if errors:
            error = "Found the following illegal connections:\n"

            for row, stations in errors:
                error = "".join([error, f"\t'{stations}'    \ton row "
                                        f"{row + 1}.\n"])

            raise check50.Failure(error)

        # Check if the time limit has not been exceeded.
        errors = []

        for row, track in enumerate(output_cons):
            time = 0

            for con in track:
                time += connections[(connections["station1"].isin([con[0]])) &
                                    (connections["station2"].isin([con[1]]))] \
                                   ["distance"].values

            if time > MAX_TIME:
                errors.append([row, time[0]])

        if errors:
            error = f"Found tracks that exceed the maximum time of " \
                    f"{MAX_TIME} minutes on:\n"

            for row, time in errors:
                error = "".join([error, f"\tRow {row + 1} with a time of "
                                        f"{time} minutes\n"])

            raise check50.Failure(error)


@check50.check(check_tracks)
def check_score():
    """Check if solution produces score specified in output.csv."""
    with open("output.csv") as csvfile, \
            open("data/connections.csv") as connectionsfile:
        df = pd.read_csv(csvfile)
        connections = pd.read_csv(connectionsfile)

        # Get all tracks in output.csv.
        tracks = df["stations"][:-1].map(lambda x: x[1:-1].split(", ")).values
        valid_cons = connections.iloc[:, :-1].values.tolist()
        output_cons = []
        tot_time = 0

        for i, track in enumerate(tracks):
            output_cons.append([])

            for j, t in enumerate(track[:-1]):
                if [t, track[j + 1]] in valid_cons:
                    output_cons[i].append([t, track[j + 1]])
                elif [track[j + 1], t] in valid_cons:
                    output_cons[i].append([track[j + 1], t])

        # Compute total time and the used connections.
        used_cons = pd.DataFrame()

        for row, track in enumerate(output_cons):
            used_cons = used_cons.append(pd.DataFrame(track))
            time = 0

            for con in track:
                time += connections[(connections["station1"].isin([con[0]])) &
                                    (connections["station2"].isin([con[1]]))] \
                                   ["distance"].values

            tot_time += time[0]

        # Drop duplicate connections and compute the fraction of used
        # connections. Also compute the score generated by output.csv.
        used_cons.drop_duplicates(keep="first", inplace=True, ignore_index=True)
        perc_con_used = len(used_cons) / len(connections)

        score = perc_con_used * 10000 - (len(df[:-1]) * 100 + tot_time)
        user_score = float(df.iloc[-1]["stations"])

        if score != user_score:
            raise check50.Failure("Score in output.csv is not equal to the "
                                  "computed score from the output.\n    "
                                  "Computed score is calculated as:\n"
                                  f"\tK = {perc_con_used} * 10,000 - "
                                  f"({len(df[:-1])} * 100 + {tot_time})\n"
                                  f"\tK = {score:,}\n"
                                  f"\tYour score: {user_score:,}")



# TODO: Check de hoeveelheid trajescten: 20 voor NL, 7 voor Holland

