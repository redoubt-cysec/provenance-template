# Quick Start: Docker/OCI

**Status:** ✅ Production Ready | **Test Coverage:** Phase 1 + Phase 2 | **Automated:** Yes

## Installation

### Install Docker (if needed)

```bash
# macOS (using Homebrew)
brew install --cask docker

# Ubuntu/Debian
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Fedora
sudo dnf install docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### Pull Image from GitHub Container Registry (GHCR)

```bash
# Pull latest version
docker pull ghcr.io/redoubt-cysec/provenance-demo:latest

# Pull specific version
docker pull ghcr.io/redoubt-cysec/provenance-demo:v0.0.1-alpha.40

# Pull specific tag
docker pull ghcr.io/redoubt-cysec/provenance-demo:0.0.1-alpha.40

# Verify image
docker images | grep provenance-demo
```

### Run Container

```bash
# Run with command
docker run ghcr.io/redoubt-cysec/provenance-demo:latest --version

# Run interactive
docker run -it ghcr.io/redoubt-cysec/provenance-demo:latest

# Run with arguments
docker run ghcr.io/redoubt-cysec/provenance-demo:latest hello "World"

# Run verify command (requires artifacts)
docker run -v $(pwd):/workspace \
  ghcr.io/redoubt-cysec/provenance-demo:latest verify
```

### Create Alias for Convenience

```bash
# Add to ~/.bashrc or ~/.zshrc
alias provenance-demo='docker run --rm -v $(pwd):/workspace ghcr.io/redoubt-cysec/provenance-demo:latest'

# Reload shell
source ~/.bashrc

# Use like native command
provenance-demo --version
provenance-demo hello "Docker"
```

## Verification

### Verify Image Signature

```bash
# Install cosign (if needed)
brew install cosign  # macOS
# or: sudo apt install cosign  # Linux

# Verify image signature
cosign verify \
  --certificate-identity-regexp="https://github.com/redoubt-cysec/provenance-template" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/redoubt-cysec/provenance-demo:latest
```

### Verify Image Attestations

```bash
# Download attestations
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp="https://github.com/redoubt-cysec/provenance-template" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/redoubt-cysec/provenance-demo:latest
```

### Run Built-in Verification

```bash
# Set repository
export GITHUB_REPOSITORY=redoubt-cysec/provenance-template

# Download release artifacts
gh release download v0.0.1-alpha.40 --repo $GITHUB_REPOSITORY

# Run verification
docker run -v $(pwd):/workspace \
  -e GITHUB_REPOSITORY=$GITHUB_REPOSITORY \
  ghcr.io/redoubt-cysec/provenance-demo:latest verify

# Expected: ✓ 14/14 checks passed
```

## Validation Script

Quick validation that everything works:

```bash
#!/bin/bash
set -e

echo "=== Docker/OCI Installation Validation ==="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi
echo "✓ Docker found"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running"
    echo "Start with: sudo systemctl start docker"
    exit 1
fi
echo "✓ Docker daemon running"

# Set image name
IMAGE="ghcr.io/redoubt-cysec/provenance-demo:latest"

# Check if image exists locally
if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "$IMAGE"; then
    echo "⚠️  Image not found locally, pulling..."
    docker pull "$IMAGE"
fi
echo "✓ Image available: $IMAGE"

