# Docker Setup for RAG Project

This document provides comprehensive instructions for building, running, and managing the RAG application using Docker.

## Overview

The Docker setup orchestrates four main components in a single container:
- **Ollama**: LLM and embedding models (models downloaded at runtime)
- **Qdrant**: Vector database for semantic search
- **Flask API**: RESTful backend server (port 5001)
- **Streamlit UI**: Web interface for querying (port 8501)

All services are managed by the `entrypoint.sh` startup script, which:
1. Starts Ollama daemon and verifies availability
2. Downloads required models (nomic-embed-text, deepseek-r1:1.5b)
3. Starts Qdrant with persistent storage
4. Starts Flask API server
5. Starts Streamlit UI in the foreground

## Prerequisites

- Docker installed (version 20.10 or later)
- Docker Compose (optional, for easier volume management)
- 30+ GB free disk space (Ollama models + vectors + OS)
- 8+ GB RAM recommended (2GB for Ollama, 2GB for Qdrant, 2GB for Python services)

## Quick Start

### 1. Build the Docker Image

```bash
# Build the image (takes ~5-10 minutes on first run)
docker build -t rag-app:latest .
```

### 2. Run the Container

```bash
# Create .env file from example
cp .env.example .env

# Run the container with persistent volumes
docker run -d \
  --name rag-app \
  -p 5001:5001 \
  -p 8501:8501 \
  -p 6333:6333 \
  -v qdrant_data:/qdrant_storage \
  -v app_data:/app/data \
  -v ollama_models:/home/appuser/.ollama \
  --env-file .env \
  rag-app:latest
```

### 3. Access the Application

- **Streamlit UI**: http://localhost:8501
- **Flask API**: http://localhost:5001
- **Qdrant Dashboard**: http://localhost:6333/dashboard (if available)

### 4. View Logs

```bash
# Follow logs in real-time
docker logs -f rag-app

# View last 100 lines
docker logs --tail 100 rag-app
```

## Detailed Configuration

### Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```bash
cp .env.example .env
```

Key environment variables:
- `QDRANT_URL`: Vector database endpoint (default: `http://localhost:6333`)
- `DEFAULT_COLLECTION_NAME`: Initial Qdrant collection (default: `RAG-Project-Langchain`)
- `VECTOR_SIZE`: Embedding dimension (768 for nomic-embed-text)
- `DISTANCE_METRIC`: Vector similarity metric (`DOT`, `COSINE`, `EUCLID`)
- `OLLAMA_HOST`: Ollama service endpoint (default: `localhost:11434`)
- `LLM_MODEL`: LLM model to use (default: `deepseek-r1:1.5b`)
- `EMBEDDING_MODEL`: Embedding model (default: `nomic-embed-text`)

### Volume Mounts

The container uses three volumes for persistence:

```bash
docker run \
  -v qdrant_data:/qdrant_storage \           # Vector database storage
  -v app_data:/app/data \                     # Uploaded PDFs and docs
  -v ollama_models:/home/appuser/.ollama \   # Downloaded Ollama models
  rag-app:latest
```

**Important**: These volumes survive container restarts and upgrades. To reset data:

```bash
# List volumes
docker volume ls | grep rag-app

# Remove a specific volume
docker volume rm qdrant_data
docker volume rm app_data
docker volume rm ollama_models
```

### Port Mappings

| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| Ollama | 11434 | (optional) | LLM API |
| Qdrant | 6333 | 6333 | Vector DB |
| Flask API | 5001 | 5001 | Backend API |
| Streamlit UI | 8501 | 8501 | Web UI |

To change external ports:

```bash
docker run -d \
  -p 8080:5001 \      # Map Flask to 8080
  -p 9000:8501 \      # Map Streamlit to 9000
  -p 7000:6333 \      # Map Qdrant to 7000
  rag-app:latest
```

## Common Operations

### Start the Container

```bash
docker run -d \
  --name rag-app \
  -p 5001:5001 \
  -p 8501:8501 \
  -p 6333:6333 \
  -v qdrant_data:/qdrant_storage \
  -v app_data:/app/data \
  -v ollama_models:/home/appuser/.ollama \
  --env-file .env \
  rag-app:latest
```

### Stop the Container

```bash
docker stop rag-app
```

### Restart the Container

```bash
docker restart rag-app
```

### Remove the Container

```bash
# Stop first
docker stop rag-app

# Remove container
docker rm rag-app

# Optional: Remove volumes if you want to clean up data
docker volume rm qdrant_data app_data ollama_models
```

### View Container Status

```bash
# Get container info
docker ps -a | grep rag-app

# Get detailed information
docker inspect rag-app

# Get resource usage
docker stats rag-app
```

### Execute Commands Inside Container

```bash
# Open a shell
docker exec -it rag-app /bin/bash

# Run a Python command
docker exec rag-app python -c "import ollama; print(ollama.__version__)"

# Check Ollama models
docker exec rag-app ollama list
```

## Troubleshooting

### Container Exits Immediately

**Problem**: Container starts but exits after a few seconds.

**Solution**:
1. Check logs: `docker logs rag-app`
2. Common causes:
   - Qdrant failed to start (check disk space, permissions)
   - Ollama failed to start (check available RAM)
   - Port already in use (change external port in `docker run`)

