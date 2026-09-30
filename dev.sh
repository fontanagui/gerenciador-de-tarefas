#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"

if [[ ! -x .venv/bin/python ]]; then
    echo "Crie a venv primeiro: python3 -m venv .venv" >&2
    exit 1
fi
if ! .venv/bin/python -c 'import uvicorn' >/dev/null 2>&1; then
    echo "Instale as dependências: .venv/bin/python -m pip install -r requirements.txt" >&2
    exit 1
fi
if ! command -v node >/dev/null 2>&1; then
    echo "Instale o Node.js 22.12+ ou 24 LTS para iniciar o frontend." >&2
    exit 1
fi
if [[ ! -f frontend/node_modules/vite/bin/vite.js ]]; then
    echo "Instale as dependências do frontend: cd frontend && npm install" >&2
    exit 1
fi

backend_pid=""
frontend_pid=""
cleanup() {
    trap - EXIT INT TERM
    echo
    echo "Encerrando backend e frontend…"
    for process_id in "$backend_pid" "$frontend_pid"; do
        if [[ -n "$process_id" ]]; then
            kill "$process_id" 2>/dev/null || true
        fi
    done
    for process_id in "$backend_pid" "$frontend_pid"; do
        if [[ -n "$process_id" ]]; then
            wait "$process_id" 2>/dev/null || true
        fi
    done
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Reload watches Python sources; Vite handles frontend hot reload separately.
.venv/bin/python -m uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000 &
backend_pid=$!
(
    cd frontend
    exec node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort
) &
frontend_pid=$!

echo "Frontend: http://localhost:5173/ui/"
echo "API / Swagger: http://127.0.0.1:8000/docs"
echo "Pressione Ctrl+C para encerrar os dois."

# If either server stops, shut down the other rather than leave it behind.
wait -n "$backend_pid" "$frontend_pid"
