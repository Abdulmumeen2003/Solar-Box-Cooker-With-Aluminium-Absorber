# Field Test Results

This directory stores figures generated from the experimental CSV files in the parent `Field test/` folder.

- `Day1_Temperature_Humidity.png`, `Day2_Temperature_Humidity.png`, `Day3_Temperature_Humidity.png` — day-specific plots, where available.
- `Day1_Day2_Day3_Comparison.png` — comparison of the three test days.

To regenerate the comparison, run `python ../compare_days.py` from this directory or run `compare_days.py` from the parent folder. The script writes its output to this directory.

Figures are visual summaries of the supplied experimental readings; consult the original CSV files for the underlying values.
