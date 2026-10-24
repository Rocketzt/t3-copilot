@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
if exist "tests\run_tests.py" (
  "%PY%" tests\run_tests.py --writer-mode offline --out exports\test_results.json
  exit /b %errorlevel%
)
if exist "tests\runner.py" (
  "%PY%" tests\runner.py --writer-mode offline --out exports\test_results.json
  exit /b %errorlevel%
)
echo Exam runner is not available on this branch yet (Jason owns tests/).
echo The web app still runs: run_app.bat
exit /b 0
