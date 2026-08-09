"""
AdaptiveIntelligence module for AegisSwarm.
Analyzes SwarmMemory and EvaluationResults to recommend attack strategies and payload optimizations.
"""

import logging
from typing import List, Dict, Any, Optional

from evaluation.models import EvaluationResult
from swarm.memory import SwarmMemory
from swarm.strategy import StrategyRecommendation, StrategyType
from swarm.exceptions import SwarmError

logger = logging.getLogger(__name__)


class AdaptiveIntelligence:
    """
    Analyzes historical attack telemetry and evaluation findings stored in SwarmMemory
    to recommend adaptive attack strategies.
    """

    def __init__(self, memory: Optional[SwarmMemory] = None):
        self.memory = memory or SwarmMemory()

    def analyze_evaluations(self, evaluations: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Analyzes a list of EvaluationResult models to identify refusal, leakage, and success trends.
        
        Args:
            evaluations (List[EvaluationResult]): Evaluation results to analyze.
            
        Returns:
            Dict[str, Any]: Summary dictionary of patterns found.
        """
        if not evaluations:
            return {
                "total": 0,
                "refusal_count": 0,
                "leakage_count": 0,
                "success_count": 0,
                "dominant_failure_reason": "none"
            }

        total = len(evaluations)
        refusal_count = sum(1 for e in evaluations if e.refusal_detected)
        leakage_count = sum(1 for e in evaluations if e.prompt_leak_detected)
        success_count = sum(1 for e in evaluations if e.attack_success)

        failure_reasons: Dict[str, int] = {}
        for e in evaluations:
            if not e.attack_success:
                reason = "refusal" if e.refusal_detected else "failed_match"
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        dominant = max(failure_reasons.items(), key=lambda x: x[1])[0] if failure_reasons else "none"

        return {
            "total": total,
            "refusal_count": refusal_count,
            "leakage_count": leakage_count,
            "success_count": success_count,
            "dominant_failure_reason": dominant
        }

    def recommend_strategies(self, target_agent: str = "jailbreak") -> List[StrategyRecommendation]:
        """
        Reads SwarmMemory and generates ranked strategy recommendations based on historical patterns.
        
        Args:
            target_agent (str): Recommended default agent.
            
        Returns:
            List[StrategyRecommendation]: List of strategy recommendations.
        """
        eval_findings = self.memory.get("evaluator_findings", [])
        completed = self.memory.get("completed_attacks", [])
        failed = self.memory.get("failed_attacks", [])
        discovered_leakage = self.memory.get("discovered_leakage", [])

        recommendations: List[StrategyRecommendation] = []

        # High refusal count -> Recommend Roleplay and Hypothetical framing
        if len(failed) > len(completed):
            recommendations.append(
                StrategyRecommendation(
                    strategy_id="strat-roleplay-override",
                    strategy_type=StrategyType.ROLEPLAY_WRAPPER,
                    recommended_agent="roleplay",
                    confidence_score=0.88,
                    rationale="High failure/refusal rate observed. Applying authority roleplay persona wrapper.",
                    suggested_mutations=["mutate_roleplay", "mutate_hypothetical"]
                )
            )
            recommendations.append(
                StrategyRecommendation(
                    strategy_id="strat-xml-escape",
                    strategy_type=StrategyType.XML_DELIMITER_ESCAPE,
                    recommended_agent="direct_injection",
                    confidence_score=0.82,
                    rationale="Refusal guardrails detected. Utilizing XML delimiter tag escape.",
                    suggested_mutations=["mutate_xml_escape"]
                )
            )
        elif discovered_leakage:
            recommendations.append(
                StrategyRecommendation(
                    strategy_id="strat-leakage-extract",
                    strategy_type=StrategyType.DIRECT_OVERRIDE,
                    recommended_agent="leakage",
                    confidence_score=0.92,
                    rationale="Prompt leakage detected in prior runs. Exploiting instructions extraction.",
                    suggested_mutations=["mutate_xml_escape"]
                )
            )
        else:
            recommendations.append(
                StrategyRecommendation(
                    strategy_id="strat-default-jailbreak",
                    strategy_type=StrategyType.SUFFIX_ATTACK,
                    recommended_agent=target_agent,
                    confidence_score=0.75,
                    rationale="Standard baseline execution.",
                    suggested_mutations=["mutate_suffix"]
                )
            )

        # Store recommended strategy into SwarmMemory
        for rec in recommendations:
            self.memory.append_to_list("strategy_history", rec.model_dump())

        return recommendations