# Check version
VERSION=$(docker run --rm "$IMAGE" --version 2>&1)
if [[ -z "$VERSION" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION"

# Test basic functionality
OUTPUT=$(docker run --rm "$IMAGE" hello "Test" 2>&1)
if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Verify image metadata
CREATED=$(docker inspect "$IMAGE" --format='{{.Created}}')
SIZE=$(docker inspect "$IMAGE" --format='{{.Size}}' | numfmt --to=iec)
echo "✓ Image created: $CREATED"
echo "✓ Image size: $SIZE"

# Check if cosign is available for verification
if command -v cosign &> /dev/null; then
    echo "✓ cosign available for signature verification"
    # Note: Actual verification requires proper setup
else
    echo "⚠️  cosign not installed (optional)"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Docker installation is working correctly."
```

Save as `validate-docker.sh` and run:

```bash
chmod +x validate-docker.sh
./validate-docker.sh
```

## Upgrading

```bash
# Pull latest version
docker pull ghcr.io/redoubt-cysec/provenance-demo:latest

# Or pull specific newer version
docker pull ghcr.io/redoubt-cysec/provenance-demo:v0.1.1

# Remove old images
docker image prune -a

# Verify new version
docker run ghcr.io/redoubt-cysec/provenance-demo:latest --version
```

## Uninstalling

```bash
# Remove container images
docker rmi ghcr.io/redoubt-cysec/provenance-demo:latest
docker rmi ghcr.io/redoubt-cysec/provenance-demo:v0.0.1-alpha.40

# Remove all provenance-demo images
docker images | grep provenance-demo | awk '{print $3}' | xargs docker rmi

# Clean up unused images
docker image prune -a

# Remove stopped containers
docker container prune

# Verify removal
! docker images | grep -q provenance-demo && echo "Successfully uninstalled"
```

## Troubleshooting

### Docker Daemon Not Running

**Problem:** `Cannot connect to the Docker daemon`

**Solution:**
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker

# macOS: Start Docker Desktop
open -a Docker
```

### Permission Denied

**Problem:** `permission denied while trying to connect to the Docker daemon socket`

**Solution:**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Or use sudo (not recommended)
sudo docker run ghcr.io/redoubt-cysec/provenance-demo:latest --version

# Verify group membership
groups | grep docker
```

### Image Pull Failed

**Problem:** `Error response from daemon: pull access denied`

**Solution:**
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Or use gh CLI
gh auth token | docker login ghcr.io -u USERNAME --password-stdin

# For public images, no auth needed
docker pull ghcr.io/redoubt-cysec/provenance-demo:latest
```

### Network Timeout

**Problem:** `TLS handshake timeout` or network errors

**Solution:**
```bash
# Check network connectivity
docker run --rm busybox ping -c 3 ghcr.io

# Configure Docker proxy (if behind firewall)
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo cat > /etc/systemd/system/docker.service.d/http-proxy.conf << EOF
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=https://proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Container Exits Immediately

**Problem:** Container exits without output

**Solution:**
```bash
# Run with interactive terminal
docker run -it ghcr.io/redoubt-cysec/provenance-demo:latest

# Check container logs
docker run --name test ghcr.io/redoubt-cysec/provenance-demo:latest --version
docker logs test
docker rm test

# Run with debugging
docker run --rm -it --entrypoint /bin/sh ghcr.io/redoubt-cysec/provenance-demo:latest
```

### Volume Mount Issues

**Problem:** `cannot mount volume` or permission errors

**Solution:**
```bash
# Use absolute paths
docker run -v /absolute/path:/workspace ghcr.io/redoubt-cysec/provenance-demo:latest

# Fix permissions
chmod 755 /path/to/mount

# Use named volumes instead
docker volume create provenance-data
docker run -v provenance-data:/workspace ghcr.io/redoubt-cysec/provenance-demo:latest

# SELinux issues (Linux)
docker run -v $(pwd):/workspace:z ghcr.io/redoubt-cysec/provenance-demo:latest
```

## Best Practices

### Pin Image Versions

```bash
# Use specific version tags (recommended)
docker pull ghcr.io/redoubt-cysec/provenance-demo:v0.1.0

# Avoid using :latest in production
# docker pull ghcr.io/redoubt-cysec/provenance-demo:latest  # Not recommended

# Use digest for immutability
docker pull ghcr.io/redoubt-cysec/provenance-demo@sha256:abc123...
```

### Verify Image Signatures

```bash
# Always verify signatures before use
cosign verify \
  --certificate-identity-regexp="https://github.com/redoubt-cysec/provenance-template" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/redoubt-cysec/provenance-demo:latest

# Verify attestations
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp="https://github.com/redoubt-cysec/provenance-template" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/redoubt-cysec/provenance-demo:latest
```

### Use Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  provenance-demo:
    image: ghcr.io/redoubt-cysec/provenance-demo:v0.0.1-alpha.40
    volumes:
      - ./workspace:/workspace
    environment:
      - GITHUB_REPOSITORY=redoubt-cysec/provenance-template
    command: verify
```

```bash
# Run with compose
docker-compose run provenance-demo --version
docker-compose run provenance-demo verify
```

### Minimize Image Size

```bash
# Use specific tags to avoid pulling unnecessary layers
docker pull ghcr.io/redoubt-cysec/provenance-demo:v0.1.0-slim

# Clean up regularly
docker system prune -a

# Remove dangling images
docker image prune
```

### Security Scanning

```bash
# Scan image for vulnerabilities
docker scout cves ghcr.io/redoubt-cysec/provenance-demo:latest

# Or use trivy
trivy image ghcr.io/redoubt-cysec/provenance-demo:latest

# Or use grype
grype ghcr.io/redoubt-cysec/provenance-demo:latest
```

## Multi-Architecture Support

**provenance-demo is built for multiple architectures:**

| Architecture | Status | Notes |
|--------------|--------|-------|
| **linux/amd64** | ✅ Fully Supported | x86_64 processors (Intel, AMD) |
| **linux/arm64** | ✅ Fully Supported | ARM64 processors (Apple Silicon, AWS Graviton, Raspberry Pi 4+) |

### Pull Architecture-Specific Images

```bash
# Pull for specific architecture (automatic on native platform)
docker pull --platform linux/amd64 ghcr.io/redoubt-cysec/provenance-demo:latest
docker pull --platform linux/arm64 ghcr.io/redoubt-cysec/provenance-demo:latest

# Docker automatically selects the correct architecture for your platform
docker pull ghcr.io/redoubt-cysec/provenance-demo:latest
```

### Verify Multi-Arch Manifest

```bash
# Inspect image manifest
docker manifest inspect ghcr.io/redoubt-cysec/provenance-demo:latest

# Check available architectures
docker buildx imagetools inspect ghcr.io/redoubt-cysec/provenance-demo:latest
```

### Build Multi-Arch Images Locally

```bash
# Set up buildx for multi-arch builds
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t provenance-demo:local \
  --load \
  .

# Or build and push to registry
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/YOUR_USERNAME/provenance-demo:latest \
  --push \
  .
```

### Platform-Specific Testing

```bash
# Test on amd64
docker run --rm --platform linux/amd64 \
  ghcr.io/redoubt-cysec/provenance-demo:latest --version

# Test on arm64 (requires QEMU if running on amd64)
docker run --rm --platform linux/arm64 \
  ghcr.io/redoubt-cysec/provenance-demo:latest --version

# QEMU setup (if needed for cross-platform testing)
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

### Performance Notes

- **Native execution** (matching your CPU architecture) provides best performance
- **Cross-platform execution** (e.g., ARM on Intel) uses QEMU emulation and is slower
- **Apple Silicon (M1/M2/M3)**: Use linux/arm64 for best performance
- **AWS Graviton**: Use linux/arm64 for best performance and cost
- **Intel/AMD servers**: Use linux/amd64 for best performance

## Platform-Specific Notes

### macOS

- Docker Desktop recommended
- **Apple Silicon (M1/M2/M3)**: Automatically uses linux/arm64 images
- **Intel Macs**: Automatically uses linux/amd64 images
- Can run both architectures with QEMU emulation
- File sharing settings may affect volume mounts
- Resource limits configurable in Docker Desktop

### Linux

- Native Docker support
- Best performance
- Requires systemd or init system
- SELinux/AppArmor considerations
- **ARM64 Linux** (Raspberry Pi, AWS Graviton): Automatically uses linux/arm64
- **x86_64 Linux**: Automatically uses linux/amd64

### Windows

- Docker Desktop or WSL2 backend
- Automatically uses linux/amd64 images
- Volume mount path format different: `/c/Users/...`
- PowerShell syntax differences
- Hyper-V or WSL2 required

## Advanced Usage

### Multi-Stage Builds

```dockerfile
# Example: Custom image extending provenance-demo
FROM ghcr.io/redoubt-cysec/provenance-demo:latest AS base

FROM python:3.11-slim
COPY --from=base /app /app
# Add your customizations
```

### Custom Entrypoint

```bash
# Override entrypoint
docker run --entrypoint /bin/bash \
  ghcr.io/redoubt-cysec/provenance-demo:latest

# Use as base for scripts
docker run --rm -v $(pwd):/scripts \
  --entrypoint /scripts/my-script.sh \
  ghcr.io/redoubt-cysec/provenance-demo:latest
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run verification in Docker
  run: |
    docker pull ghcr.io/redoubt-cysec/provenance-demo:latest
    docker run -v ${{ github.workspace }}:/workspace \
      -e GITHUB_REPOSITORY=${{ github.repository }} \
      ghcr.io/redoubt-cysec/provenance-demo:latest verify
```

### Build from Source

```bash
# Clone repository
git clone https://github.com/redoubt-cysec/provenance-demo.git
cd provenance-demo

# Build Docker image
docker build -t provenance-demo:local .

# Run local image
docker run provenance-demo:local --version
```

## Container Registries

### GitHub Container Registry (GHCR)

```bash
# Pull from GHCR (default)
docker pull ghcr.io/redoubt-cysec/provenance-demo:latest

# Login (for private repos)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Docker Hub (if published)

```bash
# Pull from Docker Hub
docker pull redoubtcysec/provenance-demo:latest
```

### Private Registry

```bash
# Pull from private registry
docker pull registry.example.com/provenance-demo:latest

# Login to private registry
docker login registry.example.com
```

## Next Steps

1. ✅ Image pulled
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project
7. 💡 Explore Docker Compose for complex setups
8. 🔒 Set up automated security scanning
9. 📦 Consider Kubernetes deployment

## Support

- **Issues:** Report Docker-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run verification for all images
- **Docker Help:** Visit [docs.docker.com](https://docs.docker.com)
- **OCI Spec:** See [opencontainers.org](https://opencontainers.org)

---

**Installation Method:** Docker/OCI (Container Images)
**Production Ready:** ✅ Yes
**Automated Testing:** ✅ Phase 1 + Phase 2
**Last Updated:** 2025-11-01
