from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# CSV file should be in the same folder as this script
file_path = Path(__file__).parent / "day3_30min.csv"
output_path = Path(__file__).parent / "Results" / "Day3_Temperature_Humidity.png"

# Load data
df = pd.read_csv(file_path)

# Convert elapsed time to numeric values and remove incomplete rows
df["Elapsed time (min)"] = pd.to_numeric(df["Elapsed time (min)"], errors="coerce")
for column in ["Plate (°C)", "Ambient (°C)", "Humidity"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=[
    "Elapsed time (min)", "Plate (°C)", "Ambient (°C)", "Humidity"
]).sort_values("Elapsed time (min)")

# Create output folder
output_path.parent.mkdir(parents=True, exist_ok=True)

# Plot temperatures and humidity
fig, ax_temp = plt.subplots(figsize=(11, 6))

ax_temp.plot(
    df["Elapsed time (min)"], df["Plate (°C)"],
    marker="o", linewidth=2, label="Absorber plate temperature (°C)"
)
ax_temp.plot(
    df["Elapsed time (min)"], df["Ambient (°C)"],
    marker="s", linewidth=2, label="Ambient temperature (°C)"
)

ax_temp.set_xlabel("Elapsed time (min)")
ax_temp.set_ylabel("Temperature (°C)")
ax_temp.grid(True, linestyle="--", alpha=0.4)

# Second vertical axis for humidity
ax_humidity = ax_temp.twinx()
ax_humidity.plot(
    df["Elapsed time (min)"], df["Humidity"],
    marker="^", linestyle="--", linewidth=2, label="Relative humidity (%)"
)
ax_humidity.set_ylabel("Relative humidity (%)")

# Combine legends from both axes
lines1, labels1 = ax_temp.get_legend_handles_labels()
lines2, labels2 = ax_humidity.get_legend_handles_labels()
ax_temp.legend(lines1 + lines2, labels1 + labels2, loc="best")

ax_temp.set_title("Day 3: Absorber Plate Temperature, Ambient Temperature, and Humidity")
fig.tight_layout()

fig.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Chart saved to: {output_path}")