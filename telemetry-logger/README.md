# Telemetry Logger & Dashboard

Local telemetry ingestion system: devices POST sensor readings to a
FastAPI service, readings are stored in SQLite, and a dashboard shows
live stats, per-sensor trends and recent readings. Built as the kind of
data-logging tool used in industrial and plant environments.

## Stack
Python · FastAPI · SQLite · HTML/CSS/JavaScript (no frontend framework)

## Run it
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 — the dashboard is served by the API itself.
API docs (auto-generated): http://127.0.0.1:8000/docs

## Generate demo traffic
In a second terminal:
```bash
python simulator.py
```
This simulates temperature, pressure and vibration sensors posting
every 2 seconds. Watch the dashboard update live.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/readings` | Store one reading (`sensor_id`, `value`, `unit`) |
| GET | `/api/readings?limit=100` | Recent readings, newest first |
| GET | `/api/sensors/{id}/history` | History for one sensor (chart data) |
| GET | `/api/stats` | Totals, per-sensor min/max/avg, latest values |

## Why this matters
- **Industrial relevance:** telemetry and data-logging are core to plant
  monitoring, the exact domain of industrial operations support.
- **Real backend skills:** REST design, validation (Pydantic), indexed
  queries, stats aggregation in SQL.
- **Extensible:** add alert thresholds, CSV export, or authentication
  as a next step.
