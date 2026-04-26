# 🚀 Local Development Setup

## Prerequisites
- Python 3.11+ (via conda)
- Node.js 18+ (for frontend)
- Git

## Quick Start

### 1. Backend Setup

```bash
# Activate conda environment
conda activate trading_env

# Install dependencies (one time only)
cd backend
pip install -r requirements.txt

# Start backend
cd backend
uvicorn app_working:app --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

### 2. Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies (one time only, uses npm cache)
npm ci

# Start dev server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## API Endpoints

- **Health Check**: `GET http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`
- **Test Analysis**: `GET http://localhost:8000/api/v1/analysis/test`
- **Users**: `GET http://localhost:8000/api/v1/users`

## Database

- **Type**: SQLite (local development)
- **File**: `backend/datacollect.db`
- **Auto-initialized** on first backend startup

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>
```

### Frontend won't start
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
npm ci
```

### Slow npm install
- Use `npm ci` instead of `npm install`
- The `.npmrc` file has optimized timeout settings
- GitHub Actions will build the frontend for production

## Production Deployment

Frontend builds are compiled automatically via GitHub Actions on every push to `main`.

Backend deployment to Render will use `app_working.py` as the entry point.

## Notes

- Backend uses SQLite for local development (no PostgreSQL needed)
- Frontend uses Vite for fast development
- All API calls are CORS-enabled
- Database is auto-created on startup
