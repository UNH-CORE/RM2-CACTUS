#!/usr/bin/env python

from __future__ import division, print_function
from subprocess import call, check_output
import os
import sys
import numpy as np
import pandas as pd
from multiprocessing import cpu_count


R = 0.5375


def create_input_file(u_infty=1.0, tsr=3.1, dynamic_stall=2, **kwargs):
    """Create CACTUS input file `config/RM2.in`."""
    params = {"dynamic_stall": dynamic_stall,
              "tsr": tsr,
              "rpm": tsr*u_infty/R/(2*np.pi)*60}
    params.update(kwargs)
    with open("config/RM2.in.template") as f:
        txt = f.read()
    with open("config/RM2.in", "w") as f:
        f.write(txt.format(**params))


def create_geom_file(nbelem=12):
    """Create CACTUS geometry file using Octave script."""
    call("octave -q scripts/makegeom.m {}".format(nbelem), shell=True)


def get_param(param="nti", dtype=float):
    """Get parameter value by reading input file."""
    with open("config/RM2.in") as f:
        for line in f:
            line = line.lower()
            if param.lower() in line and "=" in line:
                return dtype(line.replace("=", " ").split()[1])


def cpu_hrs_per_sec(hyperthreading=True, tsr=3.1, u_infty=1.0, nrevs=8):
    """Compute CPU hours per simulated second metric."""
    cores = cpu_count()
    # If hyperthreading is enabled, it may not be fair to count all "cores"
    if hyperthreading:
        cores /= 2
    omega = tsr*u_infty/R
    wall_time = check_output("tail cactus.log -n10 | grep Total", shell=True)
    wall_time = float(wall_time.decode().split()[-1])
    revs_per_second = omega/(2*np.pi)
    total_seconds = nrevs/revs_per_second
    return cores*(wall_time/3600)/(total_seconds)


def get_nbelem():
    """Read number of blade elements."""
    with open("config/RM2.geom") as f:
        for line in f:
            line = line.lower()
            if "nelem" in line:
                return int(line.split()[1])


def run_cactus(tsr=3.1, nbelem=12, overwrite=False, **kwargs):
    """Run CACTUS and write output to `cactus.log`."""
    if not os.path.isfile("cactus.log") or overwrite:
        create_geom_file(nbelem)
        create_input_file(tsr=tsr, **kwargs)
        call("./clean.sh")
        print("Running CACTUS for TSR={}".format(tsr))
        call("./cactus/bin/cactus ./config/RM2.in > ./cactus.log",
             shell=True)
    else:
        sys.exit("Simulation results present; use ./clean.sh to remove "
                 "or -f to overwrite")


