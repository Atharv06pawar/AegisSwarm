from typing import Optional
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
