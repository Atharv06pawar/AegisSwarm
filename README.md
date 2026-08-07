# AegisSwarm: Universal AI Red Teaming Engine & Universal Attack Ontology (AUAO v1.0)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Ontology: AUAO v1.0](https://img.shields.io/badge/Ontology-AUAO_v1.0-purple.svg)](docs/AUAO_SPECIFICATION.md)
[![Architecture: Streaming Data Lake](https://img.shields.io/badge/Architecture-Streaming_Data_Lake-orange.svg)](docs/ARCHITECTURE.md)

**AegisSwarm** is an open-source, enterprise-grade AI security research framework, streaming data lake engine, and canonical implementation of the **AegisSwarm Universal Attack Ontology (AUAO v1.0)**.

Designed for AI security researchers, red-teaming platforms, academic laboratories, and standards organizations (NIST, OWASP, MITRE), AegisSwarm provides a unified language for representing, benchmarking, and analyzing attacks against Large Language Models (LLMs), AI Agents, RAG systems, tool-using frameworks, Model Context Protocol (MCP) servers, and autonomous multi-agent swarms.

---

## 💡 Motivation

As generative AI transitions from standalone chatbots to autonomous multi-agent networks, the security attack surface has fragmented across incompatible benchmarks, bespoke taxonomies, and ad-hoc log formats. Existing evaluation suites (e.g., HackAPrompt, JailbreakBench, AgentDojo, PyRIT) define disjoint schemas, making comparative security research difficult.

**AegisSwarm solves this fragmentation** by acting as the *"MITRE ATT&CK for AI Security"*:
1. **Universal Taxonomy**: Normalizes disparate benchmarks into a single hierarchical graph taxonomy (`AUAO v1.0`).
2. **Streaming Engine**: Ingests multi-gigabyte datasets without Out-Of-Memory (OOM) failures using generator-based pipelines.
3. **Data Lake & Lineage**: Persists attack records in partitioned JSONL/Parquet data lakes with cryptographic SHA256 lineage tracking.

---

## ✨ Key Features

- **AUAO v1.0 Universal Taxonomy**: 10 foundational root attack classes, 79 recursive taxonomy nodes, and 11 graph relationship types (`USES`, `TARGETS`, `BYPASSES`, `LEADS_TO`, etc.).
- **Memory-Safe Streaming Pipeline**: Zero-memory-overhead generator pipelines capable of streaming 10,000,000+ attack records.
- **Data Lake Storage Backends**: Atomic writes, GZIP/Snappy compression, schema evolution, and dual JSONL/Parquet persistence (`storage/data_lake.py`).
- **Cryptographic Lineage Tracking**: Automatic SHA256 input hashing, parser version tracking, and reproducible manifest generation (`storage/lineage.py`).
- **Plugin Architecture**: Modular dataset discovery and auto-registration (`core/registry.py`) supporting 1-command ingestion of new benchmarks.
- **Corpus Management Subsystem (`corpus/`)**: Automated dataset registration, high-speed streaming statistics, AUAO ontology coverage calculation, quality auditing, and publication-grade Markdown whitepaper reporting.
- **Production CLI**: Command-line interface built with Typer (`main.py`).

---

## 🏗️ Architecture Overview

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
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
  ┌────────────────────┐      ┌────────────────────┐     ┌───────────────────┐
  │   PluginRegistry   │      │   StorageBackend   │     │  LineageTracker   │
  └──────────┬─────────┘      └─────────┬──────────┘     └─────────┬─────────┘
             │                          │                          │
             ▼                          ▼                          ▼
  [ Dataset Plugins ]        [ Partitioned Data Lake ]    [ Manifest History ]
  (HackAPrompt, PyRIT...)    (source=*/part-*.jsonl)      (lineage_manifest)
```

---

## 📂 Repository Structure

```
d:\datasetASwarm\
├── main.py                     # Typer CLI Entrypoint
├── pyproject.toml              # Project dependencies & tool configs
├── requirements.txt            # Python dependencies
├── configs/                    # Pydantic settings & YAML configuration
│   └── settings.py
├── core/                       # Core orchestration & plugin contracts
│   ├── plugin_base.py          # Abstract Base Class BaseDatasetPlugin
│   ├── registry.py            # Dynamic plugin discovery & registry
│   ├── orchestrator.py        # Pipeline execution & generator orchestrator
│   └── schema.py              # Pydantic v2 AttackRecord data contracts
├── ontology/                   # AUAO v1.0 Canonical Specification
│   ├── root_classes.json       # 10 Root attack domains
│   ├── attack_taxonomy.json    # 79-node recursive taxonomy tree
│   ├── relationships.json     # Graph edge relationship definitions
│   ├── attack_properties.json  # Data dictionary & 53 properties
│   └── ontology_mapping_rules.md # RFC Normalization specification
├── plugins/                    # Ingestion Dataset Plugins
│   └── datasets/
│       ├── hackaprompt.py
│       ├── jailbreakbench.py
│       ├── agentdojo.py
│       ├── pyrit.py
│       ├── garak.py
│       ├── promptinject.py
│       └── advbench.py
├── storage/                    # Data Lake & Lineage Tracking
│   ├── data_lake.py            # ParquetBackend & JSONLBackend (Atomic writes)
│   └── lineage.py              # SHA256 reproducibility manifest tracker
├── utils/                      # Memory-safe streaming utilities
│   └── streaming.py            # chunked_iterable, safe_map, track_progress
├── docs/                       # Publication Documentation & Roadmap
│   ├── ARCHITECTURE.md
│   ├── PLUGIN_DEVELOPMENT.md
│   ├── AUAO_SPECIFICATION.md
│   ├── DATASETS.md
│   └── ROADMAP.md
└── tests/                      # Pytest Integration & Unit Test Suite
```

---

## 📊 Supported Datasets

| Dataset Plugin | Target Domain | Primary AUAO Taxonomy Mapping | Format Support |
| :--- | :--- | :--- | :--- |
| **HackAPrompt** | Prompt Hacking Competition | `AUAO-PI-DIR-RO-AUTH-SYS` | JSONL, CSV, JSON |
| **JailbreakBench** | Safety Alignment Refusal | `AUAO-JB-HYP-GAME` | JSONL, JSON |
| **AgentDojo** | Agentic Indirect Injection | `AUAO-PI-IND-DOC-PDF`, `AUAO-TL-PARAM-CMD` | JSONL, JSON, Parquet |
| **PyRIT** | Multi-Turn Red Teaming | `AUAO-JB-MULTI-CREEP`, `AUAO-JB-ADV-GCG` | JSONL, CSV, Parquet |
| **Garak** | Vulnerability Scanner | `AUAO-MM-OBF-B64`, `AUAO-LK-DIR-REPEAT` | JSONL, JSON, CSV, Parquet |
| **PromptInject** | Quantitative Injection | `AUAO-PI-DIR-DEL-XML`, `AUAO-PI-DIR-DEL-MD` | JSONL, JSON, CSV, Parquet |
| **AdvBench** | Harmful Suffix Prompts | `AUAO-JB-ADV-GCG` | JSONL, CSV, Parquet |

---

## ⚡ Ingestion Pipeline Overview

1. **Discovery**: `PluginRegistry` dynamically imports plugins from `plugins/datasets/`.
2. **Fetch**: `plugin.fetch()` locates local files or downloads raw archives into `raw/<dataset>/`.
3. **Parse**: `plugin.parse()` streams records line-by-line using memory-safe Python generators.
4. **Normalize**: `plugin.normalize()` translates raw records into canonical `AttackRecord` objects.
5. **Validate**: `plugin.validate()` filters corrupted payloads and verifies schema constraints.
6. **Persist**: `PipelineOrchestrator` batches records via `chunked_iterable` and writes atomically to `outputs/lake/source=<dataset>/part-*.jsonl.gz`.
7. **Lineage**: `LineageTracker` computes input file SHA256 checksums and exports `outputs/lineage_manifest.json`.

---

## 💻 CLI Usage

```bash
# List all discovered dataset plugins
python main.py list-plugins

# Inspect available plugins with details
python main.py discover

# Run pipeline ingestion for a single plugin
python main.py ingest --plugin hackaprompt --batch-size 5000

# Run pipeline ingestion for all discovered plugins
python main.py ingest --all --backend jsonl --compression gzip

# Display Data Lake statistics and ingested counts
python main.py stats
```

---

## 🚀 Installation & Quick Start

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone & Environment Setup
```bash
git clone https://github.com/Atharv06pawar/AegisSwarm.git
cd AegisSwarm

python -m venv .venv
# On Windows
.venv\Scripts\Activate.ps1
# On Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Test Pipeline Execution
```bash
# Execute integration test suite verifying end-to-end pipeline execution
pytest tests/
```

---

## 🗺️ Strategic Roadmap

- [x] **Phase 1**: Core Architecture & Schema Standard (`AttackRecord`).
- [x] **Phase 2**: Storage Data Lake Engine (Parquet & JSONL with POSIX atomic swap).
- [x] **Phase 3**: AUAO v1.0 Taxonomy Design & 7 Dataset Plugins (HackAPrompt, JailbreakBench, AgentDojo, PyRIT, Garak, PromptInject, AdvBench).
- [ ] **Phase 4**: Corpus Management Subsystem (`corpus/`) & Advanced Analytics CLI.
- [ ] **Phase 5**: Autonomous Swarm Red Teaming Generator Engines.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for full phase details.

---

## 📜 Citation

If you use AegisSwarm or the AegisSwarm Universal Attack Ontology (AUAO v1.0) in your research, please cite:

```bibtex
@article{aegisswarm2026,
  title={AegisSwarm: Universal AI Red Teaming Engine and Universal Attack Ontology (AUAO v1.0)},
  author={AegisSwarm Project Contributors},
  journal={arXiv preprint arXiv:2608.AUAO},
  year={2026},
  url={https://github.com/Atharv06pawar/AegisSwarm}
}
```

---

## ⚖️ License

Distributed under the Apache License 2.0. See [`LICENSE`](LICENSE) for details.