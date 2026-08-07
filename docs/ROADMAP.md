# AegisSwarm Strategic Development Roadmap

**Document Version**: 2.0.0  
**Status**: Active Research Roadmap  
**Target Horizon**: 2026 - 2028  

---

## 🟢 Completed Phases

### Phase 1: Core Architecture & Schema Standard
- Established standard Pydantic v2 data models (`AttackRecord`, `ConversationTurn`, `Message`, `EvaluationMetadata`).
- Built abstract plugin contract (`BaseDatasetPlugin`) and dynamic discovery engine (`PluginRegistry`).
- Standardized schema terminology across the codebase.

### Phase 2: Memory-Safe Streaming Engine & Data Lake
- Created memory-safe streaming utilities (`chunked_iterable`, `safe_map`, `track_progress`).
- Built partitioned Data Lake backends (`ParquetBackend`, `JSONLBackend`) with POSIX atomic swap protection (`tempfile` + `os.replace`).
- Built cryptographic SHA256 lineage tracking and manifest generation (`LineageTracker`).

### Phase 3: AUAO v1.0 Taxonomy & Benchmark Plugins
- Designed the **AegisSwarm Universal Attack Ontology (AUAO v1.0)**: 10 root classes, 79 taxonomy tree nodes, 53 properties, and 11 graph edge types.
- Authored RFC Normalization Specification (`ontology/ontology_mapping_rules.md`).
- Developed and verified 7 dataset plugins:
  - HackAPrompt
  - JailbreakBench
  - AgentDojo
  - PyRIT
  - Garak
  - PromptInject
  - AdvBench
- Built Typer CLI suite (`main.py`).

---

## 🟡 Active & Near-Term Phases

### Phase 4: Corpus Management Subsystem (`corpus/`)
- Implement `corpus/registry.py`, `catalog.py`, `statistics.py`, `coverage.py`, `quality.py`, `verifier.py`, `manifest.py`, `reporter.py`, `search.py`, and `manager.py`.
- Integrate CLI commands: `corpus-status`, `corpus-stats`, `corpus-coverage`, `corpus-verify`, and `corpus-report`.
- Support streaming AUAO v1.0 ontology coverage calculation across 10,000,000+ data lake records.

### Phase 5: Additional Dataset Integrations
- Integrate WildTeaming, TensorTrust, PoisonedRAG, BIORXIV security traces, and OWASP GenAI benchmark suites into `plugins/datasets/`.

---

## 🔵 Future Strategic Roadmap (2026 - 2028)

### Phase 6: Swarm Attack Generation Engines
- **Autonomous Red Teaming Swarms**: Multi-agent reinforcement learning (MARL) and evolutionary prompt generation engines synthesizing zero-day AUAO payloads.
- **Cross-Modal Attack Generators**: Generative visual steganography and sub-audible speech prompt injection generators.

### Phase 7: Real-Time Web Dashboard & Visualizer
- **Interactive UI**: Next.js / Vite web application visualizing AUAO graph relationships (Neo4j interface), live ingestion statistics, and attack category heatmaps.
- **Interactive Playground**: Web interface for inspecting normalized multi-turn conversation traces.

### Phase 8: Distributed Streaming & Cloud Execution
- **Ray / Celery Integration**: Sharding ingestion, normalization, and evaluation jobs across distributed GPU worker clusters.
- **Cloud Connectors**: Native data lake sync connectors for AWS S3, Google Cloud Storage (GCS), and Azure Blob Storage.

### Phase 9: AegisSwarm Community Edition & Research Publications
- **Academic Paper Publication**: Submit AUAO v1.0 whitepaper to top AI security conferences (IEEE S&P, USENIX Security, NeurIPS AI Safety Track).
- **Public Benchmark Leaderboard**: Host open leaderboard benchmarking commercial and open-weight LLMs against AUAO attack categories.
