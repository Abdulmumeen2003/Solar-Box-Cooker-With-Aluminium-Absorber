# Model & Simulation

This section contains the MATLAB implementation of the simplified thermal model for the solar box cooker, the exported aluminium simulation time series, and PDF plots of the predicted response.

## Contents

- `solar_box_cooker_matlab_simulation_script.m` — MATLAB script for the independent aluminium absorber prediction.
- `aluminium_simulation.csv` — exported simulation time-series data used by the comparison workflow.
- `Simulation Result.pdf` — simulation result summary plot.
- `Simulation Result(Time VS Temp).pdf` — predicted temperature against time.
- `Simulation Result(Time VS Amb).pdf` — ambient temperature against time.
- `Simulation Result(Time VS Irreden).pdf` — solar irradiance against time.

## Model overview

The MATLAB script implements a lumped, one-node energy balance for an empty solar box cooker with a black-coated aluminium absorber. Solar energy transmitted through the assumed glazing and modified by an approximate reflector factor is added to the absorber/cooker thermal capacitance. An effective heat-loss term accounts for thermal losses to ambient air. The ordinary differential equation is integrated using an explicit forward-Euler time step.

The model uses a 10-second time step over 09:00–16:00. It assumes a 0.50 m × 0.30 m × 0.25 mm aluminium plate, single glazing, a fixed reflector angle of 90°, sawdust insulation and a plywood outer box.

## Important assumptions

The script labels its weather and construction inputs as illustrative assumptions. In particular, the irradiance and ambient-temperature profiles are assumed clear-sky Maiduguri scenarios, not measured data from the experimental CSV files. The glazing transmission, reflector factor, effective heat-loss coefficient and additional cooker thermal capacitance are also assumed values.

Consequently, outputs are model predictions under the stated assumptions; they should not be presented as measured performance or as a fully calibrated model.

## Running the model

1. Open MATLAB.
2. Set the current folder to this directory, or open the `.m` file.
3. Run `solar_box_cooker_matlab_simulation_script.m`.
4. Inspect the figures and exported CSV files in MATLAB's current working directory.

The script requires standard MATLAB functionality (`interp1`, plotting, `table` and `writetable`).

## Outputs

The script displays predicted peak absorber temperature, time of peak, end-of-period temperature and temperature rise. It also creates temperature, irradiance and ambient-temperature plots and exports a time-series CSV plus a summary CSV.

## Scope

The current script models aluminium only. Do not infer zinc or aluminium-alloy simulation results from this file unless separate material-specific models and outputs are added.
