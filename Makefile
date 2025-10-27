# Makefile for Redoubt Release Template
# Provides convenient commands for development, testing, and building

.PHONY: help
help: ## Show this help message
	@echo "Redoubt Release Template - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install package in development mode with all dependencies
	@echo "📦 Installing package in development mode..."
	uv pip install -e ".[dev]"
	@echo "✅ Installation complete"

.PHONY: dev-setup
dev-setup: ## Complete development environment setup (first-time setup)
	@echo "🚀 Setting up development environment..."
	./scripts/dev-setup.sh
	@echo "✅ Development environment ready"

.PHONY: build
build: ## Build the .pyz binary and wheels
	@echo "🔨 Building project..."
	./scripts/build_pyz.sh
	@echo "✅ Build complete: dist/redoubt-release-template.pyz"

.PHONY: test
test: ## Run all fast tests (excludes slow and integration tests)
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v -m "not slow and not integration and not published"

.PHONY: test-all
test-all: ## Run all tests including slow and integration tests
	@echo "🧪 Running all tests (including slow tests)..."
	uv run pytest tests/ -v

.PHONY: test-quick
test-quick: ## Run only fast unit tests
	@echo "⚡ Running quick tests..."
	uv run pytest tests/test_cli.py tests/test_cryptographic_integrity.py -v

.PHONY: test-integration
test-integration: ## Run integration tests (VM testing)
	@echo "🔧 Running integration tests..."
	uv run pytest tests/ -v -m "integration"

.PHONY: test-security
test-security: ## Run security tests
	@echo "🔒 Running security tests..."
	uv run pytest tests/test_security_pipeline.py tests/test_cryptographic_integrity.py tests/test_runtime_security.py -v

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term -m "not slow and not integration"
	@echo "✅ Coverage report: htmlcov/index.html"

.PHONY: lint
lint: ## Run linting checks (ruff, mypy, bandit)
	@echo "🔍 Running linters..."
	@command -v ruff >/dev/null 2>&1 || { echo "Installing ruff..."; uv pip install ruff; }
	ruff check src/ tests/
	@echo "✅ Linting complete"

.PHONY: format
format: ## Format code with ruff
	@echo "✨ Formatting code..."
	@command -v ruff >/dev/null 2>&1 || { echo "Installing ruff..."; uv pip install ruff; }
	ruff format src/ tests/
	ruff check --fix src/ tests/
	@echo "✅ Formatting complete"

.PHONY: type-check
type-check: ## Run type checking with mypy
	@echo "🔍 Running type checks..."
	@command -v mypy >/dev/null 2>&1 || { echo "Installing mypy..."; uv pip install mypy; }
	mypy src/ --ignore-missing-imports
	@echo "✅ Type checking complete"

.PHONY: security-check
security-check: ## Run security checks (bandit, safety)
	@echo "🔒 Running security checks..."
	@command -v bandit >/dev/null 2>&1 || { echo "Installing bandit..."; uv pip install bandit; }
	bandit -r src/ -ll
	@echo "✅ Security checks complete"

.PHONY: clean
clean: ## Remove build artifacts and cache files
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

.PHONY: clean-all
clean-all: clean ## Remove all generated files including .env
	@echo "🧹 Deep cleaning..."
	rm -rf .venv
	rm -f .env
	@echo "✅ Deep cleanup complete"

.PHONY: verify
verify: ## Verify the built binary
	@echo "🔍 Verifying binary..."
	./dist/redoubt-release-template.pyz --version
	./dist/redoubt-release-template.pyz hello "verification"
	@echo "✅ Binary verification complete"

.PHONY: verify-full
verify-full: build verify ## Build and run full verification
	@echo "🔍 Running full verification..."
	./dist/redoubt-release-template.pyz verify
	@echo "✅ Full verification complete"

.PHONY: phase2-homebrew
phase2-homebrew: ## Run Phase 2 Homebrew testing
	@echo "🍺 Testing Homebrew tap..."
	./scripts/phase2-testing/setup-homebrew-tap.sh
	./scripts/phase2-testing/test-homebrew-tap-vm.sh

.PHONY: phase2-pypi
phase2-pypi: ## Run Phase 2 PyPI testing
	@echo "🐍 Testing PyPI..."
	./scripts/phase2-testing/setup-test-pypi.sh
	./scripts/phase2-testing/test-test-pypi-vm.sh

