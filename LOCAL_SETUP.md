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
pip install -r requirements-prod.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:NJtz24HYFr9JNrNK@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres"
export SECRET_KEY="datacollect-cameroun-secret-key-2024"

# Start backend (connects to Supabase)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

### 2. Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies (one time only, uses npm cache)
npm ci

# Create .env.local file
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## API Endpoints

- **Health Check**: `GET http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Datasets**: `GET http://localhost:8000/api/v1/datasets`
- **Analyses**: `GET http://localhost:8000/api/v1/analyses`
- **Data Collection**: `GET http://localhost:8000/api/v1/collect/sources`

## Database

- **Type**: PostgreSQL (Supabase)
- **Host**: `db.qsuemkbonmgfufpcscua.supabase.co`
- **Database**: `postgres`
- **Auto-initialized** on first backend startup

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Verify database connection
psql postgresql://postgres:NJtz24HYFr9JNrNK@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres
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

- **Backend**: Deployed to Render at https://datacollect-cameroun-prod.onrender.com
- **Frontend**: Built automatically via GitHub Actions on every push to `main`
- **Database**: Supabase PostgreSQL (shared across local and production)

## Notes

- Backend uses Supabase PostgreSQL for both local and production
- Frontend uses Vite for fast development
- All API calls are CORS-enabled
- Database tables are auto-created on startup
- Environment variables are required for backend to connect to Supabase
