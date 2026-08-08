# AegisSwarm Dataset Plugin Production Audit (Sprint 7.1)

## Executive Summary

This document provides a comprehensive production readiness audit of all 7 dataset ingestion plugins in AegisSwarm:
1. **HackAPrompt** (`hackaprompt`)
2. **JailbreakBench** (`jailbreakbench`)
3. **PromptInject** (`promptinject`)
4. **AdvBench** (`advbench`)
5. **Garak** (`garak`)
6. **PyRIT** (`pyrit`)
7. **AgentDojo** (`agentdojo`)

Each audit section details the current implementation of `fetch()`, `parse()`, `normalize()`, and `validate()`, checks for synthetic placeholder generation, verifies licensing and legal distribution constraints, defines the required local directory structure, identifies missing production capabilities, and estimates the engineering effort required for production ingestion.

---

## 1. HackAPrompt Plugin (`hackaprompt`)

### Metadata & Overview
- **Dataset ID**: `hackaprompt`
- **Parser Version**: `1.0.0`
- **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)
- **Official Source**: Hugging Face Datasets (`https://huggingface.co/datasets/HackAPrompt/HackAPrompt-dataset`)

### Implementation Audit
- **`fetch()` Implementation**:
  Checks for local existence of `raw/hackaprompt/dataset.jsonl`. If absent, it logs a warning and generates 2 synthetic JSONL fallback rows (`"prompt": "Ignore everything..."` and `"prompt": "Translate to French..."`).
- **`parse()` Implementation**:
  Memory-safe generator supporting `.jsonl`, `.csv`, and `.json`. Reads `.jsonl` and `.csv` line-by-line. Uses standard `json.load()` for `.json` files.
- **`normalize()` Implementation**:
  Maps single-turn prompts to `ConversationTurn(MessageRole.USER, is_injection_source=True)`. Assigns taxonomy node `"Direct Prompt Injection"` and difficulty level `f"Level {level}"`. Sets historical `attack_success=True` and default `severity_score=5.0`.
- **`validate()` Implementation**:
  Filters out records where injection source text is empty or whitespace-only.

### Production Assessment
- **Synthetic Data Generated**: **YES** (Generates 2 mock rows in `fetch()` if missing).
- **Automatic Download Permitted**: **YES** (`CC-BY-4.0` open dataset).
- **Required Local Directory Structure**:
  ```
  raw/hackaprompt/
  ├── dataset.jsonl (or dataset.csv / hackaprompt_v1.json)
  ```
- **Supported File Formats**: `.jsonl`, `.csv`, `.json`.
- **Missing Production Functionality**:
  1. Automatic HTTP/Hugging Face Hub streaming fetch from official dataset repository.
  2. Complete field mapping for multi-level competition submissions, scores, and judge evaluation tokens.
  3. Fine-grained AUAO taxonomy classification (`AUAO-PI-DIR-*` specific nodes instead of generic text string).
- **Estimated Implementation Effort**: **Low (2 - 3 hours)**.

---

## 2. JailbreakBench Plugin (`jailbreakbench`)

### Metadata & Overview
- **Dataset ID**: `jailbreakbench`
- **Parser Version**: `1.0.0`
- **License**: MIT License (`MIT`)
- **Official Source**: JailbreakBench GitHub Repository (`https://github.com/JailbreakBench/jailbreakbench`) / HuggingFace `JailbreakBench/JailbreakBench`

### Implementation Audit
- **`fetch()` Implementation**:
  Checks for `raw/jailbreakbench/dataset.jsonl`. If missing, creates the directory and writes 2 synthetic JSONL records representing bomb-building and hate-speech jailbreak attempts.
- **`parse()` Implementation**:
  Memory-safe generator for `.jsonl` and `.json`.
- **`normalize()` Implementation**:
  Maps `goal`, `prompt`, `category`, `behavior`, `target_model`, `jailbroken` to single-turn `AttackRecord`. Assigns taxonomy node `f"Jailbreak -> {category}"`, `difficulty_level="Hard"`, `severity_score=8.0`, and `evaluator_model="jailbreakbench_judge"`.
- **`validate()` Implementation**:
  Filters out records with empty or whitespace-only prompt strings.

### Production Assessment
- **Synthetic Data Generated**: **YES** (Generates 2 mock rows in `fetch()` if missing).
- **Automatic Download Permitted**: **YES** (`MIT` License, open public repository).
- **Required Local Directory Structure**:
  ```
  raw/jailbreakbench/
  ├── dataset.jsonl (or prompts_artifacts.json)
  ```
