#!/usr/bin/env python
"""Run multiple simulations varying a single parameter."""

from __future__ import division, print_function
import foampy
from foampy.dictionaries import replace_value
import numpy as np
from subprocess import call, check_output
import os
import shutil
import pandas as pd


def get_param(param="nti", type=float):
    """Get parameter value by reading input file."""
    with open("config/RM2.in") as f:
        for line in f:
            if param in line and "=" in line:
                return type(line.replace("=", " ").split()[1])


def log_perf(param="tsr", append=True):
    """Log performance to file."""
    if not os.path.isdir("processed"):
        os.mkdir("processed")
    fpath = "processed/{}_sweep.csv".format(param)
    if append and os.path.isfile(fpath):
        df = pd.read_csv(fpath)
    else:
        df = pd.DataFrame(columns=["nx", "ny", "nz", "dt", "tsr", "cp", "cd"])
    d = pr.calc_perf(t1=3.0)
    d.update(get_mesh_dims())
    d["dt"] = get_dt()
    df = df.append(d, ignore_index=True)
    df.to_csv(fpath, index=False)


def param_sweep(param="tsr", start=None, stop=None, step=None, dtype=float,
                append=False, parallel=True):
    """Run multiple simulations, varying `quantity`.

    `step` is not included.
    """
    print("Running {} sweep".format(param))
    fpath = "results/{}_sweep.csv".format(param)
    if not append and os.path.isfile(fpath):
        os.remove(fpath)
    if param == "nx":
        dtype = int
    param_list = np.arange(start, stop, step, dtype=dtype)
    if param == "tsr":
        set_tsr_fluc(0.0)
    for p in param_list:
        print("Setting {} to {}".format(param, p))
        if param == "tsr":
            set_tsr(p)
            # Set time step to keep steps-per-rev constant
            set_dt(tsr=p)
        elif param == "nx":
            set_blockmesh_resolution(nx=p)
        elif param == "dt":
            set_dt(p)
        if p == param_list[0] or param == "nx":
            call("./Allclean")
            print("Running blockMesh")
            call("blockMesh > log.blockMesh", shell=True)
            print("Running snappyHexMesh")
            call("snappyHexMesh -overwrite > log.snappyHexMesh", shell=True)
            print("Running topoSet")
            call("topoSet > log.topoSet", shell=True)
            shutil.copytree("0.org", "0")
            if parallel:
                print("Running decomposePar")
                call("decomposePar > log.decomposePar", shell=True)
                call("ls -d processor* | xargs -I {} rm -rf ./{}/0", shell=True)
                call("ls -d processor* | xargs -I {} cp -r 0.org ./{}/0",
                     shell=True)
            print("Running pimpleFoam")
            run_solver(parallel=parallel)
        else:
            print("Running pimpleFoam")
            run_solver(parallel=parallel)
        os.rename("log.pimpleFoam", "log.pimpleFoam." + str(p))
        log_perf(param=param, append=True)
    # Set parameters back to defaults
    if param == "tsr":
        set_tsr(1.9)
        set_tsr_fluc(0.0)
        set_dt()
    elif param == "nx":
        set_blockmesh_resolution()
    elif param == "dt":
        set_dt()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run mulitple simulations, "
                                     "varying a single parameter.")
    parser.add_argument("parameter", default="tsr", help="Parameter to vary",
                        nargs="?", choices=["tsr", "nx", "dt"])
    parser.add_argument("start", default=0.4, type=float, nargs="?")
    parser.add_argument("stop", default=3.5, type=float, nargs="?")
    parser.add_argument("step", default=0.5, type=float, nargs="?")
    parser.add_argument("--serial", default=False, action="store_true")
    parser.add_argument("--append", "-a", default=False, action="store_true")

    args = parser.parse_args()

    param_sweep(args.parameter, args.start, args.stop, args.step,
                append=args.append, parallel=not args.serial)
