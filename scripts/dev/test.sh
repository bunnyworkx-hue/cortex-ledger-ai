#!/usr/bin/env bash
# Run the test suite.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
uv run pytest "$@"
