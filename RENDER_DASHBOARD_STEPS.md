# 📊 Render Dashboard - Frontend Configuration Steps

## Current Status
- ❌ Frontend build failing: `Cannot find module 'tailwindcss-animate'`
- ✅ Code pushed to GitHub with fixes
- ⏳ Need to update Render service configuration

## Step-by-Step Fix

### Step 1: Go to Render Dashboard
1. Open: https://dashboard.render.com
2. Login with your account

### Step 2: Select Frontend Service
1. Click on service: **datacollect-cameroun-frontend**
2. Service ID: `srv-d7n15q28qa3s739vgmv0`

### Step 3: Update Build Command
1. Go to **Settings** tab
2. Find **Build & Deploy** section
3. Update **Build Command** field:
   - **OLD**: `npm install && npm run build`
   - **NEW**: `npm --prefix frontend ci && npm --prefix frontend run build`
4. Click **Save**

### Step 4: Verify Publish Directory
1. In same **Settings** section
2. Verify **Publish directory**: `frontend/dist`
3. If different, update to `frontend/dist`
4. Click **Save**

### Step 5: Verify Environment Variables
1. Go to **Environment** tab
2. Ensure variable exists:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://datacollect-cameroun-prod.onrender.com`
3. If missing, add it
4. Click **Save**

### Step 6: Trigger Manual Deploy
1. Go to **Deploys** tab
2. Click **Create Deploy** button
3. Select **Deploy latest commit**
4. Wait for build to complete

### Step 7: Monitor Build Progress
1. Watch the build logs in real-time
2. Look for:
   - ✅ `npm ci` installing dependencies
   - ✅ `npm run build` building Vite
   - ✅ `Build successful 🎉`
3. If errors, check logs for details

### Step 8: Verify Deployment
1. Once build succeeds, check:
   - Frontend URL: https://datacollect-cameroun-frontend.onrender.com
   - Should load the dashboard
   - Check browser console for API errors

## Expected Build Output

```
==> Running build command 'npm --prefix frontend ci && npm --prefix frontend run build'...

> npm ci
added 688 packages in 45s

> npm run build
vite v5.4.21 building for production...
✓ 4 modules transformed.
✓ built in 2.34s

==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉
```

## If Build Still Fails

### Check 1: Dependencies
```bash
# Verify tailwindcss-animate is in package.json
grep "tailwindcss-animate" frontend/package.json
# Should show: "tailwindcss-animate": "^1.0.7"
```

### Check 2: Tailwind Config
```bash
# Verify tailwind.config.js syntax
cat frontend/tailwind.config.js | tail -5
# Should show: plugins: [require("tailwindcss-animate")]
```

### Check 3: TypeScript Config
```bash
# Verify tsconfig.json has path aliases
grep -A 3 '"paths"' frontend/tsconfig.json
# Should show: "@/*": ["./src/*"]
```

### Check 4: Vite Config
```bash
# Verify vite.config.ts has aliases
grep -A 5 "alias:" frontend/vite.config.ts
# Should show path aliases matching tsconfig.json
```

## Render Service Details

| Property | Value |
|----------|-------|
| Service Name | datacollect-cameroun-frontend |
| Service ID | srv-d7n15q28qa3s739vgmv0 |
| Type | Static Site |
| Region | Oregon |
| Plan | Free |
| Build Command | `npm --prefix frontend ci && npm --prefix frontend run build` |
| Publish Path | `frontend/dist` |
| Environment | `VITE_API_URL=https://datacollect-cameroun-prod.onrender.com` |

## Backend Service (Reference)

| Property | Value |
|----------|-------|
| Service Name | datacollect-cameroun-prod |
| Service ID | srv-d7n00o57vvec738re8ng |
| Type | Web Service |
| Runtime | Python 3 |
| URL | https://datacollect-cameroun-prod.onrender.com |
| Status | ✅ Live |

---

**Next**: After updating settings, trigger a manual deploy and monitor the build logs.
