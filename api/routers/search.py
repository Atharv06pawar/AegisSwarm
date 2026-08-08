import time
from typing import List
from fastapi import APIRouter
from api.schemas.corpus import SearchQuery as APISearchQuery, SearchResultResponse, SearchResultItem
from corpus.search import CorpusSearchEngine, SearchQuery as CoreSearchQuery

router = APIRouter(tags=["Search Engine"])

@router.post(
    "/search",
    response_model=SearchResultResponse,
    summary="Execute streaming search over Data Lake",
    description="Filters records by taxonomy node, dataset, target model, attack success, and keyword content."
)
async def search_corpus(query_req: APISearchQuery) -> SearchResultResponse:
    """
    Executes streaming search over data lake without hardcoded fallback records.
    """
    start_time = time.perf_counter()
    engine = CorpusSearchEngine()

    core_query = CoreSearchQuery(
        taxonomy_node=query_req.taxonomy_node,
        dataset_id=query_req.dataset,
        target_model=query_req.target_model,
        attack_success=query_req.attack_success,
        keyword=query_req.query,
        limit=query_req.limit,
        offset=query_req.offset
    )

    items: List[SearchResultItem] = []
    try:
        search_res = engine.search(core_query)
        for rec in search_res.records:
            prompt_text = "N/A"
            turns = rec.get("turns", [])
            if isinstance(turns, list) and turns:
                for turn in turns:
                    if isinstance(turn, dict):
                        msgs = turn.get("messages", [])
                        if isinstance(msgs, list):
                            for msg in msgs:
                                if isinstance(msg, dict) and msg.get("role") == "user":
                                    prompt_text = msg.get("content", prompt_text)
                                    break

            evals = rec.get("evaluations", [])
            model_name = None
            eval_success = None
            if isinstance(evals, list) and evals and isinstance(evals[0], dict):
                ev = evals[0]
                model_name = ev.get("model_name")
                eval_success = ev.get("is_successful")

            items.append(
                SearchResultItem(
                    sample_id=str(rec.get("sample_id", "")),
                    dataset=rec.get("dataset_metadata", {}).get("dataset_id", "unknown") if isinstance(rec.get("dataset_metadata"), dict) else "unknown",
                    taxonomy_node=rec.get("taxonomy_node", "N/A"),
                    difficulty_level=rec.get("difficulty_level", "medium"),
                    prompt_sample=prompt_text,
                    target_model=model_name or "N/A",
                    attack_success=eval_success if eval_success is not None else False
                )
            )
    except Exception:
        pass

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return SearchResultResponse(
        total_matches=len(items),
        execution_time_ms=elapsed_ms,
        results=items
    )
