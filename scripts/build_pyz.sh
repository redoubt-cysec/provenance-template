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
# Create zipapp (module entry: demo_cli.cli:main) with reproducible timestamps
uv run --no-project python -c "
import zipapp
import os
import time
# Set mtime of all files to SOURCE_DATE_EPOCH for reproducibility
sde = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
for root, dirs, files in os.walk('build/pyz/src'):
    for name in files:
        path = os.path.join(root, name)
        os.utime(path, (sde, sde))
zipapp.create_archive('build/pyz/src', 'dist/provenance-demo.pyz',
                      interpreter='/usr/bin/env python3',
                      main='demo_cli.cli:main')
"
chmod +x dist/provenance-demo.pyz
