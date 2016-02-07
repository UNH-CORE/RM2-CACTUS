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
        create_input_file(tsr=tsr, **kwargs)
        if not os.path.isdir("results"):
            os.mkdir("results")
        os.chdir("results")
        call("cactus ../config/RM2.in | tee ../cactus.log", shell=True)
    else:
        sys.exit("Simulation results present; use ./clean.sh to remove "
                 "or -f to overwrite")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run CACTUS for the RM2.")
    parser.add_argument("tsr", default=3.1, type=float, nargs="?",
                        help="Tip speed ratio")
    parser.add_argument("--dynamic-stall", "-d", default=0, type=int,
                        help="Dynamic stall model", choices=[0, 1, 2])
    parser.add_argument("--overwrite", "-f", default=False, action="store_true",
                        help="Overwrite existing results")

    args = parser.parse_args()
    run_cactus(tsr=args.tsr, dynamic_stall=args.dynamic_stall,
               overwrite=args.overwrite)
