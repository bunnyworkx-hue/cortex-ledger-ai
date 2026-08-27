#!/usr/bin/env bash
# Run the Cortex Ledger AI World 3D interface locally. Requires the API running
# (see scripts/dev/run.sh) at the URL in apps/world/.env.local.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../apps/world"
npm run dev
