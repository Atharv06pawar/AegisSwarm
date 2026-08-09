# AegisSwarm Research Automation Launchers & Production Validator Guide

This directory contains production-grade automated research environment launchers and runtime validators for Windows environments:
- **`run_research.bat`**: Windows Command Prompt batch launcher and validator.
- **`run_research.ps1`**: PowerShell research launcher and real-time system validator.

Both scripts automatically initialize, verify, ingest, execute, validate real system health, run mini end-to-end benchmarks, and launch the complete AegisSwarm V2 research ecosystem end-to-end.

---

## Quick Start

### Option 1: Using Windows Command Prompt (`run_research.bat`)

Open Command Prompt in the repository root directory and run:

```cmd
run_research.bat
```

### Option 2: Using PowerShell (`run_research.ps1`)

Open PowerShell in the repository root directory and run:

```powershell
.\run_research.ps1
```

> **Note for PowerShell execution policy**: If script execution is restricted on your machine, run PowerShell with:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\run_research.ps1
> ```

---

## What the Launcher & Validator Does (10 Automated Steps)

1. **Virtual Environment Activation**: Checks for `.venv\Scripts\Activate.ps1` and sources the Python virtual environment.
2. **Directory Structure Verification**: Ensures `outputs/`, `outputs/lake/`, `outputs/reports/`, `outputs/telemetry/`, `outputs/learning/`, `outputs/missions/`, and `logs/` exist.
3. **Dataset Verification**: Inspects raw datasets (`hackaprompt`, `agentdojo`, `garak`, `pyrit`, `promptinject`, `jailbreakbench`, `advbench`).
4. **Data Lake Streaming Ingestion**: Runs `python main.py ingest`, inspects `outputs/lake/` partitions, and verifies partition count and total storage size.
5. **Corpus Analytics Report Generation**: Computes streaming corpus statistics and lineage manifests.
6. **FastAPI Backend Launch**: Starts FastAPI backend at `http://127.0.0.1:8000` and polls `http://127.0.0.1:8000/docs` until HTTP 200 reachable.
7. **Next.js Studio Launch**: Starts Studio dev server at `http://localhost:3000` and polls reachability.
8. **Browser Auto-Open**: Opens your default browser pointing to `http://localhost:3000`.
9. **Real Endpoint Health Checks & Mini-Benchmark**:
   - Executes real HTTP requests against `/api/v1/dashboard`, `/api/v1/corpus`, `/api/v1/search`, `/api/v1/reports`, `/api/v1/telemetry`, `/api/v1/learning`, and `/api/v1/orchestrator/status`.
   - Records latency, status code, byte size, and error strings.
   - Executes an end-to-end mini benchmark via POST `/api/v1/orchestrator/mission`.
   - Writes `outputs/reports/startup_benchmark.json` and `outputs/reports/startup_health_report.json`.
10. **Real Console Summary**: Displays live metrics (requests, latency, memory entries, mission engine state, overall health).

---

## Output Artifacts

- **Startup Health Report**: `outputs/reports/startup_health_report.json`
- **Mini-Benchmark Report**: `outputs/reports/startup_benchmark.json`

---

## Services & Ports Summary

- **FastAPI API Backend**: `http://localhost:8000`
- **Swagger Interactive API Docs**: `http://localhost:8000/docs`
- **AegisSwarm Studio UI**: `http://localhost:3000`

---

## Troubleshooting

- **Port Conflicts**: Ensure ports `8000` and `3000` are free before running the launchers.
- **Python Encodings**: `PYTHONUTF8=1` is automatically set by both scripts to prevent UTF-8 console output issues on legacy Windows terminals.
- **Idempotency**: Both scripts are idempotent and safe to run multiple times without corrupting existing Data Lake partitions or state files.