def log_perf(fpath="processed/tsr_sweep.csv"):
    """Log mean performance from last revolution."""
    params = pd.read_csv("output/RM2_Param.csv")
    tsr = params["TSR (-)"].iloc[0]
    u_infty = np.round(params["U (ft/s)"].iloc[0]*0.3048, decimals=5)
    run = pd.read_csv("output/RM2_RevData.csv")
    nrevs = int(run["Rev"].max())
    run = run.iloc[len(run)//2:].mean()
    cp = run["Power Coeff. (-)"]
    cd = run["Fx Coeff. (-)"]
    savedir = os.path.split(fpath)[0]
    if not os.path.isdir(savedir):
        os.makedirs(savedir)
    if os.path.isfile(fpath):
        df = pd.read_csv(fpath)
    else:
        df = pd.DataFrame(columns=["tsr", "cp", "cd", "u_infty", "dsflag", "tp",
                                   "nti", "nbelem", "nrevs", "walls",
                                   "cpu_hrs_per_sec"])
    d = {"tsr": tsr, "cp": cp, "cd": cd, "u_infty": u_infty}
    d["dsflag"] = get_param("dsflag", dtype=int)
    d["tp"] = get_param("LBDynStallTp", dtype=float)
    d["nbelem"] = get_nbelem()
    d["nti"] = get_param("nti", dtype=int)
    d["nrevs"] = nrevs
    d["walls"] = get_param("WPFlag", dtype=int)
    d["cpu_hrs_per_sec"] = cpu_hrs_per_sec(tsr=tsr, u_infty=u_infty,
                                           nrevs=d["nrevs"])
    df = df.append(d, ignore_index=True)
    df.to_csv(fpath, index=False)


def param_sweep(param="tsr", start=None, stop=None, step=None, dtype=float,
                overwrite=False, append=False, **kwargs):
    """Run multiple simulations, varying `quantity`.

    `step` is not included.
    """
    print("Running {} sweep".format(param))
    fpath = "processed/{}_sweep.csv".format(param)
    if kwargs["foildata"] == "Jacobs":
        fpath = fpath.replace(".csv", "_Jacobs.csv")
    if kwargs["dynamic_stall"] == 1:
        fpath = fpath.replace(".csv", "_bv.csv")
    if os.path.isfile(fpath):
        if not overwrite and not append:
            sys.exit("{} sweep results present; remove, --append, or "
                     "--overwrite".format(param))
        if not append or overwrite:
            os.remove(fpath)
    param_list = np.arange(start, stop, step, dtype=dtype)
    for p in param_list:
        print("Setting {} to {}".format(param, p))
        args = kwargs.copy()
        args[param] = p
        run_cactus(overwrite=True, **args)
        log_perf(fpath=fpath)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run CACTUS for the RM2.")
    parser.add_argument("--tsr", default=3.1, type=float,
                        help="Tip speed ratio")
    parser.add_argument("--param-sweep", "-p", nargs=4,
                        help="Run parameter sweep [name] [start] [stop] [step]")
    parser.add_argument("--dynamic-stall", "-d", default=2, type=int,
                        help="Dynamic stall model; 0: None, 1: BV, 2: LB",
                        choices=[0, 1, 2])
    parser.add_argument("--u_infty", "-U", type=float, default=1.0,
                        help="Free stream velocity in m/s")
    parser.add_argument("--nti", "-n", type=int, default=24,
                        help="Time steps per rev")
    parser.add_argument("--nbelem", "-e", type=int, default=16,
                        help="Number of elements per blade")
    parser.add_argument("--tp", type=float, default=1.7,
                        help="Leishman-Beddoes DS model Tp time constant")
    parser.add_argument("--no-walls", default=False, action="store_true")
    parser.add_argument("--foil-data", default="Sheldahl",
                        choices=["Sheldahl", "Jacobs"],
                        help="Foil coefficient database")
    parser.add_argument("--overwrite", "-f", default=False, action="store_true",
                        help="Overwrite existing results")
    parser.add_argument("--append", "-a", default=False, action="store_true",
                        help="Append if running parameter sweep")

    args = parser.parse_args()

    walls = not args.no_walls
    if walls:
        call(["python", "./scripts/makewalls.py"])

    if args.foil_data == "Jacobs":
        print("Creating hybrid Jacobs foil coefficient database")
        call(["python", "./scripts/jacobs-data.py"])

    if args.param_sweep:
        name, start, stop, step = args.param_sweep
        if name in ["nti", "nbelem", "dynamic_stall"]:
            dtype = int
        else:
            dtype = float
        start, stop, step = dtype(start), dtype(stop), dtype(step)
        param_sweep(name, start=start, stop=stop, step=step, dtype=dtype,
                    append=args.append, overwrite=args.overwrite, tp=args.tp,
                    dynamic_stall=args.dynamic_stall, u_infty=args.u_infty,
                    nti=args.nti, nbelem=args.nbelem, walls=int(walls),
                    foildata=args.foil_data)
    else:
        run_cactus(tsr=args.tsr, dynamic_stall=args.dynamic_stall,
                   u_infty=args.u_infty, overwrite=args.overwrite, tp=args.tp,
                   nti=args.nti, nbelem=args.nbelem, walls=int(walls),
                   foildata=args.foil_data)
