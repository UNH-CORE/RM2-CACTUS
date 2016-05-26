# Validation of a vortex line model for a medium solidity vertical-axis turbine

_Peter Bachant, Phillip Chiu, Victor Nevarez, Martin Wosnik, Vincent Neary_


## Abstract


## Introduction

To accelerate the development of marine hydrokinetic turbine technology, Sandia
National Laboratories (SNL) developed the Code for Axial and Cross-flow TUrbine
Simulation (CACTUS), based on Strickland's VDART model [@Strickland1981],
originally developed for SNL in the 1980s to aid in the design of Darrieus
vertical-axis wind turbines (VAWTs). Upgrades to CACTUS beyond VDART include
ground plane and free surface modeling, as well as a new added mass correction
[@Murray2011].

CACTUS was previously validated using experimental data from relatively low
solidity $\sigma = Nc/(2 \pi R)$ rotors. However, when applied to a high
solidity (or chord-to-radius ratio $c/R$) H-rotor, CACTUS significantly
overpredicted blade loading, and therefore mean performance coefficients
[@Michelin2014].


### Objectives

1. Evaluate the effectiveness of the CACTUS vortex line model for predicting the
experimental performance results acquired for the 1:6 scale RM2 physical model
experiments at UNH.
2. Suggest what could be done to improve CACTUS predictions, and develop some
best practice guidelines for its use.


## Methods

### Numerical setup

In this study we are modeling the 1:6 scale RM2 experiment performed in the UNH
tow tank, for which the data is available from [@Bachant2016-RM2-paper].


## Results

### Static foil comparison

XFOIL data shows overprediction of lift at stall compared with two experimental
(Gregorek, Jacobs) and one semi-empirical datasets (Sheldahl).


### Verification

Sensitivity of the model results to the time step (or number of time steps per
revolution) and number of blade elements was assessed.


### Mean performance

The performance curve of the RM2 was simulated using both the Boeing--Vertol and
Leishman--Beddoes dynamic stall models, as well as with dynamic stall modeling
deactivated.

![RM2 performance curves simulated with CACTUS using the Boeing--Vertol, Leishman--Beddoes, and no dynamic stall model.](figures/perf-curves.png)


## Conclusions
