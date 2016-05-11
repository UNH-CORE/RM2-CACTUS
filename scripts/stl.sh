#!/usr/bin/env bash
# Download CAD if not present and transform to appropriate coordinate system
# for visualization

CAD_ZIP=figures/cad.zip
STL=figures/turbine.stl

# Download zip of CAD files if doesn't exist
if [ ! -f $CAD_ZIP ]
then
    wget https://ndownloader.figshare.com/files/2013052 -O $CAD_ZIP
fi

# Unzip CAD files if not existing
if [ ! -f $STL ]
then
    unzip -j $CAD_ZIP "UNH RM2 CAD package/Simplified/STL/turbine.STL" -d figures
    mv figures/turbine.STL $STL
fi
