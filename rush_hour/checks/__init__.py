#!/usr/bin/env python3
"""
This file uses check50 to check the output of a Rush Hour solution. It does so
by doing the following tests in this order:
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

# Global for tracking the boards borders. This global is changed in the
# sub-folders according to their board size.
BOARD_SIZE = 0


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
                              "an header row.")

    with open("output.csv") as csvfile:
        df = pd.read_csv(csvfile)

        # Check header for correct format.
        if list(df) != ["car", "move"]:
            raise check50.Failure("Expected header of the csv to be "
                                  "'car,move'")

        # Stop checking if there are no moves in the output file.
        if len(df) == 1:
            return

        # Check if all values in the car column are of correct datatype and
        # value.
        car_name_bools = np.array([True if x.isalpha() else False
                                   for x in df["car"]])

        if False in car_name_bools:
            idxs = np.where(car_name_bools == False)[0]
            error = "Invalid letter(s) used for a car. Expected only " \
                    "alphabets, but found:\n"

            for idx in idxs:
                error = "".join([error, f"\t'{df['car'][idx]}' \ton row "
                                        f"{idx+2}\n"])

            raise check50.Failure(error)

        # Check if all values in the move column are of correct datatype and
        # value.
        if df["move"].dtype != "int":
            if df["move"].dtype == "float":
                error = "Invalid value(s) used for a move. Expected " \
                        "only integers but floats were used."
            else:
                error = "Invalid value(s) used for a move. Expected, " \
                        "integers but found:\n"

                for i, item in enumerate(df['move']):
                    try:
                        int(item)
                    except ValueError:
                        error = "".join([error, f"\t'{df['move'][i]}' \ton "
                                                f"row {i}\n"])

            raise check50.Failure(error)

        # Check if all car letters are valid.
        # TODO: Compare car letters from output.csv with car letters from board.csv


@check50.check(check_file)
def check_moves():
    """Check if the moves are valid and the red car exits."""
    with open("output.csv") as csvfile, \
            open("board.csv") as boardfile:
        df = pd.read_csv(csvfile)
        board_df = pd.read_csv(boardfile)
        print(board_df)
        print(BOARD_SIZE)

        # Setup tracking dictionaries. Their key,value pairs are:
        #   - Board -> (pos): car_letter.
        #   - Car_data -> car_letter: [orientation, [coordinates]]
        board = {}
        car_data = {}

        # Setup board.
        for _, [car, orientation, pos, length] in board_df.iterrows():
            pos = list(map(int, pos.split(",")))
            car_data[car] = [orientation, []]

            for _ in range(length):
                board[tuple(pos)] = car
                car_data[car][1].append(pos[:])

                if orientation == "H":
                    pos[0] += 1
                else:
                    pos[1] += 1

        # Perform all moves.
        for idx, [car, move] in df.iterrows():
            orientation, pos = car_data[car]
            orientation_idx = ["H", "V"].index(orientation)

            print("\nFor: ", car)

            if move > 0:
                new_pos = pos[-1][:]
            elif move < 0:
                new_pos = pos[0][:]

            new_pos[orientation_idx] += move

            # Check if the new position is outside of the board.
            if new_pos[0] > BOARD_SIZE or new_pos[0] < 0 \
                    or new_pos[1] > BOARD_SIZE or new_pos[1] < 0:
                raise check50.Failure(f"Car '{car}' moved outside of the board"
                                      f" by performing '{car} {move}' on"
                                      f" row {idx+2}")

            # Check if all positions between the car and new_pos are free.
            path = [[new_pos[0] + i, new_pos[1]] if orientation == "H" else
                    [new_pos[0], new_pos[1] + i]
                    for i in range(0, -move, -move//abs(move))]

            # Sort path so the order is correct for performing the moves.
            if move > 0:
                path.sort()

            # print("Orientation:  ", orientation)
            # print("Positions:    ", pos)
            # print("New_pos:      ", new_pos)
            # print("Move:         ", move)
            # print("PATH:         ", path)

            for path_pos in path:
                if tuple(path_pos) in board:
                    crash_car = board[tuple(path_pos)]
                    raise check50.Failure(f"Car '{car}' moved into car "
                                          f"'{crash_car}' by performing "
                                          f"'{car} {move}' on row {idx+2}")

            # Move car to the new location.
            for p in pos:
                del board[tuple(p)]

            if len(path) < len(pos):
                if move > 0:
                    pos = pos[-len(pos) + len(path):]
                    pos.extend(path)
                    car_data[car][1] = pos
                elif move < 0:
                    pos = pos[:len(pos) - len(path)]
                    path.extend(pos)
                    car_data[car][1] = path
            else:
                # Compute new positions by taking the front or end of the path,
                # depending on the direction of the move.
                if move > 0:
                    car_data[car][1] = path[-len(pos):]
                elif move < 0:
                    car_data[car][1] = path[:len(pos)]

            for p in car_data[car][1]:
                board[tuple(p)] = car

            # print("After move:   ", car_data[car][1])

        # Check if the red car moved to the edge of the board.
        if car_data["X"][1][-1] != BOARD_SIZE:
            raise check50.Failure("Red car did not end at the edge of the "
                                  "board.")
