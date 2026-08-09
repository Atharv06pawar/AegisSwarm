@echo off
rem ============================================================================
rem AegisSwarm Research Automation Runner & Production Validator (Windows Batch)
rem Production-Grade Automated Pipeline Execution & Real Runtime Health Verification
rem ============================================================================

setlocal enabledelayedexpansion

rem Ensure UTF-8 output encoding across Python and Windows Command Prompt
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

powershell -ExecutionPolicy Bypass -File "%~dp0run_research.ps1"
if %ERRORLEVEL% neq 0 (
    exit /b %ERRORLEVEL%
)

endlocal
