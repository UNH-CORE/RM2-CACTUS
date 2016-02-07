#!/usr/bin/env python

from __future__ import division, print_function
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


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


def plot_perf(print_perf=True):
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


if __name__ == "__main__":
    import seaborn as sns

    plot_perf()
    plt.show()
