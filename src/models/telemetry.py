from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FleetTelemetryEvent(BaseModel):
    event_id: str
    vehicle_id: str
    driver_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed_mph: float = Field(..., ge=0, le=120)
    fuel_level_pct: float = Field(..., ge=0, le=100)
    engine_temp_f: float
    status: str  # 'IN_TRANSIT', 'IDLE', 'MAINTENANCE_REQUIRED'