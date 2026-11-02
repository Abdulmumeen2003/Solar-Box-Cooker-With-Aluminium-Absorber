"""
Solar Box Cooker Monitoring Dashboard
Reads real sensor data from an Arduino over USB serial and logs it to CSV.

Expected Arduino CSV:
Time_s,Probe_C,Ambient_C,Humidity_pct,Status
2.0,35.25,31.20,64.80,READINGS_VALID

Also accepts the older four-column format:
Time_s,Probe_C,Ambient_C,Humidity_pct
"""

from datetime import datetime
from pathlib import Path
import csv
import math
import threading
import time

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import serial
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output


# ------------------------- USER SETTINGS -------------------------
SERIAL_PORT = "COM5"
BAUD_RATE = 9600
SERIAL_TIMEOUT_SECONDS = 0.15
UPDATE_INTERVAL_MS = 2000
MAX_DISPLAY_ROWS = 200

# Keep False for real hardware. True is only for testing the dashboard.
SIMULATION_MODE = False
# -----------------------------------------------------------------


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SESSION_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_PATH = DATA_DIR / f"cooker_data_{SESSION_STAMP}.csv"
CSV_COLUMNS = [
    "Timestamp",
    "Time_s",
    "Thermocouple_C",
    "Ambient_C",
    "Humidity_pct",
    "Status",
]

rows = []
rows_lock = threading.Lock()
serial_lock = threading.Lock()
serial_connection = None
last_serial_error = ""
last_received_time = None
valid_line_count = 0
ignored_line_count = 0
sample_number = 0
start_time = time.time()


def create_csv():
    """Create this session's CSV file and write its header."""
    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()


def number_or_none(value):
    """Convert a numeric field to float; sensor error markers become None."""
    value = value.strip()
    if value.upper() in {"", "ERROR", "NAN", "NA", "N/A", "NULL", "NONE"}:
        return None
    try:
        result = float(value)
        if not math.isfinite(result):
            return None
        return result
    except (TypeError, ValueError):
        return None


def parse_arduino_line(line):
    """
    Parse a single Arduino CSV row.
    Accepts 4 or 5 fields:
      elapsed, probe, ambient, humidity
      elapsed, probe, ambient, humidity, status
    Returns a normalized dictionary, or None for headers/messages.
    """
    line = line.strip().lstrip("\ufeff")
    if not line:
        return None

    lower_line = line.lower()
    if lower_line.startswith("time_s,"):
        return None
    if lower_line.startswith("solar box cooker"):
        return None

    fields = [field.strip() for field in line.split(",")]
    if len(fields) not in (4, 5):
        return None

    elapsed = number_or_none(fields[0])
    if elapsed is None:
        return None

    probe = number_or_none(fields[1])
    ambient = number_or_none(fields[2])
    humidity = number_or_none(fields[3])
    status = fields[4] if len(fields) == 5 and fields[4] else "READINGS_VALID"

    # Do not silently label invalid sensor data as valid.
    if any(value is None for value in (probe, ambient, humidity)):
        if status.upper() == "READINGS_VALID":
            status = "SENSOR_ERROR"

    return {
        "Timestamp": datetime.now().isoformat(timespec="seconds"),
        "Time_s": elapsed,
        "Thermocouple_C": probe,
        "Ambient_C": ambient,
        "Humidity_pct": humidity,
        "Status": status,
    }


def open_serial():
    """Open the configured Arduino serial port if it is not already open."""
    global serial_connection, last_serial_error
    if SIMULATION_MODE:
        return True

    with serial_lock:
        if serial_connection is not None and serial_connection.is_open:
            return True

        try:
            serial_connection = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUD_RATE,
                timeout=SERIAL_TIMEOUT_SECONDS,
            )
            # Opening an Arduino serial port often resets the board.
            time.sleep(2.0)
            serial_connection.reset_input_buffer()
            last_serial_error = ""
            print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
            return True
        except (serial.SerialException, OSError) as exc:
            serial_connection = None
            last_serial_error = str(exc)
            return False


def close_serial():
    """Close serial safely."""
    global serial_connection
    with serial_lock:
        if serial_connection is not None:
            try:
                if serial_connection.is_open:
                    serial_connection.close()
            except (serial.SerialException, OSError):
                pass
        serial_connection = None


def write_row(row):
    """Append one accepted sensor reading to the CSV file."""
    with CSV_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writerow(row)


