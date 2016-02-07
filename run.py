#!/usr/bin/env python

from __future__ import division, print_function
from subprocess import call
import os
import sys


def run_cactus(overwrite=False):
    """Run CACTUS and write output to `cactus.log`."""
    if not os.path.isfile("cactus.log") or overwrite:
        if not os.path.isdir("results"):
            os.mkdir("results")
        os.chdir("results")
        call("cactus ../config/RM2.in | tee ../cactus.log", shell=True)
    else:
        sys.exit("Simulation results present; use ./clean.sh to remove")


if __name__ == "__main__":
    overwrite = True
    run_cactus(overwrite=overwrite)