- **Supported File Formats**: `.jsonl`, `.json`.
- **Missing Production Functionality**:
  1. Automated Git / HTTP release asset downloader or integration with `jailbreakbench` Python package API.
  2. Dynamic taxonomy node mapping to specific AUAO sub-classes (`AUAO-JB-ADV-GCG`, `AUAO-JB-HYP-GAME`, etc.).
  3. Multi-prompt pair parsing for defense evaluation artifacts and target model responses.
- **Estimated Implementation Effort**: **Low (2 - 4 hours)**.

---

## 3. PromptInject Plugin (`promptinject`)

### Metadata & Overview
- **Dataset ID**: `promptinject`
- **Parser Version**: `1.0.0`
- **License**: MIT License (`MIT`)
- **Official Source**: PromptInject GitHub Repository (`https://github.com/prompthing/promptinject`)

### Implementation Audit
- **`fetch()` Implementation**:
  Checks for `raw/promptinject/dataset.jsonl`. If missing, creates the directory and writes 2 synthetic JSONL records (XML tag escape and persona change vectors).
- **`parse()` Implementation**:
  Memory-safe generator supporting `.jsonl`, `.csv`, `.json`, and `.parquet` (via Pandas).
- **`normalize()` Implementation**:
  Maps `base_prompt`, `injected_prompt`, `attack_type`, `target_model`, `similarity_score` to canonical `AttackRecord`. Assigns specific AUAO taxonomy nodes (`AUAO-PI-DIR-DEL-XML`, `AUAO-PI-DIR-RO-PERS`, `AUAO-MM-OBF-B64`, etc.).
- **`validate()` Implementation**:
  Verifies presence of turns and non-empty injection source content.

### Production Assessment
- **Synthetic Data Generated**: **YES** (Generates 2 mock rows in `fetch()` if missing).
- **Automatic Download Permitted**: **YES** (`MIT` License, open-source dataset).
- **Required Local Directory Structure**:
  ```
  raw/promptinject/
  ├── dataset.jsonl (or promptinject_data.json / data.parquet)
  ```
- **Supported File Formats**: `.jsonl`, `.json`, `.csv`, `.parquet`.
- **Missing Production Functionality**:
  1. Automated GitHub raw dataset file release downloader.
  2. Integration with PromptInject Python framework generator to dynamically build custom attack matrices.
  3. Expanded artifact type mapping for encoded HTML/Markdown payloads.
- **Estimated Implementation Effort**: **Medium (3 - 5 hours)**.

---

## 4. AdvBench Plugin (`advbench`)

### Metadata & Overview
- **Dataset ID**: `advbench`
- **Parser Version**: `1.0.0`
- **License**: MIT License (`MIT`)
- **Official Source**: `llm-attacks` GitHub Repository (`https://github.com/llm-attacks/llm-attacks/tree/main/data/advbench`)

### Implementation Audit
- **`fetch()` Implementation**:
  Checks for `raw/advbench/dataset.jsonl`. If missing, creates directory and writes 2 synthetic JSONL records (Cybercrime GCG adversarial suffix and Network Security harmful goal).
- **`parse()` Implementation**:
  Memory-safe generator supporting `.jsonl`, `.csv`, `.json`, and `.parquet`.
- **`normalize()` Implementation**:
  Maps `goal`, `prompt`, `target`, `category`, `target_model`, `attack_success` to `AttackRecord`. Assigns taxonomy node `AUAO-JB-ADV-GCG` or `AUAO-PI-DIR-RO-PERS` with `severity_score` (8.5 on success, 3.0 on failure).
- **`validate()` Implementation**:
  Verifies non-empty injection text and goal instruction.

### Production Assessment
- **Synthetic Data Generated**: **YES** (Generates 2 mock rows in `fetch()` if missing).
- **Automatic Download Permitted**: **RESTRICTED / DUAL-USE**. Distribution is MIT-licensed, but raw dataset files contain dual-use harmful instructions (`harmful_behaviors.csv` and `harmful_strings.csv`). Automated download requires explicit local folder placement or explicit user confirmation.
- **Required Local Directory Structure**:
  ```
  raw/advbench/
  ├── harmful_behaviors.csv
  ├── harmful_strings.csv
  └── dataset.jsonl (optional converted format)
  ```
