"""
Composite EvaluationEngine orchestrator for AegisSwarm.
Runs a pipeline of evaluators on an ExecutionResult and synthesizes a unified EvaluationResult.
"""

import time
import logging
from typing import List, Optional
from evaluation.base import BaseEvaluator
from evaluation.factory import EvaluationFactory
from evaluation.models import EvaluationRequest, EvaluationResult

logger = logging.getLogger(__name__)


class EvaluationEngine:
    """
    Composite evaluation engine that executes a suite of evaluators and produces
    a consolidated EvaluationResult.
    """

    DEFAULT_EVALUATORS = ["regex", "refusal", "leakage", "jailbreak"]

    def __init__(self, evaluators: Optional[List[BaseEvaluator]] = None):
        if evaluators is not None:
            self.evaluators = evaluators
        else:
            self.evaluators = [
                EvaluationFactory.create(name) for name in self.DEFAULT_EVALUATORS
            ]

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Executes all configured evaluators on the request and merges their findings.
        
        Args:
            request (EvaluationRequest): Input execution result and context.
            
        Returns:
            EvaluationResult: Merged evaluation result model.
        """
        start_time = time.perf_counter()
        exec_res = request.execution_result

        attack_success = False
        refusal_detected = False
        prompt_leak_detected = False
        jailbreak_detected = False
        
        max_severity = 0.0
        confidences: List[float] = []
        reasons: List[str] = []
        detectors_used: List[str] = []
        total_eval_cost = 0.0

        for evaluator in self.evaluators:
            try:
                sub_res: EvaluationResult = evaluator.evaluate(request)
                detectors_used.extend(sub_res.detectors_used)
                
                if sub_res.attack_success:
                    attack_success = True
                if sub_res.refusal_detected:
                    refusal_detected = True
                if sub_res.prompt_leak_detected:
                    prompt_leak_detected = True
                if sub_res.jailbreak_detected:
                    jailbreak_detected = True

                if sub_res.severity_score > max_severity:
                    max_severity = sub_res.severity_score

                confidences.append(sub_res.confidence)
                if sub_res.evaluation_reason:
                    reasons.append(f"[{evaluator.name}] {sub_res.evaluation_reason}")
                total_eval_cost += sub_res.estimated_cost

            except Exception as err:
                logger.error(f"Error executing evaluator '{evaluator.name}': {err}")

        avg_confidence = (sum(confidences) / len(confidences)) if confidences else 1.0
        combined_reason = " | ".join(reasons) if reasons else "Evaluation completed cleanly."
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return EvaluationResult(
            execution_id=exec_res.execution_id,
            sample_id=exec_res.attack_id,
            provider=exec_res.provider,
            model=exec_res.model,
            attack_success=attack_success,
            refusal_detected=refusal_detected,
            prompt_leak_detected=prompt_leak_detected,
            jailbreak_detected=jailbreak_detected,
            severity_score=max_severity,
            confidence=round(avg_confidence, 2),
            evaluation_reason=combined_reason,
            detectors_used=list(dict.fromkeys(detectors_used)),
            evaluation_latency_ms=round(latency_ms, 2),
            estimated_cost=round(total_eval_cost, 6)
        )
