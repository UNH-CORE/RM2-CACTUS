#!/usr/bin/env python

from __future__ import division, print_function
from subprocess import call
import os
import sys


if not os.path.isfile("cactus.log"):
    if not os.path.isdir("results"):
        os.mkdir("results")
    os.chdir("results")
    call("cactus ../config/RM2.in | tee ../cactus.log", shell=True)
    call("pwd")
else:
    sys.exit("Simulation results present; use ./clean.sh to remove")
