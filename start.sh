#!/usr/bin/env bash
set -e

echo "Starting Hackathon Judge..."

uvicorn hackathon_judge.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

sleep 2

streamlit run frontend/app.py --server.port 8501 &
UI_PID=$!

trap "kill $API_PID $UI_PID 2>/dev/null" EXIT

echo "API running at http://127.0.0.1:8000"
echo "UI  running at http://127.0.0.1:8501"

wait
