#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
BACK_PORT="${BACK_PORT:-5001}"
FRONT_PORT="${FRONT_PORT:-5173}"
API_URL="${VITE_API_BASE_URL:-http://localhost:$BACK_PORT}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python binary '$PYTHON_BIN' not found. Set PYTHON_BIN to an installed version." >&2
  exit 1
fi

mkdir -p "$BACKEND_DIR/datos/datasets" "$BACKEND_DIR/datos/procesadas" \
  "$BACKEND_DIR/datos/caracteristicas" "$BACKEND_DIR/datos/indices" "$BACKEND_DIR/datos/busquedas"

cd "$BACKEND_DIR"
if [ ! -x .venv/bin/python ]; then
  "$PYTHON_BIN" -m venv .venv
fi
source .venv/bin/activate
pip install -r requisitos.txt

FLASK_APP=app FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT="$BACK_PORT" \
  flask run > "$BACKEND_DIR/server.log" 2>&1 &
BACK_PID=$!

echo "Backend starting on http://localhost:$BACK_PORT (pid $BACK_PID)" >&2

cd "$FRONTEND_DIR"
if [ ! -d node_modules ]; then
  npm install
fi
VITE_API_BASE_URL="$API_URL" npm run dev -- --host --port "$FRONT_PORT" > "$FRONTEND_DIR/frontend.log" 2>&1 &
FRONT_PID=$!

echo "Frontend starting on http://localhost:$FRONT_PORT (pid $FRONT_PID)" >&2
echo "VITE_API_BASE_URL=$API_URL" >&2

echo "Logs: $BACKEND_DIR/server.log and $FRONTEND_DIR/frontend.log" >&2

echo "Press Ctrl+C to stop both." >&2
cleanup() {
  kill "$BACK_PID" "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT

wait
