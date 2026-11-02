from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. File locations
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

SIMULATION_FILE = BASE_DIR / "aluminium_simulation.csv"
EXPERIMENT_FILE = BASE_DIR / "day3_30min.csv"

OUTPUT_DIR = BASE_DIR / "Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------
# 2. CSV column names
# Change these if your actual headers are different.
# ------------------------------------------------------------
COLUMN_MAP = {
    "simulation_time": "Elapsed_time_minutes",
    "simulation_temp": "Predicted_aluminium_temperature_C",
    "experiment_time": "Elapsed time (min)",
    "experiment_temp": "Plate (°C)",
}
# ------------------------------------------------------------
# 3. Read and check the CSV files
# ------------------------------------------------------------
for file_path in [SIMULATION_FILE, EXPERIMENT_FILE]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}\n"
            "Place both CSV files in the same folder as this script."
        )

sim = pd.read_csv(SIMULATION_FILE)
exp = pd.read_csv(EXPERIMENT_FILE)

for file_name, df, required_columns in [
    ("simulation", sim, [
        COLUMN_MAP["simulation_time"],
        COLUMN_MAP["simulation_temp"],
    ]),
    ("experiment", exp, [
        COLUMN_MAP["experiment_time"],
        COLUMN_MAP["experiment_temp"],
    ]),
]:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"{file_name.title()} CSV is missing columns: {missing}\n"
            f"Columns found: {list(df.columns)}"
        )

# ------------------------------------------------------------
# 4. Convert columns to numbers and remove incomplete rows
# ------------------------------------------------------------
sim_time = COLUMN_MAP["simulation_time"]
sim_temp = COLUMN_MAP["simulation_temp"]
exp_time = COLUMN_MAP["experiment_time"]
exp_temp = COLUMN_MAP["experiment_temp"]

sim[sim_time] = pd.to_numeric(sim[sim_time], errors="coerce")
sim[sim_temp] = pd.to_numeric(sim[sim_temp], errors="coerce")
exp[exp_time] = pd.to_numeric(exp[exp_time], errors="coerce")
exp[exp_temp] = pd.to_numeric(exp[exp_temp], errors="coerce")

sim = sim.dropna(subset=[sim_time, sim_temp]).sort_values(sim_time)
exp = exp.dropna(subset=[exp_time, exp_temp]).sort_values(exp_time)

# ------------------------------------------------------------
# 5. Match temperatures by elapsed time
# Use exact matches first. If a simulation value is not
# available at an experimental time, interpolate between
# nearby simulation points.
# ------------------------------------------------------------
sim = sim.drop_duplicates(subset=sim_time, keep="first")

matched = pd.DataFrame({
    "Elapsed time (min)": exp[exp_time].to_numpy(),
    "Experimental temperature (°C)": exp[exp_temp].to_numpy(),
})

matched["Simulated temperature (°C)"] = np.interp(
    matched["Elapsed time (min)"],
    sim[sim_time],
    sim[sim_temp],
    left=np.nan,
    right=np.nan,
)

# Keep only experimental times within the simulation time range
matched = matched.dropna(
    subset=["Simulated temperature (°C)"]
).reset_index(drop=True)

if matched.empty:
    raise ValueError(
        "No overlapping measurement times were found. "
        "Check that both files use elapsed time in minutes "
        "and cover the same test period."
    )

# ------------------------------------------------------------
# 6. Calculate validation metrics
# Error = simulation - experiment
# ------------------------------------------------------------
error = (
    matched["Simulated temperature (°C)"]
    - matched["Experimental temperature (°C)"]
)

mae = np.mean(np.abs(error))
rmse = np.sqrt(np.mean(error ** 2))

# MAPE is not defined when an experimental temperature is zero
nonzero_exp = matched["Experimental temperature (°C)"] != 0
if nonzero_exp.any():
    mape = np.mean(
        np.abs(
            error[nonzero_exp]
            / matched.loc[nonzero_exp, "Experimental temperature (°C)"]
        )
    ) * 100
else:
    mape = np.nan

# ------------------------------------------------------------
# 7. Plot grouped bars
# ------------------------------------------------------------
x = np.arange(len(matched))
bar_width = 0.38

fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(
    x - bar_width / 2,
    matched["Simulated temperature (°C)"],
    bar_width,
    label="Simulation",
)

ax.bar(
    x + bar_width / 2,
    matched["Experimental temperature (°C)"],
    bar_width,
    label="Experiment",
)

# Use elapsed time labels on the x-axis
time_labels = matched["Elapsed time (min)"].map(
    lambda value: f"{value:g}"
)

ax.set_xticks(x)
ax.set_xticklabels(time_labels, rotation=45, ha="right")
ax.set_xlabel("Elapsed time (min)")
ax.set_ylabel("Absorber plate temperature (°C)")
ax.set_title("Aluminium Solar Box Cooker: Simulation vs Day 3 Experiment")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.35)

# Include metrics in the figure
metrics_text = (
    f"MAE = {mae:.2f} °C\n"
    f"RMSE = {rmse:.2f} °C\n"
    f"MAPE = {mape:.2f}%"
    if not np.isnan(mape)
    else f"MAE = {mae:.2f} °C\nRMSE = {rmse:.2f} °C\nMAPE = N/A"
)

ax.text(
    0.02,
    0.98,
    metrics_text,
    transform=ax.transAxes,
    va="top",
    ha="left",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85),
)

fig.tight_layout()

chart_path = OUTPUT_DIR / "Aluminium_Simulation_vs_Day3.png"
fig.savefig(chart_path, dpi=300, bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------
# 8. Save matched data and print results
# ------------------------------------------------------------
matched["Error (Simulation - Experiment) (°C)"] = error

matched_path = OUTPUT_DIR / "Aluminium_Simulation_vs_Day3_Matched_Data.csv"
matched.to_csv(matched_path, index=False)

print("\nVALIDATION RESULTS")
print("------------------")
print(f"Matched observations: {len(matched)}")
print(f"MAE:  {mae:.3f} °C")
print(f"RMSE: {rmse:.3f} °C")
print(f"MAPE: {mape:.2f}%" if not np.isnan(mape) else "MAPE: N/A")
print(f"\nChart saved to: {chart_path}")
print(f"Matched data saved to: {matched_path}")