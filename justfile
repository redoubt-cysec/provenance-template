# justfile - A modern command runner

# Default task to run when no command is specified
default: help

# Show help message with available commands
help:
    @echo "Provenance Demo - Development Commands"
    @echo ""
    @echo "Usage: just [command]"
    @echo ""
    @just --list

# Install package in development mode with all dependencies
install:
    @echo "📦 Installing package in development mode..."
    uv pip install -e ".[dev]"
    @echo "✅ Installation complete"

# Complete development environment setup (first-time setup)
dev-setup:
    @echo "🚀 Setting up development environment..."
    ./scripts/dev-setup.sh
    @echo "✅ Development environment ready"

# Build the .pyz binary and wheels
build:
    @echo "🔨 Building project..."
    ./scripts/build_pyz.sh
    @echo "✅ Build complete: dist/provenance-demo.pyz"

# Run all fast tests (excludes slow and integration tests)
test:
    @echo "🧪 Running all tests sequentially (no skipped tests)..."
    find tests -name 'test_*.py' -print0 | xargs -0 -n 1 sh -c '.venv/bin/python -m pytest "$0" -v; test $? -eq 0 -o $? -eq 5 || { echo "Tests failed in $0"; exit 1; }'

# Run all tests including slow and integration tests
test-all:
    @echo "🧪 Running all tests (including slow tests)..."
    uv run pytest tests/ -v

# Run only fast unit tests
test-quick:
    @echo "⚡ Running quick tests..."
    uv run pytest tests/test_cli.py tests/test_cryptographic_integrity.py -v

# Run integration tests (VM testing)
test-integration:
    @echo "🔧 Running integration tests..."
    uv run pytest tests/ -v -m "integration"

# Run security tests
test-security:
    @echo "🔒 Running security tests..."
    uv run pytest tests/test_security_pipeline.py tests/test_cryptographic_integrity.py tests/test_runtime_security.py -v

# Run tests with coverage report
test-coverage:
    @echo "📊 Running tests with coverage..."
    uv run pytest tests/ --cov=src --cov-report=html --cov-report=term -m "not slow and not integration"
    @echo "✅ Coverage report: htmlcov/index.html"

# Run linting checks (ruff, mypy, bandit)
lint:
    @echo "🔍 Running linters..."
    @command -v ruff >/dev/null 2>&1 || (echo "Installing ruff..." && uv pip install ruff)
    ruff check src/ tests/
    @echo "✅ Linting complete"

# Format code with ruff
format:
    @echo "✨ Formatting code..."
    @command -v ruff >/dev/null 2>&1 || (echo "Installing ruff..." && uv pip install ruff)
    ruff format src/ tests/
    ruff check --fix src/ tests/
    @echo "✅ Formatting complete"

# Run type checking with mypy
type-check:
    @echo "🔍 Running type checks..."
    @command -v mypy >/dev/null 2>&1 || (echo "Installing mypy..." && uv pip install mypy)
    mypy src/ --ignore-missing-imports
    @echo "✅ Type checking complete"

# Run security checks (bandit, safety)
security-check:
    @echo "🔒 Running security checks..."
    @command -v bandit >/dev/null 2>&1 || (echo "Installing bandit..." && uv pip install bandit)
    bandit -r src/ -ll
    @echo "✅ Security checks complete"

# Remove build artifacts and cache files
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf .pytest_cache
    rm -rf .ruff_cache
    rm -rf .mypy_cache
    rm -rf htmlcov
    rm -rf .coverage
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    @echo "✅ Cleanup complete"

# Remove all generated files including .env
clean-all:
    @echo "🧹 Deep cleaning..."
    just clean
    rm -rf .venv
    rm -f .env
    @echo "✅ Deep cleanup complete"

# Verify the built binary
verify:
    @echo "🔍 Verifying binary..."
    ./dist/provenance-demo.pyz --version
    ./dist/provenance-demo.pyz hello "verification"
    @echo "✅ Binary verification complete"

# Build and run full verification
verify-full:
    @echo "🔍 Running full verification..."
    just build
    just verify
    ./dist/provenance-demo.pyz verify
    @echo "✅ Full verification complete"

# Install pre-commit hooks
pre-commit-install:
    @echo "🪝 Installing pre-commit hooks..."
    @command -v pre-commit >/dev/null 2>&1 || (echo "Installing pre-commit..." && pip install pre-commit)
    pre-commit install
    pre-commit install --hook-type commit-msg
    @echo "✅ Pre-commit hooks installed"

# Run pre-commit hooks on all files
pre-commit-run:
    @echo "🪝 Running pre-commit hooks..."
    pre-commit run --all-files

# Watch for changes and run tests automatically
watch-tests:
    @echo "👀 Watching for changes..."
    @command -v pytest-watch >/dev/null 2>&1 || (echo "Installing pytest-watch..." && uv pip install pytest-watch)
    ptw tests/ -- -v -m "not slow and not integration"

