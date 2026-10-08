from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from telemetry_engine.models.vehicle_state import OperatingState, VehicleState

@pytest.mark.parametrize(
    "operating_state, speed_mph",
    [
        (OperatingState.PARKED, 0),
        (OperatingState.IDLE, 0),
        (OperatingState.MOVING, 35.0),
    ],
)
def test_valid_operating_state_speed_combinations(operating_state, speed_mph):
    vehicle = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime.now(timezone.utc),
        operating_state=operating_state,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=speed_mph,
        fuel_level_pct=75.0,
        engine_temp_f=190.0,
        heading=90.0,
    )

    assert vehicle.operating_state == operating_state
    assert vehicle.speed_mph == speed_mph

@pytest.mark.parametrize(
    "operating_state, speed_mph",
    [
        (OperatingState.PARKED, 10.0),
        (OperatingState.IDLE, 10.0),
        (OperatingState.MOVING, 0),
    ],
)
def test_invalid_operating_state_speed_combinations(operating_state, speed_mph):
    with pytest.raises(ValidationError):
        VehicleState(
            vehicle_id="VEH-1001",
            driver_id="DRV-5001",
            timestamp=datetime.now(timezone.utc),
            operating_state=operating_state,
            latitude=34.05,
            longitude=-118.25,
            speed_mph=speed_mph,
            fuel_level_pct=75.0,
            engine_temp_f=190.0,
            heading=90.0,
        )

@pytest.mark.parametrize(
    "field_name, invalid_value",
    [
        ("latitude", 91),
        ("longitude", -181),
        ("fuel_level_pct", 101),
        ("heading", 360),
    ],
)
def test_invalid_invalid_numeric_boundaries(field_name, invalid_value):
    vehicle_data = {
        "vehicle_id": "VEH-1001",
        "driver_id": "DRV-5001",
        "timestamp": datetime.now(timezone.utc),
        "operating_state": OperatingState.MOVING,
        "latitude": 34.05,
        "longitude": -118.25,
        "speed_mph": 35.0,
        "fuel_level_pct": 75.0,
        "engine_temp_f": 190.0,
        "heading": 90.0,
    }

    vehicle_data[field_name] = invalid_value

    with pytest.raises(ValidationError):
        VehicleState(**vehicle_data)
    
def test_vehicle_without_driver_is_valid():
    vehicle = VehicleState(
        vehicle_id="VEH-1001",
        driver_id=None,
        timestamp=datetime.now(timezone.utc),
        operating_state=OperatingState.MOVING,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=35.0,
        fuel_level_pct=75.0,
        engine_temp_f=190.0,
        heading=90.0,
    )
    assert vehicle.driver_id is None

def test_naive_timestamp_is_invalid():
    with pytest.raises(ValidationError):
        VehicleState(
            vehicle_id="VEH-1001",
            driver_id="DRV-5001",
            timestamp=datetime.now(),
            operating_state=OperatingState.MOVING,
            latitude=34.05,
            longitude=-118.25,
            speed_mph=35.0,
            fuel_level_pct=75.0,
            engine_temp_f=190.0,
            heading=90.0,
        )