# 🔧 Render Workaround - src/frontend Redirect

## Problem
Render's rootDir is misconfigured and looking for files at `/opt/render/project/src/frontend/src/lib/api` instead of `/opt/render/project/frontend/src/lib/api`.

## Solution
Created a redirect structure at `src/frontend/` that mirrors the actual frontend and redirects all build commands to the real frontend directory.

## How It Works

### Directory Structure
```
datacollect-pro-cameroun/
├── frontend/                    (actual frontend)
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   └── ...
│
└── src/
    └── frontend/                (redirect structure)
        ├── package.json         (redirects to ../../frontend)
        ├── vite.config.ts       (points to ../../frontend/src)
        ├── tsconfig.json        (points to ../../frontend)
        ├── index.html
        └── src/
            └── main.tsx         (redirect file)
```

### Build Flow

When Render runs `npm install && npm run build` in `/opt/render/project/src/frontend/`:

1. npm finds `package.json` at `/opt/render/project/src/frontend/`
2. npm runs `postinstall` script: `cd ../../frontend && npm ci`
3. npm installs dependencies in the real frontend directory
4. npm runs `build` script: `cd ../../frontend && npm run build`
5. Vite builds the real frontend
6. Output goes to `../../frontend/dist/`

### Key Files

1. **`src/frontend/package.json`**
   - Has `postinstall` script that installs dependencies in real frontend
   - Has `build` script that builds real frontend
   - Redirects all npm commands to real frontend

2. **`src/frontend/vite.config.ts`**
   - Points all aliases to `../../frontend/src`
   - Sets output directory to `../../frontend/dist`
   - Handles all Vite configuration

3. **`src/frontend/tsconfig.json`**
   - Points baseUrl to `../../frontend`
   - Points paths to `../../frontend/src`
   - Handles TypeScript configuration

4. **`src/frontend/index.html`**
   - Entry point for Vite
   - Points to `/src/main.tsx` (which is a redirect)

## Why This Works

1. **Render finds the package.json** - At `/opt/render/project/src/frontend/package.json`
2. **npm runs postinstall** - Installs dependencies in real frontend
3. **npm runs build** - Builds real frontend
4. **Vite uses correct paths** - All aliases point to real frontend
5. **Output is in correct location** - `frontend/dist/` is where Render expects it

## What You Need to Do

### In Render Dashboard

1. Go to: https://dashboard.render.com
2. Select: `datacollect-cameroun-frontend`
3. Go to: **Settings** tab
4. Update:
   - Root Directory: `src/frontend` (or leave empty)
   - Build Command: `npm install && npm run build` (keep as is)
   - Publish Directory: `dist` (or `frontend/dist`)
5. Go to: **Environment** tab
6. Add:
   - VITE_API_URL: `https://datacollect-cameroun-prod.onrender.com`
7. Go to: **Deploys** tab
8. Click: **Create Deploy**
9. Select: **Deploy latest commit**

## Expected Build Output

```
==> Running build command 'npm install && npm run build'...

> npm install
added 687 packages in 50s

> npm run build
> cd ../../frontend && npm run build

> datacollect-frontend@1.0.0 build
> vite build

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
| Root Directory | `src/frontend` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `dist` or `frontend/dist` |
| VITE_API_URL | `https://datacollect-cameroun-prod.onrender.com` |

## Troubleshooting

### If Build Still Fails

1. Check Render logs for error message
2. Verify Root Directory is `src/frontend`
3. Verify Build Command is `npm install && npm run build`
4. Verify Publish Directory is `dist` or `frontend/dist`
5. Trigger another deploy

### Common Issues

| Issue | Solution |
|-------|----------|
| `Cannot find module` | Check Publish Directory is `dist` or `frontend/dist` |
| `postinstall` not running | npm should run it automatically |
| Files not found | Check Root Directory is `src/frontend` |
| API not working | Check VITE_API_URL environment variable |

## Files Added

1. **`src/frontend/package.json`** - Redirect package.json
2. **`src/frontend/vite.config.ts`** - Vite config pointing to real frontend
3. **`src/frontend/tsconfig.json`** - TypeScript config pointing to real frontend
4. **`src/frontend/tsconfig.node.json`** - TypeScript node config
5. **`src/frontend/.npmrc`** - npm configuration
6. **`src/frontend/index.html`** - HTML entry point
7. **`src/frontend/src/main.tsx`** - Redirect file
8. **`src/package.json`** - Root src package.json
9. **`frontend/build-wrapper.sh`** - Build wrapper script

## Why This Workaround?

Render's service was created manually with an incorrect rootDir. We can't change it via git, so we created a redirect structure that works with Render's configuration.

This is a temporary workaround. The proper solution would be to:
1. Delete the service and recreate it with correct settings
2. Or use render.yaml for deployment

## Next Steps

1. Go to https://dashboard.render.com
2. Update frontend service settings as shown above
3. Trigger deploy
4. Monitor build logs
5. Verify frontend loads

---

**Status**: Ready for deployment with workaround ✅

**Time to completion**: 15-20 minutes
