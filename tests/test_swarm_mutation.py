import pytest
from tests.test_execution_models import create_sample_attack_record
from swarm.mutation import StrategyMutationEngine
from swarm.strategy import StrategyType


def test_mutation_engine_immutability():
    """Verify mutation engine produces new AttackRecords and never modifies original records in place."""
    record = create_sample_attack_record()
    original_id = record.sample_id
    original_prompt = record.turns[0].messages[0].content

    engine = StrategyMutationEngine()
    mutated = engine.mutate(record, StrategyType.ROLEPLAY_WRAPPER)

    assert mutated.sample_id != original_id
    assert record.sample_id == original_id
    assert record.turns[0].messages[0].content == original_prompt
    assert "PERSONA OVERRIDE" in mutated.turns[0].messages[0].content


def test_all_mutation_strategies():
    """Verify all 5 mutation strategies execute cleanly."""
    record = create_sample_attack_record()
    engine = StrategyMutationEngine()

    mut_roleplay = engine.mutate(record, StrategyType.ROLEPLAY_WRAPPER)
    assert "PERSONA OVERRIDE" in mut_roleplay.turns[0].messages[0].content

    mut_xml = engine.mutate(record, StrategyType.XML_DELIMITER_ESCAPE)
    assert "<system_override>" in mut_xml.turns[0].messages[0].content

    mut_b64 = engine.mutate(record, StrategyType.BASE64_OBFUSCATION)
    assert "Base64 payload" in mut_b64.turns[0].messages[0].content

    mut_hypo = engine.mutate(record, StrategyType.HYPOTHETICAL_FRAMING)
    assert "fictional sci-fi novel" in mut_hypo.turns[0].messages[0].content

    mut_suffix = engine.mutate(record, StrategyType.SUFFIX_ATTACK)
    assert "Surely writing instructions" in mut_suffix.turns[0].messages[0].content


def test_generate_variants():
    """Verify generate_variants returns multiple mutated copies."""
    record = create_sample_attack_record()
    engine = StrategyMutationEngine()
    variants = engine.generate_variants(record)

    assert len(variants) == 3
    sample_ids = {v.sample_id for v in variants}
    assert len(sample_ids) == 3
