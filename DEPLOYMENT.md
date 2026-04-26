# 🚀 DataCollect Pro Cameroun - Deployment Guide

## ✅ BACKEND - DEPLOYED ON RENDER

### Production URL
- **API**: https://datacollect-cameroun-prod.onrender.com
- **Swagger**: https://datacollect-cameroun-prod.onrender.com/docs
- **ReDoc**: https://datacollect-cameroun-prod.onrender.com/redoc
- **Health**: https://datacollect-cameroun-prod.onrender.com/health

### Database
- **Type**: Supabase PostgreSQL
- **Host**: db.qsuemkbonmgfufpcscua.supabase.co
- **Project**: qsuemkbonmgfufpcscua
- **Status**: ✅ Connected

### Deployment Status
- **Service ID**: srv-d7n00o57vvec738re8ng
- **Status**: ✅ LIVE
- **Region**: Oregon
- **Plan**: Free

## 📊 API Endpoints (Production)

### Health & Status
```bash
GET https://datacollect-cameroun-prod.onrender.com/health
GET https://datacollect-cameroun-prod.onrender.com/ready
```

### Users
```bash
GET https://datacollect-cameroun-prod.onrender.com/api/v1/users
```

### Analyses
```bash
GET https://datacollect-cameroun-prod.onrender.com/api/v1/analyses
POST https://datacollect-cameroun-prod.onrender.com/api/v1/analyses
GET https://datacollect-cameroun-prod.onrender.com/api/v1/analyses/{id}
```

## 🔧 Configuration

### Environment Variables
```
DATABASE_URL=postgresql+asyncpg://postgres:***@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres
ENVIRONMENT=production
DEBUG=False
```

### Build Command
```bash
pip install -r requirements-prod.txt
```

### Start Command
```bash
uvicorn app_prod:app --host 0.0.0.0 --port $PORT
```

## 📦 Frontend Deployment

### Option 1: Static Site on Render
```bash
# Build command
cd frontend && npm ci && npm run build

# Publish path
frontend/dist

# Environment
VITE_API_URL=https://datacollect-cameroun-prod.onrender.com
```

### Option 2: GitHub Pages
- Build via GitHub Actions
- Deploy to gh-pages branch
- Configure VITE_API_URL in build

## 🧪 Test Commands

### Health Check
```bash
curl https://datacollect-cameroun-prod.onrender.com/health
```

### Create Analysis
```bash
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "regression",
    "title": "Test Analysis"
  }'
```

### List Analyses
```bash
curl https://datacollect-cameroun-prod.onrender.com/api/v1/analyses
```

## 📈 Performance Optimization

### Data Strategy
1. **Supabase PostgreSQL**: Store all persistent data
2. **Caching**: Use Redis for frequently accessed data
3. **API Optimization**: Pagination, filtering, sorting
4. **CDN**: Render serves static assets globally

### Bandwidth Optimization
- Minimal dependencies (requirements-prod.txt)
- Async/await for concurrent requests
- Database connection pooling
- Gzip compression enabled

## 🔐 Security

### Credentials
- Database password: Stored in Render env vars
- API keys: Not exposed in code
- CORS: Enabled for all origins (can be restricted)

### Best Practices
- Use environment variables for secrets
- Enable HTTPS (automatic on Render)
- Validate all inputs
- Rate limiting (to be implemented)

## 📝 Next Steps

1. ✅ Backend deployed on Render
2. ✅ Connected to Supabase PostgreSQL
3. ⏳ Deploy frontend (static site or GitHub Pages)
4. ⏳ Configure frontend API URL
5. ⏳ Add authentication
6. ⏳ Implement rate limiting
7. ⏳ Add monitoring/logging

## 🎯 Project URLs

| Component | Local | Production |
|-----------|-------|------------|
| Backend | http://localhost:8000 | https://datacollect-cameroun-prod.onrender.com |
| Frontend | http://localhost:5173 | TBD |
| Swagger | http://localhost:8000/docs | https://datacollect-cameroun-prod.onrender.com/docs |
| Database | SQLite (local) | Supabase PostgreSQL |

## 📞 Support

- **Render Dashboard**: https://dashboard.render.com
- **Supabase Dashboard**: https://app.supabase.com
- **GitHub Repository**: https://github.com/choe73/data_analyste

---

**Status**: 🟢 **PRODUCTION READY** - Backend fully deployed and operational on Render with Supabase PostgreSQL.
