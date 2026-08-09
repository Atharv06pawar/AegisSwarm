"""
Thread-safe MissionStateMachine enforcing valid mission lifecycle state transitions.
"""

import threading
from typing import Dict, Set
from orchestrator.models import MissionState
from orchestrator.exceptions import StateTransitionError


class MissionStateMachine:
    """
    Enforces valid state transition paths across mission lifecycle states.
    """

    ALLOWED_TRANSITIONS: Dict[MissionState, Set[MissionState]] = {
        MissionState.CREATED: {MissionState.READY, MissionState.CANCELLED},
        MissionState.READY: {MissionState.PLANNING, MissionState.CANCELLED},
        MissionState.PLANNING: {MissionState.SCHEDULED, MissionState.FAILED, MissionState.CANCELLED},
        MissionState.SCHEDULED: {MissionState.EXECUTING, MissionState.CANCELLED},
        MissionState.EXECUTING: {MissionState.EVALUATING, MissionState.RECOVERING, MissionState.FAILED, MissionState.CANCELLED},
        MissionState.EVALUATING: {MissionState.LEARNING, MissionState.RECOVERING, MissionState.FAILED},
        MissionState.LEARNING: {MissionState.COMPLETED, MissionState.FAILED},
        MissionState.RECOVERING: {MissionState.EXECUTING, MissionState.FAILED, MissionState.CANCELLED},
        MissionState.FAILED: {MissionState.RECOVERING, MissionState.CANCELLED},
        MissionState.COMPLETED: set(),
        MissionState.CANCELLED: set()
    }

    def __init__(self, initial_state: MissionState = MissionState.CREATED):
        self._lock = threading.RLock()
        self._current_state = initial_state

    @property
    def current_state(self) -> MissionState:
        with self._lock:
            return self._current_state

    def transition_to(self, target_state: MissionState) -> MissionState:
        """
        Transitions state machine to target_state if allowed, else raises StateTransitionError.
        """
        with self._lock:
            allowed = self.ALLOWED_TRANSITIONS.get(self._current_state, set())
            if target_state not in allowed:
                raise StateTransitionError(
                    from_state=self._current_state.value,
                    to_state=target_state.value
                )
            self._current_state = target_state
            return self._current_state