def read_serial_rows():
    """Read available serial lines, parse valid data, and persist them."""
    global last_serial_error, last_received_time, valid_line_count, ignored_line_count

    if SIMULATION_MODE:
        return

    if not open_serial():
        return

    new_rows = []
    try:
        with serial_lock:
            if serial_connection is None or not serial_connection.is_open:
                return

            # Read only lines already waiting; timeout prevents long dashboard stalls.
            while serial_connection.in_waiting:
                raw = serial_connection.readline()
                if not raw:
                    break
                line = raw.decode("utf-8", errors="replace").strip()
                parsed = parse_arduino_line(line)

                if parsed is None:
                    ignored_line_count += 1
                    # Useful diagnostics without flooding the terminal.
                    if ignored_line_count <= 5:
                        print(f"Ignored serial line: {line!r}")
                    continue

                new_rows.append(parsed)

        if new_rows:
            with rows_lock:
                rows.extend(new_rows)
                if len(rows) > MAX_DISPLAY_ROWS:
                    del rows[:-MAX_DISPLAY_ROWS]

            for row in new_rows:
                write_row(row)
            last_received_time = datetime.now()
            valid_line_count += len(new_rows)
            last_serial_error = ""

    except (serial.SerialException, OSError) as exc:
        last_serial_error = str(exc)
        close_serial()


def add_simulated_row():
    """Optional clearly labelled demo data; disabled by default."""
    global sample_number, last_received_time, valid_line_count
    sample_number += 1
    elapsed = time.time() - start_time
    probe = 35.0 + 0.15 * sample_number
    ambient = 30.5 + 0.03 * sample_number
    humidity = 65.0 - 0.04 * sample_number
    row = {
        "Timestamp": datetime.now().isoformat(timespec="seconds"),
        "Time_s": round(elapsed, 1),
        "Thermocouple_C": round(probe, 2),
        "Ambient_C": round(ambient, 2),
        "Humidity_pct": round(humidity, 2),
        "Status": "SIMULATED",
    }
    with rows_lock:
        rows.append(row)
        if len(rows) > MAX_DISPLAY_ROWS:
            del rows[:-MAX_DISPLAY_ROWS]
    write_row(row)
    last_received_time = datetime.now()
    valid_line_count += 1


def snapshot_rows():
    with rows_lock:
        return [dict(row) for row in rows]


def make_empty_figure(title, y_title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font={"color": "#E5E7EB"},
        xaxis_title="Elapsed time (s)",
        yaxis_title=y_title,
        margin={"l": 45, "r": 20, "t": 55, "b": 45},
    )
    fig.add_annotation(
        text="Waiting for valid Arduino readings…",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 14, "color": "#9CA3AF"},
    )
    return fig


def make_line_figure(data, column, title, y_title, line_color):
    valid = [row for row in data if row.get(column) is not None]
    if not valid:
        return make_empty_figure(title, y_title)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[row["Time_s"] for row in valid],
            y=[row[column] for row in valid],
            mode="lines+markers",
            name=title,
            line={"color": line_color, "width": 3},
            marker={"size": 6},
            hovertemplate="%{x:.1f} s<br>%{y:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font={"color": "#E5E7EB"},
        xaxis_title="Elapsed time (s)",
        yaxis_title=y_title,
        margin={"l": 45, "r": 20, "t": 55, "b": 45},
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="#273449")
    fig.update_yaxes(gridcolor="#273449")
    return fig


def make_3d_figure(data):
    valid = [
        row for row in data
        if row.get("Thermocouple_C") is not None
        and row.get("Ambient_C") is not None
        and row.get("Humidity_pct") is not None
    ]
    if not valid:
        fig = go.Figure()
        fig.update_layout(
            title="3D Sensor Relationship",
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font={"color": "#E5E7EB"},
            margin={"l": 0, "r": 0, "t": 55, "b": 0},
        )
        fig.add_annotation(
            text="Waiting for valid readings…",
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font={"size": 14, "color": "#9CA3AF"},
        )
        return fig

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=[r["Thermocouple_C"] for r in valid],
                y=[r["Ambient_C"] for r in valid],
                z=[r["Humidity_pct"] for r in valid],
                mode="lines+markers",
                marker={
                    "size": 5,
                    "color": [r["Time_s"] for r in valid],
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {"title": "Time (s)"},
                },
                line={"color": "#38BDF8", "width": 3},
                text=[r["Timestamp"] for r in valid],
                hovertemplate=(
                    "Probe: %{x:.2f} °C<br>"
                    "Ambient: %{y:.2f} °C<br>"
                    "Humidity: %{z:.2f}%<br>"
                    "%{text}<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(
        title="3D Sensor Relationship",
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font={"color": "#E5E7EB"},
        scene={
            "xaxis_title": "Probe (°C)",
            "yaxis_title": "Ambient (°C)",
            "zaxis_title": "Humidity (%)",
            "bgcolor": "#111827",
        },
        margin={"l": 0, "r": 0, "t": 55, "b": 0},
    )
    return fig


