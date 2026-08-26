#!/usr/bin/env bash
# Run the Axiom API locally with auto-reload.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
uv run uvicorn axiom_api.main:app --reload
