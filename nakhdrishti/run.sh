#!/usr/bin/env bash
# One-step launcher for macOS / Linux
cd "$(dirname "$0")"
if [ ! -d venv ]; then
  echo "Creating virtual environment (first run only)..."
  python3 -m venv venv
  ./venv/bin/pip install --upgrade pip
  ./venv/bin/pip install -r requirements.txt
fi
./venv/bin/python app.py
