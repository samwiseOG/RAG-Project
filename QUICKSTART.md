# RAG Project - Docker Quick Start

## 🚀 Quick Start (2 minutes)

### 1. Build the Image
```bash
docker build -t rag-app .
```

### 2. Run the Container
```bash
docker run -d \
  --name rag-app \
  -p 5001:5001 \
  -p 8501:8501 \
  -p 6333:6333 \
  -v qdrant_data:/qdrant_storage \
  -v app_data:/app/data \
  -v ollama_models:/home/appuser/.ollama \
  rag-app
```

### 3. Open Application
- **UI**: http://localhost:8501
- **API**: http://localhost:5001
- **Logs**: `docker logs -f rag-app`

---

## 📋 What This Does

✅ Starts **Ollama** (LLM inference)  
✅ Starts **Qdrant** (vector database)  
✅ Starts **Flask** API (backend)  
✅ Starts **Streamlit** UI (frontend)  
✅ All services auto-managed with health checks  

---

## 🔧 Common Commands

```bash
# Check status
docker ps | grep rag-app

# View logs
docker logs -f rag-app

# Stop container
docker stop rag-app

# Restart
docker restart rag-app

# Execute command in container
docker exec rag-app ollama list

# Clean up
docker stop rag-app && docker rm rag-app
```

---

## 📚 Advanced Configuration

See [DOCKER_README.md](DOCKER_README.md) for:
- ✅ Environment variables
- ✅ Volume management
- ✅ Custom ports
- ✅ Docker Compose setup (alternative)
- ✅ Troubleshooting guide
- ✅ Performance tuning
- ✅ Production deployment

---

## ⚠️ System Requirements

- **Disk**: 30+ GB (for Ollama models + Qdrant vectors)
- **RAM**: 8+ GB
- **Docker**: v20.10+

---

## 🐳 Alternative: Docker Compose

If you prefer easier volume management:

```bash
# Create .env file
cp .env.example .env

# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

**For detailed documentation, see [DOCKER_README.md](DOCKER_README.md)**
