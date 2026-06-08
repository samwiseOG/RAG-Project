# 🚀 Docker Compose Deployment Guide

## Overview

This RAG application uses **Docker Compose** to orchestrate 3 services:

```
┌─────────────────┐
│   Docker        │
├─────────────────┤
│ ollama          │  Ollama LLM service
│ (official img)  │  Port: 11434
├─────────────────┤
│ qdrant          │  Vector database
│ (official img)  │  Port: 6333
├─────────────────┤
│ app (Flask +    │  Python services
│ Streamlit)      │  Ports: 5001, 8501
│ (custom image)  │
└─────────────────┘
```

## Quick Start (3 steps)

### Step 1: Copy Environment File
```bash
cp .env.example .env
```

### Step 2: Start Services
```bash
docker-compose up -d
```

### Step 3: Access Application
- **Streamlit UI**: http://localhost:8501
- **Flask API**: http://localhost:5001
- **Qdrant**: http://localhost:6333

---

## 📋 What docker-compose Does

When you run `docker-compose up -d`:

1. **Ollama service starts** (official `ollama/ollama:latest` image)
   - Listens on port 11434
   - Models are stored in `ollama_models` volume
   - Pre-loads models on first startup

2. **Qdrant service starts** (official `qdrant/qdrant:latest` image)
   - Listens on port 6333
   - Data stored in `qdrant_storage` volume
   - Waits for Ollama health check

3. **Python app service starts** (custom Python image)
   - Builds from `Dockerfile`
   - Starts Flask API (port 5001)
   - Starts Streamlit UI (port 8501)
   - Waits for Qdrant to be healthy before starting

---

## 📊 Service Status

```bash
# View all services
docker-compose ps

# Expected output:
# NAME              COMMAND                 STATE      PORTS
# rag-ollama        "ollama serve"          Up         0.0.0.0:11434->11434/tcp
# rag-qdrant        "/qdrant --storage..."  Up         0.0.0.0:6333->6333/tcp
# rag-app           "/app/entrypoint-..."   Up         0.0.0.0:5001->5001/tcp, 0.0.0.0:8501->8501/tcp
```

---

## 🔍 Checking Service Health

```bash
# Check Ollama is loaded with models
curl http://localhost:11434/api/tags

# Expected response:
# {"models":[{"name":"nomic-embed-text:latest",...},{"name":"deepseek-r1:1.5b:latest",...}]}

# Check Qdrant is healthy
curl http://localhost:6333/healthz

# Expected response:
# {"status":"ok"}

# Check Flask API is responding
curl http://localhost:5001/collections

# Expected response:
# {...collections data...}
```

---

## 📜 Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ollama
docker-compose logs -f qdrant
docker-compose logs -f app

# Last 50 lines
docker-compose logs --tail 50

# Without following (one-time output)
docker-compose logs
```

---

## ⚙️ Common Operations

### Stop All Services
```bash
docker-compose stop
```
Services remain in Docker; data persists in volumes.

### Restart All Services
```bash
docker-compose restart
```

### Rebuild and Restart
```bash
docker-compose up -d --build
```
Use this after updating requirements.txt or Python code.

### Remove Everything (clean slate)
```bash
docker-compose down -v
```
⚠️ **Warning**: This deletes all volumes and data!

### View Service Resources
```bash
docker stats
```

### Execute Command in Service
```bash
# Run Python command in app service
docker-compose exec app python -c "import ollama; print(ollama.__version__)"

# Open shell in app service
docker-compose exec app bash

# Run curl in qdrant service
docker-compose exec qdrant curl http://localhost:6333/healthz
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Vector database
QDRANT_URL=http://qdrant:6333
DEFAULT_COLLECTION_NAME=RAG-Project-Langchain
VECTOR_SIZE=768
DISTANCE_METRIC=DOT

# Add any custom variables here
```

### Port Customization

Edit `docker-compose.yml` to change ports:
```yaml
services:
  app:
    ports:
      - "8080:5001"  # Change 5001 to 8080
      - "9000:8501"  # Change 8501 to 9000
  
  qdrant:
    ports:
      - "7000:6333"  # Change 6333 to 7000
  
  ollama:
    ports:
      - "12000:11434"  # Change 11434 to 12000
```

Then restart:
```bash
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Look for errors, especially in app service waiting for dependencies
```

### Out of Memory

```bash
# Check resource usage
docker stats

# Increase Docker memory limit and restart services
# (Docker Desktop: Settings → Resources → Memory)
```

### Port Already in Use

```bash
# Find what's using port 5001
lsof -i :5001

# Change port in docker-compose.yml and restart
docker-compose up -d
```

### Models Not Loaded in Ollama

```bash
# Check what models are available
docker-compose exec ollama ollama list

# Manually pull a model (takes time)
docker-compose exec ollama ollama pull nomic-embed-text
docker-compose exec ollama ollama pull deepseek-r1:1.5b
```

### Data Persists After Stop

This is **intentional** and good! Volumes keep data:

```bash
# To keep data:
docker-compose stop    # Temporary stop, data safe

# To delete data:
docker-compose down -v # Remove volumes
```

---

## 📦 Volume Locations

Docker volumes are managed by Docker. View them:

```bash
# List all volumes
docker volume ls | grep rag

# Expected output:
# rag-app-app_data
# rag-app-ollama_models
# rag-app-qdrant_storage

# View volume details
docker volume inspect <volume_name>

# Example:
docker volume inspect rag-app-app_data
```

---

## 🌐 Network Isolation

Services communicate through a Docker network (`rag-network`):

- **Ollama**: Accessible from app at `http://ollama:11434`
- **Qdrant**: Accessible from app at `http://qdrant:6333`
- **App**: Exposed to host at `localhost:5001` and `localhost:8501`

---

## 🚀 Production Deployment

For production, consider:

1. **Use docker-compose in production**: Works great for small to medium deployments
2. **Pin image versions**: Instead of `latest`, use specific versions:
   ```yaml
   ollama:
     image: ollama/ollama:v0.23.0
   qdrant:
     image: qdrant/qdrant:v1.7.0
   ```

3. **Use environment secrets**: Store sensitive variables securely
4. **Setup logging**: Configure Docker logging driver:
   ```yaml
   app:
     logging:
       driver: "json-file"
       options:
         max-size: "10m"
         max-file: "3"
   ```

5. **Use reverse proxy**: Put Nginx/Caddy in front for SSL/TLS
6. **Monitor services**: Use Prometheus, Grafana, or other monitoring tools

---

## 📚 Further Reading

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Ollama Docker Image](https://hub.docker.com/r/ollama/ollama)
- [Qdrant Docker Image](https://hub.docker.com/r/qdrant/qdrant)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Last Updated**: 2026-05-04  
**Recommended**: Docker 20.10+, Docker Compose 1.29+
