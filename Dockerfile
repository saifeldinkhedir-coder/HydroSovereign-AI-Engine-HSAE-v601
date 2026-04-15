# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package
COPY pyproject.toml README_PYPI.md ./
COPY hydrosovereign/ hydrosovereign/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        numpy pandas scipy scikit-learn \
        torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir fastapi uvicorn[standard] plotly requests


# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM python:3.12-slim AS production

LABEL maintainer="Seifeldin M.G. Alkedir <saifeldinkhedir@gmail.com>"
LABEL org.opencontainers.image.title="HydroSovereign AI Engine"
LABEL org.opencontainers.image.version="6.5.0"
LABEL org.opencontainers.image.description="AI-powered transboundary water governance"
LABEL org.opencontainers.image.authors="Seifeldin M.G. Alkedir (ORCID: 0000-0003-0821-2991)"
LABEL org.opencontainers.image.source="https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601"
LABEL org.opencontainers.image.licenses="GPL-3.0"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY --from=builder /build/hydrosovereign ./hydrosovereign

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=2

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE 8000

# Create non-root user
RUN addgroup --system hsae && adduser --system --ingroup hsae hsae
RUN chown -R hsae:hsae /app
USER hsae

# Start server
CMD uvicorn hydrosovereign.api_server:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --log-level info
