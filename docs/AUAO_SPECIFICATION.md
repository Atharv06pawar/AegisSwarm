# AegisSwarm Universal Attack Ontology (AUAO v1.0) Specification

**Standard Reference**: AUAO-STD-2026-01  
**Status**: Formal Research Specification  
**Version**: 1.0.0  

---

## 1. Overview & Philosophy

The **AegisSwarm Universal Attack Ontology (AUAO v1.0)** is an international, open-standard framework for representing attack vectors, security exploits, alignment bypasses, and threat behaviors across AI foundation models, autonomous agents, RAG systems, Model Context Protocol (MCP) ecosystems, and multi-agent swarms.

AUAO functions as the "MITRE ATT&CK for AI Security", providing a graph-relational ontology designed for 10-year durability, Neo4j / RDF compatibility, and Pydantic v2 validation.

---

## 2. Root Classes (`AUAO-RC-01` to `AUAO-RC-10`)

AUAO categorizes all known AI security threats into 10 foundational root domains:

1. `AUAO-RC-01`: **Prompt Injection** (Direct & Indirect instruction subversion).
2. `AUAO-RC-02`: **Safety Filter Bypass & Jailbreaking** (RLHF alignment override, persona exploits, GCG suffixes).
3. `AUAO-RC-03`: **System Prompt & Context Leakage** (Verbatim developer instruction exfiltration, Chain-of-Thought leakage).
4. `AUAO-RC-04`: **Tool, Function Calling & Plugin Abuse** (Parameter hijacking, unauthorized tool execution).
5. `AUAO-RC-05`: **Model Context Protocol (MCP) Exploitation** (Rogue MCP server discovery, prompt template poisoning).
6. `AUAO-RC-06`: **RAG, Context & Knowledge Base Poisoning** (Vector DB contamination, embedding collisions).
7. `AUAO-RC-07`: **Agent Memory & State Manipulation** (Episodic vector memory corruption, scratchpad state injection).
8. `AUAO-RC-08`: **Multi-Agent & Autonomous Swarm Cascades** (Agent impersonation, consensus poisoning, viral payload propagation).
9. `AUAO-RC-09`: **Remote Code Execution & System Abuse** (Python REPL breakout, shell injection, path traversal).
10. `AUAO-RC-10`: **Multimodal, Structural & Obfuscated Attacks** (Visual steganography, Base64/Unicode obfuscation).

---

## 3. Taxonomy Tree & Node Hierarchy

The taxonomy comprises 79 recursive nodes, structuring attacks down to terminal leaf nodes (`is_leaf: true`).

```
Prompt Injection (AUAO-RC-01)
├── Direct Prompt Injection (AUAO-PI-DIR)
│   ├── Role Override (AUAO-PI-DIR-RO)
│   │   ├── Authority Override (AUAO-PI-DIR-RO-AUTH)
│   │   │   ├── System Prompt Override (AUAO-PI-DIR-RO-AUTH-SYS) [LEAF]
│   │   │   └── Admin Privilege Escalation (AUAO-PI-DIR-RO-AUTH-ADM) [LEAF]
│   │   └── Persona Hijacking (AUAO-PI-DIR-RO-PERS) [LEAF]
│   └── Delimiter Hijacking (AUAO-PI-DIR-DEL)
│       ├── XML/HTML Tag Manipulation (AUAO-PI-DIR-DEL-XML) [LEAF]
│       ├── Markdown Code Block Escape (AUAO-PI-DIR-DEL-MD) [LEAF]
│       └── JSON Key/Value Injection (AUAO-PI-DIR-DEL-JSON) [LEAF]
└── Indirect Prompt Injection (AUAO-PI-IND)
    ├── Document / File Injection (AUAO-PI-IND-DOC-PDF) [LEAF]
    ├── Web Page / Scraping Injection (AUAO-PI-IND-WEB-DOM) [LEAF]
    └── API Response Injection (AUAO-PI-IND-API-JSON) [LEAF]
```

---

## 4. Graph Edge Relationships

AUAO defines 11 formal directed graph edge types connecting taxonomy nodes and security entities:

- `USES`: Indicates payload encoding or sub-technique usage.
- `TARGETS`: Specifies architecture component targeted.
- `CAUSES`: Maps attack technique to security consequence.
- `ESCALATES_TO`: Denotes privilege escalation.
- `REQUIRES`: Specifies runtime prerequisites (tools, browser, RAG).
- `BYPASSES`: Identifies guardrail or refusal filter evaded.
- `LEADS_TO`: Defines multi-stage attack chaining.
- `MITIGATED_BY`: Maps security control or architecture defense.
- `OBSERVED_IN`: Links technique to public benchmark datasets.
- `SIMILAR_TO`: Establishes tactical similarity.
- `DEPENDS_ON`: Identifies prerequisite execution steps.

---

## 5. Attack Properties & Data Dictionary

Defined in `ontology/attack_properties.json`, specifying 53 canonical properties across 10 groups:
- **Identity**: `record_id`, `attack_id`, `ontology_node`, `ontology_path`, `aliases`.
- **Classification**: `root_class`, `family`, `technique`, `taxonomy_depth`, `is_leaf`.
- **Characteristics**: `attack_vector`, `delivery_method`, `interaction_type`, `turn_count`, `encoding`, `obfuscation`, `payload_type`, `stealth_level`, `difficulty`.
- **Target**: `target_type`, `target_component`, `target_model`, `target_framework`.
- **Execution**: `requires_tools`, `requires_browser`, `requires_code_execution`, `requires_mcp`, `requires_rag`.
- **Impact**: `confidentiality_impact`, `integrity_impact`, `availability_impact`, `overall_severity`, `risk_score`.
- **Evaluation**: `attack_success`, `evaluation_method`, `judge_model`.
- **Provenance**: `dataset_name`, `parser_version`, `raw_sha256`, `ingestion_timestamp`.

---

## 6. Versioning & Evolution

AUAO follows Semantic Versioning 2.0.0 (SemVer):
- **Major (vX.0.0)**: Breaking schema alterations or node removals.
- **Minor (v1.X.0)**: Adding new taxonomy sub-nodes or dataset mappings.
- **Patch (v1.0.X)**: Bug fixes in regexes or metadata documentation.
- **Deprecation**: Deprecated nodes maintain a 6-month grace period before removal.
