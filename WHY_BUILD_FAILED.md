# 🔍 Why the Build Failed - Technical Analysis

## The Error

```
Could not load /opt/render/project/src/frontend/src/lib/api
ENOENT: no such file or directory
```

## What This Means

Vite (the build tool) is looking for the file at:
```
/opt/render/project/src/frontend/src/lib/api
```

But the actual file is at:
```
/opt/render/project/frontend/src/lib/api.ts
```

Notice the extra `src/` in the path Render is looking at.

## Root Cause

### The Problem Chain

1. **Frontend service created manually** (not via render.yaml)
   - When you create a service manually on Render, you have to specify the root directory
   - The root directory tells Render where the project root is

2. **Root directory not configured correctly**
   - Render thinks the root is `/opt/render/project/src/`
   - Actually, the root should be `/opt/render/project/`
   - Or if using a subdirectory, it should be `/opt/render/project/frontend/`

3. **Vite can't find the file**
   - Vite looks for `@/lib/api` (which resolves to `./src/lib/api.ts`)
   - But Render is looking in the wrong directory
   - So Vite can't find the file

### Why This Happened

When the frontend service was created on Render:
- ❌ Root Directory was set to something wrong (maybe `src` or empty)
- ❌ Build Command was `npm install && npm run build` (should be `npm ci && npm run build`)
- ❌ Publish Directory was wrong (maybe `frontend/dist` instead of `dist`)

## The Solution

### What Needs to Change

**Render Service Configuration**:

| Setting | Wrong | Correct |
|---------|-------|---------|
| Root Directory | `src` or empty | `frontend` |
| Build Command | `npm install && npm run build` | `npm ci && npm run build` |
| Publish Directory | `frontend/dist` | `dist` |

### Why These Changes Fix It

1. **Root Directory = `frontend`**
   - Tells Render that the project root is the `frontend/` directory
   - Now when Render runs `npm ci`, it's in the right directory
   - Now when Vite builds, it can find all files correctly

2. **Build Command = `npm ci && npm run build`**
   - `npm ci` (clean install) respects `package-lock.json`
   - `npm install` might install different versions
   - This ensures consistent builds

3. **Publish Directory = `dist`**
   - Tells Render where the built files are
   - Relative to the root directory (`frontend/`)
   - So Render will serve files from `frontend/dist/`

## How Render Works

### Build Process (Current - Wrong)

```
1. Render clones repo to /opt/render/project/
2. Render thinks root is /opt/render/project/src/
3. Render runs: npm install && npm run build
   (but this is in the wrong directory!)
4. Vite tries to find @/lib/api
5. Vite looks in /opt/render/project/src/src/lib/api
6. File not found! ❌
```

### Build Process (After Fix - Correct)

```
1. Render clones repo to /opt/render/project/
2. Render knows root is /opt/render/project/frontend/
3. Render runs: npm ci && npm run build
   (in the correct directory!)
4. Vite tries to find @/lib/api
5. Vite looks in /opt/render/project/frontend/src/lib/api.ts
6. File found! ✅
7. Build succeeds
8. Render serves files from /opt/render/project/frontend/dist/
```

## Why We Didn't Catch This Earlier

1. **Local development works fine**
   - When you run `npm run build` locally, you're already in the `frontend/` directory
   - So the paths are correct

2. **Render service created manually**
   - We didn't use `render.yaml` (which would have the correct config)
   - Manual creation requires careful configuration

3. **The error message is confusing**
   - It shows the wrong path, which makes it hard to debug
   - But it's actually telling us the root directory is wrong

## Prevention for Future

### Use render.yaml

Instead of creating services manually, use `render.yaml`:

```yaml
services:
  - type: static
    name: datacollect-frontend
    buildCommand: npm --prefix frontend ci && npm --prefix frontend run build
    staticPublishPath: frontend/dist
```

This way:
- ✅ Root directory is always correct
- ✅ Build command is always correct
- ✅ Publish path is always correct
- ✅ Configuration is version controlled

### Or Use GitHub Actions

Deploy via GitHub Actions instead of Render:
- ✅ Build happens on GitHub (not Render)
- ✅ Deploy to GitHub Pages or Render
- ✅ More control over build process

## Key Learnings

1. **Root directory matters** - It tells Render where to run commands
2. **Path resolution is relative** - All paths are relative to the root directory
3. **Manual configuration is error-prone** - Use YAML configs when possible
4. **Error messages can be misleading** - The path shown might not be the actual problem
5. **Test locally first** - If it works locally, it should work on Render (with correct config)

## Verification

After applying the fix, you should see:

```
==> Running build command 'npm ci && npm run build'...

> npm ci
added 688 packages in 45s

> npm run build
vite v5.4.21 building for production...
✓ 1098 modules transformed.
✓ built in 3.94s

==> Build successful 🎉
```

---

**Summary**: The root directory was wrong, so Render was looking for files in the wrong place. Fixing the Render service configuration will solve the problem.
