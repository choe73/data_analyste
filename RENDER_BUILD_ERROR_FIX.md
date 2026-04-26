# 🔧 Render Build Error - Root Directory Issue

## Error Message
```
Could not load /opt/render/project/src/frontend/src/lib/api
ENOENT: no such file or directory
```

## Root Cause
Render is looking for the file at the wrong path:
- **Render is looking at**: `/opt/render/project/src/frontend/src/lib/api`
- **Actual path**: `/opt/render/project/frontend/src/lib/api.ts`

This happens because:
1. The frontend service was created manually (not via render.yaml)
2. Render doesn't know the correct root directory
3. Render is treating `src/` as the root instead of the project root

## Solution

### Step 1: Update Render Service Configuration

Go to https://dashboard.render.com and select the frontend service (srv-d7n15q28qa3s739vgmv0):

1. **Go to Settings**
2. **Find "Root Directory" field**
3. **Set it to**: `frontend` (or leave empty if it's the default)
4. **Update Build Command** to:
   ```
   npm ci && npm run build
   ```
5. **Update Publish Directory** to:
   ```
   dist
   ```
6. **Click Save**

### Step 2: Trigger Manual Deploy

1. Go to **Deploys** tab
2. Click **Create Deploy**
3. Select **Deploy latest commit**
4. Monitor the build logs

## Why This Happens

When Render creates a static site service, it needs to know:
- **Root Directory**: Where the project root is (should be `frontend` or empty)
- **Build Command**: How to build the project
- **Publish Directory**: Where the built files are (relative to root directory)

If the root directory is wrong, Render will look for files in the wrong place.

## Expected Build Output (After Fix)

```
==> Running build command 'npm ci && npm run build'...

> npm ci
added 688 packages in 45s

> npm run build
vite v5.4.21 building for production...
✓ 1098 modules transformed.
✓ built in 3.94s

==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉
```

## Configuration Files

We've added several configuration files to help:

1. **render.yaml** - Full stack deployment config (for reference)
2. **render.json** - Frontend-only config
3. **render-build.sh** - Build script for local testing
4. **vite.config.ts** - Updated with proper extension resolution

## Testing Locally

To test the build locally:

```bash
cd frontend
npm ci --legacy-peer-deps
npm run build
```

If this works locally, it should work on Render.

## Render Service Details

| Setting | Value |
|---------|-------|
| Service Name | datacollect-cameroun-frontend |
| Service ID | srv-d7n15q28qa3s739vgmv0 |
| Type | Static Site |
| Root Directory | `frontend` |
| Build Command | `npm ci && npm run build` |
| Publish Directory | `dist` |
| Environment | `VITE_API_URL=https://datacollect-cameroun-prod.onrender.com` |

## Troubleshooting

### If Build Still Fails

1. **Check Render Logs**
   - Go to Render dashboard
   - Select frontend service
   - Go to **Logs** tab
   - Look for error messages

2. **Verify Root Directory**
   - Should be `frontend` or empty
   - NOT `src` or `src/frontend`

3. **Verify Build Command**
   - Should be `npm ci && npm run build`
   - NOT `npm install && npm run build`

4. **Verify Publish Directory**
   - Should be `dist`
   - NOT `frontend/dist` or `src/frontend/dist`

### Common Mistakes

❌ **Wrong**: Root Directory = `src/frontend`
✅ **Correct**: Root Directory = `frontend`

❌ **Wrong**: Build Command = `npm install && npm run build`
✅ **Correct**: Build Command = `npm ci && npm run build`

❌ **Wrong**: Publish Directory = `frontend/dist`
✅ **Correct**: Publish Directory = `dist`

## Next Steps

1. Update Render service settings (see Step 1 above)
2. Trigger manual deploy
3. Monitor build logs
4. Verify frontend loads at https://datacollect-cameroun-frontend.onrender.com

---

**Status**: Ready for Render deployment with correct configuration ✅
