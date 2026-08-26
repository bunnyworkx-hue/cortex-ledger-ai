#!/usr/bin/env bash
# Serve the agency-agents knowledge graph over MCP for local dev.
# Rebuild the graph first with: graphify extract ~/Desktop/agency-agents --backend claude --out var
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
graphify-mcp var/graphify-out/graph.json --transport http --host 127.0.0.1 --port 8080
