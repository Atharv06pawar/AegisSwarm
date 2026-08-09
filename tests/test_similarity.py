"""
Unit tests for SimilarityEngine in reasoning package.
"""

from reasoning.similarity import SimilarityEngine


def test_similarity_engine_metrics():
    engine = SimilarityEngine()
    t1 = "Direct prompt injection via XML framing"
    t2 = "Direct prompt injection with persona framing"

    overlap = engine.token_overlap(t1, t2)
    jaccard = engine.jaccard_similarity(t1, t2)
    cosine = engine.cosine_similarity(t1, t2)
    hybrid = engine.hybrid_score(t1, t2)

    assert 0.0 <= overlap <= 1.0
    assert 0.0 <= jaccard <= 1.0
    assert 0.0 <= cosine <= 1.0
    assert 0.0 <= hybrid <= 1.0
    assert hybrid > 0.5


def test_similarity_empty_strings():
    engine = SimilarityEngine()
    assert engine.hybrid_score("", "text") == 0.0
    assert engine.cosine_similarity("", "") == 0.0
