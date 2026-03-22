# ─────────────────────────────────────────────────────────────────
# HSAE v10.0 Dockerfile
# Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
# ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="saifeldinkhedir@gmail.com" \
      version="10.0.0" \
      description="HydroSovereign AI Engine v10.0"

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget git gcc g++ \
    libgdal-dev libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY . .

# Create required directories
RUN mkdir -p /app/HSAE_Data /app/data/grdc /app/data/glofas \
             /app/outputs /app/logs

# Expose ports
EXPOSE 8501 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v9/health || exit 1

# Default: run both API + Streamlit
# Override with: docker run ... streamlit run app.py
CMD ["sh", "-c", \
  "uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 1 & \
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true"]
