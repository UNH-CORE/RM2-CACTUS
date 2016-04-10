#!/usr/bin/env python

from __future__ import division, print_function
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pxl.styleplot import set_sns
import argparse


def clean_column_names(df):
    """Rename CSV column names so they are easier to work with."""
    df.columns = [n.replace("(-)", "").lower().replace(".", "").strip()\
                  .replace(" ", "_").replace("(", "").replace(")", "") \
                  for n in df.columns]
    return df


def load_timedata():
    df = pd.read_csv("results/RM2_TimeData.csv")
    df = clean_column_names(df)
    df["theta_deg"] = np.rad2deg(df.theta_rad)
    return df


def plot_perf(print_perf=True, save=False):
    """Plot power coefficient versus azimuthal angle."""
    df = load_timedata()
    if print_perf:
        df_last = df.iloc[len(df)//2:]
        print("From {:.1f}--{:.1f} degrees, mean_cp: {:.2f}".format(
              df_last.theta_deg.min(), df_last.theta_deg.max(),
              df_last.power_coeff.mean()))
    fig, ax = plt.subplots()
    ax.plot(df.theta_deg, df.power_coeff)
    ax.set_xlabel(r"$\theta$ (degrees)")
    ax.set_ylabel(r"$C_P$")
    fig.tight_layout()
    if save:
        fig.savefig("figures/perf.pdf")


def plot_perf_curves(exp=False, save=False):
    """Plot performance curves."""
    fig, ax = plt.subplots(figsize=(7.5, 3), nrows=1, ncols=2)
    df = pd.read_csv("results/tsr_sweep.csv")
    ax[0].plot(df.tsr, df.cp, marker="o", label="CACTUS")
    ax[1].plot(df.tsr, df.cd, marker="o", label="CACTUS")
    ax[0].set_ylabel("$C_P$")
    ax[1].set_ylabel("$C_D$")
    [a.set_xlabel(r"$\lambda$") for a in ax]
    if exp:
        df_exp = pd.read_csv("https://raw.githubusercontent.com/UNH-CORE/"
                             "RM2-tow-tank/master/Data/Processed/Perf-1.0.csv")
        df_exp2 = pd.read_csv("https://raw.githubusercontent.com/UNH-CORE/"
                              "RM2-tow-tank/master/Data/Processed/"
                              "Perf-1.0-b.csv")
        df_exp = df_exp.append(df_exp2, ignore_index=True)
        df_exp = df_exp.groupby("tsr_nom").mean()
        ax[0].plot(df_exp.mean_tsr, df_exp.mean_cp, marker="^",
                   markerfacecolor="none", color="black", label="Exp.")
        ax[1].plot(df_exp.mean_tsr, df_exp.mean_cd, marker="^",
                   markerfacecolor="none", color="black", label="Exp.")
        ax[1].legend(loc="lower right")
    fig.tight_layout()
    if save:
        fig.savefig("figures/perf-curves.pdf")


def plot_verification(save=False):
    """Plot the sensitivity to time step and number of blade elements."""
    fig, ax = plt.subplots(figsize=(7.5, 3), nrows=1, ncols=2)
    df = pd.read_csv("results/nti_sweep.csv")
    ax[0].plot(df.nti, df.cp, marker="o")
    ax[0].set_xlabel("Time steps per rev.")
    df = pd.read_csv("results/nbelem_sweep.csv")
    ax[1].plot(df.nbelem, df.cp, marker="o")
    ax[1].set_xlabel("Elements per blade")
    [a.set_ylabel("$C_P$") for a in ax]
    fig.tight_layout()
    if save:
        fig.savefig("figures/verification.pdf")


def plot_foildata(save=False):
    """Plot static foil data for comparison."""
    fig, ax = plt.subplots(figsize=(7.5, 3.25), nrows=1, ncols=2)
    data = {"Gregorek": pd.read_csv("config/foildata/NACA_0021_Gregorek.csv"),
            "Sheldahl": pd.read_csv("config/foildata/"
                                    "NACA_0021_Sheldahl_1.5e6.csv")}
    for d, m in zip(["Gregorek", "Sheldahl"], ["o", "^"]):
        df = data[d]
        if d == "Sheldahl":
            df = df[df.alpha_deg >= -2]
            df = df[df.alpha_deg <= 45]
            df["alpha"] = df.alpha_deg
        elif d == "Gregorek":
            df["cd"] = df.cd_wake
        df = df.sort_values(by="alpha")
        ax[0].plot(df.alpha, df.cl, marker=m, label=d)
        ax[1].plot(df.alpha, df.cd, marker=m, label=d)
    [a.set_xlabel(r"$\alpha$ (degrees)") for a in ax]
    ax[0].set_ylabel("$C_l$")
    ax[1].set_ylabel("$C_d$")
    ax[0].legend(loc="lower right")
    fig.tight_layout()
    if save:
        fig.savefig("figures/foil-data.pdf")


if __name__ == "__main__":
    set_sns()
    plt.rcParams["axes.grid"] = True

    parser = argparse.ArgumentParser(description="Generate plots.")
    parser.add_argument("plot", nargs="*", help="What to plot", default="perf",
                        choices=["perf", "perf-curves", "perf-curves-exp",
                                 "verification", "foil-data"])
    parser.add_argument("--all", "-A", help="Generate all figures",
                        default=False, action="store_true")
    parser.add_argument("--save", "-s", help="Save to `figures` directory",
                        default=False, action="store_true")
    parser.add_argument("--no-show", default=False, action="store_true",
                        help="Do not call matplotlib show function")
    parser.add_argument("-q", help="Quantities to plot", nargs="*",
                        default=["alpha", "rel_vel_mag"])
    args = parser.parse_args()

    if args.save:
        if not os.path.isdir("figures"):
            os.mkdir("figures")

    if "perf" in args.plot or args.all:
        plot_perf(save=args.save)
    if "perf-curves" in args.plot or args.all:
        plot_perf_curves(exp=False, save=args.save)
    if "perf-curves-exp" in args.plot or args.all:
        plot_perf_curves(exp=True, save=args.save)
    if "verification" in args.plot or args.all:
        plot_verification(save=args.save)
    if "foil-data" in args.plot or args.all:
        plot_foildata(save=args.save)

    if not args.no_show:
        plt.show()
