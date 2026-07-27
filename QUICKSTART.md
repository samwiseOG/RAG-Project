# RAG Project - Docker Quick Start

## 🚀 Quick Start (3 minutes)

### Prerequisites
- Docker and Docker Compose installed
- 30+ GB disk space (for Ollama models)
- 8+ GB RAM

### 1. Create Environment File
```bash
cp .env.example .env
```

### 2. Start All Services
```bash
docker-compose up -d
```

This automatically:
- ✅ Pulls Ollama official image and starts LLM service
- ✅ Pulls Qdrant official image and starts vector database
- ✅ Builds Python app image (Flask + Streamlit)
- ✅ Waits for Qdrant and Ollama to be ready
- ✅ Starts Flask API and Streamlit UI
- ✅ Shows all services are healthy

### 3. Open Application
- **UI**: http://localhost:8501
- **API**: http://localhost:5001
- **Qdrant**: http://localhost:6333/dashboard (if available)

### 4. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f ollama
docker-compose logs -f qdrant
```

---

## 📋 What This Does

✅ **Ollama** (11434) - LLM inference with official image  
✅ **Qdrant** (6333) - Vector database with official image  
✅ **Flask** (5001) - REST API backend  
✅ **Streamlit** (8501) - Web UI frontend  
✅ **Auto health checks** - Services won't start until dependencies are ready  
✅ **Persistent volumes** - Data survives container restarts  

---

## 🔧 Common Commands

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart a specific service
docker-compose restart app

# Execute command in running container
docker-compose exec app python -c "import sys; print(sys.version)"

# Rebuild and restart
docker-compose up -d --build

# View resource usage
docker stats
```

---

## ⚙️ Configuration

Edit `.env` file to customize:
- `DEFAULT_COLLECTION_NAME` - Qdrant collection name
- `VECTOR_SIZE` - Embedding dimension (768 for nomic-embed-text)
- `DISTANCE_METRIC` - Vector similarity metric (DOT, COSINE, EUCLID)

---

## 📚 Advanced

See [DOCKER_README.md](DOCKER_README.md) for:
- Port mapping customization
- Volume management
- Troubleshooting
- Performance tuning
- Production deployment

---

## ✅ Verify Everything Works

1. **Check UI loads**: Open http://localhost:8501
2. **Check API responds**: `curl http://localhost:5001/collections`
3. **Check Ollama models are loaded**: `curl http://localhost:11434/api/tags`
4. **Check Qdrant is healthy**: `curl http://localhost:6333/healthz`

---

**All services should start within 1-3 minutes. Initial Ollama model downloads may take 5-10 minutes on first run.**
