#!/usr/bin/env python

from __future__ import division, print_function
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pxl.styleplot import set_sns
import os
import argparse
from itertools import islice

R = 0.5375
D = R*2
nu = 1e-6
c = (0.04 + 0.06667)/2
H = 0.807


def clean_column_names(df):
    """Rename CSV column names so they are easier to work with."""
    df.columns = [n.replace("(-)", "").lower().replace(".", "").strip()\
                  .replace(" ", "_").replace("(", "").replace(")", "") \
                  for n in df.columns]
    return df


def load_timedata():
    df = pd.read_csv("output/RM2_TimeData.csv")
    df = clean_column_names(df)
    df["theta_deg"] = np.rad2deg(df.theta_rad)
    return df


def load_raw_xfoil_data(Re=1.5e6, alpha_name="alpha_deg"):
    """Load raw XFOIL data as DataFrame."""
    fdir = "config/foildata/xfoil-raw"
    fname = "NACA 0021_T1_Re{:.3f}_M0.00_N9.0.dat".format(Re/1e6)
    fpath = os.path.join(fdir, fname)
    alpha_deg = []
    cl = []
    cd = []
    with open(fpath) as f:
        for n, line in enumerate(f.readlines()):
            if n >= 14:
                ls = line.split()
                alpha_deg.append(float(ls[0]))
                cl.append(float(ls[1]))
                cd.append(float(ls[2]))
    df = pd.DataFrame()
    df[alpha_name] = alpha_deg
    df["cl"] = cl
    df["cd"] = cd
    return df


def load_probe_data(t1_fraction=0.5):
    """Load velocity probe data to dictionary of NumPy arrays.

    Parameters
    ----------
    t1_fraction : float
        Fraction of simulation time after which statistics are computed.
    """
    # First, obtain a list of all probe file names
    probe_dir = "./output/probe"
    fnames = sorted(os.listdir(probe_dir))
    # For all probe files, read coordinates and average velocities
    x_R = []
    y_R = []
    z_R = []
    mean_u = []
    mean_v = []
    mean_w = []
    for fname in fnames:
        with open(os.path.join(probe_dir, fname)) as f:
            for line in islice(f, 1, 2):
                line = line.split(",")
                x_R.append(float(line[0]))
                y_R.append(float(line[1]))
                z_R.append(float(line[2]))
            t, u, v, w, _, _, _ = np.loadtxt(f, skiprows=2, delimiter=",",
                                             unpack=True)
            i1 = int(len(t)*t1_fraction)
            mean_u.append(u[i1:].mean())
            mean_w.append(v[i1:].mean()) # Swap v and w since y-up coord sys
            mean_v.append(-w[i1:].mean())
    x_R = np.array(x_R)
    y_R_org = np.array(y_R)
    z_R_org = np.array(z_R)
    # Swap y and z since this is a y-up coord sys
    z_R = y_R_org.copy()
    y_R = -z_R_org.copy()
    z_H = z_R*R/H
    nz = len(np.unique(z_H))
    ny = len(np.unique(y_R))
    mean_u, mean_v, mean_w = (np.array(mean_u), np.array(mean_v),
                              np.array(mean_w))
    # Reshape arrays so y_R indicates columns and z_R rows
    y_R = y_R.reshape(nz, ny)
    z_H = z_H.reshape(nz, ny)
    mean_u = mean_u.reshape(nz, ny)
    mean_v = mean_v.reshape(nz, ny)
    mean_w = mean_w.reshape(nz, ny)
    return {"y_R": y_R, "z_H": z_H, "mean_u": mean_u, "mean_v": mean_v,
            "mean_w": mean_w}


