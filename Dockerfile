# RAG Application - Python Services (Flask API + Streamlit UI)
#
# IMPORTANT: This Dockerfile works with docker-compose.yml
# Ollama and Qdrant run in separate containers
#
# Usage: docker-compose up -d

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . /app/

# Create data directory
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Set environment variables for docker-compose networking
ENV PYTHONUNBUFFERED=1
ENV QDRANT_URL=http://qdrant:6333
ENV DEFAULT_COLLECTION_NAME=RAG-Project-Langchain
ENV VECTOR_SIZE=768
ENV DISTANCE_METRIC=DOT
ENV FLASK_APP=server/api.py
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

USER appuser

# Expose Flask and Streamlit ports
EXPOSE 5001 8501

# Copy entrypoint script
COPY --chown=appuser:appuser entrypoint-app.sh /app/
RUN chmod +x /app/entrypoint-app.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5001/collections || exit 1

ENTRYPOINT ["/app/entrypoint-app.sh"]
