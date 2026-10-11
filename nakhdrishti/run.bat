@echo off
REM One-step launcher for Windows
cd /d "%~dp0"
if not exist venv (
  echo Creating virtual environment (first run only)...
  python -m venv venv
  venv\Scripts\python -m pip install --upgrade pip
  venv\Scripts\pip install -r requirements.txt
)
venv\Scripts\python app.py
pause
