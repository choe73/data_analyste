# 📊 Render Dashboard - Update Instructions

## Service to Update
- **Name**: datacollect-cameroun-frontend
- **ID**: srv-d7n15q28qa3s739vgmv0
- **URL**: https://dashboard.render.com/services/srv-d7n15q28qa3s739vgmv0

---

## Step 1: Go to Settings Tab

1. Open: https://dashboard.render.com
2. Click on: `datacollect-cameroun-frontend` service
3. Click on: **Settings** tab

---

## Step 2: Update Root Directory

**Location**: Settings tab → Root Directory field

**Current**: (probably empty or wrong)  
**Change to**: `.` (dot) or leave empty

**Why**: Tells Render the project root is the current directory

---

## Step 3: Update Build Command

**Location**: Settings tab → Build Command field

**Current**: `npm install && npm run build`  
**Change to**: `npm run build`

**Why**: Uses the root-level package.json which handles everything

---

## Step 4: Update Publish Directory

**Location**: Settings tab → Publish Directory field

**Current**: (probably `dist` or wrong)  
**Change to**: `frontend/dist`

**Why**: Tells Render where the built files are located

---

## Step 5: Save Settings

1. Click **Save** button
2. Wait for confirmation

---

## Step 6: Add Environment Variable

1. Click on: **Environment** tab
2. Check if `VITE_API_URL` exists
3. If not, click: **Add Environment Variable**
4. Fill in:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://datacollect-cameroun-prod.onrender.com`
5. Click **Save**

---

## Step 7: Trigger Deploy

1. Click on: **Deploys** tab
2. Click: **Create Deploy** button
3. Select: **Deploy latest commit**
4. Click: **Create Deploy**

---

## Step 8: Monitor Build

1. Watch the build logs in real-time
2. Look for these messages:
   - ✅ `npm run build` starting
   - ✅ `cd frontend && npm ci` running
   - ✅ `npm run build` building Vite
   - ✅ `Build successful 🎉`

3. If you see errors:
   - Check the error message
   - Verify settings are correct
   - Trigger another deploy

---

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

---

## Step 9: Verify Frontend

1. Once build succeeds, open:
   https://datacollect-cameroun-frontend.onrender.com

2. Check:
   - ✅ Page loads without errors
   - ✅ Dashboard displays
   - ✅ Stats cards visible
   - ✅ System health section shows
   - ✅ No blank page
   - ✅ Browser console has no errors

---

## Configuration Summary

| Setting | Value |
|---------|-------|
| Root Directory | `.` or empty |
| Build Command | `npm run build` |
| Publish Directory | `frontend/dist` |
| VITE_API_URL | `https://datacollect-cameroun-prod.onrender.com` |

---

## Troubleshooting

### Build Fails with "Cannot find module"

1. Check Publish Directory is `frontend/dist`
2. Check Build Command is `npm run build`
3. Trigger another deploy

### Build Fails with "npm install"

1. Check Build Command is `npm run build` (not `npm install && npm run build`)
2. Trigger another deploy

### Frontend Loads but API Doesn't Work

1. Check VITE_API_URL environment variable is set
2. Check value is `https://datacollect-cameroun-prod.onrender.com`
3. Trigger another deploy

### Frontend Shows Blank Page

1. Check browser console for errors
2. Check Render logs for build errors
3. Verify all settings are correct
4. Trigger another deploy

---

## Timeline

| Step | Time |
|------|------|
| Go to Render dashboard | 1 min |
| Update Root Directory | 1 min |
| Update Build Command | 1 min |
| Update Publish Directory | 1 min |
| Add Environment Variable | 1 min |
| Trigger Deploy | 1 min |
| Build Process | 5-10 min |
| Deployment | 1-2 min |
| Verification | 5 min |
| **Total** | **15-20 min** |

---

## Success Criteria

✅ Build completes without errors  
✅ Frontend loads at https://datacollect-cameroun-frontend.onrender.com  
✅ Dashboard displays with stats  
✅ No console errors  
✅ API calls work  
✅ All pages are accessible  

---

## Support

- Render Dashboard: https://dashboard.render.com
- Render Docs: https://render.com/docs
- GitHub: https://github.com/choe73/data_analyste

---

**Status**: Ready to deploy ✅

**Next Action**: Go to https://dashboard.render.com and follow these steps!
