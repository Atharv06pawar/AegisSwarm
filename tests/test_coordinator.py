"""
Unit tests for MissionCoordinator in orchestrator package.
"""

from orchestrator.coordinator import MissionCoordinator
from orchestrator.models import MissionRequest, MissionState
from learning.memory import LearningMemory


def test_mission_coordinator_end_to_end():
    coordinator = MissionCoordinator()
    learning_mem = LearningMemory()

    req = MissionRequest(
        objective="End-to-End Orchestrator Audit Mission",
        target_provider="openai",
        target_model="gpt-4o",
        max_attacks=4,
        budget_usd=10.0
    )

    mission = coordinator.execute_mission(req, learning_memory=learning_mem)
    assert mission.state == MissionState.COMPLETED
    assert mission.attack_count == 4
    assert mission.successful_attacks == 4
    assert mission.cost_usd > 0.0

    retrieved_m = coordinator.get_mission(mission.mission_id)
    assert retrieved_m is not None
    assert retrieved_m.mission_id == mission.mission_id

    graph = coordinator.get_graph(mission.mission_id)
    assert graph is not None
    assert len(graph.nodes) == 8

    stats = coordinator.statistics()
    assert stats.total_missions == 1
    assert stats.completed_missions == 1
