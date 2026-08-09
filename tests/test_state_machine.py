"""
Unit tests for MissionStateMachine in orchestrator package.
"""

import pytest
from orchestrator.state_machine import MissionStateMachine
from orchestrator.models import MissionState
from orchestrator.exceptions import StateTransitionError


def test_state_machine_valid_flow():
    sm = MissionStateMachine(initial_state=MissionState.CREATED)
    assert sm.current_state == MissionState.CREATED

    assert sm.transition_to(MissionState.READY) == MissionState.READY
    assert sm.transition_to(MissionState.PLANNING) == MissionState.PLANNING
    assert sm.transition_to(MissionState.SCHEDULED) == MissionState.SCHEDULED
    assert sm.transition_to(MissionState.EXECUTING) == MissionState.EXECUTING
    assert sm.transition_to(MissionState.EVALUATING) == MissionState.EVALUATING
    assert sm.transition_to(MissionState.LEARNING) == MissionState.LEARNING
    assert sm.transition_to(MissionState.COMPLETED) == MissionState.COMPLETED


def test_state_machine_invalid_transition():
    sm = MissionStateMachine(initial_state=MissionState.CREATED)
    with pytest.raises(StateTransitionError):
        sm.transition_to(MissionState.COMPLETED)
