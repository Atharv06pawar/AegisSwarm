# AegisSwarm Security Policy

The AegisSwarm maintainers take the security of AI models, autonomous swarms, red-teaming infrastructure, and our dataset ingestion pipeline seriously. We encourage responsible disclosure of vulnerabilities in AegisSwarm code, dependencies, or the AegisSwarm Universal Attack Ontology (AUAO v1.0).

---

## 1. Supported Versions

Security updates and security-related patches are provided for the following versions:

| Version | Supported | Maintenance End Date |
| :--- | :---: | :--- |
| `v2.x` (Current Development) | Yes | Active Development |
| `v1.x` | Yes | December 31, 2026 |
| `< 1.0` | No | End of Life |

---

## 2. Reporting a Vulnerability

**DO NOT report security vulnerabilities through public GitHub issues or public discussions.**

If you discover a security flaw in AegisSwarm (e.g., remote code execution in tool execution sandboxes, data lake path traversal vulnerabilities, or memory safety exploits in generator pipelines):

1. **Email Contact**: Send a detailed report to `security@aegisswarm.org` (or contact project maintainers via encrypted email).
2. **Report Contents**: Include the following details in your submission:
   - Type of vulnerability (e.g., Path Traversal, Arbitrary Code Execution, Injection).
   - Component affected (`core/orchestrator.py`, `storage/data_lake.py`, CLI commands, or specific dataset plugins).
   - Step-by-step reproduction instructions or Proof-of-Concept (PoC) script.
   - Potential impact and suggested mitigation steps.

---

## 3. Expected Response Timeline

The AegisSwarm Security Team commits to the following SLA:

- **Initial Acknowledgment**: Within 24 hours of receipt.
- **Triage & Risk Rating**: Within 72 hours of receipt.
- **Patch Release & Advisory**: Within 14 business days for critical vulnerabilities; 30 business days for medium/low vulnerabilities.

---

## 4. Responsible Disclosure & Bounty Guidelines

- **Coordinated Disclosure**: We follow a 90-day coordinated disclosure policy. We request that you give us reasonable time to fix the issue before making any public announcement.
- **Safe Harbor**: If you conduct your security research in accordance with this policy, we consider your research to be authorized, and we will not pursue legal action against you.

---

## 5. Safe Handling of AI Attack Datasets

AegisSwarm processes adversarial attack prompts, jailbreaks, prompt injection payloads, and exploit vectors targeting Large Language Models and AI agents.

> [!CAUTION]
> **Adversarial Content Notice**: AegisSwarm dataset plugins download and parse raw attack artifacts (e.g., JailbreakBench, HackAPrompt, AdvBench, Garak). These artifacts contain hostile prompt strings designed to bypass LLM safety guardrails. Maintainers and researchers MUST ensure these payloads are executed ONLY inside sandboxed evaluation environments and NEVER evaluated directly on unmonitored production API endpoints.
