# Experiment vs Simulation

This section compares the aluminium absorber temperature predicted by the MATLAB simulation with the supplied experimental absorber-plate measurements from three test days.

## Inputs

- `aluminium_simulation.csv` — simulation time-series data.
- `day1_30min.csv`, `day2_30min.csv`, `day3_30min.csv` — experimental readings.
- `Simulation_Experiment.py` — detailed comparison of the simulation against Day 3.
- `compare_simulation_all_days.py` — comparison of the simulation against all three experimental days.
- `Results/` — matched datasets, validation metrics and plots.

## Processing approach

The scripts check the expected column names, convert time and temperature fields to numeric values, remove incomplete records and sort by elapsed time. For the all-days comparison, only elapsed times present in all three experimental datasets and covered by the simulation are retained. The simulation is interpolated at those common experimental times; experimental observations are not interpolated to manufacture missing measurements.

The scripts calculate mean absolute error (MAE), root mean square error (RMSE), mean bias error (MBE) and mean absolute percentage error (MAPE), where defined. They also save matched data and visual comparisons.

## Run

```bash
python -m pip install numpy pandas matplotlib
python Simulation_Experiment.py
python compare_simulation_all_days.py
```

Run commands from this directory. Results are written to `Results/`.

## Expected columns

Simulation:
- `Elapsed_time_minutes`
- `Predicted_aluminium_temperature_C`

Experiment:
- `Elapsed time (min)`
- `Plate (°C)`

Update the constants near the top of the scripts if the actual CSV headers differ.

## Important interpretation

The comparison is a model-to-observation comparison for the aluminium case. Error metrics quantify agreement over the matched times but do not, by themselves, prove causation or validate every model assumption. The MATLAB simulation's weather profile and thermal coefficients are assumed inputs; the experimental files should be cited as the source of the measured observations. Ensure the experimental and simulation clocks use the same elapsed-time origin before interpreting the comparison.
