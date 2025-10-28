#!/usr/bin/env bash
set -euo pipefail

# Deterministic environment
export TZ=UTC
export LC_ALL=C
export LANG=C
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git log -1 --pretty=%ct || date +%s)}"
umask 0022

# Clean & build wheel/sdist (for SBOM, reproducibility)
uv pip install --system --upgrade pip build
rm -rf dist && uv run --no-project python -m build

# Make a .pyz from the installed package sources
rm -rf build/pyz && mkdir -p build/pyz/src
rsync -a --delete src/ build/pyz/src/
# Create zipapp (module entry: demo_cli.cli:main)
uv run --no-project python -m zipapp build/pyz/src -m "demo_cli.cli:main" -p "/usr/bin/env python3" -o dist/provenance-demo.pyz
chmod +x dist/provenance-demo.pyz
