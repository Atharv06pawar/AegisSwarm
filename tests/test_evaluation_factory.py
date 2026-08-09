import pytest
from evaluation.base import BaseEvaluator
from evaluation.factory import EvaluationFactory
from evaluation.evaluators.rule_based import RuleBasedEvaluator
from evaluation.evaluators.regex import RegexEvaluator
from evaluation.evaluators.refusal_detector import RefusalDetector
from evaluation.evaluators.leakage_detector import LeakageDetector
from evaluation.evaluators.jailbreak_detector import JailbreakDetector
from evaluation.evaluators.semantic import SemanticEvaluator
from evaluation.evaluators.llm_judge import LLMJudgeEvaluator


def test_factory_creates_built_in_evaluators():
    """Verify EvaluationFactory creates instances of all built-in evaluators."""
    regex_ev = EvaluationFactory.create("regex")
    assert isinstance(regex_ev, RegexEvaluator)
    assert isinstance(regex_ev, BaseEvaluator)
    assert regex_ev.name == "regex"
    assert regex_ev.version == "1.0.0"

    rule_ev = EvaluationFactory.create("rule_based")
    assert isinstance(rule_ev, RuleBasedEvaluator)
    assert rule_ev.name == "rule_based"

    refusal_ev = EvaluationFactory.create("refusal")
    assert isinstance(refusal_ev, RefusalDetector)
    assert refusal_ev.name == "refusal"

    leakage_ev = EvaluationFactory.create("leakage")
    assert isinstance(leakage_ev, LeakageDetector)
    assert leakage_ev.name == "leakage"

    jailbreak_ev = EvaluationFactory.create("jailbreak")
    assert isinstance(jailbreak_ev, JailbreakDetector)
    assert jailbreak_ev.name == "jailbreak"

    semantic_ev = EvaluationFactory.create("semantic")
    assert isinstance(semantic_ev, SemanticEvaluator)
    assert semantic_ev.name == "semantic"

    llm_judge_ev = EvaluationFactory.create("llm_judge")
    assert isinstance(llm_judge_ev, LLMJudgeEvaluator)
    assert llm_judge_ev.name == "llm_judge"
