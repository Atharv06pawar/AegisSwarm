import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Union
from pydantic import BaseModel, Field, ConfigDict

from corpus.registry import CorpusRegistry
from corpus.statistics import CorpusStatisticsCalculator

class SearchQuery(BaseModel):
    """
    Pydantic v2 data contract defining search criteria and filter conditions for data lake querying.
    """
    model_config = ConfigDict(frozen=True)

    taxonomy_node: Optional[Union[str, List[str]]] = Field(None, description="Taxonomy node ID or list of IDs.")
    dataset_id: Optional[Union[str, List[str]]] = Field(None, description="Dataset source ID or list of IDs.")
    source_plugin: Optional[str] = Field(None, description="Source plugin name.")
    difficulty_level: Optional[str] = Field(None, description="Assessed difficulty level.")
    target_model: Optional[str] = Field(None, description="Target evaluation model name.")
    attack_success: Optional[bool] = Field(None, description="Filter by attack success flag.")
    keyword: Optional[str] = Field(None, description="Keyword search string in messages, tools, artifacts.")
    validator_name: Optional[str] = Field(None, description="Validation check name.")
    parser_version: Optional[str] = Field(None, description="Parser plugin version.")
    date_from: Optional[datetime] = Field(None, description="Minimum creation date.")
    date_to: Optional[datetime] = Field(None, description="Maximum creation date.")
    
    filter_mode: str = Field(default="AND", description="Filter combination logic ('AND' or 'OR').")
    limit: int = Field(default=100, ge=1, le=5000, description="Maximum matching records to return.")
    offset: int = Field(default=0, ge=0, description="Offset for pagination.")
    sort_by: Optional[str] = Field(default=None, description="Field name to sort results by (e.g. 'created_at').")
    sort_descending: bool = Field(default=False, description="Sort order.")


class SearchResult(BaseModel):
    """
    Pydantic v2 data contract containing search execution response payload and pagination metadata.
    """
    model_config = ConfigDict(frozen=True)

    total_matches_scanned: int = Field(default=0, ge=0, description="Total matching records found during scan.")
    returned_count: int = Field(default=0, ge=0, description="Number of records returned in payload.")
    offset: int = Field(default=0, ge=0, description="Pagination offset used.")
    limit: int = Field(default=100, ge=1, description="Limit used.")
    execution_time_ms: float = Field(default=0.0, ge=0.0, description="Query execution time in milliseconds.")
    records: List[Dict[str, Any]] = Field(default_factory=list, description="List of matching raw or AttackRecord dictionaries.")


