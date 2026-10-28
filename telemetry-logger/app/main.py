"""Telemetry Logger API.

Devices (or the bundled simulator) POST readings; the dashboard and any
other client GET them back. The API serves the dashboard itself, so the
whole system runs from one command: `uvicorn app.main:app --reload`.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import database
from app.models import ReadingIn

app = FastAPI(title="Telemetry Logger",
              description="Local telemetry ingestion + dashboard API")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup() -> None:
    database.init_db()


@app.get("/")
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/readings", status_code=201)
def add_reading(reading: ReadingIn):
    reading_id = database.insert_reading(
        reading.sensor_id, reading.value, reading.unit, reading.timestamp()
    )
    return {"id": reading_id, "status": "stored"}


@app.get("/api/readings")
def list_readings(limit: int = 100):
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be 1-1000")
    return database.fetch_recent(limit)


@app.get("/api/sensors/{sensor_id}/history")
def sensor_history(sensor_id: str, limit: int = 50):
    return database.fetch_sensor_history(sensor_id, limit)


@app.get("/api/stats")
def stats():
    return database.fetch_stats()
