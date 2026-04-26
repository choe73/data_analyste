# 🔧 Render Final Fix - Root Directory Issue

## The Real Problem

Render is looking for files at the wrong path because it doesn't know the correct root directory.

**Render is looking at**: `/opt/render/project/src/frontend/src/lib/api`  
**Should be**: `/opt/render/project/frontend/src/lib/api.ts`

The extra `src/` in the path means Render thinks the root directory is `/opt/render/project/src/` instead of `/opt/render/project/`.

## Solution

We've added a root-level `package.json` that tells Render how to build the project correctly.

### What Changed

1. **Added `package.json` at root** - Tells Render how to build
2. **Added `build.sh` script** - Handles the build process
3. **Updated `render.yaml`** - Has correct configuration

### How It Works Now

When Render deploys:
1. Clones repo to `/opt/render/project/`
2. Finds `package.json` at root
3. Runs: `npm run build`
4. This executes: `cd frontend && npm ci && npm run build`
5. Vite builds correctly
6. Files are in `frontend/dist/`

## What You Need to Do in Render Dashboard

### Step 1: Go to Render Dashboard
https://dashboard.render.com

### Step 2: Select Frontend Service
- Service: `datacollect-cameroun-frontend`
- ID: `srv-d7n15q28qa3s739vgmv0`

### Step 3: Update Settings

Go to **Settings** tab:

```
Root Directory:      (leave empty or set to .)
Build Command:       npm run build
Publish Directory:   frontend/dist
```

### Step 4: Environment Variables

Go to **Environment** tab:

```
VITE_API_URL = https://datacollect-cameroun-prod.onrender.com
```

### Step 5: Deploy

Go to **Deploys** tab → **Create Deploy** → **Deploy latest commit**

## Expected Build Output

```
==> Running build command 'npm run build'...

> datacollect-pro-cameroun@1.0.0 build
> cd frontend && npm ci --legacy-peer-deps && npm run build

added 687 packages in 49s

> datacollect-frontend@1.0.0 build
> vite build

vite v5.4.21 building for production...
✓ 1098 modules transformed.
✓ built in 3.40s

==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉
```

## Why This Works

1. **Root directory is correct** - Render knows where the project root is
2. **Build command is simple** - Just `npm run build`
3. **Publish directory is correct** - Points to `frontend/dist/`
4. **Package.json handles the rest** - Navigates to frontend and builds

## Configuration Reference

| Setting | Value |
|---------|-------|
| Root Directory | `.` (current) or empty |
| Build Command | `npm run build` |
| Publish Directory | `frontend/dist` |
| VITE_API_URL | `https://datacollect-cameroun-prod.onrender.com` |

## Files Added

1. **`package.json`** - Root-level package.json with build script
2. **`build.sh`** - Build script for local testing
3. **`render.yaml`** - Full stack deployment config (reference)

## Testing Locally

To test the build locally:

```bash
npm run build
```

This will:
1. Navigate to `frontend/`
2. Run `npm ci --legacy-peer-deps`
3. Run `npm run build`
4. Generate `frontend/dist/`

## Troubleshooting

### If Build Still Fails

1. Check Render logs for error message
2. Verify Root Directory is empty or `.`
3. Verify Build Command is `npm run build`
4. Verify Publish Directory is `frontend/dist`
5. Trigger another deploy

### Common Issues

| Issue | Solution |
|-------|----------|
| `Cannot find module` | Check Publish Directory is `frontend/dist` |
| `npm install` running | Build Command should be `npm run build` |
| Files not found | Check Root Directory is empty or `.` |
| API not working | Check VITE_API_URL environment variable |

## Next Steps

1. Go to https://dashboard.render.com
2. Select `datacollect-cameroun-frontend`
3. Update settings as shown above
4. Trigger deploy
5. Monitor build logs
6. Verify frontend loads

---

**Status**: Ready for final deployment ✅

**Time to completion**: 15-20 minutes
