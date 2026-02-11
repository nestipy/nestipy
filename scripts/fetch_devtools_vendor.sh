#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$ROOT_DIR/src/nestipy/devtools/frontend/static/vendor"

mkdir -p "$VENDOR_DIR"

echo "Downloading Cytoscape.js..."
curl -L -o "$VENDOR_DIR/cytoscape.min.js" \
  "https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"

echo "Downloading Mermaid..."
curl -L -o "$VENDOR_DIR/mermaid.min.js" \
  "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"

echo "Saved to $VENDOR_DIR/cytoscape.min.js"
echo "Saved to $VENDOR_DIR/mermaid.min.js"
