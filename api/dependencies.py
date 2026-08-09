from typing import Optional, Any
from core.registry import PluginRegistry
from storage.data_lake import StorageBackend, JSONLBackend
from corpus.manager import CorpusManager
from api.services.plugin_service import PluginService
from api.services.ingest_service import JobManager, IngestService

# Singleton instances
_plugin_registry: Optional[PluginRegistry] = None
_plugin_service: Optional[PluginService] = None
_corpus_manager: Optional[CorpusManager] = None
_storage_backend: Optional[StorageBackend] = None
_job_manager: Optional[JobManager] = None
_ingest_service: Optional[IngestService] = None
_campaign_manager: Optional[Any] = None
_event_bus: Optional[Any] = None
_telemetry_collector: Optional[Any] = None
_telemetry_dashboard: Optional[Any] = None
_cluster_coordinator: Optional[Any] = None
_learning_memory: Optional[Any] = None
_adaptive_planner: Optional[Any] = None
_strategy_optimizer: Optional[Any] = None
_replay_engine: Optional[Any] = None
_attack_graph: Optional[Any] = None
_reasoning_memory: Optional[Any] = None
_autonomous_planner: Optional[Any] = None
_autonomous_strategist: Optional[Any] = None
_mission_coordinator: Optional[Any] = None
_research_harness: Optional[Any] = None

def get_plugin_registry() -> PluginRegistry:
    """
    FastAPI dependency providing singleton instance of PluginRegistry.
    """
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
        _plugin_registry.discover()
    return _plugin_registry

def get_plugin_service() -> PluginService:
    """
    FastAPI dependency providing singleton instance of PluginService.
    """
    global _plugin_service
    if _plugin_service is None:
        registry = get_plugin_registry()
        _plugin_service = PluginService(registry=registry)
    return _plugin_service

def get_corpus_manager() -> CorpusManager:
    """
    FastAPI dependency providing singleton instance of CorpusManager.
    """
    global _corpus_manager
    if _corpus_manager is None:
        _corpus_manager = CorpusManager()
    return _corpus_manager

def get_storage_backend() -> StorageBackend:
    """
    FastAPI dependency providing singleton instance of StorageBackend (JSONL default).
    """
    global _storage_backend
    if _storage_backend is None:
        _storage_backend = JSONLBackend(base_path="outputs/lake", compression="gzip")
    return _storage_backend

def get_job_manager() -> JobManager:
    """
    FastAPI dependency providing singleton instance of in-memory JobManager.
    """
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager

def get_ingest_service() -> IngestService:
    """
    FastAPI dependency providing singleton instance of IngestService.
    """
    global _ingest_service
    if _ingest_service is None:
        backend = get_storage_backend()
        job_mgr = get_job_manager()
        _ingest_service = IngestService(storage_backend=backend, job_manager=job_mgr)
    return _ingest_service

def get_campaign_manager():
    """
    FastAPI dependency providing singleton instance of CampaignManager.
    """
    global _campaign_manager
    if _campaign_manager is None:
        from campaign.manager import CampaignManager
        _campaign_manager = CampaignManager()
    return _campaign_manager

def get_event_bus():
    """FastAPI dependency providing singleton EventBus."""
    global _event_bus
    if _event_bus is None:
        from observability.event_bus import EventBus
        _event_bus = EventBus()
    return _event_bus

def get_telemetry_collector():
    """FastAPI dependency providing singleton TelemetryCollector."""
    global _telemetry_collector
    if _telemetry_collector is None:
        from observability.collector import TelemetryCollector
        bus = get_event_bus()
        _telemetry_collector = TelemetryCollector(event_bus=bus)
    return _telemetry_collector

def get_telemetry_dashboard():
    """FastAPI dependency providing singleton TelemetryDashboard."""
    global _telemetry_dashboard
    if _telemetry_dashboard is None:
        from observability.dashboard import TelemetryDashboard
        collector = get_telemetry_collector()
        _telemetry_dashboard = TelemetryDashboard(
            event_bus=collector.event_bus,
            metrics_collector=collector.metrics_collector,
            tracer=collector.tracer
        )
    return _telemetry_dashboard