- **Supported File Formats**: `.jsonl`, `.csv`, `.json`, `.parquet`.
- **Missing Production Functionality**:
  1. Direct CSV parser for raw `harmful_behaviors.csv` and `harmful_strings.csv` columns as formatted in the official `llm-attacks` repository.
  2. Local directory presence check with explicit validation error messages when raw CSV files are missing.
  3. GCG adversarial suffix isolation into dedicated `Artifact` fields.
- **Estimated Implementation Effort**: **Medium (3 - 4 hours)**.

---

## 5. Garak Plugin (`garak`)

### Metadata & Overview
- **Dataset ID**: `garak`
- **Parser Version**: `1.0.0`
- **License**: Apache License 2.0 (`Apache-2.0`)
- **Official Source**: Garak Vulnerability Scanner (`https://github.com/leondz/garak`)

### Implementation Audit
- **`fetch()` Implementation**:
  Checks for `raw/garak/dataset.jsonl`. If missing, creates directory and writes 2 synthetic Garak hitlog JSONL records (`encoding.Base64` hit and `leakto.SystemPromptLeak` hit).
- **`parse()` Implementation**:
  Memory-safe generator supporting `.jsonl`, `.csv`, `.json`, and `.parquet`.
- **`normalize()` Implementation**:
  Maps `probe_name`, `detector_name`, `generator_name`, `target_model`, `prompt`, `output`, `passed` to `AttackRecord`. Assigns AUAO taxonomy nodes (`AUAO-MM-OBF-B64`, `AUAO-LK-DIR-REPEAT`, `AUAO-JB-HYP-GAME`, etc.).
- **`validate()` Implementation**:
  Verifies non-empty prompt payloads.

### Production Assessment
- **Synthetic Data Generated**: **YES** (Generates 2 mock rows in `fetch()` if missing).
- **Automatic Download Permitted**: **YES** (`Apache-2.0` License).
- **Required Local Directory Structure**:
  ```
  raw/garak/
  ├── garak_runs/
  │   └── *.hitlog.jsonl
  └── dataset.jsonl (optional unified log)
  ```
- **Supported File Formats**: `.jsonl`, `.json`, `.csv`, `.parquet`.
- **Missing Production Functionality**:
  1. Native directory scanner for Garak's default hitlog output directory (`~/.local/share/garak/garak_runs/*.hitlog.jsonl`).
  2. Comprehensive probe-to-AUAO mapping table covering all 50+ Garak probe modules.
  3. Extraction of detector confidence scores and generator hyperparameters.
- **Estimated Implementation Effort**: **Medium (4 - 6 hours)**.

---

## 6. PyRIT Plugin (`pyrit`)

### Metadata & Overview
- **Dataset ID**: `pyrit`
- **Parser Version**: `1.0.0`
- **License**: MIT License (`MIT`)
- **Official Source**: Microsoft PyRIT Framework (`https://github.com/Azure/PyRIT`)

### Implementation Audit
- **`fetch()` Implementation**:
  Checks for `raw/pyrit/dataset.jsonl`. If missing, creates directory and writes 2 synthetic multi-turn traces (Crescendo strategy and Base64 converter).
- **`parse()` Implementation**:
  Memory-safe generator supporting `.jsonl`, `.csv`, `.json`, and `.parquet`. Handles nested JSON conversation strings in CSV rows.
- **`normalize()` Implementation**:
  Maps multi-turn conversation lists (`role`, `content`, `is_injection`), `attack_strategy`, `target_system`, `evaluator_model`, `score`, `tool_calls`, `artifacts`, and `embedding` references to canonical `AttackRecord`. Assigns AUAO taxonomy nodes (`AUAO-JB-MULTI-CREEP`, `AUAO-JB-ADV-GCG`, `AUAO-MM-OBF-B64`, etc.).
- **`validate()` Implementation**:
  Validates multi-turn sequence integrity and injection source presence.

### Production Assessment
- **Synthetic Data Generated**: **YES** (Generates 2 mock rows in `fetch()` if missing).
- **Automatic Download Permitted**: **YES** (`MIT` License, Microsoft PyRIT repository).
- **Required Local Directory Structure**:
  ```
  raw/pyrit/
  ├── pyrit_duckdb.db (or pyrit_export.json)
  └── dataset.jsonl
  ```
- **Supported File Formats**: `.jsonl`, `.json`, `.csv`, `.parquet`.
- **Missing Production Functionality**:
  1. Native SQLite / DuckDB ingestion connector for PyRIT's default memory database file (`pyrit_duckdb.db`).
  2. Preservation of multi-turn tool call execution trees across 5+ conversation turns.
  3. Dynamic embedding vector extraction and storage.
