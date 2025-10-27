# Integration Testing Guide

This repository includes comprehensive integration tests that verify the CLI works correctly across different platforms and installation methods.

## Overview

**Integration tests validate:**

- ✅ .pyz works on Ubuntu, Debian, Fedora, Alpine, macOS, Windows
- ✅ pip/wheel installation on all platforms
- ✅ Homebrew tap installation (macOS)
- ✅ Snap installation (Ubuntu)
- ✅ pipx installation
- ✅ Different Python versions (3.11, 3.12+)
- ✅ Attestation verification workflow

## Test Approaches

### 1. Docker-based Tests (Fast, GitHub Actions)

Tests run in Docker containers across multiple Linux distributions:

- Ubuntu 22.04
- Debian 12
- Fedora 39
- Alpine 3.19

**Run in CI:** Automatically on releases and PRs
**Runtime:** ~5-10 minutes total

### 2. Multipass-based Tests (Comprehensive, Local)

Tests run in full VMs using Multipass for realistic scenarios:

- Fresh OS installations
- Real package manager installations
- Cross-platform testing

**Run locally:** Manual trigger
**Runtime:** ~15-30 minutes total

### 3. Native Runner Tests (Platform-specific)

Tests run on actual macOS and Windows runners:

- macOS 14 (latest)
- Windows Server 2022

**Run in CI:** Automatically on releases
**Runtime:** ~5 minutes per platform

## Running Tests

### Quick Test (Docker-based)

```bash
# Run all Docker-based integration tests
pytest tests/test_distribution_integration.py::TestDirectPyzInstallation -v

# These tests are fast and don't require Multipass
```

### Local Integration Tests (Multipass)

**Prerequisites:**

```bash
# Install Multipass
# macOS:
brew install multipass

# Ubuntu/Debian:
sudo snap install multipass

# Windows:
# Download from https://multipass.run/
```

**Run tests:**

```bash
# Run all Multipass integration tests
pytest tests/test_distribution_integration.py -v -s -m integration

# Run specific distribution test
pytest tests/test_distribution_integration.py::TestHomebrewInstallation -v -s
pytest tests/test_distribution_integration.py::TestSnapInstallation -v -s
pytest tests/test_distribution_integration.py::TestPipInstallation -v -s
```

### CI Integration Tests

```bash
# Trigger manually via GitHub Actions
# Go to: Actions → Integration Tests → Run workflow

# Or push a tag
git tag v1.0.0
git push origin v1.0.0
```

## Test Categories

### TestHomebrewInstallation

Tests Homebrew tap installation:

- ✅ Homebrew installation on macOS/Linux
- ✅ Tap addition and formula installation
- ✅ Formula syntax validation
- ✅ .pyz execution after installation

**Platforms:** macOS, Linux (with Linuxbrew)
**Runtime:** ~5-10 minutes

### TestSnapInstallation

Tests Snap package installation:

- ✅ snapd installation and setup
- ✅ Snap package installation
- ✅ Confined execution
- ✅ Permission handling

**Platforms:** Ubuntu, any Linux with snapd
**Runtime:** ~3-5 minutes

### TestPipInstallation

Tests pip/PyPI installation:

- ✅ Wheel installation via pip
- ✅ Virtual environment isolation
- ✅ pipx installation
- ✅ CLI functionality after install

**Platforms:** All (Ubuntu, Debian, Fedora, Alpine, macOS, Windows)
**Runtime:** ~2-3 minutes per platform

### TestDirectPyzInstallation

Tests direct .pyz usage:

- ✅ Execution with python3
- ✅ Execution as executable (./client.pyz)
- ✅ Functionality testing (version, args)
- ✅ File permissions

**Platforms:** All
**Runtime:** ~1-2 minutes per platform

### TestCrossPlatformCompatibility

Tests across Python versions:

- ✅ Python 3.11
- ✅ Python 3.12+
- ✅ Version-specific issues
- ✅ Compatibility warnings

**Platforms:** Ubuntu (easily extended to others)
**Runtime:** ~3-5 minutes

### TestEndToEndVerification

Tests complete user workflow:

- ✅ Download artifact
- ✅ Verify attestation (gh CLI)
- ✅ Verify checksums
- ✅ Execute application
- ✅ From-source verification

**Platforms:** Ubuntu
**Runtime:** ~5-10 minutes

## Docker vs Multipass

### Use Docker When

- ✅ Testing basic .pyz functionality
- ✅ Testing pip installation
- ✅ Need fast feedback in CI
- ✅ Testing multiple distributions quickly

### Use Multipass When

- ✅ Testing Homebrew/Snap (need full OS)
- ✅ Testing package manager interactions
- ✅ Need realistic user environment
- ✅ Testing system-level integration

## CI/CD Integration

### GitHub Actions Workflow

The integration test workflow runs:

1. **On every release tag** (`v*`)
   - Full test suite across all platforms
   - Validates distribution methods
   - Ensures artifacts work

2. **On schedule** (weekly)
   - Catches platform drift
   - Tests against latest OS updates

3. **Manual trigger**
   - For testing before releases
   - For debugging installation issues

### Workflow Structure

```
build-artifacts → test-docker-* → summary
                → test-macos
                → test-windows
                → test-multipass (optional)
```

**Total runtime:** ~15-20 minutes (parallel execution)

## Adding New Platform Tests

### Add Docker-based Test

