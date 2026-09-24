from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models.telemetry import OperatingState, VehicleState

def test_moving_vehicle_with_positive_speed_is_valid():
    vehicle = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime.now(timezone.utc),
        operating_state=OperatingState.MOVING,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=35.0,
        fuel_level_pct=75.0,
        engine_temp_f=190.0,
        heading=90.0,
    )

    assert vehicle.operating_state == OperatingState.MOVING
    assert vehicle.speed_mph == 35.0

def test_moving_vehicle_with_zero_speed_is_invalid():
    with pytest.raises(ValidationError):
        VehicleState(
            vehicle_id="VEH-1001",
            driver_id="DRV-5001",
            timestamp=datetime.now(timezone.utc),
            operating_state=OperatingState.MOVING,
            latitude=34.05,
            longitude=-118.25,
            speed_mph=0,
            fuel_level_pct=75.0,
            engine_temp_f=190.0,
            heading=90.0,
        )