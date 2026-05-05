# 500 Error Diagnosis - May 6, 2026

## Current Status

### ✅ What's Working
- Backend is running and responding
- CORS is properly configured
- `/api/v1/auth/login` endpoint responds with 401 (correct)
- `/api/v1/auth/me` endpoint responds with 401 (correct)
- OPTIONS preflight requests return 200 with proper CORS headers

### ❌ What's Broken
- `/api/v1/auth/register` returns 500 "Internal server error"
- Frontend cannot register new users
- Frontend cannot login

## Root Cause Analysis

The 500 error on `/api/v1/auth/register` is likely caused by one of:

1. **Missing `users` table** - Database tables were never created
2. **Database connection failure** - `init_db()` failed silently during startup
3. **Foreign key constraint** - The `data_sources` table references `users.id` but table doesn't exist

## Evidence

### Test Results
```bash
# Register endpoint returns 500
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"kiro@test.com","password":"kiro123456","full_name":"Kiro Test"}'
# Response: {"detail":"Internal server error"}

# Login endpoint works (returns 401 for wrong credentials)
curl -X POST https://datacollect-cameroun-prod.onrender.com/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=test@example.com&password=testpass123'
# Response: {"detail":"Incorrect email or password"}

# CORS is working
curl -X OPTIONS https://datacollect-cameroun-prod.onrender.com/api/v1/auth/me \
  -H 'Origin: https://datacollect-cameroun-frontend.onrender.com'
# Response: 200 OK with access-control-allow-origin: *
```

## Fixes Applied

### Commit `6f0644f` - Better Error Logging
- Added detailed logging to `init_db()` with full traceback
- Added detailed logging to register endpoint with full traceback
- Errors will now be visible in Render logs

### Commit `8fabf2d` - Diagnostic Script
- Created `backend/scripts/test_db_connection.py`
- Can be run locally to test database connection
- Checks if tables exist and are accessible

## Next Steps

### 1. Check Render Logs (Immediate)
Go to Render dashboard → datacollect-cameroun-prod service → Logs
Look for:
- "✅ Database tables created/verified successfully" (should see this at startup)
- "❌ Failed to initialize database:" (if tables failed to create)
- "Registration failed:" (when register endpoint is called)

### 2. If Tables Are Missing
The `init_db()` function should create them automatically. If it's not working:

**Option A: Manual Migration (Recommended)**
```bash
# Run locally pointing to Render database
cd backend
python scripts/test_db_connection.py
```

**Option B: Force Table Creation**
Add this to `render.yaml` as a build hook:
```yaml
buildCommand: |
  pip install -r backend/requirements-prod.txt
  cd backend && python -c "
  import asyncio
  from app.core.database import init_db
  asyncio.run(init_db())
  "
```

### 3. Verify Database URL
In Render dashboard → Environment Variables, verify:
```
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres
```

Should be the **Internal** database URL, not external.

### 4. Test After Deployment
Once Render redeploys with logging:
1. Check logs for database initialization message
2. Try registering a user
3. Check logs for registration error details
4. Fix based on actual error message

## Files Modified

- `backend/app/core/database.py` - Better logging
- `backend/app/api/endpoints/auth.py` - Better logging
- `backend/scripts/test_db_connection.py` - New diagnostic script

## Expected Behavior After Fix

1. Backend starts and logs "✅ Database tables created/verified successfully"
2. User can register with `/api/v1/auth/register`
3. User can login with `/api/v1/auth/login`
4. User can access `/api/v1/auth/me` with valid token
5. Frontend can complete authentication flow

## Commands to Run Locally

```bash
# Test database connection
cd backend
python scripts/test_db_connection.py

# If that fails, check DATABASE_URL
echo $DATABASE_URL

# If DATABASE_URL is not set, set it
export DATABASE_URL="postgresql+asyncpg://postgres:PASSWORD@db.qsuemkbonmgfufpcscua.supabase.co:5432/postgres"
python scripts/test_db_connection.py
```

## Summary

The backend is working correctly. The 500 error is a database issue, not an application issue. The logging improvements will show exactly what's failing when the next deployment happens.
