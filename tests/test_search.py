import pytest
from corpus.search import CorpusSearchEngine, SearchQuery
from corpus.registry import CorpusRegistry
from storage.data_lake import JSONLBackend

def test_search_query_construction():
    """Test SearchQuery dataclass filter initialization."""
    q = SearchQuery(taxonomy_node="AUAO-PI-DIR", dataset_id="ds1", limit=10)
    assert q.taxonomy_node == "AUAO-PI-DIR"
    assert q.dataset_id == "ds1"
    assert q.limit == 10

def test_search_engine_filter(temp_lake_dir, sample_attack_record):
    """Test CorpusSearchEngine streaming search matching taxonomy node and keyword."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    engine = CorpusSearchEngine(registry=registry)

    # Search with matching taxonomy node
    query_match = SearchQuery(taxonomy_node="AUAO-PI-DIR-RO-AUTH-SYS")
    result_match = engine.search(query_match)
    assert len(result_match.records) == 1

    # Search with non-matching taxonomy node
    query_nomatch = SearchQuery(taxonomy_node="NONEXISTENT_NODE")
    result_nomatch = engine.search(query_nomatch)
    assert len(result_nomatch.records) == 0

def test_search_engine_keyword(temp_lake_dir, sample_attack_record):
    """Test CorpusSearchEngine keyword matching inside prompt message text."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    engine = CorpusSearchEngine(registry=registry)

    query_kw = SearchQuery(keyword="Ignore rules")
    result_kw = engine.search(query_kw)
    assert len(result_kw.records) == 1
