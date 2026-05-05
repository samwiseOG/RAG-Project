#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

echo "=========================================="
echo "RAG Application - Python Services"
echo "=========================================="
echo ""

# Wait for Qdrant to be ready
echo "Waiting for Qdrant vector database at ${QDRANT_URL}..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "${QDRANT_URL}/health" > /dev/null 2>&1; then
        echo "✓ Qdrant is ready"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "  Waiting... ($attempt/${max_attempts})"
    fi
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "✗ Qdrant failed to start. Check docker-compose logs."
    exit 1
fi

echo ""
echo "Starting Flask API server on port 5001..."
python -u server/api.py &
FLASK_PID=$!
echo "  Flask PID: $FLASK_PID"

sleep 2

# Wait for Flask to be ready
echo "Waiting for Flask API to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:5001/collections" > /dev/null 2>&1; then
        echo "✓ Flask API is ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

echo ""
echo "Starting Streamlit UI on port 8501..."
echo ""
streamlit run ui/app.py --logger.level=info 2>&1 &
STREAMLIT_PID=$!
echo "  Streamlit PID: $STREAMLIT_PID"

echo ""
echo "=========================================="
echo "Services running:"
echo "  • Flask API: http://localhost:5001"
echo "  • Streamlit UI: http://localhost:8501"
echo "  • Qdrant: ${QDRANT_URL}"
echo "=========================================="
echo ""

# Keep script running and handle signals
trap 'kill $FLASK_PID $STREAMLIT_PID 2>/dev/null; exit 0' SIGTERM SIGINT

# Wait for all services
wait
