import pytest
from pydantic import ValidationError
from datetime import datetime, timezone, timedelta

from telemetry_engine.simulator.vehicle_simulator import (
    InvalidStateTransitionError,
    is_valid_transition,
    step_vehicle_state,
)
from telemetry_engine.models.vehicle_state import OperatingState, VehicleState

@pytest.mark.parametrize(
    "current_state, next_state",
    [
        (OperatingState.PARKED, OperatingState.PARKED),
        (OperatingState.PARKED, OperatingState.IDLE),
        (OperatingState.IDLE, OperatingState.PARKED),
        (OperatingState.IDLE, OperatingState.IDLE),
        (OperatingState.IDLE, OperatingState.MOVING),
        (OperatingState.MOVING, OperatingState.IDLE),
        (OperatingState.MOVING, OperatingState.MOVING),
    ],
)
def test_valid_transitions(current_state, next_state):
    assert is_valid_transition(current_state, next_state) is True

@pytest.mark.parametrize(
    "current_state, next_state",
    [
        (OperatingState.PARKED, OperatingState.MOVING),
        (OperatingState.MOVING, OperatingState.PARKED),
    ],
)
def test_invalid_transitions(current_state, next_state):
    assert is_valid_transition(current_state, next_state) is False

def test_invalid_state_transition():
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id=None,
        timestamp=datetime.now(timezone.utc),
        operating_state=OperatingState.PARKED,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=0,
        fuel_level_pct=75.0,
        engine_temp_f=150.0,
        heading=90.0,
    )
    with pytest.raises(InvalidStateTransitionError):
        step_vehicle_state(
            current_state=current_state,
            next_state=OperatingState.MOVING,
            next_speed_mph=30.0,
        )

def test_parked_to_idle_updates_vehicle_state():
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=OperatingState.PARKED,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=0,
        fuel_level_pct=75.0,
        engine_temp_f=150.0,
        heading=90.0,
    )

    next_vehicle = step_vehicle_state(
        current_state=current_state,
        next_state=OperatingState.IDLE,
        next_speed_mph=0,
    )

    assert next_vehicle.vehicle_id == current_state.vehicle_id
    assert next_vehicle.driver_id == current_state.driver_id
    assert next_vehicle.operating_state == OperatingState.IDLE
    assert next_vehicle.speed_mph == 0
    assert next_vehicle.latitude == current_state.latitude
    assert next_vehicle.longitude == current_state.longitude
    assert next_vehicle.heading == current_state.heading
    assert next_vehicle.timestamp == current_state.timestamp + timedelta(seconds=5)

def test_step_rejects_invalid_resulting_vehicle_state():
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=OperatingState.IDLE,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=0,
        fuel_level_pct=75.0,
        engine_temp_f=180.0,
        heading=90.0,
    )
    with pytest.raises(ValidationError):
        step_vehicle_state(
            current_state=current_state,
            next_state=OperatingState.PARKED,
            next_speed_mph=30.0,
        )

def test_non_default_timestep():
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=OperatingState.IDLE,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=0,
        fuel_level_pct=75.0,
        engine_temp_f=180.0,
        heading=90.0,
    )
    
    next_vehicle = step_vehicle_state(
        current_state=current_state,
        next_state=OperatingState.PARKED,
        next_speed_mph=0.0,
        step_seconds=10
    )

    assert next_vehicle.timestamp == (
        current_state.timestamp + timedelta(seconds=10)
    )

def test_step_rejects_invalid_step_seconds():
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=OperatingState.IDLE,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=0,
        fuel_level_pct=75.0,
        engine_temp_f=180.0,
        heading=90.0,
    )
    with pytest.raises(ValueError):
        step_vehicle_state(
            current_state=current_state,
            next_state=OperatingState.PARKED,
            next_speed_mph=0.0,
            step_seconds=-5
        )
        
