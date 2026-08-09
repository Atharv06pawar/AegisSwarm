"""
EvaluationFactory for creating BaseEvaluator instances.
"""

from evaluation.base import BaseEvaluator
from evaluation.registry import EvaluatorRegistry


class EvaluationFactory:
    """
    Factory class capable of instantiating evaluators by name.
    Simplifies creation of rule_based, regex, refusal, leakage, jailbreak, semantic, and llm_judge evaluators.
    """

    @staticmethod
    def create(evaluator_name: str, **kwargs) -> BaseEvaluator:
        """
        Creates and returns a configured BaseEvaluator instance.
        
        Args:
            evaluator_name (str): Evaluator identifier (e.g. 'regex', 'refusal', 'jailbreak').
            **kwargs: Arguments passed to the evaluator constructor.
            
        Returns:
            BaseEvaluator: Configured evaluator instance.
            
        Example:
            evaluator = EvaluationFactory.create("regex")
        """
        evaluator_cls = EvaluatorRegistry.get_evaluator(evaluator_name)
        return evaluator_cls(**kwargs)