- **Estimated Implementation Effort**: **High (5 - 8 hours)**.

---

## 7. AgentDojo Plugin (`agentdojo`)

### Metadata & Overview
- **Dataset ID**: `agentdojo`
- **Parser Version**: `1.0.0`
- **License**: MIT License (`MIT`)
- **Official Source**: AgentDojo GitHub Repository (`https://github.com/dreadnode/agentdojo` / `https://github.com/epfl-dlab/agentdojo`)

### Implementation Audit
- **`fetch()` Implementation**:
  Checks for `raw/agentdojo/dataset.jsonl`. If missing, creates directory and writes 2 synthetic agent interaction scenarios (Email agent indirect injection and Filesystem agent indirect injection).
- **`parse()` Implementation**:
  Memory-safe generator supporting `.jsonl`, `.json`, and `.parquet`.
- **`normalize()` Implementation**:
  Maps `scenario_id`, `environment`, `user_task`, `injection_task`, `tools_available`, `injection_vector`, `conversation` (including `role="tool"`, `tool_calls`, `is_injection=True`) to canonical `AttackRecord`. Assigns AUAO taxonomy nodes (`AUAO-PI-IND-DOC-PDF`, `AUAO-PI-IND-WEB-DOM`, `AUAO-TL-PARAM-CMD`, `AUAO-TL-UNAUTH-BYPASS`).
- **`validate()` Implementation**:
  Asserts presence of turns and injection sources.

### Production Assessment
- **Synthetic Data Generated**: **YES** (Generates 2 mock rows in `fetch()` if missing).
- **Automatic Download Permitted**: **YES** (`MIT` License, open-source benchmark).
- **Required Local Directory Structure**:
  ```
  raw/agentdojo/
  ├── benchmark_tasks.jsonl
  ├── suite_results.json
  └── dataset.jsonl
  ```
- **Supported File Formats**: `.jsonl`, `.json`, `.parquet`.
- **Missing Production Functionality**:
  1. Automated downloader for official AgentDojo benchmark suite tasks and evaluation traces.
  2. Environmental state tracking for tool execution outputs (email attachments, web DOM elements, filesystem trees).
  3. Deep inspection of tool parameter injection vectors.
- **Estimated Implementation Effort**: **High (6 - 8 hours)**.

---

## Summary Matrix & Implementation Checklist

| Dataset ID | License | Synthetic Fallback? | Auto Download Legal? | Required Raw File | Effort Estimate |
|---|---|---|---|---|---|
| `hackaprompt` | CC-BY-4.0 | YES | YES | `raw/hackaprompt/dataset.jsonl` | Low (2-3 hrs) |
| `jailbreakbench` | MIT | YES | YES | `raw/jailbreakbench/dataset.jsonl` | Low (2-4 hrs) |
| `promptinject` | MIT | YES | YES | `raw/promptinject/dataset.jsonl` | Medium (3-5 hrs) |
| `advbench` | MIT | YES | RESTRICTED (Local File Required) | `raw/advbench/harmful_behaviors.csv` | Medium (3-4 hrs) |
| `garak` | Apache-2.0 | YES | YES | `raw/garak/garak_runs/*.hitlog.jsonl` | Medium (4-6 hrs) |
| `pyrit` | MIT | YES | YES | `raw/pyrit/pyrit_duckdb.db` / `dataset.jsonl` | High (5-8 hrs) |
| `agentdojo` | MIT | YES | YES | `raw/agentdojo/benchmark_tasks.jsonl` | High (6-8 hrs) |

---

## Production Ingestion Implementation Checklist

- [ ] **Phase 1: Direct Remote Downloaders**
  - Implement HTTP / HuggingFace Hub downloaders for `hackaprompt`, `jailbreakbench`, `promptinject`, and `agentdojo`.
- [ ] **Phase 2: Local File Validation & Pre-flight Checks**
  - Implement pre-flight file validation for `advbench` (`harmful_behaviors.csv`) and `garak` (`*.hitlog.jsonl`).
  - Raise informative `FileNotFoundError` instructions if raw files are absent.
- [ ] **Phase 3: Database & Multi-Turn Extensions**
  - Implement DuckDB / SQLite connector for `pyrit` (`pyrit_duckdb.db`).
  - Enhance multi-turn tool call tree mapping for `agentdojo` and `pyrit`.
- [ ] **Phase 4: Synthetic Fallback Removal**
  - Remove all mock data creation from `fetch()` methods across all 7 plugins.
