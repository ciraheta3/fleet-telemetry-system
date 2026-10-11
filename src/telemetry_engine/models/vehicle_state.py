from pydantic import BaseModel, Field, AwareDatetime, model_validator
from enum import Enum
from typing import Self

class OperatingState(str, Enum):
    PARKED = 'PARKED'
    IDLE = 'IDLE'
    MOVING = 'MOVING'

class VehicleState(BaseModel):
    vehicle_id: str = Field(..., min_length=1)
    driver_id: str | None = Field(default=None, min_length=1) 
    timestamp: AwareDatetime
    operating_state: OperatingState
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed_mph: float = Field(..., ge=0)
    fuel_level_pct: float = Field(..., ge=0, le=100)
    engine_temp_f: float
    heading: float = Field(..., ge=0, lt=360)

    @model_validator(mode='after')
    def validate_operating_state(self) -> Self:
        if self.operating_state == OperatingState.MOVING and self.speed_mph == 0:
            raise ValueError('Speed must be greater than 0 when moving')
        
        elif self.operating_state == OperatingState.PARKED and self.speed_mph > 0:
            raise ValueError('Speed must be 0 when parked')

        elif self.operating_state == OperatingState.IDLE and self.speed_mph > 0:
            raise ValueError('Speed must be 0 when idle')

        return self