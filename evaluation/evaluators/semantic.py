"""
Semantic Evaluator for AegisSwarm (Production Interface).
Placeholder for future vector embedding and semantic similarity distance evaluation.
"""

import time
from typing import List, Dict, Any
from evaluation.base import BaseEvaluator
from evaluation.models import EvaluationRequest, EvaluationResult


class SemanticEvaluator(BaseEvaluator):
    """
    Production interface for semantic embedding distance evaluation.
    Currently returns an unconfigured status indicator.
    """

    @property
    def name(self) -> str:
        return "semantic"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_attack_types(self) -> List[str]:
        return ["AUAO-PI-DIR-*", "AUAO-JB-*"]

    def health(self) -> Dict[str, Any]:
        return {
            "status": "degraded",
            "evaluator": self.name,
            "version": self.version,
            "message": "Vector embedding backend not configured"
        }

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        start_time = time.perf_counter()
        exec_res = request.execution_result
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return EvaluationResult(
            execution_id=exec_res.execution_id,
            sample_id=exec_res.attack_id,
            provider=exec_res.provider,
            model=exec_res.model,
            attack_success=False,
            refusal_detected=False,
            prompt_leak_detected=False,
            jailbreak_detected=False,
            severity_score=0.0,
            confidence=0.5,
            evaluation_reason="Semantic evaluation placeholder: Vector embeddings not configured.",
            detectors_used=[self.name],
            evaluation_latency_ms=round(latency_ms, 2),
            estimated_cost=0.0,
            metadata={"status": "unconfigured"}
        )
