# Multi-stage Dockerfile for Provenance Demo
# Produces a minimal container with only the verified binary

FROM python:3.10-slim as builder

# Set build environment for reproducibility
ENV TZ=UTC \
    LC_ALL=C \
    LANG=C \
    PYTHONHASHSEED=0

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Copy source
WORKDIR /build
COPY . .

# Build the .pyz
RUN ./scripts/build_pyz.sh

# Final minimal image
FROM python:3.10-slim

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

WORKDIR /app
USER appuser

# Copy only the built artifact
COPY --from=builder --chown=appuser:appuser /build/dist/provenance-demo.pyz /app/provenance-demo.pyz

# Make executable
RUN chmod +x /app/provenance-demo.pyz

# Metadata
LABEL org.opencontainers.image.title="Provenance Demo"
LABEL org.opencontainers.image.description="Self-verifying CLI with complete supply chain security"
LABEL org.opencontainers.image.source="https://github.com/redoubt-cysec/provenance-template"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.documentation="https://github.com/redoubt-cysec/provenance-template/blob/main/README.md"

# Default entrypoint
ENTRYPOINT ["/app/provenance-demo.pyz"]
CMD ["--help"]

# Usage examples:
# docker build -t provenance-demo .
# docker run provenance-demo hello world
# docker run provenance-demo verify
# docker run provenance-demo --version
#
# Or pull from GHCR:
# docker pull ghcr.io/redoubt-cysec/provenance-demo:latest
# docker run ghcr.io/redoubt-cysec/provenance-demo:latest --version
