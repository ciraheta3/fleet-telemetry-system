from datetime import timedelta
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
        
class InvalidStateTransitionError(ValueError):
    """Raised when an operating-state transition is not allowed."""

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
    return VehicleState(**next_vehicle_data)