class CorpusSearchEngine:
    """
    Memory-safe streaming search engine for the AegisSwarm Data Lake.
    Executes filtered queries over partitioned JSONL, JSONL.GZ, and Parquet datastores
    using line-by-line generators without loading full datasets into memory.
    """

    def __init__(
        self,
        registry: Optional[CorpusRegistry] = None,
        calculator: Optional[CorpusStatisticsCalculator] = None
    ):
        self.registry = registry or CorpusRegistry()
        self.calculator = calculator or CorpusStatisticsCalculator(registry=self.registry)

    def _matches_query(self, rec: Dict[str, Any], query: SearchQuery) -> bool:
        """
        Evaluates a raw AttackRecord dictionary against SearchQuery filters using AND/OR logic.
        """
        checks: List[bool] = []

        # 1. Taxonomy Node Filter
        if query.taxonomy_node:
            rec_node = rec.get("taxonomy_node", "")
            if isinstance(query.taxonomy_node, list):
                checks.append(rec_node in query.taxonomy_node)
            else:
                checks.append(rec_node == query.taxonomy_node)

        # 2. Dataset ID Filter
        if query.dataset_id:
            ds_meta = rec.get("dataset_metadata", {})
            ds_id = ds_meta.get("dataset_id", "") if isinstance(ds_meta, dict) else ""
            if isinstance(query.dataset_id, list):
                checks.append(ds_id in query.dataset_id)
            else:
                checks.append(ds_id == query.dataset_id)

        # 3. Source Plugin Filter
        if query.source_plugin:
            p_meta = rec.get("parser_metadata", {})
            src_plug = p_meta.get("source_plugin", "") if isinstance(p_meta, dict) else ""
            checks.append(src_plug == query.source_plugin)

        # 4. Difficulty Level Filter
        if query.difficulty_level:
            checks.append(rec.get("difficulty_level") == query.difficulty_level)

        # 5. Target Model Filter
        if query.target_model:
            matched_tm = False
            for ev in rec.get("evaluations", []):
                if isinstance(ev, dict) and query.target_model.lower() in str(ev.get("target_model", "")).lower():
                    matched_tm = True
                    break
            checks.append(matched_tm)

        # 6. Attack Success Filter
        if query.attack_success is not None:
            matched_succ = False
            for ev in rec.get("evaluations", []):
                if isinstance(ev, dict) and ev.get("attack_success") == query.attack_success:
                    matched_succ = True
                    break
            checks.append(matched_succ)

        # 7. Validator Name Filter
        if query.validator_name:
            matched_val = False
            vals = rec.get("validation_results", [])
            if isinstance(vals, list):
                for val_item in vals:
                    if isinstance(val_item, dict) and val_item.get("validator_name") == query.validator_name:
                        matched_val = True
                        break
            val_single = rec.get("validation")
            if isinstance(val_single, dict) and val_single.get("validator_name") == query.validator_name:
                matched_val = True
            checks.append(matched_val)

        # 8. Parser Version Filter
        if query.parser_version:
            p_meta = rec.get("parser_metadata", {})
            p_ver = p_meta.get("parser_version", "") if isinstance(p_meta, dict) else ""
            checks.append(p_ver == query.parser_version)

        # 9. Keyword Search (inside messages, tool calls, artifacts, validation error messages)
        if query.keyword:
            kw = query.keyword.lower()
            found_kw = False

            # Check messages content
            turns = rec.get("turns", [])
            if isinstance(turns, list):
                for turn in turns:
                    if isinstance(turn, dict):
                        msgs = turn.get("messages", [])
                        if isinstance(msgs, list):
                            for msg in msgs:
                                if isinstance(msg, dict):
                                    content = str(msg.get("content", "")).lower()
                                    if kw in content:
                                        found_kw = True
                                        break
                                    # Check tool calls
                                    tool_calls = msg.get("tool_calls", [])
                                    if isinstance(tool_calls, list):
                                        for tc in tool_calls:
                                            if isinstance(tc, dict):
                                                t_name = str(tc.get("tool_name", "")).lower()
                                                t_args = str(tc.get("arguments", "")).lower()
                                                if kw in t_name or kw in t_args:
                                                    found_kw = True
                                                    break
                                    # Check artifacts
                                    artifacts = msg.get("artifacts", [])
                                    if isinstance(artifacts, list):
                                        for art in artifacts:
                                            if isinstance(art, dict):
                                                art_uri = str(art.get("uri_or_base64", art.get("uri", ""))).lower()
                                                if kw in art_uri:
                                                    found_kw = True
                                                    break
                    if found_kw:
                        break

            # Check validation result messages if not found yet
            if not found_kw:
                vals = rec.get("validation_results", [])
                if isinstance(vals, list):
                    for val_item in vals:
                        if isinstance(val_item, dict):
                            val_msg = str(val_item.get("message", "")).lower()
                            if kw in val_msg:
                                found_kw = True
                                break

            checks.append(found_kw)

        if not checks:
            return True

        if query.filter_mode.upper() == "OR":
            return any(checks)
        else: # AND
            return all(checks)

    def stream_search(self, query: SearchQuery) -> Iterator[Dict[str, Any]]:
        """
        Memory-safe generator streaming matching records line by line.
        """
        discovered = self.registry.discover_partitions()

        # Pre-filter partitions by dataset_id if supplied
        if query.dataset_id:
            target_ids = [query.dataset_id] if isinstance(query.dataset_id, str) else query.dataset_id
            discovered = [p for p in discovered if p.source_id in target_ids]

        for part in discovered:
            for rec in self.calculator.stream_records(part.partition_path):
                if self._matches_query(rec, query):
                    yield rec

    def search(self, query: SearchQuery) -> SearchResult:
        """
        Executes search query with pagination (offset/limit) and optional in-memory sorting.
        
        Args:
            query (SearchQuery): SearchQuery filter configuration.
            
        Returns:
            SearchResult: Paginated result set metadata and matching record array.
        """
        start_time = time.perf_counter()
        matching_records: List[Dict[str, Any]] = []

        total_matches = 0
        current_idx = 0

        for rec in self.stream_search(query):
            total_matches += 1
            if current_idx >= query.offset and len(matching_records) < query.limit:
                matching_records.append(rec)
            current_idx += 1

        # Optional Sorting
        if query.sort_by and matching_records:
            sort_key = query.sort_by
            matching_records.sort(
                key=lambda r: str(r.get(sort_key, "")),
                reverse=query.sort_descending
            )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return SearchResult(
            total_matches_scanned=total_matches,
            returned_count=len(matching_records),
            offset=query.offset,
            limit=query.limit,
            execution_time_ms=elapsed_ms,
            records=matching_records
        )

    def search_dataset(self, dataset_id: str, keyword: Optional[str] = None, limit: int = 100) -> SearchResult:
        """
        Convenience API to search records within a single dataset.
        """
        query = SearchQuery(dataset_id=dataset_id, keyword=keyword, limit=limit)
        return self.search(query)

    def search_taxonomy(self, taxonomy_node: str, limit: int = 100) -> SearchResult:
        """
        Convenience API to search records by taxonomy node ID.
        """
        query = SearchQuery(taxonomy_node=taxonomy_node, limit=limit)
        return self.search(query)

    def search_keyword(self, keyword: str, limit: int = 100) -> SearchResult:
        """
        Convenience API to search records by keyword content.
        """
        query = SearchQuery(keyword=keyword, limit=limit)
        return self.search(query)
