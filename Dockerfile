# Multi-stage build: base image with Python and system dependencies
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies required for Ollama, build tools, and utilities
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama (download and setup)
RUN curl -fsSL https://ollama.ai/install.sh | sh || \
    wget -O /usr/bin/ollama https://ollama.ai/download/ollama-linux-x86_64 && \
    chmod +x /usr/bin/ollama

# Create non-root user for running services
RUN useradd -m -u 1000 appuser

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . /app/

# Create necessary directories with proper permissions
RUN mkdir -p /app/data \
    && mkdir -p /app/cache \
    && mkdir -p /qdrant_storage \
    && chown -R appuser:appuser /app /qdrant_storage

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0:11434
ENV QDRANT_URL=http://localhost:6333
ENV DEFAULT_COLLECTION_NAME=RAG-Project-Langchain
ENV VECTOR_SIZE=768
ENV DISTANCE_METRIC=DOT
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=server/api.py
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Copy entrypoint script
COPY --chown=appuser:appuser entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 5001 8501 6333 11434

# Define volumes for persistent data
VOLUME ["/qdrant_storage", "/app/data", "/home/appuser/.ollama"]

# Health check for Ollama
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Start services via entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