def status_message():
    if SIMULATION_MODE:
        return "DEMO MODE — simulated values, not live sensor data"

    if last_serial_error:
        return f"SERIAL ERROR on {SERIAL_PORT}: {last_serial_error}"

    if valid_line_count > 0 and last_received_time:
        age = (datetime.now() - last_received_time).total_seconds()
        if age <= 8:
            return (
                f"CONNECTED · {SERIAL_PORT} · LIVE DATA · "
                f"{valid_line_count} readings received · "
                f"Last reading {age:.0f}s ago"
            )
        return (
            f"CONNECTED · {SERIAL_PORT} · NO NEW DATA for {age:.0f}s · "
            f"{valid_line_count} readings received in this session"
        )

    if serial_connection is not None and serial_connection.is_open:
        return (
            f"CONNECTED to {SERIAL_PORT}, but no valid sensor rows received yet. "
            f"Check Arduino CSV output. Ignored lines: {ignored_line_count}."
        )

    return f"Waiting to connect to {SERIAL_PORT} at {BAUD_RATE} baud."


app = Dash(__name__)
app.title = "Solar Box Cooker Monitoring"

CARD_STYLE = {
    "backgroundColor": "#1F2937",
    "border": "1px solid #374151",
    "borderRadius": "12px",
    "padding": "16px",
    "minWidth": "0",
}

app.layout = html.Div(
    style={
        "backgroundColor": "#0B1120",
        "color": "#E5E7EB",
        "minHeight": "100vh",
        "padding": "24px",
        "fontFamily": "Arial, sans-serif",
    },
    children=[
        html.Div(
            [
                html.H1(
                    "Solar Box Cooker Monitoring System",
                    style={"marginBottom": "6px"},
                ),
                html.Div(
                    "Live temperature, humidity and data logging",
                    style={"color": "#9CA3AF", "marginBottom": "14px"},
                ),
                html.Div(
                    id="connection-status",
                    children="Starting serial connection…",
                    style={
                        "backgroundColor": "#172033",
                        "border": "1px solid #334155",
                        "borderRadius": "8px",
                        "padding": "12px 14px",
                        "marginBottom": "20px",
                    },
                ),
            ]
        ),
        html.Div(
            id="metric-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(190px, 1fr))",
                "gap": "14px",
                "marginBottom": "18px",
            },
        ),
        html.Div(
            [
                dcc.Graph(id="probe-chart", config={"displaylogo": False}),
                dcc.Graph(id="ambient-chart", config={"displaylogo": False}),
                dcc.Graph(id="humidity-chart", config={"displaylogo": False}),
                dcc.Graph(id="three-d-chart", config={"displaylogo": False}),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(330px, 1fr))",
                "gap": "14px",
            },
        ),
        html.Div(
            [
                html.H3("Recent Sensor Readings"),
                dash_table.DataTable(
                    id="readings-table",
                    columns=[
                        {"name": "Timestamp", "id": "Timestamp"},
                        {"name": "Time (s)", "id": "Time_s", "type": "numeric"},
                        {"name": "Probe (°C)", "id": "Thermocouple_C", "type": "numeric"},
                        {"name": "Ambient (°C)", "id": "Ambient_C", "type": "numeric"},
                        {"name": "Humidity (%)", "id": "Humidity_pct", "type": "numeric"},
                        {"name": "Status", "id": "Status"},
                    ],
                    data=[],
                    page_size=10,
                    sort_action="native",
                    style_table={"overflowX": "auto"},
                    style_header={
                        "backgroundColor": "#1F2937",
                        "color": "#F9FAFB",
                        "fontWeight": "bold",
                        "border": "1px solid #374151",
                    },
                    style_cell={
                        "backgroundColor": "#111827",
                        "color": "#E5E7EB",
                        "border": "1px solid #374151",
                        "padding": "10px",
                        "textAlign": "left",
                        "minWidth": "90px",
                        "maxWidth": "240px",
                        "whiteSpace": "normal",
                    },
                    style_data_conditional=[
                        {
                            "if": {"filter_query": '{Status} = "SENSOR_ERROR"', "column_id": "Status"},
                            "color": "#FCA5A5",
                        },
                        {
                            "if": {"filter_query": '{Status} = "READINGS_VALID"', "column_id": "Status"},
                            "color": "#86EFAC",
                        },
                    ],
                ),
                html.Div(
                    f"CSV logging to: {CSV_PATH}",
                    style={"color": "#9CA3AF", "fontSize": "12px", "marginTop": "12px"},
                ),
            ],
            style={**CARD_STYLE, "marginTop": "18px"},
        ),
        dcc.Interval(id="refresh-interval", interval=UPDATE_INTERVAL_MS, n_intervals=0),
    ],
)


