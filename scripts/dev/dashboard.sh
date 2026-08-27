#!/usr/bin/env bash
# Run the Cortex Ledger AI dashboard locally. Requires the API running (see
# scripts/dev/run.sh) at the URL in apps/dashboard/.env.local.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../apps/dashboard"
npm run dev
