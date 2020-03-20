#!/usr/bin/env python3
"""
This file uses check50 to check the output of a Rush Hour solution. It does so
by executing the checks from the checks problem folder. The board used during
the checks will be changed to the one from this problem folder.

@author: Okke van Eck
@contact: okke.van.eck@gmail.com
"""

checks = __import__("check50").import_checks("../checks")
from checks import *
