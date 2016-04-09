# RM2 CACTUS simulation case

This repository contains configuration files and scripts for modeling the
DOE/Sandia RM2 cross-flow turbine with [CACTUS](http://energy.sandia.gov/energy
/renewable-energy/wind-power/wind-resources/wind-software-downloads/cactus-
software-download/). Note that the simulation may require an unreleased,
non-backwards-compatible version of CACTUS.


## Getting started

Runs are automated and post-processed with Python. It is recommended users
download and install the
[Anaconda Python distribution](http://continuum.io/downloads) (3.5).

To download and compile CACTUS, initialize the submodules, then run

    ./scripts/make-cactus.sh


## Usage

Executing CACTUS is done with `run.py`. To see usage and options, execute

    python run.py -h

A similar script, `plot.py` is used for plotting the results.


### Examples

Run at a single tip speed ratio without dynamic stall:

    python run.py --tsr=3.1 --dynamic-stall=0

Calculate turbine performance curve:

    python run.py -p tsr 1.1 5.2 0.5

Run time step dependence parameter sweep:

    python run.py -p nti 8 57 8

Run parameter sweep for number of blade elements:

    python run.py -p nbelem 6 19 2


## Acknowledgements

Original configuration files (added in
[`e42f3ad3`](https://github.com/petebachant/RM2-CACTUS/commit/e42f3ad36f224e5e59e2d13fc2a9224a132c962b))
from Andrew Murphy Wilson (@awilmurph).


### Foil data

| File name | Reference |
|-----------|-----------|
| `config/NACA_0021.dat` | Sheldahl, R. and Klimas, P. (1981) "Aerodynamic Characteristics of Seven Symmetrical Airfoil Sections Through 180-Degrees Angle of Attack for Use in Aerodynamic Analysis of Vertical Axis Wind Turbines" |
| `config/foildata/NACA_0021_Gregorek.csv` | Gregorek, G. M.; Hoffman, M. J. and Berchak, M. J. (1989) "Steady state and oscillatory aerodynamic characteristics of a NACA 0021 airfoil" |


## License

Code licensed under the MIT license. See `LICENSE` for details.
All other materials licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
Creative Commons Attribution 4.0 International License</a>.

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/4.0/88x31.png" />
</a>
