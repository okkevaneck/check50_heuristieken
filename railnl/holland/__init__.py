#!/usr/bin/env python3
"""
This file uses check50 to check the output of a RailNL solution. It does so by
executing the checks from the national problem folder. The maximum time per
track is changed according to the problem. It will also use the `stations.csv`
and `connections.csv` files stored in the holland problem folder.

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

national = __import__("check50").import_checks("../national")
from national import *

# Global from the national test to specify the maximum time in minutes per
# track. This global is changed according to this problem and will be used
# during the tests.
national.MAX_TIME = 120
