# AegisSwarm System Architecture

**Document Version**: 2.0.0  
**Status**: Technical Architecture Specification  
**Scope**: AegisSwarm Core Engine, Streaming Data Lake, Subsystems, and AUAO v1.0 Framework  

---

## 1. Executive Summary

AegisSwarm is designed as a high-performance, modular, and memory-safe platform for AI red teaming and dataset normalization. The system operates on a **streaming-first philosophy**: no pipeline component loads complete datasets into RAM. This enables AegisSwarm to ingest multi-gigabyte files (10,000,000+ records) on commodity hardware without triggering Out-Of-Memory (OOM) exceptions.

---

## 2. Component Architecture Diagram

```
                               ┌───────────────────────────┐
                               │   main.py (Typer CLI)     │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │    PipelineOrchestrator   │
                               └─────────────┬─────────────┘
                                             │
      ┌──────────────────────────┬───────────┴──────────────┬──────────────────────────┐
      ▼                          ▼                          ▼                          ▼
┌───────────┐          ┌───────────────────┐      ┌───────────────────┐      ┌──────────────────┐
│  Plugin   │          │  Streaming Utils  │      │  StorageBackend   │      │  LineageTracker  │
│ Registry  │          │(chunk, safe_map)  │      │(JSONL / Parquet)  │      │(SHA256 Manifest) │
└─────┬─────┘          └─────────┬─────────┘      └─────────┬─────────┘      └─────────┬────────┘
      │                          │                          │                          │
      ▼                          ▼                          ▼                          ▼
[Plugins]              [Generator Streams]       [outputs/lake/source=*]    [lineage_manifest]
```

---

## 3. Streaming Pipeline Execution Flow

The ingestion pipeline executes in 8 sequential stages, maintaining complete memory isolation:

1. **Discovery**: `PluginRegistry.discover()` imports plugins from `plugins/datasets/`.
2. **Fetch**: `plugin.fetch()` returns the absolute file path to raw data in `raw/<dataset>/`.
3. **Stream Parsing**: `plugin.parse(path)` opens the file and yields raw Python dictionaries line-by-line (`Iterator[Dict[str, Any]]`).
4. **Safe Normalization**: `utils.streaming.safe_map()` wraps `plugin.normalize(raw_dict)`, mapping raw data to Pydantic `AttackRecord` objects without aborting the stream on single-record failures.
5. **Validation Pass**: `plugin.validate(record_stream)` filters corrupted payloads or invalid records.
6. **Progress Tracking**: `track_progress()` logs dynamic ingestion metrics every N items.
7. **Fixed-Size Chunking**: `chunked_iterable(stream, batch_size)` slices the record generator into memory-bounded batches (e.g. 5,000 items).
8. **Atomic Storage Persistence**: `StorageBackend.batch_write()` writes batches to temporary files in the partition directory before issuing an atomic POSIX rename (`os.replace`).

---

## 4. Subsystem Specifications

### 4.1 Plugin System (`core/plugin_base.py`, `core/registry.py`)
- **Abstract Base Class**: `BaseDatasetPlugin` requires implementing `dataset_id`, `parser_version`, `fetch()`, `parse()`, `normalize()`, `metadata()`, and `validate()`.
- **Dynamic Registration**: `PluginRegistry.discover()` inspects the filesystem at runtime, enforcing unique `dataset_id` constraints across all plugins.

### 4.2 Data Lake (`storage/data_lake.py`)
- **Abstract Storage Backend**: `StorageBackend` defines the contract for partitioned writes.
- **Partition Format**: Data is stored under Hive-style partitions: `outputs/lake/source=<dataset_id>/part-<uuid>.jsonl.gz` or `.parquet`.
- **Atomic Operations**: All writes utilize temporary files (`tempfile.mkstemp`) on the same filesystem before calling `os.replace()`, guaranteeing that query engines never observe partial writes.

### 4.3 Lineage & Reproducibility (`storage/lineage.py`)
- **Cryptographic Tracking**: `LineageTracker` computes 256-bit SHA256 digests of raw input files and logs all generated partition paths.
- **Manifest Export**: Produces `outputs/lineage_manifest.json`, ensuring bit-for-bit research reproducibility.

### 4.4 Universal Attack Ontology (`ontology/`)
- Canonical representation of attack vectors across 10 root domains, 79 taxonomy tree nodes, 53 properties, and 11 graph edge types (`ontology/attack_taxonomy.json`, `ontology/root_classes.json`, `ontology/relationships.json`).

### 4.5 Corpus Management Subsystem (`corpus/`)
- Facade (`CorpusManager`) coordinating registry indexing, cataloging, streaming statistics calculation, AUAO ontology coverage analysis, quality auditing, cryptographic verification, and Markdown whitepaper generation.

---

## 5. Future Architecture Evolution

- **Distributed Streaming Workers**: Sharding dataset parsing across Ray or Celery worker nodes.
- **Vector Embedding Indexing**: Native integration of vector indexing (Qdrant / Milvus) into `storage/data_lake.py`.
- **Autonomous Swarm Generators**: Generative agent loops producing synthetic AUAO records dynamically.
