from datetime import timedelta
from math import cos, radians, sin

from telemetry_engine.models.vehicle_state import OperatingState, VehicleState

_ALLOWED_TRANSITIONS = {
    OperatingState.PARKED: {
        OperatingState.PARKED,
        OperatingState.IDLE,
    },
    OperatingState.IDLE: {
        OperatingState.PARKED,
        OperatingState.IDLE,
        OperatingState.MOVING,
    },
    OperatingState.MOVING: {
        OperatingState.IDLE,
        OperatingState.MOVING,
    },
}

_IDLE_FUEL_BURN_PCT_PER_HOUR = 0.6
_MOVING_FUEL_BURN_PCT_PER_HOUR = 6.0

_PARKED_TARGET_ENGINE_TEMP_F = 70.0
_IDLE_TARGET_ENGINE_TEMP_F = 190.0
_MOVING_TARGET_ENGINE_TEMP_F = 195.0

_ENGINE_TEMP_CHANGE_F_PER_SECOND = 0.2

_MILES_PER_DEGREE_LATITUDE = 69.0

class InvalidStateTransitionError(ValueError):
    """Raised when an operating-state transition is not allowed."""

def _calculate_next_fuel_level(
    current_fuel_level_pct: float,
    operating_state: OperatingState,
    step_seconds: int,
) -> float:
    if operating_state == OperatingState.PARKED:
        burn_rate =  0
    elif operating_state == OperatingState.IDLE:
        burn_rate = _IDLE_FUEL_BURN_PCT_PER_HOUR
    elif operating_state == OperatingState.MOVING:
        burn_rate =  _MOVING_FUEL_BURN_PCT_PER_HOUR
    else:
        raise ValueError(f"Unsupported operating state: {operating_state}")
    fuel_burned = burn_rate * (step_seconds / 3600)
    return  max(0.0, current_fuel_level_pct - fuel_burned)

def _calculate_next_engine_temp(
    current_temp_f: float,
    operating_state: OperatingState,
    step_seconds: int,
) -> float:
    if operating_state == OperatingState.PARKED:
        target_temp = _PARKED_TARGET_ENGINE_TEMP_F
    elif operating_state == OperatingState.IDLE:
        target_temp = _IDLE_TARGET_ENGINE_TEMP_F
    elif operating_state == OperatingState.MOVING:
        target_temp = _MOVING_TARGET_ENGINE_TEMP_F
    else:
        raise ValueError(f"Unsupported operating state: {operating_state}")
    max_temp_change = (
        _ENGINE_TEMP_CHANGE_F_PER_SECOND * step_seconds
    )
    if current_temp_f < target_temp:
        return min(target_temp, current_temp_f + max_temp_change)
    elif current_temp_f > target_temp:
        return max(target_temp, current_temp_f - max_temp_change)
    else:
        return current_temp_f

def _calculate_next_position(
    latitude: float,
    longitude: float,
    speed_mph: float,
    heading: float,
    operating_state: OperatingState,
    step_seconds: int,
) -> tuple[float, float]:
    if operating_state != OperatingState.MOVING:
        return latitude, longitude
    distance_miles = speed_mph * (step_seconds / 3600)
    heading_radians = radians(heading)
    north_south_miles = distance_miles * cos(heading_radians)
    east_west_miles = distance_miles * sin(heading_radians)

    latitude_change = (
        north_south_miles / _MILES_PER_DEGREE_LATITUDE
    )
    new_latitude = latitude + latitude_change

    miles_per_degree_longitude = (
        _MILES_PER_DEGREE_LATITUDE
        * cos(radians(latitude))
    )
    longitude_change = (
        east_west_miles / miles_per_degree_longitude
    )
    new_longitude = longitude + longitude_change
    return new_latitude, new_longitude
        
def is_valid_transition(current_state: OperatingState, next_state: OperatingState) -> bool:
    return next_state in _ALLOWED_TRANSITIONS[current_state]

def step_vehicle_state(
    current_state: VehicleState,
    next_state: OperatingState,
    next_speed_mph: float,
    step_seconds: int = 5,
) -> VehicleState:
    if not is_valid_transition(
        current_state.operating_state,
        next_state,
    ):
        raise InvalidStateTransitionError(
            f"Invalid operating state transition: "
            f"{current_state.operating_state.value} -> {next_state.value}"
        )
    if step_seconds <= 0:
        raise ValueError("step_seconds must be greater than 0")
    next_vehicle_data = current_state.model_dump()
    next_vehicle_data["timestamp"] = (
        current_state.timestamp + timedelta(seconds=step_seconds)
    )
    next_vehicle_data["operating_state"] = next_state
    next_vehicle_data["speed_mph"] = next_speed_mph
    next_vehicle_data["fuel_level_pct"] = _calculate_next_fuel_level(
        current_state.fuel_level_pct,
        next_state,
        step_seconds,
    )
    next_vehicle_data["engine_temp_f"] = _calculate_next_engine_temp(
        current_state.engine_temp_f,
        next_state,
        step_seconds,
    )
    next_vehicle_data["latitude"], next_vehicle_data["longitude"] = _calculate_next_position(
        latitude=current_state.latitude,
        longitude=current_state.longitude,
        speed_mph=next_speed_mph,
        heading=current_state.heading,
        operating_state=next_state,
        step_seconds=step_seconds,
    )
    return VehicleState(**next_vehicle_data)