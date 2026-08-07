# AegisSwarm Integrated Dataset Catalog

This document details all 7 integrated dataset benchmark plugins supported by AegisSwarm V2.

---

## 1. HackAPrompt

- **Purpose**: Global competition dataset for measuring LLM vulnerability to direct prompt injection and system prompt subversion.
- **Original Source**: [HackAPrompt Competition (HuggingFace)](https://huggingface.co/datasets/HackAPrompt/HackAPrompt-dataset)
- **License**: CC-BY-4.0
- **Attack Categories**: System Prompt Override, Delimiter Hijacking, Role Override.
- **Mapping Strategy**: Single-turn user prompt mapping (`is_injection_source = True`). Competition levels map to `difficulty_level = "Level {level}"`.
- **Primary AUAO Mapping**: `AUAO-PI-DIR-RO-AUTH-SYS`
- **Known Limitations**: Lacks multi-turn context; limited to single-turn text prompts.
- **Implementation Status**: `COMPLETED` (`plugins/datasets/hackaprompt.py`)

---

## 2. JailbreakBench

- **Purpose**: Open benchmark evaluating LLM safety alignment and refusal boundaries against curated jailbreak prompts.
- **Original Source**: [JailbreakBench (GitHub)](https://github.com/JailbreakBench/jailbreakbench)
- **License**: MIT
- **Attack Categories**: Persona Override, Hypothetical Roleplay, Cybercrime, Physical Harm.
- **Mapping Strategy**: Single-turn prompt mapping. Binary `jailbroken` flag maps directly to `EvaluationMetadata.attack_success`.
- **Primary AUAO Mapping**: `AUAO-JB-HYP-GAME`
- **Known Limitations**: Single-turn prompts; relies on external model judges for refusal classification.
- **Implementation Status**: `COMPLETED` (`plugins/datasets/jailbreakbench.py`)

---

## 3. AgentDojo

- **Purpose**: Dynamic execution benchmark evaluating indirect prompt injection in tool-using autonomous AI agents.
- **Original Source**: [AgentDojo Framework (GitHub)](https://github.com/dreadnode/agentdojo)
- **License**: MIT
- **Attack Categories**: Indirect Document Injection, Web Scraping DOM Injection, Tool Parameter Hijacking.
- **Mapping Strategy**: Multi-turn agent transcript mapping (`ConversationTurn`). Tool calls mapped to `ToolCall(tool_call_id, tool_name, arguments)`. Injected text tagged as `is_injection_source = True`.
- **Primary AUAO Mapping**: `AUAO-PI-IND-DOC-PDF`, `AUAO-TL-PARAM-CMD`
- **Known Limitations**: Requires tool execution environment context.
- **Implementation Status**: `COMPLETED` (`plugins/datasets/agentdojo.py`)

---

## 4. PyRIT (Python Risk Identification Tool)

- **Purpose**: Microsoft automation framework for multi-turn red teaming, Crescendo strategies, and TAP attacks.
- **Original Source**: [Azure PyRIT (GitHub)](https://github.com/Azure/PyRIT)
- **License**: MIT
- **Attack Categories**: Crescendo Multi-Turn Drift, GCG Adversarial Suffixes, Base64 Encoding.
- **Mapping Strategy**: Parses full multi-turn conversation traces into ordered `ConversationTurn` arrays. Strategy maps to `interaction_type = "Multi-Turn Sequential"`.
- **Primary AUAO Mapping**: `AUAO-JB-MULTI-CREEP`, `AUAO-JB-ADV-GCG`
- **Known Limitations**: Multi-turn transcripts vary depending on red-teaming orchestrator configuration.
- **Implementation Status**: `COMPLETED` (`plugins/datasets/pyrit.py`)

---

## 5. Garak (Generative AI Vulnerability Scanner)

- **Purpose**: Automated vulnerability scanner probing LLMs for safety filter bypass, prompt leakage, and encoding flaws.
- **Original Source**: [Garak (GitHub)](https://github.com/leondz/garak)
- **License**: Apache-2.0
- **Attack Categories**: Base64 Obfuscation, System Prompt Leakage, Continuation Attacks.
- **Mapping Strategy**: Maps Garak probe hits (`passed = False` -> `attack_success = True`). Probe module path determines AUAO node.
- **Primary AUAO Mapping**: `AUAO-MM-OBF-B64`, `AUAO-LK-DIR-REPEAT`
- **Known Limitations**: Evaluates single probes independently.
- **Implementation Status**: `COMPLETED` (`plugins/datasets/garak.py`)

---

## 6. PromptInject

- **Purpose**: Quantitative evaluation framework measuring LLM robustness against rogue instructions and delimiter escapes.
- **Original Source**: [PromptInject (GitHub)](https://github.com/prompthing/promptinject)
- **License**: MIT
- **Attack Categories**: XML Delimiter Escape, Markdown Escape, Persona Change.
- **Mapping Strategy**: Concatenates base instructions and injected payloads into structured user turns with explicit injection source tagging.
- **Primary AUAO Mapping**: `AUAO-PI-DIR-DEL-XML`, `AUAO-PI-DIR-DEL-MD`
- **Known Limitations**: Synthetic prompt composition templates.
- **Implementation Status**: `COMPLETED` (`plugins/datasets/promptinject.py`)

---

## 7. AdvBench

- **Purpose**: Standard benchmark of harmful behavior goals and adversarial GCG token suffixes.
- **Original Source**: [LLM-Attacks / AdvBench (GitHub)](https://github.com/llm-attacks/llm-attacks)
- **License**: MIT
- **Attack Categories**: Greedy Coordinate Gradient (GCG) Adversarial Suffixes, Harmful Goals.
- **Mapping Strategy**: Harmful goals and adversarial prompt suffixes mapped as primary injection source payload.
- **Primary AUAO Mapping**: `AUAO-JB-ADV-GCG`
- **Known Limitations**: Static prompt string list; requires model execution for success evaluation.
- **Implementation Status**: `COMPLETED` (`plugins/datasets/advbench.py`)
