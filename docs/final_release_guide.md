# Final Release Execution Guide

**Project**: Unity Football Match Center  
**Version**: v1.0.0  
**Platforms**: Backend (Render/Railway) + WebGL (Netlify/Vercel)  
**Estimated Time**: 20-30 minutes

---

## Quick Start

This guide walks you through releasing the entire application:
1. Deploy backend to a production server
2. Build and deploy WebGL frontend
3. Verify everything works
4. Troubleshoot if needed

---

## Table of Contents

1. [Backend Deployment](#backend-deployment)
2. [WebGL Build & Deployment](#webgl-build--deployment)
3. [Final Verification](#final-verification)
4. [Troubleshooting](#troubleshooting)
5. [Release Notes Template](#release-notes-template)

---

## Backend Deployment

### Prerequisites

- API-Football API key (from [api-football.com](https://api-football.com))
- Git repository pushed to GitHub
- Account on Render.com or Railway.app

### Option A: Deploy to Render (Recommended)

**Duration**: 10 minutes

#### Step 1: Create Web Service on Render

1. Visit [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Select **Deploy from GitHub**
4. Authorize Render and select your repository
5. Click **Connect**

#### Step 2: Configure Service

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `unity-stats-api` (or your choice) |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (adequate for hobby projects) |

#### Step 3: Add Environment Variables

Click **Environment** in the left sidebar and add:

```
API_FOOTBALL_KEY=<your_actual_api_key_here>
API_FOOTBALL_BASE=https://v3.football.api-sports.io
API_FOOTBALL_HOST=v3.football.api-sports.io
FRONTEND_ORIGIN=https://your-frontend-domain.com
```

**Important**: Replace values:
- `<your_actual_api_key_here>` — your real API-Football key
- `https://your-frontend-domain.com` — where WebGL will be hosted (e.g., `https://my-app.netlify.app`)

#### Step 4: Deploy

Click **Create Web Service**. Render will:
- Clone your repository
- Install dependencies
- Start the server
- Assign a public URL (e.g., `https://unity-stats-api.onrender.com`)

Wait 2-3 minutes for deployment. You'll see a green "Live" indicator when ready.

#### Step 5: Verify Health

```bash
curl https://unity-stats-api.onrender.com/health
```

Expected: `{"status":"ok"}`

---

### Option B: Deploy to Railway

**Duration**: 10 minutes

#### Step 1: Create Project on Railway

1. Visit [railway.app](https://railway.app)
2. Click **New Project**
3. Select **Deploy from GitHub**
4. Authorize Railway and select your repository

#### Step 2: Add Environment Variables

In Railway dashboard, click your service and go to **Variables**:

```
API_FOOTBALL_KEY=<your_actual_api_key_here>
API_FOOTBALL_BASE=https://v3.football.api-sports.io
API_FOOTBALL_HOST=v3.football.api-sports.io
FRONTEND_ORIGIN=https://your-frontend-domain.com
```

#### Step 3: Configure Start Command

Click **Deploy** tab and ensure start command is:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Or create `Procfile` in repository root:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Step 4: Generate Domain

In **Settings**, click **Generate Domain**. You'll get a URL like:
```
https://unity-stats-api-prod.up.railway.app
```

#### Step 5: Verify Health

```bash
curl https://unity-stats-api-prod.up.railway.app/health
```

Expected: `{"status":"ok"}`

---

### Backend Deployment Checklist

- [ ] Environment variables set correctly
- [ ] `API_FOOTBALL_KEY` is a valid active key
- [ ] `FRONTEND_ORIGIN` matches where WebGL will be deployed
- [ ] Health endpoint returns 200 OK
- [ ] Logs show no startup errors
- [ ] `/api/bulletin/today` returns data (or cached data)

**Backend URL** (needed for next step): Write down your backend domain:
```
https://your-backend-domain.com
```

---

## WebGL Build & Deployment

### Prerequisites

- Unity 6.0+
- Backend URL from previous step
- Account on Netlify, Vercel, or GitHub Pages

### Step 1: Configure Backend URL in Unity

1. Open the Unity project: `İstatistik/`
2. Open `Assets/Scripts/Core/AppConfig.cs`
3. Locate this line (around line 40):
   ```csharp
   private const string ProductionBackendPlaceholder = "https://YOUR_BACKEND_DOMAIN_HERE";
   ```
4. Replace with your actual backend URL:
   ```csharp
   private const string ProductionBackendPlaceholder = "https://unity-stats-api.onrender.com";
   ```
   (Use your actual backend domain from previous step)

5. Save the file

### Step 2: Build WebGL

1. **File** → **Build Settings**
2. In **Scenes In Build**, ensure `Assets/Scenes/MainScene.unity` is included
3. **Platform** list on the left: Select **WebGL**
4. Click **Switch Platform** (this may take 1-2 minutes)
5. Click **Build** (or **Build and Run**)
6. Choose a folder (e.g., `WebGL_Build/`)
7. Wait for build to complete (2-5 minutes)

Check the build folder contains:
```
WebGL_Build/
  index.html
  Build/
    unity.framework.js
    unity.loader.js
    unity.wasm
  StreamingAssets/
```

### Step 3: Deploy WebGL

#### Option A: Netlify (Simplest)

1. Visit [netlify.com](https://netlify.com)
2. Sign up / log in
3. Drag and drop `WebGL_Build/` folder onto the page
4. Your site is live immediately at a URL like `https://my-app.netlify.app`

That's it! No configuration needed.

#### Option B: Vercel

1. Visit [vercel.com](https://vercel.com)
2. Sign up / log in
3. Click **New Project**
4. Upload your Git repository (or drag folder)
5. Deploy
6. Get a URL like `https://my-app.vercel.app`

#### Option C: GitHub Pages

1. Create a `gh-pages` branch in your repository
2. Push `WebGL_Build/` contents to that branch
3. In GitHub: **Settings** → **Pages**
4. Select `gh-pages` branch as source
5. Your site is live at `https://username.github.io/repo-name`

---

### Step 4: Update Backend CORS

Now that your WebGL is deployed, update the backend to allow it.

1. Go to your Render/Railway dashboard
2. In **Environment Variables**, update:
   ```
   FRONTEND_ORIGIN=https://your-webgl-domain.netlify.app
   ```
   (Use your actual WebGL URL)

3. Redeploy/restart the backend service

Wait 1 minute for changes to take effect.

---

### WebGL Build & Deployment Checklist

- [ ] `AppConfig.cs` has correct production backend URL
- [ ] WebGL build completes without errors
- [ ] `index.html` and `Build/` folder exist
- [ ] WebGL deployed to Netlify/Vercel/GitHub Pages
- [ ] WebGL domain added to backend `FRONTEND_ORIGIN`
- [ ] Backend redeployed with updated CORS

**WebGL URL** (needed for verification): Write down:
```
https://your-webgl-domain.netlify.app
```

---

## Final Verification

### Test 1: Backend Health

```bash
curl https://your-backend-domain.com/health
```

Expected:
```json
{"status":"ok"}
```

**Status**: ✅ Pass / ❌ Fail

---

### Test 2: Backend API

```bash
curl https://your-backend-domain.com/api/bulletin/today
```

Expected: Array of matches with data like:
```json
[
  {
    "id": 123456,
    "league_name": "Premier League",
    "match_date": "2026-05-11",
    "home_team": "Team A",
    "away_team": "Team B",
    ...
  }
]
```

**Status**: ✅ Pass / ❌ Fail

---

### Test 3: WebGL Loads

1. Open your WebGL URL in a browser: `https://your-webgl-domain.netlify.app`
2. Wait 10-20 seconds for Unity to initialize
3. You should see the loading screen, then the main UI

**Expected**: Match list visible, no console errors

To check for errors:
- Press **F12** (Developer Tools)
- Click **Console** tab
- Should see no red error messages (yellow warnings are OK)

**Status**: ✅ Pass / ❌ Fail

---

### Test 4: Match List Loads

1. On the WebGL app, watch the **Bulletin** tab (first tab)
2. After loading, you should see a list of matches
3. Click on any match to open details

**Expected**: List has 5+ matches, clickable

**Status**: ✅ Pass / ❌ Fail

---

### Test 5: Match Detail Screen

1. Click any match from the list
2. The detail screen should open with tabs: **Genel**, **Sut ve Oyun**, **Olaylar**, **Kadro**, **H2H**, **Oranlar**
3. Click each tab to verify they load

**Expected**: All tabs load without hanging, no red errors in console

**Status**: ✅ Pass / ❌ Fail

---

### Test 6: Localization (TR/EN)

1. Go to **Ayarlar** (Settings) tab
2. Click **Language** dropdown
3. Switch between **TR** and **EN**
4. UI text should update immediately

**Expected**: Language changes instantly, no reload needed

**Status**: ✅ Pass / ❌ Fail

---

### Test 7: No API Keys Exposed

1. Open browser **DevTools** → **Network** tab
2. Reload the app
3. Check all network requests to your backend
4. Verify **API key is NOT visible** in:
   - Request headers
   - Request body
   - URL parameters

**Expected**: No `API_FOOTBALL_KEY` in network traffic

**Status**: ✅ Pass / ❌ Fail

---

### Final Verification Checklist

- [ ] Backend `/health` returns 200 OK
- [ ] Backend `/api/bulletin/today` returns match data
- [ ] WebGL app loads without errors
- [ ] Match list visible and clickable
- [ ] Match detail screen opens
- [ ] All tabs load data (or placeholders)
- [ ] Language switch works (TR/EN)
- [ ] No API key exposed in network
- [ ] No console errors (warnings OK)

---

## Troubleshooting

### Issue: Backend returns 502 Bad Gateway

**Cause**: Service crashed or failed to start

**Solution**:
1. Check deployment platform logs
2. Verify `API_FOOTBALL_KEY` is set and valid
3. Verify `requirements.txt` has all dependencies: `fastapi`, `uvicorn`, `python-dotenv`, `requests`, `pydantic`
4. Restart the service

---

### Issue: CORS Error in WebGL Console

**Error**: `Access to XMLHttpRequest has been blocked by CORS policy`

**Cause**: `FRONTEND_ORIGIN` not set correctly

**Solution**:
1. Check your WebGL domain is correct (e.g., `https://my-app.netlify.app`)
2. Update `FRONTEND_ORIGIN` in backend environment variables
3. Redeploy/restart backend
4. Wait 1 minute
5. Refresh WebGL in browser

---

### Issue: API Returns 429 (Too Many Requests)

**Cause**: Hit API-Football rate limit (usually 10 req/min for free tier)

**Solution**:
1. Wait 5-10 minutes for rate limit to reset
2. Data should be cached, so app still works
3. Consider upgrading API-Football plan if frequent

---

### Issue: WebGL App Blank / Loading Forever

**Cause**: Backend unreachable or wrong URL

**Solution**:
1. Check `AppConfig.cs` has correct production URL
2. Verify backend is running: `curl https://your-backend-domain.com/health`
3. Check browser console for network errors
4. Verify `FRONTEND_ORIGIN` allows your WebGL domain

---

### Issue: Match List Empty

**Cause**: Backend not returning data

**Solution**:
1. Test backend directly: `curl https://your-backend-domain.com/api/bulletin/today`
2. Verify `API_FOOTBALL_KEY` is valid (check at [api-football.com](https://api-football.com))
3. Check backend logs for errors
4. Wait 5 minutes (rate limit may have paused fetches)

---

### Issue: Stats/Events/Lineups Show "No Data"

**Cause**: Normal for free tier or placeholder data

**Solution**:
1. These tabs may show placeholders if API doesn't return data
2. Verify in backend: `curl https://your-backend-domain.com/api/match/123/stats` (use real match ID)
3. Check backend logs for API errors

---

### Issue: Backend Takes Long Time to Wake Up

**Cause**: Free tier (Render/Railway) spins down after inactivity

**Solution**:
1. This is normal for free services
2. First request takes 30-60 seconds
3. Once awake, it's fast
4. Consider upgrading to paid tier for instant response

---

## Release Notes Template

Use this template for your v1.0.0 release on GitHub:

---

### v1.0.0 Release Notes

**Date**: May 11, 2026

#### 🎯 Features

- **Live Match Center**: Real-time football match data from API-Football
- **Match Details**: Stats, events, lineups, H2H comparisons, odds
- **Localization**: Turkish (TR) and English (EN) language support
- **Favorites**: Save and quick-access favorite matches
- **Responsive UI**: Works on desktop and tablet (1366x768, 1920x1080+)
- **Production Ready**: Secure backend, no API keys in frontend

#### 🔧 Technical Stack

- **Backend**: FastAPI (Python), Uvicorn, PostgreSQL-ready
- **Frontend**: Unity 6, C#, UI Toolkit, WebGL
- **Provider**: API-Football v3
- **Deployment**: Render/Railway (backend), Netlify/Vercel/GitHub Pages (WebGL)

#### 📋 Deployment Checklist

- ✅ Backend health check endpoint (`/health`)
- ✅ CORS security for production
- ✅ Environment variable configuration
- ✅ WebGL build optimization
- ✅ Comprehensive deployment guide
- ✅ Release checklist

#### 🚀 Getting Started

See [Deployment Guide](docs/deployment.md) and [Final Release Guide](docs/final_release_guide.md) for detailed setup.

**Quick Start**:
1. Deploy backend to Render/Railway (10 min)
2. Build WebGL in Unity (5 min)
3. Deploy WebGL to Netlify (2 min)
4. Run verification tests (5 min)

#### 🐛 Known Limitations

- **Free API Tier**: 10 requests/minute rate limit (data cached locally)
- **Free Hosting**: Render free tier spins down after 15 minutes (cold start ~30s)
- **Odds Tab**: Placeholder data (API endpoint available for paid plans)
- **Storage**: No database (stateless design; cache is in-memory)

#### 📖 Documentation

- [README.md](README.md) — Project overview
- [Architecture Guide](docs/architecture.md) — System design
- [Deployment Guide](docs/deployment.md) — Detailed hosting instructions
- [Final Release Guide](docs/final_release_guide.md) — Step-by-step release
- [Release Checklist](RELEASE_CHECKLIST.md) — Pre-production verification

#### 🙏 Credits

- **API Provider**: [API-Football](https://api-football.com)
- **Game Engine**: [Unity 6](https://unity.com)
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com)
- **Hosting**: [Render](https://render.com) / [Railway](https://railway.app)

#### 📝 License

MIT License. See LICENSE file for details.

---

## Final Steps Checklist

Before considering the project complete:

- [ ] All verification tests pass (7/7)
- [ ] No critical errors in logs
- [ ] Release notes published on GitHub
- [ ] Documentation reviewed and accurate
- [ ] Team members have access to deployment platforms
- [ ] Backup API keys stored securely (1Password, LastPass, etc.)
- [ ] Monitoring enabled (Render/Railway dashboards open)

---

## Support & Maintenance

### Monitoring

- **Render Dashboard**: [render.com/dashboard](https://render.com/dashboard)
- **Railway Dashboard**: [railway.app](https://railway.app)
- Check logs weekly for errors or API limit issues

### Updates

To update the application:
1. Make code changes in local branch
2. Commit and push to main branch
3. Render/Railway auto-redeploy within 2 minutes
4. Verify `/health` returns 200 OK
5. Test WebGL app

### API Key Rotation

If you need to change the API-Football key:
1. Generate new key at [api-football.com](https://api-football.com)
2. Update `API_FOOTBALL_KEY` in Render/Railway environment
3. Restart service
4. Test `/api/bulletin/today`

---

**Congratulations!** Your application is now in production. 🎉

For questions, see [docs/deployment.md](docs/deployment.md) or check the [Release Checklist](RELEASE_CHECKLIST.md).
