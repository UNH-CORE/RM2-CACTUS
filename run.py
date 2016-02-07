#!/usr/bin/env python

from __future__ import division, print_function
from subprocess import call
import os
import sys


if not os.path.isfile("cactus.log"):
    call("cactus RM2.in | tee cactus.log", shell=True)
else:
    sys.exit("Simulation results present; use ./clean.sh to remove")