def plot_perf(print_perf=True, save=False):
    """Plot power coefficient versus azimuthal angle."""
    df = load_timedata()
    if print_perf:
        df_last = df.iloc[len(df)//2:]
        print("From {:.1f}--{:.1f} degrees, mean_cp: {:.2f}".format(
              df_last.theta_deg.min(), df_last.theta_deg.max(),
              df_last.power_coeff.mean()))
    fig, ax = plt.subplots()
    ax.plot(df.theta_deg, df.power_coeff, marker="o")
    ax.set_xlabel(r"$\theta$ (degrees)")
    ax.set_ylabel(r"$C_P$")
    fig.tight_layout()
    if save:
        fig.savefig("figures/perf.pdf")
        fig.savefig("figures/perf.png", dpi=300)


def plot_perf_curves(exp=False, single_ds=False, alm=True, save=False):
    """Plot performance curves.

    Parameters
    ----------
    single_ds : bool
        Whether or not to plot results from multiple dynamic stall models.
    """
    fig, ax = plt.subplots(figsize=(7.5, 3), nrows=1, ncols=2)
    df = pd.read_csv("processed/tsr_sweep.csv")
    ax[0].plot(df.tsr, df.cp, marker="o", label="CACTUS LB")
    ax[1].plot(df.tsr, df.cd, marker="o", label="CACTUS LB")
    ax[0].set_ylabel("$C_P$")
    ax[1].set_ylabel("$C_D$")
    [a.set_xlabel(r"$\lambda$") for a in ax]
    if not single_ds:
        if os.path.isfile("processed/tsr_sweep_bv.csv"):
            df = pd.read_csv("processed/tsr_sweep_bv.csv")
            ax[0].plot(df.tsr, df.cp, marker="s", label="CACTUS BV")
            ax[1].plot(df.tsr, df.cd, marker="s", label="CACTUS BV")
        if os.path.isfile("processed/tsr_sweep_no_ds.csv"):
            df = pd.read_csv("processed/tsr_sweep_no_ds.csv")
            ax[0].plot(df.tsr, df.cp, marker="d", label="CACTUS no DS")
            ax[1].plot(df.tsr, df.cd, marker="d", label="CACTUS no DS")
    if alm:
        df_alm = pd.read_csv("https://raw.githubusercontent.com/"
                             "petebachant/RM2-turbinesFoam/master/processed/"
                             "tsr_sweep.csv")
        ax[0].plot(df_alm.tsr, df_alm.cp, marker="v", label="ALM")
        ax[1].plot(df_alm.tsr, df_alm.cd, marker="v", label="ALM")
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
    if exp or not single_ds or alm:
        ax[1].legend(loc="upper left")
    fig.tight_layout()
    if save:
        fig.savefig("figures/perf-curves.pdf")
        fig.savefig("figures/perf-curves.png", dpi=300)


def plot_perf_curves_jacobs(exp=False, save=False):
    """Plot performance curves generated by using both the Sheldahl and Jacobs
    foil coefficient databases.
    """
    fig, ax = plt.subplots(figsize=(7.5, 3), nrows=1, ncols=2)
    for db in ["Sheldahl", "Jacobs"]:
        fpath = "processed/tsr_sweep.csv"
        if db == "Jacobs":
            fpath = fpath.replace(".csv", "_Jacobs.csv")
        df = pd.read_csv(fpath)
        ax[0].plot(df.tsr, df.cp, marker="o", label=db)
        ax[1].plot(df.tsr, df.cd, marker="o", label=db)
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
    if exp or not single_ds or alm:
        ax[1].legend(loc="upper left")
    fig.tight_layout()
    if save:
        fig.savefig("figures/perf-curves.pdf")
        fig.savefig("figures/perf-curves.png", dpi=300)


def plot_perf_re_dep(exp=False, save=False):
    """Plot Reynolds number dependence of C_P."""
    fpath = "processed/u_infty_sweep.csv"
    if os.path.isfile(fpath):
        df = pd.read_csv(fpath)
        fig, ax = plt.subplots()
        df["Re_c"] = df.u_infty*c*df.tsr/nu
        ax.plot(df.Re_c, df.cp, marker="o", label="CACTUS")
        ax.set_xlabel("$Re_{c,\mathrm{ave}}$")
        ax.set_ylabel("$C_P$")
        if exp:
            df_exp = pd.read_csv("https://raw.githubusercontent.com/UNH-CORE/"
                                 "RM2-tow-tank/master/Data/Processed/"
                                 "Perf-tsr_0.csv")
            df_exp2 = pd.read_csv("https://raw.githubusercontent.com/UNH-CORE/"
                                  "RM2-tow-tank/master/Data/Processed/"
                                  "Perf-tsr_0-b.csv")
            df_exp = df_exp.append(df_exp2, ignore_index=True)
            df_exp = df_exp.groupby("tow_speed_nom").mean()
            df_exp["Re_c"] = df_exp.mean_tow_speed*df_exp.mean_tsr*c/nu
            ax.plot(df_exp.Re_c, df_exp.mean_cp, color="black", marker="^",
                    markerfacecolor="none", label="Exp.")
            ax.legend(loc="lower right")
        fig.tight_layout()
        if save:
            fig.savefig("figures/perf-re-dep.png", dpi=300)
            fig.savefig("figures/perf-re-dep.pdf")
    else:
        return None


def plot_verification(save=False):
    """Plot the sensitivity to time step and number of blade elements."""
    fig, ax = plt.subplots(figsize=(7.5, 3), nrows=1, ncols=2)
    try:
        df = pd.read_csv("processed/nti_sweep.csv")
        ax[0].plot(df.nti, df.cp, marker="o")
        ax[0].set_xlabel("Time steps per rev.")
    except OSError:
        print("No nti sweep file found")
    try:
        df = pd.read_csv("processed/nbelem_sweep.csv")
        ax[1].plot(df.nbelem, df.cp, marker="o")
        ax[1].set_xlabel("Elements per blade")
    except OSError:
        print("No nbelem sweep file found")
    [a.set_ylabel("$C_P$") for a in ax]
    fig.tight_layout()
    if save:
        fig.savefig("figures/verification.pdf")
        fig.savefig("figures/verification.png", dpi=300)


def plot_turb_lines(linestyles="solid", linewidth=2, color="gray"):
    plt.hlines(0.5, -1, 1, linestyles=linestyles, colors=color,
               linewidth=linewidth)
    plt.vlines(-1, -0.2, 0.5, linestyles=linestyles, colors=color,
               linewidth=linewidth)
    plt.vlines(1, -0.2, 0.5, linestyles=linestyles, colors=color,
               linewidth=linewidth)


def plot_meancontquiv(t1_fraction=0.5, cb_orientation="vertical", save=False):
    """Plot contours of normalized mean streamwise velocity and vectors of
    cross-stream and vertical mean velocity.
    """
    data = load_probe_data(t1_fraction=t1_fraction)
    y_R = data["y_R"]
    z_H = data["z_H"]
    mean_u = data["mean_u"]
    mean_v = data["mean_v"]
    mean_w = data["mean_w"]
    scale = 7.5/10.0
    plt.figure(figsize=(10*scale, 3*scale))
    # Add contours of mean velocity
    cs = plt.contourf(y_R, z_H, mean_u, 20, cmap=plt.cm.coolwarm)
    if cb_orientation == "horizontal":
        cb = plt.colorbar(cs, shrink=1, extend="both",
                          orientation="horizontal", pad=0.14)
    elif cb_orientation == "vertical":
        cb = plt.colorbar(cs, shrink=0.88, extend="both",
                          orientation="vertical", pad=0.02)
    cb.set_label(r"$U/U_{\infty}$")
    # Make quiver plot of v and w velocities
    Q = plt.quiver(y_R, z_H, mean_v, mean_w, width=0.0022,
                   edgecolor="none", scale=3)
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$z/H$")
    plt.ylim(-0.15, 0.85)
    plt.xlim(-1.68/R, 1.68/R)
    if cb_orientation == "horizontal":
        plt.quiverkey(Q, 0.65, 0.26, 0.1, r"$0.1 U_\infty$",
                      labelpos="E",
                      coordinates="figure",
                      fontproperties={"size": "small"})
    elif cb_orientation == "vertical":
        plt.quiverkey(Q, 0.65, 0.09, 0.1, r"$0.1 U_\infty$",
                      labelpos="E",
                      coordinates="figure",
                      fontproperties={"size": "small"})
    plot_turb_lines()
    ax = plt.axes()
    ax.set_aspect(H/R)
    plt.yticks([0, 0.13, 0.25, 0.38, 0.5, 0.63, 0.75])
    plt.grid(True)
    plt.tight_layout()
    if save:
        plt.savefig("figures/meancontquiv.pdf")
        plt.savefig("figures/meancontquiv.png", dpi=300)


def plot_foildata(save=False):
    """Plot static foil data for comparison."""
    fig, ax = plt.subplots(figsize=(7.5, 3.25), nrows=1, ncols=2)
    data = {"Gregorek": pd.read_csv("config/foildata/NACA_0021_Gregorek.csv"),
            "Sheldahl": pd.read_csv("config/foildata/"
                                    "NACA_0021_Sheldahl_1.5e6.csv"),
            "Jacobs": pd.read_csv("config/foildata/"
                                  "NACA_0021_Jacobs_1.5e6.csv"),
            "XFOIL": load_raw_xfoil_data(Re=1.5e6)}
    for d, m in zip(["Gregorek", "Sheldahl", "Jacobs", "XFOIL"],
                    ["o", "^", "s", "x"]):
        df = data[d]
        if d == "Sheldahl" or d == "Jacobs" or d == "XFOIL":
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
        fig.savefig("figures/foil-data.png", dpi=300)


def plot_foildata_lowre(xfoil=True, cfd=False, save=False):
    """Plot 0021 lift coefficient for low Reynolds number."""
    fig, ax = plt.subplots()
    data = {"Sheldahl": pd.read_csv("config/foildata/"
                                    "NACA_0021_Sheldahl_1.6e5.csv"),
            "Jacobs": pd.read_csv("config/foildata/"
                                  "NACA_0021_Jacobs_1.6e5.csv")}
    for d, m in zip(["Sheldahl", "Jacobs"], ["o", "^"]):
        df = data[d]
        if "alpha_deg" in df:
            df["alpha"] = df["alpha_deg"]
        df = df.sort_values(by="alpha")
        df = df[df.alpha >= -0.1]
        df = df[df.alpha <= 30]
        ax.plot(df.alpha, df.cl, marker=m, label=d)
    ax.set_xlabel(r"$\alpha$ (degrees)")
    if xfoil:
        df = load_raw_xfoil_data(Re=1.6e5, alpha_name="alpha")
        df = df[df.alpha >= -0.1]
        df = df[df.alpha <= 30]
        ax.plot(df.alpha, df.cl, label="XFOIL", marker="x")
    if cfd:
        df_cfd = pd.read_csv("https://raw.githubusercontent.com/petebachant/"
                             "NACAFoil-OpenFOAM/master/processed/"
                             "NACA0021_2.0e%2B05.csv")
        ax.plot(df_cfd.alpha_deg, df_cfd.cl, marker="s",
                label="2-D SST RANS")
    ax.set_ylabel("$C_l$")
    ax.legend(loc="lower right")
    fig.tight_layout()
    if save:
        fig.savefig("figures/foil-data-low-Re.pdf")
        fig.savefig("figures/foil-data-low-Re.png", dpi=300)


def plot_tp_dep(save=False):
    """Plot dependence of mean C_P on LB DS model T_p parameter."""
    fpath = "processed/tp_sweep.csv"
    if os.path.isfile(fpath):
        df = pd.read_csv(fpath)
        fig, ax = plt.subplots()
        ax.plot(df.tp, df.cp, marker="o")
        ax.set_xlabel("$T_p$")
        ax.set_ylabel("$C_P$")
        fig.tight_layout()
        if save:
            fig.savefig("figures/tp-dep.pdf")
            fig.savefig("figures/tp-dep.png", dpi=300)
    else:
        print(fpath, "not found")


if __name__ == "__main__":
    set_sns()
    plt.rcParams["axes.grid"] = True

    parser = argparse.ArgumentParser(description="Generate plots.")
    parser.add_argument("plot", nargs="*", help="What to plot", default="perf",
                        choices=["perf", "perf-curves", "perf-curves-exp",
                                 "verification", "foil-data", "re-dep",
                                 "re-dep-exp", "tp-dep", "perf-curves-jacobs"])
    parser.add_argument("--single-ds", "-d", default=False, action="store_true",
                        help="Plot perf curves for LB dynamic stall model "
                        "only")
    parser.add_argument("--no-alm", default=False, action="store_true",
                        help="Do not plot ALM results")
    parser.add_argument("--all", "-A", help="Generate all figures",
                        default=False, action="store_true")
    parser.add_argument("--save", "-s", help="Save to `figures` directory",
                        default=False, action="store_true")
    parser.add_argument("--no-show", default=False, action="store_true",
                        help="Do not call matplotlib show function")
    parser.add_argument("-q", help="Quantities to plot", nargs="*",
                        default=["alpha", "rel_vel_mag"])
    parser.add_argument("--cfd", default=False, action="store_true",
                        help="Plot CFD results for low Re static foil data")
    parser.add_argument("--xfoil", default=False, action="store_true",
                        help="Plot XFOIL results for low Re static foil data")
    args = parser.parse_args()

    if args.save:
        if not os.path.isdir("figures"):
            os.mkdir("figures")

    if "perf" in args.plot and not args.all:
        plot_perf(save=args.save)
    if "perf-curves" in args.plot:
        plot_perf_curves(exp=False, single_ds=args.single_ds,
                         alm=not args.no_alm, save=args.save)
    if "perf-curves-exp" in args.plot or args.all:
        plot_perf_curves(exp=True, single_ds=args.single_ds,
                         alm=not args.no_alm, save=args.save)
    if "perf-curves-jacobs" in args.plot or args.all:
        plot_perf_curves_jacobs(exp=True, save=args.save)
    if "re-dep" in args.plot or args.all:
        with plt.rc_context(rc={"axes.formatter.use_mathtext": True}):
            plot_perf_re_dep(save=args.save)
    if "re-dep-exp" in args.plot or args.all:
        with plt.rc_context(rc={"axes.formatter.use_mathtext": True}):
            plot_perf_re_dep(exp=True, save=args.save)
    if "verification" in args.plot or args.all:
        plot_verification(save=args.save)
    if "foil-data" in args.plot or args.all:
        plot_foildata(save=args.save)
        plot_foildata_lowre(xfoil=args.xfoil, cfd=args.cfd, save=args.save)
    if "tp-dep" in args.plot or args.all:
        plot_tp_dep(save=args.save)

    if not args.no_show:
        plt.show()
