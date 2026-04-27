# ✅ Render Correct Fix - The Real Solution

## The Real Problem

Render's service has `Root Directory` set to something that makes it look for files at `/opt/render/project/src/frontend/src/lib/api` instead of `/opt/render/project/frontend/src/lib/api.ts`.

No matter what we do with code redirects, Render will keep looking in the wrong place because the `Root Directory` is misconfigured.

## The Real Solution

We need to configure Render's service with the CORRECT settings. The service was created manually and has wrong settings.

### Step 1: Delete the Current Service (Optional but Recommended)

If possible, delete the current service and recreate it with correct settings. But if you want to keep it, proceed to Step 2.

### Step 2: Update Service Settings in Render Dashboard

Go to: https://dashboard.render.com

Select: `datacollect-cameroun-frontend` (srv-d7n15q28qa3s739vgmv0)

Go to: **Settings** tab

Update these fields:

#### Root Directory
- **Current**: (probably `src/frontend` or something wrong)
- **Change to**: `.` (dot) or leave completely empty
- **Why**: This tells Render the project root is the repository root, not a subdirectory

#### Build Command
- **Current**: `npm install && npm run build`
- **Change to**: `cd frontend && npm ci --legacy-peer-deps && npm run build`
- **Why**: This explicitly navigates to the frontend directory and builds it correctly

#### Publish Directory
- **Current**: (probably `dist` or `frontend/dist`)
- **Change to**: `frontend/dist`
- **Why**: This tells Render where the built files are located (relative to root directory)

#### Environment Variables
Go to **Environment** tab and add:
- **Key**: `VITE_API_URL`
- **Value**: `https://datacollect-cameroun-prod.onrender.com`

### Step 3: Clear Build Cache and Deploy

1. Go to **Settings** tab
2. Scroll down to **Build & Deploy** section
3. Click **Clear build cache & deploy** (if available)
4. Or go to **Deploys** tab and click **Create Deploy**

## Expected Build Output

```
==> Running build command 'cd frontend && npm ci --legacy-peer-deps && npm run build'...

> npm ci
added 687 packages in 50s

> npm run build
vite v5.4.21 building for production...
✓ 1098 modules transformed.
✓ built in 3.40s

==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉
```

## Configuration Reference

| Setting | Value |
|---------|-------|
| Root Directory | `.` (dot) or empty |
| Build Command | `cd frontend && npm ci --legacy-peer-deps && npm run build` |
| Publish Directory | `frontend/dist` |
| VITE_API_URL | `https://datacollect-cameroun-prod.onrender.com` |

## Why This Works

1. **Root Directory = `.`** - Tells Render the project root is the repository root
2. **Build Command navigates to frontend** - Explicitly goes to the frontend directory
3. **npm ci** - Uses package-lock.json for consistent installs
4. **Publish Directory = `frontend/dist`** - Tells Render where the built files are

## Files Updated

1. **`render.yaml`** - Updated with correct build command
2. **`package.json`** - Root-level package.json with build script
3. **`.render-build`** - Build script for reference
4. **Removed `src/` directory** - No longer needed

## What NOT to Do

❌ Don't set Root Directory to `src/frontend`  
❌ Don't set Root Directory to `frontend`  
❌ Don't use `npm install` (use `npm ci`)  
❌ Don't set Publish Directory to `dist` (use `frontend/dist`)  

## Troubleshooting

### If Build Still Fails

1. Check Render logs for exact error
2. Verify Root Directory is `.` or empty
3. Verify Build Command is `cd frontend && npm ci --legacy-peer-deps && npm run build`
4. Verify Publish Directory is `frontend/dist`
5. Clear build cache and deploy again

### Common Issues

| Issue | Solution |
|-------|----------|
| `Cannot find module` | Check Root Directory is `.` or empty |
| `npm install` running | Build Command should have `npm ci` |
| Files not found | Check Publish Directory is `frontend/dist` |
| API not working | Check VITE_API_URL environment variable |

## Next Steps

1. Go to https://dashboard.render.com
2. Select `datacollect-cameroun-frontend`
3. Update settings as shown above
4. Clear build cache and deploy
5. Monitor build logs
6. Verify frontend loads

---

**Status**: Ready for correct deployment ✅

**Time to completion**: 10-15 minutes