def get_cluster_coordinator():
    """FastAPI dependency providing singleton ClusterCoordinator."""
    global _cluster_coordinator
    if _cluster_coordinator is None:
        from cluster.coordinator import ClusterCoordinator
        bus = get_event_bus()
        _cluster_coordinator = ClusterCoordinator(event_bus=bus)
        _cluster_coordinator.start_cluster(initial_workers=2)
    return _cluster_coordinator

def get_learning_memory():
    """FastAPI dependency providing singleton LearningMemory."""
    global _learning_memory
    if _learning_memory is None:
        from learning.memory import LearningMemory
        _learning_memory = LearningMemory()
    return _learning_memory

def get_strategy_optimizer():
    """FastAPI dependency providing singleton StrategyOptimizer."""
    global _strategy_optimizer
    if _strategy_optimizer is None:
        from learning.optimizer import StrategyOptimizer
        _strategy_optimizer = StrategyOptimizer()
    return _strategy_optimizer

def get_adaptive_planner():
    """FastAPI dependency providing singleton AdaptivePlanner."""
    global _adaptive_planner
    if _adaptive_planner is None:
        from learning.planner import AdaptivePlanner
        mem = get_learning_memory()
        opt = get_strategy_optimizer()
        _adaptive_planner = AdaptivePlanner(memory=mem, optimizer=opt)
    return _adaptive_planner

def get_replay_engine():
    """FastAPI dependency providing singleton ReplayEngine."""
    global _replay_engine
    if _replay_engine is None:
        from learning.replay import ReplayEngine
        mem = get_learning_memory()
        _replay_engine = ReplayEngine(memory=mem)
    return _replay_engine

def get_attack_graph():
    """FastAPI dependency providing singleton AttackGraph."""
    global _attack_graph
    if _attack_graph is None:
        from learning.graph import AttackGraph
        _attack_graph = AttackGraph()
        _attack_graph.add_node("n-prompt", "Prompt", "Base Prompt")
        _attack_graph.add_node("n-mut", "Mutation", "Persona Obfuscation")
        _attack_graph.add_node("n-prov", "Provider", "openai:gpt-4o")
        _attack_graph.add_node("n-eval", "Evaluation", "Jailbreak Detected")
        _attack_graph.add_edge("n-prompt", "n-mut", "mutation")
        _attack_graph.add_edge("n-mut", "n-prov", "provider_switch")
        _attack_graph.add_edge("n-prov", "n-eval", "success")
    return _attack_graph

def get_reasoning_memory():
    """FastAPI dependency providing singleton ReasoningMemory."""
    global _reasoning_memory
    if _reasoning_memory is None:
        from reasoning.memory import ReasoningMemory
        _reasoning_memory = ReasoningMemory()
    return _reasoning_memory

def get_autonomous_planner():
    """FastAPI dependency providing singleton AutonomousPlanner."""
    global _autonomous_planner
    if _autonomous_planner is None:
        from reasoning.planner import AutonomousPlanner
        mem = get_reasoning_memory()
        _autonomous_planner = AutonomousPlanner(reasoning_memory=mem)
    return _autonomous_planner

def get_autonomous_strategist():
    """FastAPI dependency providing singleton AutonomousStrategist."""
    global _autonomous_strategist
    if _autonomous_strategist is None:
        from reasoning.strategist import AutonomousStrategist
        planner = get_autonomous_planner()
        _autonomous_strategist = AutonomousStrategist(planner=planner)
    return _autonomous_strategist

def get_mission_coordinator():
    """FastAPI dependency providing singleton MissionCoordinator."""
    global _mission_coordinator
    if _mission_coordinator is None:
        from orchestrator.coordinator import MissionCoordinator
        _mission_coordinator = MissionCoordinator()
    return _mission_coordinator

def get_research_harness():
    """FastAPI dependency providing singleton ResearchBenchmarkHarness."""
    global _research_harness
    if _research_harness is None:
        from research.harness import ResearchBenchmarkHarness
        coordinator = get_mission_coordinator()
        _research_harness = ResearchBenchmarkHarness(coordinator=coordinator)
    return _research_harness

