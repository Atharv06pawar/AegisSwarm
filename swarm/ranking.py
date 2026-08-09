"""
AgentRankingEngine module for AegisSwarm Adaptive Swarm Intelligence.
Ranks swarm attacker agents using historical success, confidence, latency, and cost telemetry.
"""

import logging
from typing import List, Dict, Tuple, Any
from swarm.models import SwarmAgentResult

logger = logging.getLogger(__name__)


class AgentRankingEngine:
    """
    Ranks attacker agents using multi-objective utility scoring.
    """

    def __init__(
        self,
        weight_success: float = 0.5,
        weight_confidence: float = 0.3,
        weight_latency: float = 0.1,
        weight_cost: float = 0.1
    ):
        self.weight_success = weight_success
        self.weight_confidence = weight_confidence
        self.weight_latency = weight_latency
        self.weight_cost = weight_cost

    def compute_agent_score(self, agent_name: str, results: List[SwarmAgentResult]) -> float:
        """
        Computes utility score for a single agent based on its execution results.
        """
        agent_results = [r for r in results if r.agent_name == agent_name]
        if not agent_results:
            # Baseline unobserved score
            return 0.5

        total = len(agent_results)
        successes = sum(1 for r in agent_results if r.attack_success)
        success_rate = successes / total

        avg_confidence = sum(r.confidence for r in agent_results) / total
        avg_latency_sec = (sum(r.execution_time_ms for r in agent_results) / total) / 1000.0

        # Normalization penalty terms
        latency_penalty = min(avg_latency_sec / 10.0, 1.0)
        cost_penalty = 0.0

        score = (
            (self.weight_success * success_rate) +
            (self.weight_confidence * avg_confidence) -
            (self.weight_latency * latency_penalty) -
            (self.weight_cost * cost_penalty)
        )
        return round(max(0.0, min(1.0, score)), 4)

    def rank_agents(self, history_results: List[SwarmAgentResult], registered_agents: List[str]) -> List[Tuple[str, float]]:
        """
        Ranks registered swarm agents in descending order of utility score.
        
        Args:
            history_results (List[SwarmAgentResult]): List of past execution results.
            registered_agents (List[str]): Registered agent names.
            
        Returns:
            List[Tuple[str, float]]: Ordered list of (agent_name, utility_score).
        """
        scores: Dict[str, float] = {}
        for agent_name in registered_agents:
            scores[agent_name] = self.compute_agent_score(agent_name, history_results)

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        logger.info(f"Ranked agents: {ranked}")
        return ranked
