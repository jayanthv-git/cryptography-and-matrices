#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -r requirements-lock.txt
python -m pytest -q
cd frontend
npm ci
npm run typecheck
npm run build
