"""
AutonomousPlanner orchestrating the complete semantic reasoning, candidate generation, critique, and planning pipeline.
"""

import time
import logging
from typing import Optional, List, Dict, Any

from reasoning.models import (
    ReasoningRequest,
    ReasoningResponse,
    StrategyCandidate,
    MutationPlan,
    ReasoningTimeline,
    ReasoningMemoryRecord
)
from reasoning.config import ReasoningConfig
from reasoning.memory import ReasoningMemory
from reasoning.retrieval import RetrievalEngine
from reasoning.generator import StrategyGenerator
from reasoning.critique import CritiqueEngine
from reasoning.ranking import RankingEngine
from reasoning.confidence import ConfidenceEstimator
from reasoning.provider_selector import ProviderSelector
from reasoning.prompt_builder import PromptBuilder
from reasoning.reflection import ReflectionEngine
from reasoning.report import ReasoningReportGenerator
from reasoning.persistence import ReasoningPersistence
from learning.memory import LearningMemory

logger = logging.getLogger(__name__)


class AutonomousPlanner:
    """
    Control plane orchestrator executing autonomous semantic reasoning and attack plan synthesis.
    """

    def __init__(
        self,
        config: Optional[ReasoningConfig] = None,
        reasoning_memory: Optional[ReasoningMemory] = None,
        retrieval_engine: Optional[RetrievalEngine] = None,
        generator: Optional[StrategyGenerator] = None,
        critique_engine: Optional[CritiqueEngine] = None,
        ranking_engine: Optional[RankingEngine] = None,
        confidence_estimator: Optional[ConfidenceEstimator] = None,
        provider_selector: Optional[ProviderSelector] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        reflection_engine: Optional[ReflectionEngine] = None,
        report_generator: Optional[ReasoningReportGenerator] = None,
        persistence: Optional[ReasoningPersistence] = None
    ):
        self.config = config or ReasoningConfig()
        self.reasoning_memory = reasoning_memory or ReasoningMemory()
        self.retrieval_engine = retrieval_engine or RetrievalEngine()
        self.generator = generator or StrategyGenerator()
        self.critique_engine = critique_engine or CritiqueEngine()
        self.ranking_engine = ranking_engine or RankingEngine()
        self.confidence_estimator = confidence_estimator or ConfidenceEstimator()
        self.provider_selector = provider_selector or ProviderSelector()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.reflection_engine = reflection_engine or ReflectionEngine()
        self.report_generator = report_generator or ReasoningReportGenerator()
        self.persistence = persistence or ReasoningPersistence()

    def plan_attack(
        self,
        request: ReasoningRequest,
        learning_memory: Optional[LearningMemory] = None
    ) -> ReasoningResponse:
        """
        Executes a complete semantic reasoning pass to generate, critique, rank, and finalize an autonomous attack plan.
        """
        timeline: List[ReasoningTimeline] = []

        # 1. Semantic Retrieval
        t0 = time.perf_counter()
        matches = self.retrieval_engine.retrieve_similar(
            query_text=f"{request.objective} {request.taxonomy_node}",
            learning_memory=learning_memory,
            top_k=self.config.top_k_retrieval
        )
        t_ret = round((time.perf_counter() - t0) * 1000.0, 2)
        timeline.append(ReasoningTimeline(step_name="SemanticRetrieval", duration_ms=t_ret, details={"matches_found": len(matches)}))

        # 2. Provider Selection
        t0 = time.perf_counter()
        provider_rec = self.provider_selector.select_provider(
            target_provider=request.target_provider,
            target_model=request.target_model
        )
        t_prov = round((time.perf_counter() - t0) * 1000.0, 2)
        timeline.append(ReasoningTimeline(step_name="ProviderSelection", duration_ms=t_prov, details={"provider": provider_rec.recommended_provider}))

        # 3. Candidate Generation (min 5 candidates)
        t0 = time.perf_counter()
        candidates = self.generator.generate_candidates(request=request, similarity_matches=matches)
        t_gen = round((time.perf_counter() - t0) * 1000.0, 2)
        timeline.append(ReasoningTimeline(step_name="CandidateGeneration", duration_ms=t_gen, details={"count": len(candidates)}))

        # 4. Self-Critique Evaluation
        t0 = time.perf_counter()
        critiques = self.critique_engine.critique_all(candidates)
        t_crit = round((time.perf_counter() - t0) * 1000.0, 2)
        timeline.append(ReasoningTimeline(step_name="SelfCritique", duration_ms=t_crit, details={"critiques_count": len(critiques)}))

        # 5. Candidate Ranking
        t0 = time.perf_counter()
        ranked_candidates = self.ranking_engine.rank_candidates(candidates=candidates, critiques=critiques)
        chosen_strategy = ranked_candidates[0]
        t_rank = round((time.perf_counter() - t0) * 1000.0, 2)
        timeline.append(ReasoningTimeline(step_name="CandidateRanking", duration_ms=t_rank, details={"chosen_candidate": str(chosen_strategy.candidate_id)}))

        # 6. Confidence Estimation
        t0 = time.perf_counter()
        overall_conf = self.confidence_estimator.estimate_confidence(candidate=chosen_strategy, historical_matches=matches)
        t_conf = round((time.perf_counter() - t0) * 1000.0, 2)
        timeline.append(ReasoningTimeline(step_name="ConfidenceEstimation", duration_ms=t_conf, details={"confidence": overall_conf}))

        # 7. Mutation Planning
        mutation_plan = MutationPlan(
            chain=["persona", "markdown", "roleplay", "delimiter", "recursive"],
            target_prompt=request.objective,
            expected_evasion_rate=0.88
        )

        # 8. Post-Execution Reflection
        reflection = self.reflection_engine.reflect(outcome_success=True)

        response = ReasoningResponse(
            request_id=request.request_id,
            chosen_strategy=chosen_strategy,
            all_candidates=ranked_candidates,
            similarity_matches=matches,
            provider_recommendation=provider_rec,
            mutation_plan=mutation_plan,
            critiques=critiques,
            reflections=[reflection],
            timeline=timeline,
            overall_confidence=overall_conf
        )

        # 9. Store Memory & Persistence
        mem_rec = ReasoningMemoryRecord(
            request_id=str(request.request_id),
            objective=request.objective,
            chosen_strategy_id=str(chosen_strategy.candidate_id),
            overall_confidence=overall_conf
        )
        self.reasoning_memory.store(mem_rec)
        
        report_md = self.report_generator.generate_report(response, format_type="markdown")
        self.persistence.save_strategies(ranked_candidates)
        self.persistence.save_reflections([reflection])
        self.persistence.save_memory(self.reasoning_memory.history())
        self.persistence.save_report(str(request.request_id), report_md, extension="md")

        return response
