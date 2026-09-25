import pytest

from app.modules.dispatch.state import validate_assignment_transition


@pytest.mark.parametrize(
    "current,target",
    [
        ("Assigned", "Accepted"),
        ("Accepted", "EnRoute"),
        ("EnRoute", "OnScene"),
        ("OnScene", "Completed"),
        ("OnScene", "Cancelled"),
    ],
)
def test_valid_assignment_transitions(current, target):
    validate_assignment_transition(current, target)


@pytest.mark.parametrize(
    "current,target",
    [
        ("Assigned", "Completed"),
        ("Completed", "Assigned"),
        ("Cancelled", "Accepted"),
    ],
)
def test_invalid_assignment_transitions(current, target):
    with pytest.raises(ValueError):
        validate_assignment_transition(current, target)
