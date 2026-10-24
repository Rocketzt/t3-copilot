@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
echo T3 Ops Copilot - SIMULATED - starting on http://127.0.0.1:8803
echo Press Ctrl+C to stop.
"%PY%" app\server.py
endlocal