@pytest.mark.parametrize(
    "operating_state, speed_mph, expected_fuel",
    [
        (OperatingState.PARKED, 0, 75.0),
        (OperatingState.IDLE, 0, 74.99),
        (OperatingState.MOVING, 30.0, 74.90),
    ],
)
def test_fuel_changes_by_operating_state(
    operating_state,
    speed_mph,
    expected_fuel,
):
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=operating_state,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=speed_mph,
        fuel_level_pct=75.0,
        engine_temp_f=180.0,
        heading=90.0,
    )

    next_vehicle = step_vehicle_state(
        current_state=current_state,
        next_state=operating_state,
        next_speed_mph=speed_mph,
        step_seconds=60,
    )

    assert next_vehicle.fuel_level_pct == pytest.approx(expected_fuel)

@pytest.mark.parametrize(
    "operating_state, speed_mph, current_temp, expected_temp",
    [
        (OperatingState.PARKED, 0, 100.0, 99.0),
        (OperatingState.IDLE, 0, 150.0, 151.0),
        (OperatingState.MOVING, 30.0, 200.0, 199.0),
        (OperatingState.IDLE, 0, 190.0, 190.0),
        (OperatingState.IDLE, 0, 189.5, 190.0),
    ],
)
def test_engine_temperature_moves_toward_target(
    operating_state,
    speed_mph,
    current_temp,
    expected_temp,
):
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=operating_state,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=speed_mph,
        fuel_level_pct=75.0,
        engine_temp_f=current_temp,
        heading=90.0,
    )

    next_vehicle = step_vehicle_state(
        current_state=current_state,
        next_state=operating_state,
        next_speed_mph=speed_mph,
        step_seconds=5,
    )

    assert next_vehicle.engine_temp_f == pytest.approx(expected_temp)

@pytest.mark.parametrize(
    "heading, latitude_direction, longitude_direction",
    [
        (0.0, 1, 0),      # north
        (90.0, 0, 1),     # east
        (180.0, -1, 0),   # south
        (270.0, 0, -1),   # west
    ],
)
def test_moving_vehicle_updates_position_in_heading_direction(
    heading,
    latitude_direction,
    longitude_direction,
):
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=OperatingState.MOVING,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=30.0,
        fuel_level_pct=75.0,
        engine_temp_f=190.0,
        heading=heading,
    )

    next_vehicle = step_vehicle_state(
        current_state=current_state,
        next_state=OperatingState.MOVING,
        next_speed_mph=30.0,
        step_seconds=60,
    )

    if latitude_direction > 0:
        assert next_vehicle.latitude > current_state.latitude
    elif latitude_direction < 0:
        assert next_vehicle.latitude < current_state.latitude
    else:
        assert next_vehicle.latitude == pytest.approx(
            current_state.latitude
        )

    if longitude_direction > 0:
        assert next_vehicle.longitude > current_state.longitude
    elif longitude_direction < 0:
        assert next_vehicle.longitude < current_state.longitude
    else:
        assert next_vehicle.longitude == pytest.approx(
            current_state.longitude
        )

@pytest.mark.parametrize(
    "operating_state",
    [
        OperatingState.PARKED,
        OperatingState.IDLE,
    ],
)
def test_stationary_vehicle_position_does_not_change(operating_state):
    current_state = VehicleState(
        vehicle_id="VEH-1001",
        driver_id="DRV-5001",
        timestamp=datetime(
            2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc
        ),
        operating_state=operating_state,
        latitude=34.05,
        longitude=-118.25,
        speed_mph=0.0,
        fuel_level_pct=75.0,
        engine_temp_f=190.0,
        heading=0.0,
    )

    next_vehicle = step_vehicle_state(
        current_state=current_state,
        next_state=operating_state,
        next_speed_mph=0.0,
        step_seconds=60,
    )

    assert next_vehicle.latitude == current_state.latitude
    assert next_vehicle.longitude == current_state.longitude