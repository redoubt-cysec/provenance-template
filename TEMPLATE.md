# Using This Repository as a Template

This repository serves a **dual purpose**:

1. **Working Demo** - A functional example (`provenance-demo`) showcasing supply chain security best practices
2. **GitHub Template** - A starting point for building your own secure Python CLI application

## Understanding the Dual Nature

### As a Working Demo 🎬

This repository is a **fully functional** example that demonstrates:
- Reproducible builds with SLSA provenance
- Sigstore signing and verification
- Multi-platform distribution (PyPI, Snap, Docker, Homebrew, etc.)
- Comprehensive security scanning and testing
- GitHub Actions-based CI/CD

You can explore it as-is:
```bash
git clone https://github.com/redoubt-cysec/provenance-template.git
cd provenance-template
./scripts/quick_setup.sh
```

### As a Template 📋

Click **"Use this template"** on GitHub to create your own repository with this structure, then customize it for your project.

## Quick Start: Customizing the Template

### Step 1: Create Your Repository

1. Click **"Use this template"** button on GitHub
2. Name your new repository
3. Clone your new repository locally

### Step 2: Run the Setup Script

The automated setup script will customize the template for your project:

```bash
cd your-new-repo
./scripts/setup_local_config.sh
```

This script will:
- Auto-detect your repository details from git remote
- Prompt for package name, CLI name, and other configurations
- Replace template placeholders across all files
- Create a `.env` file with your settings

### Step 3: Minimal Configuration

At minimum, you need to set:

```bash
# Copy the minimal template
cp .env.minimal .env

# Edit with your values
GITHUB_OWNER=your-username
GITHUB_REPO=your-repo-name
PACKAGE_NAME=your-package-name
CLI_NAME=your-cli-name
MODULE_NAME=your_module_name
```

### Step 4: Customize Your Code

Replace the demo implementation with your actual CLI:

1. **Update `src/demo_cli/`** → Rename to `src/your_module_name/`
2. **Edit `src/your_module_name/cli.py`** → Implement your CLI commands
3. **Update `pyproject.toml`** → Change project metadata
4. **Modify tests** → Update `tests/` for your functionality

### Step 5: Test Locally

```bash
# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest

# Build your package
./scripts/build_pyz.sh
```

## What Gets Replaced

When you run `setup_local_config.sh`, these template placeholders are automatically replaced:

### Repository References
- `redoubt-cysec/provenance-template` → `your-org/your-repo`
- `redoubt-cysec/provenance-demo` → `your-org/your-package`

### Package Names
- `provenance-demo` → `your-package-name`
- `demo_cli` → `your_module_name`
- `provenance-demo.pyz` → `your-cli-name.pyz`

### Template Placeholders (in packaging manifests)
- `OWNER` → `your-org`
- `REPO` → `your-repo`
- `Your Name` → Your git config name
- `your.email@example.com` → Your git config email

## Repository Structure

```
.
├── src/                    # Your Python package source code
│   └── demo_cli/          # Rename this to your module name
├── tests/                  # Test suite
├── scripts/                # Build and setup scripts
├── packaging/              # Distribution platform configs
│   ├── homebrew-tap/      # Homebrew formula
│   ├── snap/              # Snap package
│   ├── docker/            # Docker images
│   ├── flatpak/           # Flatpak manifest
│   └── ...                # Other platforms
├── .github/
│   └── workflows/         # CI/CD workflows
├── config/
│   └── tool-versions.yml  # Centralized tool version management
├── .env.minimal           # Minimal configuration template
├── .env.example           # Complete configuration options
├── pyproject.toml         # Python project configuration
└── TEMPLATE.md            # This file

```

## Configuration Files Explained

### `.env.minimal`
Bare minimum configuration to get started. Use this for:
- Initial setup
- Local development
- Basic testing

### `.env.example`
Comprehensive configuration with all options. Covers:
- **Phase 1**: Local development
- **Phase 2**: Testing platforms (TestPyPI, Snap edge, etc.)
- **Phase 3**: Production platforms (PyPI, Snap Store, Docker Hub, etc.)

### `config/tool-versions.yml`
Centralized version management for:
- Python package managers (pip, uv)
- Security tools (cosign)
- Python version matrix
- GitHub Actions

**Security Note:** This file provides a single source of truth for tool versions, making security updates easier to manage.

## Customization Checklist

### Essential (Do First)
- [ ] Run `./scripts/setup_local_config.sh`
- [ ] Update `pyproject.toml` metadata
- [ ] Rename `src/demo_cli/` to your module name
- [ ] Implement your CLI in `src/your_module/cli.py`
- [ ] Update `README.md` with your project details
- [ ] Customize `LICENSE` if not using MIT

### Recommended (Do Soon)
- [ ] Update tests in `tests/` for your functionality
- [ ] Customize GitHub workflows for your needs
- [ ] Set up GitHub Secrets for distribution platforms
- [ ] Configure packaging for platforms you plan to use
- [ ] Update security policy in `SECURITY.md`

