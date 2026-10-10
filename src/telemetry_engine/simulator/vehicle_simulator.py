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
    return VehicleState(**next_vehicle_data)