#!/bin/bash
set -e

# Color output for logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is ready
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=60
    local attempt=0

    log_info "Waiting for $service to be ready at $host:$port..."
    
    while [ $attempt -lt $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            log_info "$service is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    log_error "$service failed to start after $max_attempts attempts"
    return 1
}

# Create data directories if they don't exist
mkdir -p /app/data
mkdir -p /qdrant_storage

log_info "=========================================="
log_info "RAG Application Docker Startup"
log_info "=========================================="

# Start Ollama daemon in the background
log_info "Starting Ollama daemon..."
ollama serve &
OLLAMA_PID=$!
sleep 3

# Wait for Ollama to be ready
if ! wait_for_service localhost 11434 "Ollama"; then
    log_error "Failed to start Ollama"
    kill $OLLAMA_PID 2>/dev/null || true
    exit 1
fi

# Pull the embedding model
log_info "Pulling embedding model: nomic-embed-text..."
timeout 600 ollama pull nomic-embed-text || log_warn "Failed to pull nomic-embed-text, will retry later"

# Pull the LLM model
log_info "Pulling LLM model: deepseek-r1:1.5b..."
timeout 600 ollama pull deepseek-r1:1.5b || log_warn "Failed to pull deepseek-r1:1.5b, will retry later"

log_info "Ollama models ready!"

# Start Qdrant in the background
log_info "Starting Qdrant vector database..."
qdrant --storage-path /qdrant_storage --http-port 6333 --grpc-port 6334 &
QDRANT_PID=$!
sleep 2

# Wait for Qdrant to be ready
if ! wait_for_service localhost 6333 "Qdrant"; then
    log_error "Failed to start Qdrant"
    kill $OLLAMA_PID 2>/dev/null || true
    kill $QDRANT_PID 2>/dev/null || true
    exit 1
fi

log_info "Qdrant is ready!"

# Start Flask API server in the background
log_info "Starting Flask server on port 5001..."
cd /app
python -u server/api.py &
FLASK_PID=$!
sleep 3

# Wait for Flask to be ready
if ! wait_for_service localhost 5001 "Flask"; then
    log_warn "Flask may still be starting..."
fi

log_info "Flask server started!"

# Start Streamlit UI in the foreground
log_info "Starting Streamlit UI on port 8501..."
streamlit run ui/app.py --logger.level=info --client.showErrorDetails=true

# If we reach here, Streamlit has exited
log_error "Streamlit has exited. Cleaning up..."
kill $OLLAMA_PID 2>/dev/null || true
kill $QDRANT_PID 2>/dev/null || true
kill $FLASK_PID 2>/dev/null || true
exit 1