.PHONY: phase2-docker
phase2-docker: ## Run Phase 2 Docker testing
	@echo "🐳 Testing Docker..."
	./scripts/phase2-testing/setup-docker-registry.sh
	./scripts/phase2-testing/test-docker-registry-vm.sh

.PHONY: phase2-all
phase2-all: ## Run all Phase 2 tests
	@echo "🧪 Running all Phase 2 tests..."
	./scripts/phase2-testing/run-all-phase2-tests.sh --setup --all

.PHONY: phase2-quick
phase2-quick: ## Run quick Phase 2 tests (Homebrew, Docker)
	@echo "⚡ Running quick Phase 2 tests..."
	./scripts/phase2-testing/run-all-phase2-tests.sh --setup homebrew docker

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t redoubt-release-template:dev .
	@echo "✅ Docker image built: redoubt-release-template:dev"

.PHONY: docker-run
docker-run: docker-build ## Build and run Docker image
	@echo "🐳 Running Docker image..."
	docker run --rm redoubt-release-template:dev --version
	docker run --rm redoubt-release-template:dev hello "Docker"

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo "🪝 Installing pre-commit hooks..."
	@command -v pre-commit >/dev/null 2>&1 || { echo "Installing pre-commit..."; pip install pre-commit; }
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks installed"

.PHONY: pre-commit-run
pre-commit-run: ## Run pre-commit hooks on all files
	@echo "🪝 Running pre-commit hooks..."
	pre-commit run --all-files

.PHONY: docs
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "✅ Documentation available in markdown files"
	@echo "  - README.md"
	@echo "  - CONTRIBUTING.md"
	@echo "  - PUBLISHING-GUIDE.md"
	@echo "  - TESTING-APPROACHES.md"

.PHONY: release-check
release-check: clean build test verify-full ## Pre-release checks (build, test, verify)
	@echo "✅ Release checks complete"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review changes: git log"
	@echo "  2. Update version in pyproject.toml"
	@echo "  3. Create tag: git tag v0.X.X"
	@echo "  4. Push tag: git push origin v0.X.X"

.PHONY: watch-tests
watch-tests: ## Watch for changes and run tests automatically
	@echo "👀 Watching for changes..."
	@command -v pytest-watch >/dev/null 2>&1 || { echo "Installing pytest-watch..."; uv pip install pytest-watch; }
	ptw tests/ -- -v -m "not slow and not integration"

.PHONY: shell
shell: ## Open Python shell with project context
	@echo "🐍 Opening Python shell..."
	uv run python -i -c "from demo_cli.cli import main; from demo_cli import __version__; print(f'Redoubt Release Template v{__version__}'); print('Available: main, __version__')"

.PHONY: info
info: ## Show project information
	@echo "📦 Redoubt Release Template"
	@echo ""
	@echo "Version:    $$(grep '^version = ' pyproject.toml | cut -d'\"' -f2)"
	@echo "Python:     $$(python3 --version)"
	@echo "UV:         $$(uv --version 2>/dev/null || echo 'not installed')"
	@echo "Git branch: $$(git branch --show-current)"
	@echo "Git status: $$(git status --short | wc -l | tr -d ' ') file(s) changed"
	@echo ""
	@echo "Build artifacts:"
	@ls -lh dist/ 2>/dev/null || echo "  (none - run 'make build')"

.PHONY: benchmark
benchmark: ## Run performance benchmarks
	@echo "⚡ Running benchmarks..."
	@echo "Binary size:"
	@ls -lh dist/redoubt-release-template.pyz 2>/dev/null || echo "  (build first with 'make build')"
	@echo ""
	@echo "Startup time:"
	@time ./dist/redoubt-release-template.pyz --version >/dev/null 2>&1 || echo "  (build first)"

.PHONY: update-deps
update-deps: ## Update dependencies
	@echo "📦 Updating dependencies..."
	uv pip compile pyproject.toml --upgrade
	@echo "✅ Dependencies updated"

.PHONY: check-config
check-config: ## Check repository configuration
	@echo "⚙️  Checking configuration..."
	./scripts/check_configuration.sh

.PHONY: quick-setup
quick-setup: ## Run quick setup script
	@echo "⚡ Running quick setup..."
	./scripts/quick_setup.sh

.PHONY: all
all: clean install build test verify ## Run complete build pipeline
	@echo "✅ Complete pipeline successful"

# Default target
.DEFAULT_GOAL := help
