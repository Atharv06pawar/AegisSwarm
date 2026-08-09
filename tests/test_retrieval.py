"""
Unit tests for RetrievalEngine in reasoning package.
"""

from reasoning.retrieval import RetrievalEngine
from learning.memory import LearningMemory, LearningMemoryRecord


def test_retrieval_engine_query():
    retriever = RetrievalEngine()
    mem = LearningMemory()
    mem.store(
        LearningMemoryRecord(
            attack_id="atk-100",
            dataset="advbench",
            provider="openai",
            model="gpt-4o",
            taxonomy_node="AUAO-PI-DIR-DEL-XML",
            agent="jailbreak",
            mutation="persona",
            evaluation_score=0.9,
            attack_success=True
        )
    )

    matches = retriever.retrieve_similar(
        query_text="AUAO-PI-DIR-DEL-XML jailbreak persona",
        learning_memory=mem,
        top_k=5,
        provider_filter="openai"
    )

    assert len(matches) > 0
    assert matches[0].provider == "openai"
    assert matches[0].similarity_score > 0.0
