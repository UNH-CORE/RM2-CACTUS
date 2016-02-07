#!/usr/bin/env python

from __future__ import division, print_function
from subprocess import call
import os
import sys


def create_input_file(tsr=3.1, dynamic_stall=0):
    """Create CACTUS input file `config/RM2.in`."""
    params = {"dynamic_stall": dynamic_stall,
              "tsr": tsr}
    with open("config/RM2.in.template") as f:
        txt = f.read()
    with open("config/RM2.in", "w") as f:
        f.write(txt.format(**params))


def run_cactus(tsr=3.1, overwrite=False, **kwargs):
    """Run CACTUS and write output to `cactus.log`."""
    if not os.path.isfile("cactus.log") or overwrite:
        create_input_file(**kwargs)
        if not os.path.isdir("results"):
            os.mkdir("results")
        os.chdir("results")
        call("cactus ../config/RM2.in | tee ../cactus.log", shell=True)
    else:
        sys.exit("Simulation results present; use ./clean.sh to remove")


if __name__ == "__main__":
    run_cactus(tsr=3.1, dynamic_stall=0, overwrite=True)
