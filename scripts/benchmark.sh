#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

if command -v uv >/dev/null 2>&1; then
  exec uv run python bench_compare.py "$@"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 bench_compare.py "$@"
else
  echo "Error: uv or python3 is required to run benchmarks." >&2
  exit 1
fi
