#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pyinstaller --clean --noconfirm build_tools/backend_server.spec
echo "Build complete: dist/what_the_law_backend"
