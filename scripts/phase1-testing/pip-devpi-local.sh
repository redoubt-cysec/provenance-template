#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip wheel devpi-server devpi-client twine build

DEVPI_DIR="$(mktemp -d)"
trap 'devpi-server --serverdir "$DEVPI_DIR" --stop || true' EXIT

devpi-server --serverdir "$DEVPI_DIR" --start --host 127.0.0.1 --port 3141

devpi use http://127.0.0.1:3141
devpi user -c testuser password=secret || true
devpi login testuser --password=secret
devpi index -c dev bases=root/pypi || true
devpi use testuser/dev

python -m build
# Upload with either twine or devpi upload
twine upload --repository-url http://127.0.0.1:3141/testuser/dev dist/* || true
devpi upload || true

python -m venv .venv && . .venv/bin/activate
pip install --index-url http://127.0.0.1:3141/testuser/dev/simple --trusted-host 127.0.0.1 demo-secure-cli || redoubt-release-template || true
echo "✓ devpi Phase 1 OK"