import pytest
from uuid import uuid4
from swarm.ranking import AgentRankingEngine
from swarm.models import SwarmAgentResult


def test_agent_ranking_engine():
    """Verify AgentRankingEngine utility scoring and ranking of agents."""
    engine = AgentRankingEngine()
    
    results = [
        SwarmAgentResult(
            agent_name="jailbreak",
            execution_id=uuid4(),
            evaluation_id=uuid4(),
            attack_success=True,
            confidence=0.9,
            severity=9.0,
            provider="openai",
            model="gpt-4o",
            execution_time_ms=100.0
        ),
        SwarmAgentResult(
            agent_name="direct_injection",
            execution_id=uuid4(),
            evaluation_id=uuid4(),
            attack_success=False,
            confidence=0.9,
            severity=0.0,
            provider="openai",
            model="gpt-4o",
            execution_time_ms=100.0
        )
    ]

    registered = ["jailbreak", "direct_injection", "tool_attack"]
    ranked = engine.rank_agents(results, registered)

    assert len(ranked) == 3
    # Top ranked agent should be 'jailbreak' due to successful attack
    assert ranked[0][0] == "jailbreak"
    assert ranked[0][1] > ranked[1][1]
