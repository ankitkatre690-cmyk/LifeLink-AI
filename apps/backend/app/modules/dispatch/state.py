from typing import Final

EMERGENCY_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "Pending": frozenset({"Assigned", "Cancelled"}),
    "Assigned": frozenset({"InProgress", "Cancelled"}),
    "InProgress": frozenset({"Completed", "Cancelled"}),
    "Completed": frozenset(),
    "Cancelled": frozenset(),
}

ASSIGNMENT_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "Assigned": frozenset({"Accepted", "Cancelled"}),
    "Accepted": frozenset({"EnRoute", "Cancelled"}),
    "EnRoute": frozenset({"OnScene", "Cancelled"}),
    "OnScene": frozenset({"Completed", "Cancelled"}),
    "Completed": frozenset(),
    "Cancelled": frozenset(),
}

DISPATCH_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "Assigned": frozenset({"Accepted", "Cancelled"}),
    "Accepted": frozenset({"EnRoute", "Cancelled"}),
    "EnRoute": frozenset({"OnScene", "Cancelled"}),
    "OnScene": frozenset({"Completed", "Cancelled"}),
    "Completed": frozenset(),
    "Cancelled": frozenset(),
}


def _validate_transition(
    transitions: dict[str, frozenset[str]],
    current: str,
    target: str,
    entity: str,
) -> None:
    allowed = transitions.get(current)
    if allowed is None:
        raise ValueError(f"Unknown {entity} state: {current}")
    if target not in allowed:
        raise ValueError(
            f"Invalid {entity} transition: {current} -> {target}"
        )


def validate_emergency_transition(current: str, target: str) -> None:
    _validate_transition(EMERGENCY_TRANSITIONS, current, target, "emergency")


def validate_assignment_transition(current: str, target: str) -> None:
    _validate_transition(ASSIGNMENT_TRANSITIONS, current, target, "assignment")


def validate_dispatch_transition(current: str, target: str) -> None:
    _validate_transition(DISPATCH_TRANSITIONS, current, target, "dispatch")
