# Modelling, Simulation, and Experimental Validation of Solar Box Cooker with Reflector Using Aluminum Absorber

This repository contains the MATLAB simulation, experimental temperature data, Python analysis scripts, and comparison results for a solar box cooker using a black-coated aluminium absorber plate.

The work compares the model’s predicted absorber-plate temperature with measurements collected over three experimental days. The repository is intended to support the project report and make the analysis files and results accessible.

## Project overview

A solar box cooker uses solar radiation to heat an absorber plate inside an insulated enclosure. This project investigates the temperature response of a cooker fitted with a reflector and an aluminium absorber.

The current model represents the cooker using a simplified one-node thermal approach. It predicts absorber-plate temperature over time and is compared with the available experimental measurements.

### Cooker configuration

- Absorber: black-coated aluminium plate
- Plate dimensions: 50 cm × 30 cm × 0.25 mm
- Reflector: fixed at 90°
- Insulation: sawdust
- Cover: single glass glazing
- Outer box: plywood
- Cooking load: none during the reported test configuration

## Repository contents

| File or folder                                       | Description                                                                 |
| ---------------------------------------------------- | --------------------------------------------------------------------------- |
| `solar_box_cooker_matlab_simulation_script.m`        | MATLAB script for the aluminium cooker temperature prediction               |
| `aluminium_simulation.csv`                           | Exported simulation time-series data                                        |
| `day1_30min.csv`, `day2_30min.csv`, `day3_30min.csv` | Experimental temperature and ambient-condition data for three test days     |
| `compare_days.py`                                    | Python script for comparing the experimental days                           |
| `days_plot.py`                                       | Python script for plotting experimental results                             |
| `Simulation_Experiment.py`                           | Python script for comparing simulation and experimental measurements        |
| `compare_simulation_all_days.py`                     | Python script for comparing the simulation with all three experimental days |
| `All_Days_Matched_Temperature_Data.csv`              | Matched simulation and experimental temperature values                      |
| `All_Days_Validation_Metrics.csv`                    | Summary of the temperature-comparison metrics                               |
| `*_Comparison.png`, `*_Temperature_Humidity.png`     | Experimental plots                                                          |
| `Aluminium_Simulation_vs_Day*.png`                   | Individual simulation-to-experiment comparison plots                        |
| `Simulation_vs_Three_Days_*.png`                     | Combined comparison plots                                                   |
| `Simulation Result*.pdf`                             | Exported simulation figures                                                 |
| `src/`, `include/`, `lib/`, `test/`                  | Arduino/PlatformIO project files for the experimental logger                |
| `platformio.ini`                                     | PlatformIO project configuration                                            |
| `logger.py`                                          | Logger utility                                                              |

## Method

### 1. MATLAB simulation

The MATLAB script implements a simplified one-node thermal model for the aluminium absorber. The simulation predicts plate temperature over the selected daytime period.

The model uses prescribed weather and thermal inputs. These inputs are scenario assumptions; they are not presented as measurements taken during the experimental tests. The model is independent of the experimental temperature curves and is not calibrated to them.

### 2. Experimental measurements

The included experimental CSV files contain measurements from three test days. The available data are provided as processed, 30-minute-interval records.

### 3. Comparison and analysis

Python scripts compare predicted and measured plate temperatures at matched elapsed-time points. The repository includes individual-day comparisons and a combined comparison across the three days.

The reported metrics are:

- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- Mean Bias Error (MBE)
- Mean Absolute Percentage Error (MAPE)

These metrics describe the difference between the model predictions and the available measurements. They should be interpreted in light of the model assumptions and the experimental conditions.

## Current comparison results

The included validation summary reports the following results:

| Experimental day | Matched observations | MAE (°C) | RMSE (°C) | MBE (°C) | MAPE (%) |
| ---------------- | -------------------: | -------: | --------: | -------: | -------: |
| Day 1            |                   15 |    2.009 |     2.294 |   -1.843 |    2.170 |
| Day 2            |                   15 |    0.568 |     0.728 |    0.420 |    0.828 |
| Day 3            |                   15 |    1.545 |     1.764 |    1.545 |    2.052 |

These values are reproduced from `All_Days_Validation_Metrics.csv`. They apply to the data and model version included in this repository.

## Software and tools

- MATLAB — thermal simulation
- Python — data processing, comparison, and plotting
- Python packages used by the analysis scripts: NumPy, pandas, and Matplotlib
- PlatformIO / Arduino — experimental logger project

Install the Python packages with:

```bash
python -m pip install numpy pandas matplotlib
```

## How to use

1. Open `solar_box_cooker_matlab_simulation_script.m` in MATLAB.
2. Run the script to generate the simulation output required by the comparison scripts.
3. Ensure the simulation CSV and the three experimental CSV files are in the locations expected by the Python scripts.
4. Run the relevant Python comparison or plotting script from the repository folder.

For example:

```bash
python compare_days.py
python days_plot.py
python compare_simulation_all_days.py
```

Script filenames, input paths, and expected column names should be checked if you move files into a different folder structure.

## Scope and limitations

- This repository covers the aluminium-absorber version of the project.
- The simulation is a simplified prediction model, not a detailed CFD or multi-node thermal model.
- Weather and thermal parameters used by the simulation are prescribed assumptions, not measured experimental inputs.
- The experimental records included here are processed data; the original raw logger files and the exact data-cleaning procedure are not included.
- The comparison is based on the available three-day dataset and the matched observations shown in the validation summary.
- Results should not be generalized to other cooker geometries, absorber materials, reflector settings, or operating conditions without further testing.

## Project status

The repository contains the current aluminium simulation, available three-day experimental data, analysis scripts, and comparison outputs. It is shared as a project research and reproducibility resource.

## Author

Muhibullah Abdulmumeen

Mechanical Engineering Department
University of Maiduguri, Nigeria

## Citation

If you use this repository, please cite or acknowledge the project title and link to this GitHub repository. Add the author’s name, publication details, or a formal citation here if required by your department or supervisor.

## License

No license has been selected for this repository yet. Unless a license is added, the files remain under the applicable default copyright protections.