### Optional (As Needed)
- [ ] Add custom GitHub Actions workflows
- [ ] Configure additional distribution platforms
- [ ] Customize Docker images
- [ ] Add platform-specific packaging
- [ ] Set up additional security scanning

## Distribution Platform Setup

The template supports multiple distribution platforms. See `.env.example` for configuration details:

### Supported Platforms

**Package Managers:**
- PyPI (Python Package Index)
- Homebrew (macOS/Linux)
- Snap (Linux)
- Flatpak (Linux)
- AUR (Arch User Repository)
- apt (Debian/Ubuntu)
- yum/dnf (Red Hat/Fedora)

**Container Registries:**
- Docker Hub
- GitHub Container Registry (GHCR)
- Quay.io

**App Stores:**
- Snap Store
- Flathub

Each platform requires:
1. Platform-specific configuration in `packaging/`
2. Authentication tokens (via GitHub Secrets)
3. Enabling the workflow in `.github/workflows/release.yml`

## Security Features

This template includes comprehensive security practices:

### Supply Chain Security
- ✅ SLSA provenance generation
- ✅ Sigstore signing
- ✅ GitHub attestations
- ✅ SBOM generation
- ✅ Reproducible builds

### Dependency Management
- ✅ Pinned dependencies with SHA hashes
- ✅ Dependabot for automated updates
- ✅ OSV vulnerability scanning

### Code Security
- ✅ CodeQL analysis
- ✅ OpenSSF Scorecard
- ✅ Secret scanning
- ✅ Token permission restrictions

### Testing
- ✅ Multi-version Python testing (3.10-3.13)
- ✅ Cross-platform testing (Linux, macOS, Windows)
- ✅ Integration testing with Docker and VMs
- ✅ Unit test coverage reporting

## Common Tasks

### Building Your Package

```bash
# Build Python wheel and source distribution
uv build

# Build standalone .pyz file
./scripts/build_pyz.sh

# Build all artifacts
./scripts/build_all_artifacts.sh
```

### Testing

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=src

# Test specific Python versions
pytest --python=3.10,3.11,3.12,3.13

# Run integration tests
pytest tests/test_distribution_integration.py
```

### Local Verification

```bash
# Verify your built package
python dist/your-cli.pyz verify

# Test installation
pip install dist/*.whl
your-cli --version
```

## Template vs Demo Values

### Demo Values (in this repository)
- Repository: `redoubt-cysec/provenance-template`
- Package: `provenance-demo`
- CLI: `provenance-demo`
- Module: `demo_cli`

### After Template Customization
- Repository: `your-org/your-repo`
- Package: `your-package-name`
- CLI: `your-cli-name`
- Module: `your_module_name`

## Maintenance

### Updating Tool Versions

Edit `config/tool-versions.yml` and run:
```bash
./scripts/setup_local_config.sh --update-tools
```

### Updating Dependencies

```bash
# Update Python dependencies
uv pip compile pyproject.toml -o requirements.txt

# Update GitHub Actions
# Check for new versions and update .github/workflows/
```

### Security Updates

The template includes automated security scanning. Review:
- Dependabot pull requests
- CodeQL security alerts
- OpenSSF Scorecard recommendations

## Getting Help

### Template Issues
- Review this file (`TEMPLATE.md`)
- Check `.env.example` for configuration options
- Read script help: `./scripts/setup_local_config.sh --help`

### Demo/Example Issues
- See `README.md` for the working demo documentation
- Explore example code in `src/demo_cli/`
- Review tests in `tests/` for usage examples

### Questions or Problems
- Open an issue on GitHub
- Check existing issues for similar questions
- Review GitHub Discussions

## Philosophy: Template + Working Demo

This dual-purpose approach provides:

**For Learners:**
- A working example to study and understand
- Real-world implementation of security practices
- Comprehensive testing and CI/CD setup

**For Adopters:**
- Quick start with proven patterns
- Automated customization tools
- Production-ready workflows

**For Maintainers:**
- Single codebase to maintain
- Working demo that proves the template works
- Easier to test changes (dog-fooding)

## Next Steps

1. **Explore the Demo** - Run it, test it, understand how it works
2. **Use as Template** - Create your repository from this template
3. **Customize** - Run setup script and implement your CLI
4. **Test** - Ensure everything works with your changes
5. **Publish** - Configure distribution platforms and release

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [SLSA Framework](https://slsa.dev/)
- [Sigstore Documentation](https://docs.sigstore.dev/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Supply Chain Security Best Practices](https://www.cisa.gov/supply-chain-security)

---

**Welcome to secure software distribution!** 🔒

This template embodies production-grade security practices while remaining accessible for developers of all levels. Whether you're building your first CLI tool or enhancing an existing project's security posture, this template provides the foundation you need.
