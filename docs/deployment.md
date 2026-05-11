# Deployment Guide

This document covers deploying the Unity Stats API backend to production platforms and configuring the Unity WebGL frontend for production.

---

## Table of Contents

1. [Backend Deployment Overview](#backend-deployment-overview)
2. [Render Deployment](#render-deployment)
3. [Railway Deployment](#railway-deployment)
4. [Environment Variables](#environment-variables)
5. [Health Check Configuration](#health-check-configuration)
6. [Verifying Deployment](#verifying-deployment)
7. [Unity WebGL Frontend Setup](#unity-webgl-frontend-setup)
8. [Troubleshooting](#troubleshooting)

---

## Backend Deployment Overview

### Technology Stack

- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Port**: Configurable (default 8000, deployment platforms provide `$PORT` variable)
- **Health Check**: `GET /health` returns `{"status": "ok"}`

### Production Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Key Requirements

- **API_FOOTBALL_KEY**: Must be set as environment variable (never hardcoded)
- **CORS_ALLOW_ORIGINS**: Must include your production frontend domain
- **.env file**: Local only, never committed to git (already in .gitignore)
- **Python version**: 3.9+

---

## Render Deployment

### Step 1: Create a New Web Service on Render

1. Go to [render.com](https://render.com)
2. Sign in / create account
3. Click **New +** → **Web Service**
4. Connect your GitHub repository (authorize if needed)
5. Select the repository with your backend code

### Step 2: Configure the Web Service

| Setting | Value |
|---------|-------|
| **Name** | e.g., `unity-stats-api` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free or Paid (free has limitations) |

### Step 3: Set Environment Variables

In the Render dashboard, go to **Environment** (in the Web Service settings):

```
API_FOOTBALL_KEY=your_actual_api_key_here
API_FOOTBALL_BASE=https://v3.football.api-sports.io
API_FOOTBALL_HOST=v3.football.api-sports.io
CORS_ALLOW_ORIGINS=http://localhost,http://127.0.0.1,https://your-frontend-domain.com
```

Replace:
- `your_actual_api_key_here` with your actual API-Football key
- `https://your-frontend-domain.com` with your WebGL deployment URL (e.g., Netlify, Vercel, S3)

### Step 4: Deploy

Click **Create Web Service**. Render will:
- Clone your repository
- Install dependencies from `requirements.txt`
- Start the Uvicorn server
- Assign you a public URL like `https://unity-stats-api.onrender.com`

### Step 5: Monitor Health

Once deployed, verify the service:
```
curl https://unity-stats-api.onrender.com/health
```

Expected response: `{"status":"ok"}`

---

## Railway Deployment

### Step 1: Create a New Project on Railway

1. Go to [railway.app](https://railway.app)
2. Sign in / create account
3. Click **New Project**
4. Select **Deploy from GitHub** or **Empty Project**

### Step 2: If Using GitHub

1. Select **Deploy from GitHub**
2. Authorize and select your repository
3. Railway will auto-detect the Python project

### Step 3: Configure Environment Variables

In the Railway dashboard, click on your service and go to **Variables**:

```
API_FOOTBALL_KEY=your_actual_api_key_here
API_FOOTBALL_BASE=https://v3.football.api-sports.io
API_FOOTBALL_HOST=v3.football.api-sports.io
CORS_ALLOW_ORIGINS=http://localhost,http://127.0.0.1,https://your-frontend-domain.com
```

Replace as above.

### Step 4: Set Up Start Command

In the **Deploy** tab, ensure the start command is:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Or configure in a `Procfile` in your repo root:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Generate a Domain

Railway assigns a public domain. You can:
- Use the auto-generated domain (e.g., `https://unity-stats-api-prod.up.railway.app`)
- Add a custom domain in **Settings** → **Domain**

### Step 6: Monitor Health

Once deployed, verify:
```
curl https://your-railway-domain.up.railway.app/health
```

Expected response: `{"status":"ok"}`

---

## Environment Variables

### Required

- **API_FOOTBALL_KEY**: Your API-Football authentication key
  - Obtain from [api-football.com](https://api-football.com)
  - Never commit to git
  - Only set on deployment platform

### Recommended

- **CORS_ALLOW_ORIGINS**: Comma-separated list of allowed frontend origins
  - Development: `http://localhost,http://127.0.0.1,http://localhost:8080,http://127.0.0.1:8080`
  - Production: Add your WebGL domain (e.g., `https://your-domain.vercel.app`)
  - Format: `origin1,origin2,origin3`

### Optional

- **API_FOOTBALL_BASE**: API endpoint (default: `https://v3.football.api-sports.io`)
- **API_FOOTBALL_HOST**: API host header (default: `v3.football.api-sports.io`)

### Local Development

Copy `.env.example` to `.env` and fill in real values:
```bash
cp .env.example .env
```

Example `.env`:
```
API_FOOTBALL_KEY=abc123def456ghi789jkl012mno345
API_FOOTBALL_BASE=https://v3.football.api-sports.io
API_FOOTBALL_HOST=v3.football.api-sports.io
CORS_ALLOW_ORIGINS=http://localhost,http://127.0.0.1,http://localhost:8080,http://127.0.0.1:8080,https://my-frontend.vercel.app
```

---

## Health Check Configuration

### Render

Render automatically detects the `/health` endpoint if configured:

1. In Render dashboard → **Service** → **Health Check**
2. Set **HTTP Path**: `/health`
3. Set **Check Interval**: `10s` (default)
4. Render will poll every 10 seconds; if 3 consecutive checks fail, the service restarts

### Railway

Railway has simpler health checks:

1. In Railway dashboard → **Service** → **Settings**
2. No explicit health check config needed (Railway monitors exit code)
3. To verify: `curl https://your-domain.up.railway.app/health`

### Manual Verification

Always test health endpoint before deploying frontend:

```bash
# Render example
curl -X GET https://unity-stats-api.onrender.com/health

# Railway example
curl -X GET https://unity-stats-api-prod.up.railway.app/health

# Response
{"status":"ok"}
```

---

## Verifying Deployment

### 1. Backend Health

```bash
curl https://your-backend-domain.com/health
# Should return: {"status":"ok"}
```

### 2. API Functionality

```bash
curl https://your-backend-domain.com/api/bulletin/today
# Should return: array of matches with live data or cached data
```

### 3. CORS Headers

```bash
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS https://your-backend-domain.com/api/bulletin/today
```

Check response includes:
```
Access-Control-Allow-Origin: https://your-frontend-domain.com
Access-Control-Allow-Methods: GET, POST, OPTIONS, ...
```

### 4. Logs

**Render**: Service Logs → View logs for startup errors
**Railway**: Deployments → Click service → View logs

---

## Unity WebGL Frontend Setup

### Build Profile Configuration

Before building WebGL, ensure AppConfig.cs is set correctly:

#### Development Build
- Build Profile: `Development`
- Backend URL: `http://127.0.0.1:8000`
- Data Source: `Live`
- Verbose Logs: `On`

#### Production Build
- Build Profile: `Production`
- Backend URL: `https://your-backend-domain.com` (e.g., `https://unity-stats-api.onrender.com`)
- Data Source: `Live`
- Verbose Logs: `Off`

### Build Steps

1. **Open Unity Project**: `İstatistik/`
2. **File** → **Build Settings**
3. **Platform**: Select `WebGL`
4. **Player Settings** → **Other Settings** → **Scripting Define Symbols**:
   - Development: Leave empty
   - Production: `PRODUCTION_BUILD`
5. **Build** → Export WebGL build to a folder (e.g., `WebGL_Build/`)

### Deployment Platforms for WebGL

Choose one of these to host your WebGL build:

#### Option A: Netlify (Recommended)

1. Drag and drop `WebGL_Build/` folder into [netlify.com](https://netlify.com)
2. Your site is live instantly
3. Update backend CORS to include Netlify domain

#### Option B: Vercel

```bash
npm install -g vercel
cd WebGL_Build
vercel --prod
```

#### Option C: AWS S3 + CloudFront

1. Upload `WebGL_Build/` contents to S3 bucket
2. Create CloudFront distribution
3. Enable CORS in S3 bucket policy

#### Option D: GitHub Pages

1. Push `WebGL_Build/` to `gh-pages` branch
2. Enable GitHub Pages in repo settings
3. Site available at `https://username.github.io/repo-name/`

### CORS Configuration After Frontend Deployment

Once your WebGL is deployed, update backend environment variables:

**If WebGL is at**: `https://my-app.netlify.app`

Update `CORS_ALLOW_ORIGINS` to:
```
http://localhost,http://127.0.0.1,https://my-app.netlify.app
```

Redeploy backend for changes to take effect.

### Verify WebGL Build Works

1. Deploy WebGL to your platform
2. In browser, open DevTools **Console**
3. Load your WebGL site
4. Should see no CORS errors
5. Bulletin list should load from backend
6. Match details should be clickable
7. All tabs (stats, events, lineups, odds) should load

---

## Troubleshooting

### Issue: 502 Bad Gateway / Service Crash

**Solution**:
1. Check Render/Railway logs for startup errors
2. Verify `requirements.txt` includes all dependencies: `fastapi`, `uvicorn`, `python-dotenv`, `requests`, `pydantic`
3. Ensure `app/main.py` has no syntax errors
4. Verify `API_FOOTBALL_KEY` is set in environment

### Issue: CORS Errors in WebGL Console

**Error**: `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution**:
1. Verify `CORS_ALLOW_ORIGINS` includes your WebGL domain
2. Check domain spelling (case-sensitive)
3. Include protocol and port if non-standard (e.g., `https://example.com:3000`)
4. Redeploy backend after updating `CORS_ALLOW_ORIGINS`

### Issue: /health Returns 200 but /api/bulletin/today Returns 500

**Cause**: Missing or invalid `API_FOOTBALL_KEY`

**Solution**:
1. Verify `API_FOOTBALL_KEY` is set on deployment platform
2. Check key is valid (log into [api-football.com](https://api-football.com) and verify)
3. Restart service after setting key

### Issue: WebGL Build Blank / Doesn't Load

**Cause**: Backend URL is incorrect or unreachable

**Solution**:
1. Check AppConfig.cs `BaseUrl` is correct for production
2. Verify health endpoint is reachable: `curl https://your-backend.com/health`
3. Check browser DevTools **Network** tab for failed requests
4. Ensure CORS is configured (check previous section)

### Issue: Stale Cache / Old Data Displayed

**Cause**: Bulletin cache file (`app/data/bulletin_cache.json`) not cleared

**Solution**:
- Backend automatically clears cache after 5 minutes (TTL)
- Or manually SSH into deployment and delete cache file if using persistent storage

---

## Summary

| Component | Render | Railway |
|-----------|--------|---------|
| **Sign Up** | [render.com](https://render.com) | [railway.app](https://railway.app) |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Same or Procfile |
| **Health Check** | Auto-detected at `/health` | Manual via curl |
| **Domain** | `*.onrender.com` | `*.up.railway.app` or custom |
| **Free Tier** | Limited (spins down) | Monthly credit, then paid |
| **Recommendation** | Simple, good free tier | More flexible pricing |

Choose based on your needs. Both are excellent for hobby/portfolio projects.

---

## Next Steps

1. ✅ Ensure `.env.example` is committed (shows env var structure)
2. ✅ Ensure `.gitignore` has `.env` (never commit real keys)
3. ✅ Test backend locally: `uvicorn app.main:app --reload`
4. ✅ Deploy to Render or Railway
5. ✅ Build and deploy WebGL frontend
6. ✅ Update `CORS_ALLOW_ORIGINS` with frontend domain
7. ✅ Test end-to-end (WebGL → Backend → API-Football)
8. ✅ Monitor health checks and logs