def metric_card(title, value, unit, note):
    return html.Div(
        [
            html.Div(title, style={"color": "#9CA3AF", "fontSize": "13px"}),
            html.Div(
                value,
                style={"fontSize": "30px", "fontWeight": "bold", "margin": "8px 0"},
            ),
            html.Div(unit, style={"color": "#CBD5E1", "fontSize": "13px"}),
            html.Div(note, style={"color": "#64748B", "fontSize": "11px", "marginTop": "8px"}),
        ],
        style=CARD_STYLE,
    )


@app.callback(
    Output("connection-status", "children"),
    Output("metric-cards", "children"),
    Output("probe-chart", "figure"),
    Output("ambient-chart", "figure"),
    Output("humidity-chart", "figure"),
    Output("three-d-chart", "figure"),
    Output("readings-table", "data"),
    Input("refresh-interval", "n_intervals"),
)
def update_dashboard(_n_intervals):
    if SIMULATION_MODE:
        add_simulated_row()
    else:
        read_serial_rows()

    data = snapshot_rows()
    latest = data[-1] if data else None

    if latest:
        probe_value = (
            f'{latest["Thermocouple_C"]:.2f}'
            if latest["Thermocouple_C"] is not None else "—"
        )
        ambient_value = (
            f'{latest["Ambient_C"]:.2f}'
            if latest["Ambient_C"] is not None else "—"
        )
        humidity_value = (
            f'{latest["Humidity_pct"]:.2f}'
            if latest["Humidity_pct"] is not None else "—"
        )
        time_value = f'{latest["Time_s"]:.1f}'
        cards = [
            metric_card("Cooker Probe Temperature", probe_value, "°C", "MAX6675 thermocouple"),
            metric_card("Ambient Temperature", ambient_value, "°C", "DHT22 sensor"),
            metric_card("Relative Humidity", humidity_value, "%", "DHT22 sensor"),
            metric_card("Elapsed Time", time_value, "seconds", f'Status: {latest["Status"]}'),
        ]
    else:
        cards = [
            metric_card("Cooker Probe Temperature", "—", "°C", "Waiting for Arduino data"),
            metric_card("Ambient Temperature", "—", "°C", "Waiting for Arduino data"),
            metric_card("Relative Humidity", "—", "%", "Waiting for Arduino data"),
            metric_card("Elapsed Time", "—", "seconds", "No readings received yet"),
        ]

    recent = list(reversed(data[-MAX_DISPLAY_ROWS:]))
    table_data = [
        {
            **row,
            "Time_s": round(row["Time_s"], 2) if row["Time_s"] is not None else None,
            "Thermocouple_C": (
                round(row["Thermocouple_C"], 2)
                if row["Thermocouple_C"] is not None else None
            ),
            "Ambient_C": round(row["Ambient_C"], 2) if row["Ambient_C"] is not None else None,
            "Humidity_pct": (
                round(row["Humidity_pct"], 2)
                if row["Humidity_pct"] is not None else None
            ),
        }
        for row in recent
    ]

    return (
        status_message(),
        cards,
        make_line_figure(data, "Thermocouple_C", "Cooker Probe Temperature", "Temperature (°C)", "#F97316"),
        make_line_figure(data, "Ambient_C", "Ambient Temperature", "Temperature (°C)", "#38BDF8"),
        make_line_figure(data, "Humidity_pct", "Relative Humidity", "Humidity (%)", "#A78BFA"),
        make_3d_figure(data),
        table_data,
    )


def main():
    create_csv()
    print("\nSolar Box Cooker Monitoring Dashboard")
    print(f"Mode: {'SIMULATION (DEMO DATA)' if SIMULATION_MODE else 'REAL HARDWARE'}")
    print(f"CSV file: {CSV_PATH}")
    if not SIMULATION_MODE:
        print(f"Arduino serial port: {SERIAL_PORT}")
        print(f"Baud rate: {BAUD_RATE}")
        if not open_serial():
            print(f"WARNING: Could not open {SERIAL_PORT}: {last_serial_error}")
            print("Close PlatformIO Serial Monitor and check the USB connection.")
    else:
        print("WARNING: Dashboard is using simulated values, not actual sensors.")
    print("Open http://127.0.0.1:8050 in your browser.")
    print("Press Ctrl+C in this terminal to stop.\n")

    try:
        app.run(host="127.0.0.1", port=8050, debug=False)
    except KeyboardInterrupt:
        print("\nDashboard interrupted.")
    finally:
        close_serial()
        print("Dashboard stopped. Serial connection closed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        close_serial()
        print("\nDashboard stopped. Serial connection closed.")
