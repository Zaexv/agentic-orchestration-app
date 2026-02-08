# 🚀 Deployment Guide - AI Digital Twin

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Docker Deployment (Recommended)](#docker-deployment-recommended)
3. [Manual Deployment](#manual-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Health Checks](#health-checks)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required:
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **OpenAI API Key** (or compatible endpoint)
- **2GB RAM** minimum
- **1GB disk space**

### Optional:
- Python 3.12+ (for manual deployment)
- Node.js 20+ (for frontend development)
- PostgreSQL (for production database)

---

## Docker Deployment (Recommended)

### 1. Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd agent-orchestration-app

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

### 2. Build and Run

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost/ 

# Access the application
open http://localhost
```

### 4. Management Commands

```bash
# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Rebuild after code changes
docker-compose build
docker-compose up -d

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## Manual Deployment

### Backend Setup

```bash
# 1. Install Python dependencies
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Initialize database
python -c "from app.database import init_db; init_db()"

# 4. Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Install dependencies
cd front_end
npm install

# 2. Build for production
npm run build

# 3. Serve with nginx or any static server
# Option A: Using nginx
sudo cp dist/* /var/www/html/

# Option B: Using Node.js serve
npx serve -s dist -l 80
```

---

## Environment Configuration

### Required Variables

```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-...your-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:////app/data/database/conversations.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/digital_twin
```

### Optional Variables

```bash
# Vector Store
VECTOR_STORE_TYPE=chromadb  # or pinecone
PINECONE_API_KEY=...  # if using Pinecone
PINECONE_ENVIRONMENT=us-east-1-aws

# Model Configuration
DEFAULT_LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
LLM_TEMPERATURE=0.1

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false  # Set to false in production

# LangSmith (optional monitoring)
LANGSMITH_API_KEY=...
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT=digital-twin
```

### Production Settings

```bash
# Set environment to production
ENVIRONMENT=production

# Security
CORS_ORIGINS=https://yourdomain.com
API_RELOAD=false

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Health Checks

### Backend Health

```bash
# Health check endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "model": "gpt-4o-mini",
  "vector_store": "chromadb",
  "api_base": "https://api.openai.com/v1"
}
```

### Database Check

```bash
# Check database connection
curl http://localhost:8000/api/conversations?user_id=health_check

# Should return 200 OK
```

### Frontend Check

```bash
# Check frontend is serving
curl -I http://localhost/

# Should return 200 OK with HTML content
```

---

## Production Deployment

### Cloud Deployment (AWS/GCP/Azure)

#### 1. **Using Docker on EC2/Compute Engine/VM**

```bash
# SSH into your server
ssh user@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and deploy
git clone <your-repo>
cd agent-orchestration-app
cp .env.example .env
nano .env  # Add production values

# Run with docker-compose
docker-compose up -d

# Setup nginx reverse proxy (optional)
sudo apt install nginx
sudo nano /etc/nginx/sites-available/digital-twin
```

#### 2. **Using Container Services (ECS/Cloud Run/Container Apps)**

```bash
# Build and push images
docker build -t your-registry/digital-twin-backend:latest .
docker push your-registry/digital-twin-backend:latest

docker build -t your-registry/digital-twin-frontend:latest ./front_end
docker push your-registry/digital-twin-frontend:latest

# Deploy using cloud-specific CLI or console
```

### Database Migration (SQLite → PostgreSQL)

```bash
# 1. Export existing data (if any)
sqlite3 data/database/conversations.db .dump > backup.sql

# 2. Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/digital_twin

# 3. Restart application (auto-creates tables)
docker-compose restart backend
```

---

## Troubleshooting

### Issue: Backend won't start

**Check logs:**
```bash
docker-compose logs backend
```

**Common causes:**
- Missing OPENAI_API_KEY in .env
- Port 8000 already in use
- Database permission issues

**Solution:**
```bash
# Check port usage
lsof -i :8000

# Verify environment variables
docker-compose exec backend env | grep OPENAI

# Check database permissions
ls -la data/database/
```

### Issue: Frontend shows "Cannot connect to server"

**Check:**
1. Backend is running: `curl http://localhost:8000/health`
2. CORS configuration in production
3. API endpoint configuration in frontend

**Solution:**
```bash
# Ensure backend is accessible
docker-compose ps

# Check nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Issue: Database errors

**Check:**
```bash
# Verify database file
ls -lh data/database/conversations.db

# Check permissions
chmod 777 data/database/  # For development only!

# Reinitialize database
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### Issue: Vector DB not working

**Check:**
1. Embedding model endpoint is accessible
2. ChromaDB directory has write permissions
3. Documents are ingested

**Solution:**
```bash
# Check vector store
ls -lh data/vector_stores/

# Test ingestion
docker-compose exec backend python scripts/ingest_documents.py \
  --domain professional \
  --file data/documents/professional/technical_skills.txt
```

### Getting Help

1. **Check logs first**: `docker-compose logs -f`
2. **Verify health endpoints**: `/health` and `/api/conversations`
3. **Check GitHub issues**: [Project Issues]
4. **Review documentation**: See other docs/ files

---

## Monitoring & Maintenance

### Log Management

```bash
# View real-time logs
docker-compose logs -f

# Export logs
docker-compose logs > logs_$(date +%Y%m%d).txt

# Clean old logs
docker-compose logs --tail=1000 > recent_logs.txt
```

### Database Backups

```bash
# Backup SQLite database
cp data/database/conversations.db backups/conversations_$(date +%Y%m%d).db

# Backup vector store
tar -czf backups/vectors_$(date +%Y%m%d).tar.gz data/vector_stores/
```

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Check health after update
curl http://localhost:8000/health
```

---

## Security Checklist

- [ ] OPENAI_API_KEY not committed to Git
- [ ] `.env` file excluded from version control
- [ ] CORS origins restricted in production
- [ ] HTTPS enabled (use nginx/load balancer)
- [ ] Database backed up regularly
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] Regular dependency updates

---

## Next Steps

- Read [USER_GUIDE.md](./USER_GUIDE.md) for usage instructions
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for system details
- Check [MONITORING.md](./MONITORING.md) for observability setup

---

**Need help?** Open an issue or check existing documentation.
