from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# CSV files and output folder are alongside this script
BASE_DIR = Path(__file__).resolve().parent
FILES = {
    "Day 1": BASE_DIR / "day1_30min.csv",
    "Day 2": BASE_DIR / "day2_30min.csv",
    "Day 3": BASE_DIR / "day3_30min.csv",
}
OUTPUT_DIR = BASE_DIR / "Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Change these values if your CSV headers differ
COLUMN_MAP = {
    "time": "Elapsed time (min)",
    "plate": "Plate (°C)",
    "ambient": "Ambient (°C)",
    "humidity": "Humidity",
}

# Load and check each file
data = {}
for day, path in FILES.items():
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path.name} in {BASE_DIR}")

    df = pd.read_csv(path)

    missing = [col for col in COLUMN_MAP.values() if col not in df.columns]
    if missing:
        raise ValueError(
            f"{path.name} is missing columns: {missing}\n"
            f"Columns found: {list(df.columns)}"
        )

    for col in COLUMN_MAP.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=list(COLUMN_MAP.values()))
    df = df.sort_values(COLUMN_MAP["time"])

    data[day] = df

# Three aligned panels; each panel has one unit and compares all days
fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    figsize=(11, 10),
    sharex=True
)

series = [
    ("plate", "Absorber plate temperature (°C)"),
    ("ambient", "Ambient temperature (°C)"),
    ("humidity", "Relative humidity (%)"),
]

for ax, (key, ylabel) in zip(axes, series):
    column = COLUMN_MAP[key]

    for day, df in data.items():
        ax.plot(
            df[COLUMN_MAP["time"]],
            df[column],
            marker="o",
            markersize=3,
            linewidth=1.8,
            label=day
        )

    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend()

axes[-1].set_xlabel("Elapsed time (min)")
fig.suptitle(
    "Comparison of Solar Box Cooker Experimental Data: Days 1–3",
    fontsize=14
)
fig.tight_layout()

output_file = OUTPUT_DIR / "Day1_Day2_Day3_Comparison.png"
fig.savefig(output_file, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Comparison chart saved to: {output_file}")