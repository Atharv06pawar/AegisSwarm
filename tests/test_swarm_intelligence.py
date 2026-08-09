import pytest
from uuid import uuid4
from evaluation.models import EvaluationResult
from swarm.memory import SwarmMemory
from swarm.intelligence import AdaptiveIntelligence
from swarm.strategy import StrategyRecommendation, StrategyType


def test_adaptive_intelligence_evaluations_analysis():
    """Verify AdaptiveIntelligence analysis of EvaluationResult trends."""
    intel = AdaptiveIntelligence()
    
    evals = [
        EvaluationResult(
            execution_id=uuid4(),
            sample_id=uuid4(),
            provider="openai",
            model="gpt-4o",
            attack_success=False,
            confidence=0.9,
            refusal_detected=True,
            severity_score=0.0,
            evaluator_name="refusal",
            evaluation_reason="Model refused request."
        ),
        EvaluationResult(
            execution_id=uuid4(),
            sample_id=uuid4(),
            provider="openai",
            model="gpt-4o",
            attack_success=True,
            confidence=0.95,
            prompt_leak_detected=True,
            severity_score=8.5,
            evaluator_name="leakage",
            evaluation_reason="System prompt disclosed."
        )
    ]

    analysis = intel.analyze_evaluations(evals)
    assert analysis["total"] == 2
    assert analysis["refusal_count"] == 1
    assert analysis["leakage_count"] == 1
    assert analysis["success_count"] == 1


def test_adaptive_intelligence_strategy_recommendations():
    """Verify strategy recommendation generation based on memory state."""
    mem = SwarmMemory()
    mem.append_to_list("failed_attacks", "attack-1")
    mem.append_to_list("failed_attacks", "attack-2")

    intel = AdaptiveIntelligence(memory=mem)
    recs = intel.recommend_strategies(target_agent="jailbreak")

    assert len(recs) >= 1
    assert isinstance(recs[0], StrategyRecommendation)
    assert recs[0].strategy_type in [StrategyType.ROLEPLAY_WRAPPER, StrategyType.XML_DELIMITER_ESCAPE]

    # Verify strategy history saved to memory
    history = mem.get("strategy_history")
    assert len(history) >= 1
