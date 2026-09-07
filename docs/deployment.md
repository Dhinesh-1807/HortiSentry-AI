# HortiSentry — Production Deployment Guide

**Target Scope:** Academic MVP / Prototype / Containerized Server Deployment  
**Supported Platforms:** Docker / Docker Compose / Linux (Ubuntu 22.04 LTS) / Windows Server  

---

## 1. Prerequisites & Environment Variables

- **Python:** 3.10+
- **Node.js:** 18+ and npm
- **Docker & Docker Compose:** Optional for containerized deployment

### `.env` File Configuration
Create `.env` in the repository root:
```ini
APP_ENV=production
SECRET_KEY=change-this-secret-key-for-production
DATABASE_URL=sqlite:///./hortisentry.db
ML_MODE=REAL
CONFIDENCE_THRESHOLD=0.70
MODEL_PATH=ml/artifacts/tomato_v1.pt
MAX_UPLOAD_SIZE_MB=10
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 2. Option A: Local / Virtual Machine Production Server Setup

### 2.1 Backend Core Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or .\venv\Scripts\Activate.ps1 (Windows)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize Database
python -m app.database.init_db

# 5. Start Uvicorn Server with multi-worker process
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2.2 Frontend Production Build Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm ci

# 3. Compile static production bundle
npm run build

# 4. Serve static assets via Nginx or serve
npx serve -s dist -l 5173
```

---

## 3. Option B: Docker Container Deployment

HortiSentry includes pre-configured Dockerfiles and `docker-compose.yml`:

```bash
# Build and launch all services in containerized environment
docker-compose up -d --build
```

### Docker Services Architecture:
- **`backend` service:** Runs FastAPI on port 8000 using Python 3.10-slim, mounting pre-trained `ml/artifacts/tomato_v1.pt` model weights.
- **`frontend` service:** Compiles React TypeScript assets and serves static bundle on port 5173 via Nginx.

---

## 4. Production Security Controls

1. **CORS Headers:** Restrict `CORS_ORIGINS` to authorized frontend domain names.
2. **File Permissions:** Ensure `uploads/` directory has write permissions restricted to the execution user.
3. **Database File:** Back up `hortisentry.db` periodically.
