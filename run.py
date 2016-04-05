#!/usr/bin/env python

from __future__ import division, print_function
from subprocess import call
import os
import sys
import numpy as np
import pandas as pd


R = 0.5375


def create_input_file(u_infty=1.0, tsr=3.1, dynamic_stall=2):
    """Create CACTUS input file `config/RM2.in`."""
    params = {"dynamic_stall": dynamic_stall,
              "tsr": tsr,
              "rpm": tsr*u_infty/R/(2*np.pi)*60}
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
        start_dir = os.getcwd()
        os.chdir("results")
        call("../cactus/bin/cactus ../config/RM2.in | tee ../cactus.log",
             shell=True)
        os.chdir(start_dir)
    else:
        sys.exit("Simulation results present; use ./clean.sh to remove "
                 "or -f to overwrite")


def log_perf(fpath="results/tsr_sweep.csv"):
    """Log mean performance from last revolution."""
    tsr = pd.read_csv("results/RM2_Param.csv")["TSR (-)"].iloc[0]
    run = pd.read_csv("results/RM2_RevData.csv").iloc[-1]
    cp = run["Power Coeff. (-)"]
    cd = run["Fx Coeff. (-)"]
    if os.path.isfile(fpath):
        df = pd.read_csv(fpath)
    else:
        df = pd.DataFrame(columns=["tsr", "cp", "cd"])
    df = df.append({"tsr": tsr, "cp": cp, "cd": cd}, ignore_index=True)
    df.to_csv(fpath, index=False)


def tsr_sweep(tsr_list, append=False, overwrite=False, dynamic_stall=2,
              u_infty=1.0):
    """Run simulation for multiple TSRs and log to CSV file."""
    fpath = "results/tsr_sweep_u{:.1f}_ds{}.csv".format(u_infty, dynamic_stall)
    if os.path.isfile(fpath):
        if not overwrite and not append:
            sys.exit("TSR sweep results present; remove, --append, or "
                     "--overwrite")
        if not append or overwrite:
            os.remove(fpath)
    for tsr in tsr_list:
        run_cactus(tsr=tsr, overwrite=True, dynamic_stall=dynamic_stall,
                   u_infty=u_infty)
        log_perf(fpath=fpath)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run CACTUS for the RM2.")
    parser.add_argument("--tsr", default=3.1, type=float,
                        help="Tip speed ratio")
    parser.add_argument("--tsr-range", "-T", type=float, nargs=3,
                        help="TSR range: start, stop (non-inclusive), step")
    parser.add_argument("--tsr-list", type=float, nargs="+",
                        help="TSR list")
    parser.add_argument("--dynamic-stall", "-d", default=2, type=int,
                        help="Dynamic stall model", choices=[0, 1, 2])
    parser.add_argument("--u-infty", "-U", type=float, default=1.0,
                        help="Free stream velocity in m/s")
    parser.add_argument("--overwrite", "-f", default=False, action="store_true",
                        help="Overwrite existing results")
    parser.add_argument("--append", "-a", default=False, action="store_true",
                        help="Append if running multiple TSRs")

    args = parser.parse_args()

    if args.tsr_range or args.tsr_list:
        if args.tsr_range:
            start, stop, step = args.tsr_range
            tsr_list = np.arange(start, stop, step)
        else:
            tsr_list = args.tsr_list
        tsr_sweep(tsr_list, append=args.append, overwrite=args.overwrite,
                  dynamic_stall=args.dynamic_stall, u_infty=args.u_infty)
    else:
        run_cactus(tsr=args.tsr, dynamic_stall=args.dynamic_stall,
                   u_infty=args.u_infty, overwrite=args.overwrite)
