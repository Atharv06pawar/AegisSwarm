# AegisSwarm Universal AI Attack Corpus Research Whitepaper

**Generated UTC Timestamp**: `2026-08-08T10:21:55.761575+00:00`  
**Ontology Framework**: `AegisSwarm Universal Attack Ontology (AUAO v1.0)`  
**Data Lake Status**: `HEALTHY`

---

## 1. Executive Summary

This publication report presents the authoritative status of the **AegisSwarm AI Attack Corpus**. The corpus currently unifies **7 benchmark datasets** comprising **22 AttackRecord entries** across **22 conversation turns** and **22 messages**. Physical data lake storage footprint spans **0.01 MB** across **7 partition files**.

## 2. Corpus Overview

| Metric | Value |
| :--- | :--- |
| **Total Datasets** | 7 |
| **Total Partitions** | 7 |
| **Total Records** | 22 |
| **Total Turns** | 22 |
| **Total Messages** | 22 |
| **Storage Size** | 0.01 MB |
| **Data Lake Health** | `HEALTHY` (100.0%) |

## 3. Dataset Inventory

| Dataset ID | Partitions | Formats | Total Size (Bytes) |
| :--- | :---: | :--- | :--- |
| `advbench` | 1 | jsonl.gz | 708 |
| `agentdojo` | 1 | jsonl.gz | 617 |
| `garak` | 1 | jsonl.gz | 723 |
| `hackaprompt` | 1 | jsonl.gz | 1,432 |
| `jailbreakbench` | 1 | jsonl.gz | 724 |
| `promptinject` | 1 | jsonl.gz | 734 |
| `pyrit` | 1 | jsonl.gz | 623 |

## 4. Corpus Statistics

- **Average Turns per Record**: `1.0`
- **Average Messages per Record**: `1.0`
- **Average Injection Prompt Length**: `61.73` characters
- **Maximum Prompt Length**: `101` characters
- **Minimum Prompt Length**: `9` characters
- **Overall Evaluation Success Rate**: `77.27%`
- **Average Severity Score**: `5.73 / 10.0`

## 5. AUAO v1.0 Coverage Analysis

- **Total Taxonomy Nodes**: `79`
- **Represented Taxonomy Nodes**: `4`
- **Coverage Percentage**: `5.06%`

### Root Class Representation (`AUAO-RC-*`)

| Root Domain ID | Record Count | Representation |
| :--- | :--- | :--- |
| `AUAO-RC-01` | 8 | ✅ Covered |
| `AUAO-RC-02` | 2 | ✅ Covered |
| `AUAO-RC-03` | 0 | ❌ Uncovered |
| `AUAO-RC-04` | 0 | ❌ Uncovered |
| `AUAO-RC-05` | 0 | ❌ Uncovered |
| `AUAO-RC-06` | 0 | ❌ Uncovered |
| `AUAO-RC-07` | 0 | ❌ Uncovered |
| `AUAO-RC-08` | 0 | ❌ Uncovered |
| `AUAO-RC-09` | 0 | ❌ Uncovered |
| `AUAO-RC-10` | 0 | ❌ Uncovered |

## 6. Quality Metrics Audit

- **Audited Records**: `22`
- **Schema Compliance Rate**: `100.00%`
- **Validation Pass Rate**: `0.00%`
- **Annotation Confidence Average**: `0.0`
- **Evaluation Completeness**: `100.00%`
- **Duplicate Sample IDs**: `0`
- **Duplicate Semantic Hashes**: `2`

## 7. Data Lake Cryptographic Verification Status

- **Overall Status**: `HEALTHY`
- **Total Partitions Scanned**: `7`
- **Verified Files**: `7`
- **Missing Files**: `0`
- **Corrupted Files**: `0`
- **Modified Files**: `0`
- **Verification Percentage**: `100.0%`

## 8. Target Models Evaluated

- `claude-2`
- `claude-3-5-sonnet`
- `flan-t5-xxl`
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`
- `llama-2-70b`
- `llama-2-70b-chat`
- `llama-3-8b`
- `mistral-7b`
- `vicuna-13b`
- `vicuna-7b`

## 9. Taxonomy Distribution

| AUAO Taxonomy Node | Record Count |
| :--- | :--- |
| `AUAO-JB-ADV-GCG` | 2 |
| `AUAO-PI-IND-DOC-PDF` | 2 |
| `AUAO-PI-DIR-RO-AUTH-SYS` | 5 |
| `Direct Prompt Injection` | 10 |
| `Jailbreak -> Physical Harm` | 1 |
| `Jailbreak -> Hate Speech` | 1 |
| `AUAO-PI-DIR-DEL-XML` | 1 |

## 10. Recommendations & Future Work

1. **Expand Taxonomy Coverage**: Ingest additional datasets (WildTeaming, TensorTrust, PoisonedRAG) to cover unrepresented leaf nodes.
2. **Multimodal Payload Ingestion**: Increase dataset coverage for visual steganography and audio injection vectors (`AUAO-RC-10`).
3. **Distributed Ingestion Engine**: Scale chunked streaming ingestion using Ray worker nodes for multi-terabyte benchmarking.

---
*AegisSwarm Corpus Reporter — Publication Standard RFC 2026*