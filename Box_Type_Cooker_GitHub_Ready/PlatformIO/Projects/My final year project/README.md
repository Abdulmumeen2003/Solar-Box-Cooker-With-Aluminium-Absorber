# Solar Box Cooker Monitoring and Data Logging

Arduino Uno firmware and a Python dashboard for acquiring absorber-probe temperature, ambient temperature and relative humidity during solar box cooker tests.

## System overview

The Arduino reads:
- A MAX6675 thermocouple interface for the probe temperature.
- A DHT22 sensor for ambient temperature and relative humidity.

It streams comma-separated readings over USB serial at 9600 baud. `logger.py` reads the serial stream, validates records, writes timestamped CSV session files into `data/`, and displays live plots and a readings table in a Dash web dashboard.

## Hardware

- Arduino Uno (ATmega328P)
- MAX6675 thermocouple amplifier and compatible K-type thermocouple
- DHT22 temperature/humidity sensor
- USB cable for serial connection

### Wiring used by `src/main.cpp`

| Component | Arduino Uno |
|---|---|
| DHT22 DATA | D2 |
| DHT22 VCC / GND | 5V / GND |
| MAX6675 CLK | D10 |
| MAX6675 CS | D9 |
| MAX6675 SO | D11 |
| MAX6675 VCC / GND | As specified by module manufacturer |

The firmware in this repository does not currently implement fan or buzzer control. Use the actual `src/main.cpp` pin assignments as the source of truth; older wiring notes describing D13/D10/D12, a relay or buzzer do not match this firmware.

## Software requirements

- VS Code with PlatformIO IDE extension
- PlatformIO AVR platform and Arduino framework (resolved by PlatformIO)
- Python 3
- Python packages: `pyserial`, `pandas`, `plotly`, `dash`

Install Python dependencies:

```bash
python -m pip install pyserial pandas plotly dash
```

## Build and upload firmware

Open this directory in VS Code, then use the PlatformIO build/upload actions, or run:

```bash
pio run
pio run --target upload
pio device monitor --baud 9600
```

Check `platformio.ini` and change `upload_port = COM5` to the correct port on your computer. Also update `SERIAL_PORT` in `logger.py` to the same port. Close the serial monitor before starting the Python logger if the port is already in use.

## Run the dashboard and logger

From this directory:

```bash
python logger.py
```

The dashboard runs locally. Open the local address printed by Dash in your browser (the current script uses the Dash development server). Stop it with `Ctrl+C`.

The logger is configured for real hardware by default (`SIMULATION_MODE = False`). Set `SIMULATION_MODE = True` only when you intentionally want clearly labelled demo readings without connected hardware.

Each run creates a new timestamped CSV file under `data/`. The existing `day1_30min.csv`, `day2_30min.csv` and `day3_30min.csv` are supplied datasets, not live session files.

## Serial data format

Firmware output header:

```text
Time_s,Probe_C,Ambient_C,Humidity_pct,Status
```

The logger also accepts the older four-field format without `Status`. Sensor failures are emitted as `ERROR` and labelled with a status such as `DHT_ERROR` or `THERMOCOUPLE_ERROR`.

## Data folder

`data/` contains the supplied three-day experimental CSV files. Newly recorded session CSV files are generated there by `logger.py`.

## Notes

- Confirm the correct COM port in Windows Device Manager.
- The MAX6675 requires a suitable thermocouple and correct polarity.
- Place the thermocouple junction firmly at the intended absorber-plate measurement location.
- Allow the DHT22 to settle and avoid placing it where direct solar heating distorts ambient-air readings.
- Calibrate/check sensors and document sampling intervals before using measurements in formal analysis.
- The dashboard uses a development server and is intended for local research/testing, not public production deployment.
