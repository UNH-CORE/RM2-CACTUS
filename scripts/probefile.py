#!/usr/bin/env python
"""This script create the probe specification file to match experiments."""

from __future__ import division, print_function
import numpy as np
import pandas as pd

H = 0.807
R = 0.5375

# All coordinates should be normalized by radius
z_H = np.arange(0.0, 0.751, 0.125)
z_R = z_H * H / R

# Load y_R locations from experimental test plan
df = pd.read_csv("RM2-tow-tank/Config/Test plan/Wake-1.0-0.0.csv")
y_R = df["y/R"].values

x = 1.0
x_R = x/R

coords = []
for z in z_R:
    for y in y_R:
        coords.append("{} {} {}".format(x_R, y, z))

nprobes = len(coords)

with open("./config/probes.txt", "w") as f:
    f.write(str(nprobes) + "\n")
    for coord in coords:
        f.write(coord + "\n")