```python
def test_docker_myos(self, ubuntu_vm):
    """Test on MyOS distribution."""
    vm_name = ubuntu_vm

    # Install dependencies
    multipass_exec(vm_name, "myos-install python3", timeout=300)

    # Test .pyz
    result = multipass_exec(vm_name, "python3 /tmp/client.pyz --version")
    assert result.returncode == 0
```

### Add to CI Workflow

```yaml
test-docker-myos:
  name: Test on MyOS (Docker)
  runs-on: ubuntu-latest
  needs: build-artifacts
  container:
    image: myos:latest
  steps:
    - name: Test installation
      run: |
        python3 dist/client.pyz --version
```

## Troubleshooting

### Multipass Issues

**VM creation fails:**

```bash
# Check Multipass status
multipass list

# Clean up stuck VMs
multipass delete --all --purge

# Restart Multipass
# macOS: brew services restart multipass
# Linux: sudo snap restart multipass
```

**VM networking issues:**

```bash
# Check network
multipass exec vm-name -- ping -c 3 8.8.8.8

# Restart networking in VM
multipass restart vm-name
```

### Docker Issues

**Container fails to start:**

```bash
# Pull image manually
docker pull ubuntu:22.04

# Check disk space
docker system df
docker system prune
```

**Python not found:**

```bash
# Some minimal images don't include Python
# Add installation step to workflow
```

### Test Failures

**Import errors:**

- Ensure artifact was built before tests
- Check dist/ directory has .pyz and .whl files

**Permission errors:**

- Ensure .pyz is executable: `chmod +x dist/client.pyz`
- Check file ownership in VM

**Version mismatch:**

- Update version in test assertions
- Ensure pyproject.toml version is correct

## Best Practices

### Before Running Tests

1. **Build artifacts:**

   ```bash
   ./scripts/build_pyz.sh
   python -m build
   ```

2. **Check artifacts exist:**

   ```bash
   ls -lh dist/
   # Should see: client.pyz, *.whl, *.tar.gz
   ```

3. **Run fast tests first:**

   ```bash
   # Test basic functionality
   python dist/client.pyz --version
   ```

### During Development

- Run Docker tests frequently (fast)
- Run Multipass tests before releases (thorough)
- Add tests for new installation methods
- Document platform-specific quirks

### In CI

- Always run on releases
- Run weekly to catch platform drift
- Monitor for flaky tests (network issues)
- Keep test runtime under 20 minutes

## Performance Optimization

### Parallel Execution

Tests run in parallel by default in CI:

```yaml
jobs:
  test-ubuntu: ...
  test-debian: ...  # Runs parallel to test-ubuntu
  test-macos: ...   # Runs parallel to both
```

### VM Caching

Multipass VMs can be cached between runs:

```bash
# Create base VM
multipass launch --name base-ubuntu

# Snapshot it
multipass snapshot base-ubuntu base-snapshot

# Restore for tests
multipass restore base-ubuntu base-snapshot
```

### Artifact Reuse

Artifacts are built once and reused across all test jobs:

```yaml
needs: build-artifacts  # Reuses built artifacts
```

## Security Considerations

### VM Isolation

- Each test runs in isolated VM
- No cross-contamination between tests
- Clean state for each test run

### Network Access

Tests require network for:

- Package manager downloads
- OS updates
- Python package installation

**Mitigation:**

- Pin package versions when possible
- Use checksums for critical downloads
- Test offline installation where feasible

### Secrets

Integration tests should NOT require secrets:

- ✅ Test public packages only
- ✅ Use public registries
- ❌ Don't test private repositories
- ❌ Don't use authentication tokens

## Metrics and Reporting

### Success Criteria

All tests must:

- ✅ Complete within timeout (30 min)
- ✅ Return exit code 0
- ✅ Produce expected output
- ✅ Leave no leaked resources (VMs, containers)

### Test Coverage

Integration tests validate:

- **6 platforms** (Ubuntu, Debian, Fedora, Alpine, macOS, Windows)
- **4 installation methods** (direct .pyz, pip, Homebrew, Snap)
- **3 Python versions** (3.11, 3.12, 3.13)
- **2 VM technologies** (Docker, Multipass)

**Total test combinations:** 24+ scenarios

## Future Enhancements

### Planned Additions

1. **Windows Package Managers**
   - Winget installation test
   - Chocolatey installation test
   - Scoop installation test

2. **Linux Package Managers**
   - APT repository test
   - RPM repository test
   - AUR package test

3. **Container Registries**
   - Docker Hub pull test
   - GHCR pull test
   - Signature verification

4. **Advanced Scenarios**
   - Offline installation test
   - Proxy environment test
   - Air-gapped installation test
   - Corporate firewall test

### Roadmap

- **Q1:** Windows package managers
- **Q2:** Linux native packages (APT/RPM)
- **Q3:** Container registry tests
- **Q4:** Advanced/offline scenarios

## Contributing

When adding new installation methods:

1. Add test class in `test_distribution_integration.py`
2. Add workflow job in `integration-tests.yml`
3. Document in this file
4. Update test count in SECURITY-TESTING.md

## References

- [Multipass Documentation](https://multipass.run/docs)
- [Docker Official Images](https://hub.docker.com/_/ubuntu)
- [GitHub Actions Runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners)
- [Python Packaging Guide](https://packaging.python.org/)
