"""
StrategyGenerator generating minimum 5 distinct strategy candidates per reasoning pass.
"""

from typing import List, Optional
from reasoning.models import StrategyCandidate, ReasoningRequest, SimilarityMatch


class StrategyGenerator:
    """
    Autonomous candidate generator creating at least 5 candidate attack strategies with distinct families, mutations, and trade-offs.
    """

    CANDIDATE_TEMPLATES = [
        {"family": "direct_injection", "mutation": "persona", "severity": "High", "confidence": 0.88},
        {"family": "indirect_injection", "mutation": "tool_injection", "severity": "Critical", "confidence": 0.92},
        {"family": "jailbreak", "mutation": "roleplay", "severity": "High", "confidence": 0.85},
        {"family": "roleplay", "mutation": "delimiter", "severity": "Medium", "confidence": 0.78},
        {"family": "multi_turn", "mutation": "cot_wrapper", "severity": "High", "confidence": 0.82}
    ]

    def generate_candidates(
        self,
        request: ReasoningRequest,
        similarity_matches: Optional[List[SimilarityMatch]] = None
    ) -> List[StrategyCandidate]:
        """
        Generates minimum 5 StrategyCandidate objects tailored to request objectives and historical matches.
        """
        candidates: List[StrategyCandidate] = []

        providers = ["openai", "anthropic", "gemini", "ollama", "openrouter"]

        for i, tpl in enumerate(self.CANDIDATE_TEMPLATES):
            prov = providers[i % len(providers)]
            cand = StrategyCandidate(
                attack_family=tpl["family"],
                mutation_family=tpl["mutation"],
                provider=prov,
                model=request.target_model if prov == request.target_provider else "gpt-4o",
                estimated_cost=round(0.001 * (i + 1), 4),
                estimated_latency_ms=round(35.0 + i * 10.0, 1),
                estimated_success=round(min(0.95, 0.70 + (i * 0.05)), 2),
                estimated_severity=tpl["severity"],
                estimated_confidence=tpl["confidence"],
                reasoning_text=f"Strategic plan using {tpl['family']} paired with {tpl['mutation']} on target provider '{prov}'."
            )
            candidates.append(cand)

        # Internal ranking initialization
        for c in candidates:
            c.rank_score = round((c.estimated_success * 0.5) + (c.estimated_confidence * 0.5), 4)

        candidates.sort(key=lambda x: x.rank_score or 0.0, reverse=True)
        return candidates
