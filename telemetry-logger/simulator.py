"""Fake sensor traffic generator for demoing the dashboard.

Simulates three industrial sensors (temperature, pressure, vibration)
and POSTs a reading every 2 seconds. Run it in a second terminal while
the API is running:  python simulator.py
"""

import random
import time

import httpx

API_URL = "http://127.0.0.1:8000/api/readings"

SENSORS = [
    ("temp-01", "C", lambda: round(random.uniform(62.0, 78.0), 2)),
    ("pressure-02", "kPa", lambda: round(random.uniform(180.0, 220.0), 1)),
    ("vibration-01", "mm/s", lambda: round(random.uniform(0.8, 3.4), 2)),
]


def main() -> None:
    print("Simulator running — Ctrl+C to stop.")
    with httpx.Client(timeout=5) as client:
        while True:
            sensor_id, unit, sampler = random.choice(SENSORS)
            payload = {"sensor_id": sensor_id, "value": sampler(), "unit": unit}
            resp = client.post(API_URL, json=payload)
            print(f"{sensor_id}: {payload['value']} {unit} -> {resp.status_code}")
            time.sleep(2)


if __name__ == "__main__":
    main()
