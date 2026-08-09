"""
StrategyAdvisor module for AegisSwarm Adaptive Swarm Intelligence.
Coordinates intelligence analysis, agent ranking, and strategy mutation.
"""

import logging
from typing import Tuple, Optional, List
from core.schema import AttackRecord
from swarm.memory import SwarmMemory
from swarm.intelligence import AdaptiveIntelligence
from swarm.ranking import AgentRankingEngine
from swarm.mutation import StrategyMutationEngine
from swarm.strategy import StrategyRecommendation, StrategyType

logger = logging.getLogger(__name__)


class StrategyAdvisor:
    """
    Advisor component providing strategy advice and mutating payloads based on historical feedback.
    """

    def __init__(
        self,
        intelligence: Optional[AdaptiveIntelligence] = None,
        ranking_engine: Optional[AgentRankingEngine] = None,
        mutation_engine: Optional[StrategyMutationEngine] = None
    ):
        self.intelligence = intelligence or AdaptiveIntelligence()
        self.ranking_engine = ranking_engine or AgentRankingEngine()
        self.mutation_engine = mutation_engine or StrategyMutationEngine()

    def advise_and_mutate(self, record: AttackRecord, memory: SwarmMemory) -> Tuple[str, AttackRecord]:
        """
        Analyzes SwarmMemory state, selects the top strategy recommendation,
        and generates a mutated AttackRecord payload along with the recommended target agent.
        
        Args:
            record (AttackRecord): Original AttackRecord.
            memory (SwarmMemory): Shared memory store.
            
        Returns:
            Tuple[str, AttackRecord]: Recommended (agent_name, mutated_attack_record).
        """
        self.intelligence.memory = memory
        recommendations = self.intelligence.recommend_strategies()

        if not recommendations:
            return "jailbreak", record

        top_rec: StrategyRecommendation = recommendations[0]
        mutated_record = self.mutation_engine.mutate(record, top_rec.strategy_type)

        logger.info(
            f"StrategyAdvisor recommended agent '{top_rec.recommended_agent}' "
            f"with strategy '{top_rec.strategy_type}' for record '{record.sample_id}'"
        )
        return top_rec.recommended_agent, mutated_record
