"""
Unit tests for Pydantic v2 models in reasoning package.
"""

from uuid import uuid4
from reasoning.models import (
    ReasoningRequest,
    ReasoningResponse,
    StrategyCandidate,
    ReflectionResult,
    CritiqueResult,
    SimilarityMatch,
    ProviderRecommendation,
    MutationPlan,
    ReasoningMemoryRecord,
    ReasoningStatistics
)


def test_reasoning_models_instantiation():
    req = ReasoningRequest(objective="Test safety objective", target_provider="openai")
    assert req.objective == "Test safety objective"
    assert req.target_provider == "openai"

    cand = StrategyCandidate(
        attack_family="direct_injection",
        mutation_family="persona",
        provider="openai",
        reasoning_text="Strategic plan text"
    )
    assert cand.attack_family == "direct_injection"
    assert cand.mutation_family == "persona"

    crit = CritiqueResult(
        candidate_id=cand.candidate_id,
        novelty_score=0.8,
        expected_success_score=0.85,
        cost_efficiency_score=0.9,
        risk_score=0.2,
        complexity_score=0.3,
        overall_critique_score=0.82,
        critique_notes="Good candidate"
    )
    assert crit.overall_critique_score == 0.82

    ref = ReflectionResult(
        what_worked="Persona framing",
        what_failed="Latency",
        why_outcome="Model confusion",
        how_to_improve="Reduce tokens"
    )
    assert ref.what_worked == "Persona framing"

    match = SimilarityMatch(
        record_id="rec-1",
        attack_id="atk-1",
        provider="openai",
        model="gpt-4o",
        taxonomy_node="AUAO-1",
        similarity_score=0.95
    )
    assert match.similarity_score == 0.95

    rec = ProviderRecommendation(
        recommended_provider="openai",
        recommended_model="gpt-4o",
        confidence_score=0.9,
        rationale="Low latency"
    )
    assert rec.recommended_provider == "openai"

    plan = MutationPlan(target_prompt="Sample prompt")
    assert len(plan.chain) == 5

    res = ReasoningResponse(
        request_id=req.request_id,
        chosen_strategy=cand,
        all_candidates=[cand],
        similarity_matches=[match],
        provider_recommendation=rec,
        mutation_plan=plan,
        critiques=[crit],
        reflections=[ref],
        overall_confidence=0.88
    )
    assert res.overall_confidence == 0.88
    dump = res.model_dump(mode="json")
    assert dump["request_id"] == str(req.request_id)


def test_reasoning_exceptions_and_memory_overflow():
    from reasoning.exceptions import (
        ReasoningError, MemoryError, RetrievalError, PlannerError,
        CritiqueError, ReflectionError, RankingError
    )
    from reasoning.memory import ReasoningMemory
    from reasoning.models import ReasoningMemoryRecord
    from reasoning.strategist import AutonomousStrategist
    from reasoning.report import ReasoningReportGenerator

    err = ReasoningError("test msg", "comp")
    assert "test msg" in str(err)
    assert MemoryError("mem").component == "reasoning_memory"
    assert RetrievalError("ret").component == "retrieval"
    assert PlannerError("plan").component == "planner"
    assert CritiqueError("crit").component == "critique"
    assert ReflectionError("ref").component == "reflection"
    assert RankingError("rank").component == "ranking"

    mem = ReasoningMemory(capacity=2)
    r1 = ReasoningMemoryRecord(request_id="req-1", objective="o1", chosen_strategy_id="c1", overall_confidence=0.8)
    r2 = ReasoningMemoryRecord(request_id="req-2", objective="o2", chosen_strategy_id="c2", overall_confidence=0.9)
    r3 = ReasoningMemoryRecord(request_id="req-3", objective="o3", chosen_strategy_id="c3", overall_confidence=0.95)
    mem.store(r1)
    mem.store(r2)
    mem.store(r3)
    assert len(mem.history()) == 2
    assert mem.lookup("req-1") is None
    assert mem.lookup("req-3") is not None
    stats = mem.statistics()
    assert stats.total_plans == 2

    strategist = AutonomousStrategist()
    req = ReasoningRequest(objective="Strategist test pass", target_provider="openai")
    plan_res = strategist.plan(req)
    assert plan_res.chosen_strategy is not None

    rep_gen = ReasoningReportGenerator()
    json_rep = rep_gen.generate_report(plan_res, format_type="json")
    assert "request_id" in json_rep
