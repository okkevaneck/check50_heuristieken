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


@check50.check()
def exists():
    """Check if output.csv exists."""
    check50.exists("output.csv")


# @check50.check(exists)
# def check_file():
#     """Check if the structure and values of output.csv are correct."""
#     # Check if output.csv has content.
#     if os.stat("output.csv").st_size == 0:
#         raise check50.Failure("Output.csv may not be empty. Provide at least "
#                               "an header row.")
#
#     with open("output.csv") as csvfile:
#         df = pd.read_csv(csvfile)
#
#         # Check header for correct format.
#         if list(df) != ["car", "move"]:
#             raise check50.Failure("Expected header of the csv to be "
#                                   "'car,move'")
#
#         # Stop checking if there are no moves in the output file.
#         if len(df) == 1:
#             return
#
#         # Check if all values in the car column are of correct datatype and
#         # value, except for the last row.
#         amino_bools = df["amino"][:-1].isin(["H", "P", "C"]).values
#
#         if False in amino_bools:
#             idxs = np.where(amino_bools == False)[0]
#             error = "Invalid letter(s) used for an amino. Expected 'H', 'P' " \
#                     "or 'C', but found:\n"
#
#             for idx in idxs:
#                 error = "".join([error, f"\t'{df['amino'][idx]}' \ton row "
#                                         f"{idx}\n"])
#
#             raise check50.Failure(error)
#
#         # Check if all values in the fold column are of correct datatype and
#         # value, except for the last row.
#         if df["fold"].dtype != "int" or df["fold"].iloc[-2] != 0:
#             error = "Invalid value(s) used for a fold. Expected natural " \
#                     "numbers, but found:\n"
#
#             for i, item in enumerate(df['fold']):
#                 try:
#                     int(item)
#                 except ValueError:
#                     error = "".join([error, f"\t'{df['fold'][i]}' \ton row "
#                                             f"{i}\n"])
#
#             if df["fold"].iloc[-2] != 0:
#                 error = "".join([error, f"\t'{df['fold'].iloc[-2]}' \ton row "
#                                         f"{len(df['fold']) - 2}. Expected 0 "
#                                         f"since it is the last amino.\n"])
#
#             raise check50.Failure(error)
#
#         # Check if the score in the last row is of correct value.
#         if df["fold"].values[-1] > 0:
#             raise check50.Failure("The score for a fold should be negative.")
