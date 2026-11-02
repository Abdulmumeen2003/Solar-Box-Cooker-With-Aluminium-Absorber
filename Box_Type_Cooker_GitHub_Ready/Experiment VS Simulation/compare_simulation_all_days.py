
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 1. FILE LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "Results"
OUTPUT_DIR.mkdir(exist_ok=True)

SIMULATION_FILE = BASE_DIR / "aluminium_simulation.csv"

EXPERIMENT_FILES = {
    "Day 1": BASE_DIR / "day1_30min.csv",
    "Day 2": BASE_DIR / "day2_30min.csv",
    "Day 3": BASE_DIR / "day3_30min.csv"
}

# ============================================================
# 2. COLUMN NAMES
# ============================================================

SIM_TIME = "Elapsed_time_minutes"
SIM_TEMP = "Predicted_aluminium_temperature_C"

EXP_TIME = "Elapsed time (min)"
EXP_TEMP = "Plate (°C)"

# ============================================================
# 3. LOAD SIMULATION DATA
# ============================================================

if not SIMULATION_FILE.exists():
    raise FileNotFoundError(f"Missing file: {SIMULATION_FILE}")

sim = pd.read_csv(SIMULATION_FILE)

required_sim = [SIM_TIME, SIM_TEMP]

for col in required_sim:
    if col not in sim.columns:
        raise ValueError(
            f"Missing simulation column: {col}\n"
            f"Available columns: {list(sim.columns)}"
        )

sim[SIM_TIME] = pd.to_numeric(sim[SIM_TIME], errors="coerce")
sim[SIM_TEMP] = pd.to_numeric(sim[SIM_TEMP], errors="coerce")

sim = (
    sim.dropna(subset=required_sim)
       .sort_values(SIM_TIME)
       .drop_duplicates(subset=SIM_TIME)
)

if len(sim) < 2:
    raise ValueError("Simulation data needs at least two valid time points.")

# ============================================================
# 4. LOAD THREE EXPERIMENTAL DAYS
# ============================================================

experiments = {}

for day, file_path in EXPERIMENT_FILES.items():

    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    df = pd.read_csv(file_path)

    required_exp = [EXP_TIME, EXP_TEMP]

    for col in required_exp:
        if col not in df.columns:
            raise ValueError(
                f"{day} is missing column: {col}\n"
                f"Available columns: {list(df.columns)}"
            )

    df[EXP_TIME] = pd.to_numeric(df[EXP_TIME], errors="coerce")
    df[EXP_TEMP] = pd.to_numeric(df[EXP_TEMP], errors="coerce")

    df = (
        df.dropna(subset=required_exp)
          .sort_values(EXP_TIME)
          .drop_duplicates(subset=EXP_TIME)
    )

    experiments[day] = df

# ============================================================
# 5. FIND COMMON EXPERIMENTAL MEASUREMENT TIMES
# ============================================================

# Use only elapsed times measured on all three days.
# This avoids inventing experimental measurements through
# interpolation.

common_times = set(experiments["Day 1"][EXP_TIME])

for day in ["Day 2", "Day 3"]:
    common_times &= set(experiments[day][EXP_TIME])

common_times = sorted(common_times)

# Keep times covered by the simulation
common_times = [
    t for t in common_times
    if sim[SIM_TIME].min() <= t <= sim[SIM_TIME].max()
]

if not common_times:
    raise ValueError(
        "No common experimental times were found across all three days "
        "within the simulation time range. Check the elapsed-time columns."
    )

# ============================================================
# 6. BUILD COMPARISON TABLE
# ============================================================

comparison = pd.DataFrame({
    "Elapsed time (min)": common_times
})

# Interpolate simulation only at the common measurement times
comparison["Simulation (°C)"] = np.interp(
    common_times,
    sim[SIM_TIME],
    sim[SIM_TEMP]
)

# Add measured temperatures for each day
for day, df in experiments.items():

    lookup = df.set_index(EXP_TIME)[EXP_TEMP]

    comparison[f"{day} (°C)"] = lookup.reindex(common_times).to_numpy()

# ============================================================
# 7. CALCULATE VALIDATION METRICS FOR EACH DAY
# ============================================================

metrics = []

for day in experiments:

    measured = comparison[f"{day} (°C)"].to_numpy()
    predicted = comparison["Simulation (°C)"].to_numpy()

    error = predicted - measured

    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))
    mbe = np.mean(error)

    nonzero = measured != 0

    mape = (
        np.mean(np.abs(error[nonzero] / measured[nonzero])) * 100
        if np.any(nonzero)
        else np.nan
    )

    metrics.append({
        "Experimental Day": day,
        "Matched observations": len(measured),
        "MAE (°C)": mae,
        "RMSE (°C)": rmse,
        "Mean Bias Error (°C)": mbe,
        "MAPE (%)": mape
    })

metrics_df = pd.DataFrame(metrics)

# ============================================================
# 8. GROUPED BAR CHART
# ============================================================

series = [
    "Simulation (°C)",
    "Day 1 (°C)",
    "Day 2 (°C)",
    "Day 3 (°C)"
]

x = np.arange(len(comparison))
bar_width = 0.20

fig, ax = plt.subplots(figsize=(15, 7))

for i, column in enumerate(series):

    offset = (i - 1.5) * bar_width

    ax.bar(
        x + offset,
        comparison[column],
        width=bar_width,
        label=column.replace(" (°C)", "")
    )

ax.set_xlabel("Elapsed time (min)", fontsize=11)
ax.set_ylabel("Absorber plate temperature (°C)", fontsize=11)

ax.set_title(
    "Aluminium Solar Box Cooker:\n"
    "Simulation vs Experimental Results for Three Testing Days",
    fontsize=14
)

ax.set_xticks(x)
ax.set_xticklabels(
    [f"{t:g}" for t in common_times],
    rotation=45
)

ax.legend(title="Data series")
ax.grid(axis="y", linestyle="--", alpha=0.35)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "Simulation_vs_Three_Days_Bar_Chart.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

# ============================================================
# 9. MULTI-LINE TEMPERATURE COMPARISON
# ============================================================

fig, ax = plt.subplots(figsize=(12, 7))

for column in series:

    ax.plot(
        comparison["Elapsed time (min)"],
        comparison[column],
        marker="o",
        linewidth=2,
        markersize=4,
        label=column.replace(" (°C)", "")
    )

ax.set_xlabel("Elapsed time (min)")
ax.set_ylabel("Absorber plate temperature (°C)")

ax.set_title(
    "Temperature Profile: Simulation and Three Experimental Days"
)

ax.legend()
ax.grid(True, linestyle="--", alpha=0.35)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "Simulation_vs_Three_Days_Line_Graph.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

# ============================================================
# 10. SAVE TABLES
# ============================================================

comparison.to_csv(
    OUTPUT_DIR / "All_Days_Matched_Temperature_Data.csv",
    index=False
)

metrics_df.to_csv(
    OUTPUT_DIR / "All_Days_Validation_Metrics.csv",
    index=False
)

# ============================================================
# 11. DISPLAY RESULTS
# ============================================================

print("\n==============================================")
print("SIMULATION VS THREE EXPERIMENTAL DAYS")
print("==============================================")

print(f"Common measurement points: {len(comparison)}")

print("\nVALIDATION METRICS")
print(metrics_df.round(3).to_string(index=False))

print("\nOUTPUT FILES")
print("----------------------------------------------")

for file in OUTPUT_DIR.iterdir():
    if file.is_file():
        print(f"{file.name}  |  {file.stat().st_size:,} bytes")

print("\nCOMPARISON COMPLETED SUCCESSFULLY.")
