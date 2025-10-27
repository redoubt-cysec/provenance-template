# Multi-stage Dockerfile for Redoubt Release Demo
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
RUN useradd -m -u 1000 redoubt && \
    mkdir -p /app && \
    chown redoubt:redoubt /app

WORKDIR /app
USER redoubt

# Copy only the built artifact
COPY --from=builder --chown=redoubt:redoubt /build/dist/redoubt-release-template.pyz /app/redoubt-release-template.pyz

# Make executable
RUN chmod +x /app/redoubt-release-template.pyz

# Metadata
LABEL org.opencontainers.image.title="Redoubt Release Demo"
LABEL org.opencontainers.image.description="Self-verifying CLI with complete supply chain security"
LABEL org.opencontainers.image.source="https://github.com/OWNER/REPO"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.documentation="https://github.com/OWNER/REPO/blob/main/README.md"

# Default entrypoint
ENTRYPOINT ["/app/redoubt-release-template.pyz"]
CMD ["--help"]

# Usage examples:
# docker build -t redoubt .
# docker run redoubt hello world
# docker run redoubt verify
# docker run redoubt --version
