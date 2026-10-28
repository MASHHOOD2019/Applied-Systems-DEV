"""Request/response models for the telemetry API."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ReadingIn(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=64,
                           description="e.g. temp-01, pressure-02, vibration-01")
    value: float
    unit: str = Field(..., min_length=1, max_length=16,
                      description="e.g. C, kPa, mm/s")
    recorded_at: str | None = None

    def timestamp(self) -> str:
        if self.recorded_at:
            return self.recorded_at
        return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ReadingOut(ReadingIn):
    id: int
