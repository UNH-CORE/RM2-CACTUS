#!/usr/bin/env python
"""Create hybrid foil coefficient dataset from Sheldahl and Jacobs data."""

from __future__ import division, print_function
import numpy as np
import pandas as pd


header = \
"""Title: NACA0021
Thickness to Chord Ratio: 0.21
Zero Lift AOA (deg): 0.0
Reverse Camber Direction: 0"""

subheader = \
"""Reynolds Number: {re}
BV Dyn. Stall Model - Positive Stall AOA (deg): {bv_pos_stall_angle}
BV Dyn. Stall Model - Negative Stall AOA (deg): {bv_nev_stall_angle}
LB Dyn. Stall Model - Lift Coeff. Slope at Zero Lift AOA (per radian): {lb_lift_coeff_slope}
LB Dyn. Stall Model - Positive Critical Lift Coeff.: {lb_pos_crit_cl}
LB Dyn. Stall Model - Negative Critical Lift Coeff.: {lb_neg_crit_cl}
AOA (deg) CL CD Cm25"""

re_list = ["8.3e4", "1.6e5", "3.8e5"]

bv_stall_angles = {"8.3e4": 4.0, "1.6e5": 5.0, "3.8e5": 5.0}
lb_lift_slopes = {"8.3e4": 5.277, "1.6e5": 5.371, "3.8e5": 6.303}
lb_crit_cls = {"8.3e4": 0.829, "1.6e5": 1.031, "3.8e5": 1.32}

# Create empty dictionary for DataFrames
dfs = {}

# Load Jacobs data and mirror about zero angle of attack
for re in re_list:
    df = pd.read_csv("config/foildata/NACA_0021_Jacobs_{}.csv".format(re))
    df = df[df.alpha >= 0.0]
    alpha = np.append(-np.flipud(df.alpha), df.alpha)
    cl = np.append(np.flipud(df.cl), df.cl)
    df = pd.DataFrame()
    df["alpha_deg"] = alpha
    df["cl"] = cl
    dfs[re] = df

# Fill in Jacobs C_d and C_m data from Sheldahl, interpolating to the Jacobs
# AoAs
for re in re_list:
    df = dfs[re]
    df_sh = pd.read_csv("config/foildata/NACA_0021_Sheldahl_{}.csv".format(re))
    df["cd"] = np.interp(df.alpha_deg, df_sh.alpha_deg, df_sh.cd)
    df["cm"] = np.interp(df.alpha_deg, df_sh.alpha_deg, df_sh.cm)
    # Replace all Sheldahl data with Jacobs in its AoA range
    df_sh_save_pos = df_sh[df_sh.alpha_deg > df.alpha_deg.max()]
    df_sh_save_neg = df_sh[df_sh.alpha_deg < df.alpha_deg.min()]
    df = df_sh_save_neg.append(df, ignore_index=True)
    df = df.append(df_sh_save_pos, ignore_index=True)
    dfs[re] = df

# Write final text file in correct format
txt = header + "\n\n"
for re in re_list:
    txt += subheader.format(re=re, bv_pos_stall_angle=bv_stall_angles[re],
                            bv_nev_stall_angle=bv_stall_angles[re],
                            lb_lift_coeff_slope=lb_lift_slopes[re],
                            lb_pos_crit_cl=lb_crit_cls[re],
                            lb_neg_crit_cl=lb_crit_cls[re]) + "\n"
    df = dfs[re]
    for alpha_deg, cl, cd, cm in zip(df.alpha_deg, df.cl, df.cd, df.cm):
        txt += str(alpha_deg) + "\t" + str(cl) + "\t" + str(cd) + "\t" + str(cm)
        txt += "\n"
    txt += "\n"

with open("config/foildata/NACA_0021_Jacobs.dat", "w") as f:
    f.write(txt)
