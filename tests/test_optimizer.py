import pytest
from learning.memory import LearningMemory
from learning.strategy import StrategyManager
from learning.optimizer import StrategyOptimizer


def test_strategy_manager_and_optimizer():
    """Verify StrategyManager utility updates and StrategyOptimizer optimization parameters."""
    strat_mgr = StrategyManager()
    rankings = strat_mgr.get_rankings()
    assert len(rankings) >= 1

    updated = strat_mgr.update_score("persona", reward=1.0, learning_rate=0.2)
    assert updated > 0.8

    memory = LearningMemory()
    optimizer = StrategyOptimizer(strategy_manager=strat_mgr)
    opt_params = optimizer.optimize(memory)

    assert "agent_ordering" in opt_params
    assert "provider_ordering" in opt_params
    assert "mutation_ordering" in opt_params