### Services Not Responding

**Problem**: Cannot connect to Flask, Qdrant, or Streamlit.

**Solution**:
1. Verify container is running: `docker ps | grep rag-app`
2. Verify ports are exposed: `docker port rag-app`
3. Test connectivity: `curl http://localhost:5001/collections`
4. Check logs: `docker logs rag-app`

### Slow Model Download

**Problem**: Container takes 10+ minutes to start (downloading models).

**Solution**:
- First startup is slow due to model downloads. Subsequent starts use cached models.
- You can pre-pull models (requires rebuilding the image) for faster startup.
- Check download progress in logs: `docker logs -f rag-app`

### Out of Disk Space

**Problem**: Docker build fails or container exits during model download.

**Solution**:
```bash
# Check disk usage
docker system df

# Remove unused images/volumes
docker system prune -a

# Clean up old containers
docker rm $(docker ps -aq --filter status=exited)
```

### Permission Denied Errors

**Problem**: Cannot write to `/app/data` or `/qdrant_storage`.

**Solution**:
- The container runs as non-root user (`appuser:1000`)
- Host volumes should be writable by this user
- Fix permissions: `sudo chown -R 1000:1000 /path/to/volume`

## Performance Optimization

### Increase Available Memory

```bash
# Docker Desktop: Adjust in Settings
# Linux: Set Docker daemon memory limit

docker run --memory 8g rag-app:latest
```

### Use Named Volumes for Better Performance

```bash
# Create named volumes explicitly
docker volume create qdrant_data
docker volume create app_data
docker volume create ollama_models

# Use with docker run
docker run -v qdrant_data:/qdrant_storage ...
```

### Enable Parallel Model Pulling

Edit `entrypoint.sh` to pull multiple models in parallel:

```bash
# Instead of sequential pulls
ollama pull nomic-embed-text &
ollama pull deepseek-r1:1.5b &
wait  # Wait for both to complete
```

## Advanced Usage

### Use Docker Compose (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  rag-app:
    build: .
    container_name: rag-app
    ports:
      - "5001:5001"
      - "8501:8501"
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant_storage
      - app_data:/app/data
      - ollama_models:/home/appuser/.ollama
    env_file: .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

volumes:
  qdrant_data:
  app_data:
  ollama_models:
```

Then use:

```bash
docker-compose up -d        # Start
docker-compose logs -f      # View logs
docker-compose down         # Stop
```

### Change Default Models

Modify the `entrypoint.sh` script to use different models:

```bash
# In entrypoint.sh, change:
ollama pull your-embedding-model
ollama pull your-llm-model
```

Also update in `llm/model.py` or environment variables.

### Export Container as Image

```bash
# After successful setup, save the container state
docker commit rag-app rag-app-snapshot:latest

# Use the snapshot in the future
docker run rag-app-snapshot:latest
```

## Monitoring and Health Checks

### Verify Services Are Running

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Qdrant
curl http://localhost:6333/health

# Check Flask
curl http://localhost:5001/collections

# Check Streamlit (should return HTML)
curl http://localhost:8501
```

### Monitor Resource Usage

```bash
# Real-time stats
docker stats rag-app

# Container processes
docker exec rag-app ps aux
```

## Update and Rebuild

### Rebuild Image with Latest Code

```bash
# Stop running container
docker stop rag-app

# Rebuild image
docker build -t rag-app:latest .

# Run updated container (volumes persist data)
docker run -d --name rag-app ... rag-app:latest
```

### Upgrade Python Dependencies

```bash
# Update requirements.txt
# Then rebuild and restart
docker stop rag-app && docker rm rag-app
docker build --no-cache -t rag-app:latest .
docker run -d --name rag-app ... rag-app:latest
```

## Production Deployment

For production use, consider:

1. **Use a Docker Registry**: Push images to Docker Hub or private registry
   ```bash
   docker tag rag-app:latest myregistry/rag-app:v1.0
   docker push myregistry/rag-app:v1.0
   ```

2. **Use Kubernetes or Docker Swarm**: Orchestrate multiple instances

3. **Setup Reverse Proxy**: Use Nginx/Caddy for SSL/TLS
   ```nginx
   server {
       listen 443 ssl;
       server_name rag.example.com;
       
       location / {
           proxy_pass http://localhost:8501;
       }
       
       location /api/ {
           proxy_pass http://localhost:5001;
       }
   }
   ```

4. **Persistent Logging**: Configure Docker logging driver
   ```bash
   docker run --log-driver json-file --log-opt max-size=10m rag-app:latest
   ```

5. **Environment Secrets**: Use Docker Secrets instead of .env
   ```bash
   echo "your-secret-value" | docker secret create db_password -
   ```

## Support and Documentation

- Flask API: [Flask Documentation](https://flask.palletsprojects.com/)
- Streamlit: [Streamlit Documentation](https://docs.streamlit.io/)
- Qdrant: [Qdrant Documentation](https://qdrant.tech/documentation/)
- Ollama: [Ollama GitHub](https://github.com/ollama/ollama)
- LangChain: [LangChain Documentation](https://python.langchain.com/)

---

**Last Updated**: 2026-05-04
**Docker Version**: 20.10+
**Python Version**: 3.11