# ========================================
# Platform-Specific Testing (P0.5, P1, P2)
# ========================================

# Test AppImage Phase 1 (local build)
test-appimage-p1:
    @echo "📦 Testing AppImage Phase 1 (local build)..."
    bash scripts/phase1-testing/appimage-local-build.sh

# Test AppImage Phase 2 (VM testing)
test-appimage-p2: test-appimage-p1
    @echo "🖥️  Testing AppImage Phase 2 (VM)..."
    bash scripts/phase2-testing/test-appimage-vm.sh

# Test AUR Phase 1 (Docker-based makepkg)
test-aur-p1:
    @echo "📦 Testing AUR Phase 1 (Docker build)..."
    bash scripts/phase1-testing/aur-local-build.sh

# Test AUR Phase 2 (Arch Linux VM)
test-aur-p2: test-aur-p1
    @echo "🖥️  Testing AUR Phase 2 (Arch VM)..."
    bash scripts/phase2-testing/test-aur-vm.sh

# Test Nix Phase 1 (local build)
test-nix-p1:
    @echo "❄️  Testing Nix Phase 1 (local build)..."
    bash scripts/phase1-testing/nix-local-build.sh

# Test Homebrew local formula (always works)
test-homebrew-local-vm:
    @echo "🍺 Testing Homebrew with local formula (VM)..."
    bash scripts/phase2-testing/test-homebrew-local-vm.sh

# Test Homebrew remote tap (requires tap repository)
test-homebrew-tap-vm:
    @echo "🍺 Testing Homebrew with remote tap (VM)..."
    bash scripts/phase2-testing/test-homebrew-tap-vm.sh

# Test PyPI with devpi (improved Phase 1)
test-pypi-devpi:
    @echo "🐍 Testing PyPI with devpi (Phase 1 improved)..."
    bash scripts/phase1-testing/pip-devpi-local.sh

# Test Flatpak Beta setup
test-flatpak-beta-setup:
    @echo "📦 Setting up Flathub Beta..."
    bash scripts/phase2-testing/setup-flathub-beta.sh

# Test Flatpak Beta VM
test-flatpak-beta-vm:
    @echo "🖥️  Testing Flatpak Beta on VM..."
    bash scripts/phase2-testing/test-flathub-beta-vm.sh

# Test Docker multi-arch build
test-docker-multiarch IMG="ghcr.io/OWNER/redoubt:test":
    @echo "🐳 Testing Docker multi-arch build..."
    bash scripts/phase2-testing/test-docker-multiarch.sh {{IMG}}

# ========================================
# Release Signing (P0.1)
# ========================================

# Sign APT repository
sign-apt REPO_DIR="dist/deb-repo":
    @echo "🔐 Signing APT repository..."
    @test -n "${GPG_KEY_NAME}" || (echo "Error: GPG_KEY_NAME environment variable not set" && exit 1)
    bash scripts/release/sign-apt-repo.sh {{REPO_DIR}}

# Sign RPM packages
sign-rpm RPM_DIR="dist/rpm":
    @echo "🔐 Signing RPM packages..."
    @test -n "${GPG_KEY_NAME}" || (echo "Error: GPG_KEY_NAME environment variable not set" && exit 1)
    bash scripts/release/sign-rpm.sh {{RPM_DIR}}

# ========================================
# Convenience Targets
# ========================================

# Run all new Phase 1 tests
test-new-platforms-p1:
    @echo "🧪 Running all new platform Phase 1 tests..."
    just test-appimage-p1 || true
    just test-aur-p1 || true
    just test-nix-p1 || true

# Run all Phase 1 distribution tests
test-phase1-all:
    @echo "🧪 Running all Phase 1 distribution tests..."
    bash scripts/phase1-testing/run-all.sh

# Run all Phase 2 VM tests (requires multipass)
test-phase2-all:
    @echo "🧪 Running all Phase 2 VM tests..."
    @echo "📝 Note: Tests run sequentially, VMs cleaned up after each test"
    bash scripts/phase2-testing/run-all-phase2-tests.sh --all

# Run comprehensive VM tests (all distributions in fresh VMs)
test-vm-comprehensive:
    @echo "🧪 Running comprehensive VM distribution tests..."
    @echo "📝 Each distribution tested in its own fresh VM"
    @echo "📝 VMs are cleaned up immediately after each test"
    bash scripts/phase2-testing/comprehensive-vm-tests.sh

# Demonstrate VM test infrastructure (quick demo)
test-vm-demo:
    @echo "🎬 Running VM test infrastructure demo..."
    @echo "📝 This demonstrates the sequential execution and cleanup features"
    bash scripts/phase2-testing/test-vm-infrastructure-demo.sh

# Clean up orphaned VMs
vm-cleanup:
    @echo "🧹 Cleaning up orphaned VMs..."
    bash scripts/phase2-testing/cleanup-vms.sh --force
