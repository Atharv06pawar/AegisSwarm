import pytest
from evaluation.base import BaseEvaluator
from evaluation.registry import EvaluatorRegistry
from evaluation.exceptions import EvaluatorNotFound
from evaluation.models import EvaluationRequest, EvaluationResult


class MockEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "mock_eval"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_attack_types(self) -> list[str]:
        return ["AUAO-PI-*"]

    def health(self) -> dict:
        return {"status": "ok"}

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        exec_res = request.execution_result
        return EvaluationResult(
            execution_id=exec_res.execution_id,
            sample_id=exec_res.attack_id,
            provider=exec_res.provider,
            model=exec_res.model,
            evaluation_reason="Mock evaluation"
        )


def test_evaluator_registration_and_list():
    """Verify manual registration, listing, and lookup in EvaluatorRegistry."""
    EvaluatorRegistry.clear()
    EvaluatorRegistry.register(MockEvaluator, name="mock_eval")

    evaluators = EvaluatorRegistry.list_evaluators()
    assert "mock_eval" in evaluators

    cls = EvaluatorRegistry.get_evaluator("mock_eval")
    assert cls is MockEvaluator


def test_evaluator_register_invalid_class():
    """Verify registering a class that does not inherit from BaseEvaluator raises TypeError."""
    class InvalidEvaluator:
        pass

    with pytest.raises(TypeError, match="must inherit from BaseEvaluator"):
        EvaluatorRegistry.register(InvalidEvaluator)  # type: ignore


def test_evaluator_unregister():
    """Verify unregistering an evaluator from registry."""
    EvaluatorRegistry.clear()
    EvaluatorRegistry.register(MockEvaluator, name="mock_eval")
    assert "mock_eval" in EvaluatorRegistry.list_evaluators()

    EvaluatorRegistry.unregister("mock_eval")
    assert "mock_eval" not in EvaluatorRegistry.list_evaluators()


def test_evaluator_not_found():
    """Verify requesting an unregistered evaluator raises EvaluatorNotFound exception."""
    EvaluatorRegistry.clear()
    with pytest.raises(EvaluatorNotFound, match="non_existent_evaluator"):
        EvaluatorRegistry.get_evaluator("non_existent_evaluator")


def test_evaluator_auto_discovery_on_get():
    """Verify get_evaluator triggers auto-discovery when registry is empty."""
    EvaluatorRegistry.clear()
    cls = EvaluatorRegistry.get_evaluator("regex")
    assert cls is not None
    assert "regex" in EvaluatorRegistry.list_evaluators()
