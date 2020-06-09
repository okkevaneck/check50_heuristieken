#!/usr/bin/env python3
"""
This file uses check50 to check the output of a RailNL solution. It does so by
executing the checks from the checks problem folder. The maximum time per
track and maximum number of tracks is changed according to the national problem.
It will also use the `stations.csv` and `connections.csv` files stored in the
national problem folder.

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""
import check50
import os
import pathlib
# check50.include("./data")


checks = __import__("check50").import_checks("../checks")
from checks import *

# Global from the national test to specify the maximum time in minutes per
# track and maximum number of tracks. This global is changed according to the
# holland problem and will be used during the tests.
checks.MAX_TIME = 180
checks.MAX_TRACKS = 20

# Include data for the national problem.
