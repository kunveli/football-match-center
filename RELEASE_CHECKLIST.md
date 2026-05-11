# RELEASE CHECKLIST

Use this checklist before QA handoff, staging, or production release.

## Backend

### Local Development
- [ ] Backend starts successfully
- [ ] Health endpoint responds: `GET /health` returns `{"status": "ok"}`
- [ ] Bulletin endpoint works: `GET /api/bulletin/today`
- [ ] Stats endpoint works for a valid match ID
- [ ] Events endpoint works for a valid match ID
- [ ] CORS allows intended local origins
- [ ] No provider API key hardcoded in source files

### Deployment Preparation
- [ ] `.env` file contains `API_FOOTBALL_KEY` with valid value
- [ ] `.env.example` is committed with placeholder values
- [ ] `.gitignore` includes `.env` (never commit real keys)
- [ ] `CORS_ALLOW_ORIGINS` configured for production frontend domain
- [ ] Backend start command tested: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] `requirements.txt` is up-to-date with all dependencies

### Deployment Verification (Render/Railway)
- [ ] Backend deployed to production platform (Render/Railway)
- [ ] Health endpoint returns 200 OK: `curl https://your-backend-domain.com/health`
- [ ] Bulletin endpoint works: `curl https://your-backend-domain.com/api/bulletin/today`
- [ ] Match detail endpoint works: `curl https://your-backend-domain.com/api/match/{id}/general`
- [ ] CORS configured correctly for frontend domain
- [ ] No API key hardcoded in deployment platform (using env vars only)
- [ ] Logs show no startup errors
- [ ] Service maintains up status on health checks

## Unity Play Mode

- [ ] Unity Play Mode starts without compile errors
- [ ] Bulletin list loads from configured backend URL
- [ ] Match detail stats load correctly
- [ ] Timeline/events tab works
- [ ] Lineups tab works
- [ ] H2H comparisons load data
- [ ] Odds tab displays (placeholder or live)
- [ ] Clear, friendly error message when backend is unreachable
- [ ] No raw exception text shown to end users
- [ ] Language switch (TR/EN) updates immediately
- [ ] Settings tab allows backend URL override (for testing)

## WebGL Build

### Build Configuration
- [ ] AppConfig.cs verified for correct build profile
- [ ] Development profile uses `http://127.0.0.1:8000`
- [ ] Production profile uses `https://your-backend-domain.com`
- [ ] Build Profile setting persists in PlayerPrefs

### WebGL Build
- [ ] WebGL build completes successfully (no Unity errors)
- [ ] Build output folder contains `index.html`, `Build/` folder
- [ ] `build.js` and other assets are present

### WebGL Deployment & Testing
- [ ] WebGL deployed to static host (Netlify/Vercel/S3/GitHub Pages)
- [ ] WebGL can reach backend URL (check Network tab in DevTools)
- [ ] No CORS errors in browser console
- [ ] No "API key" visible in WebGL build files or network requests
- [ ] Bulletin list loads from production backend
- [ ] Match details clickable and functional
- [ ] Stats/events/lineups/odds tabs load without errors
- [ ] UI remains responsive on 1366x768 and 1920x1080 resolutions
- [ ] Language switching works (TR/EN)
- [ ] No JavaScript console errors

## CORS Configuration

- [ ] Backend CORS includes production WebGL domain
- [ ] CORS allows `GET`, `POST`, `OPTIONS` methods
- [ ] Local development CORS allows `http://localhost` and `http://127.0.0.1`
- [ ] CORS preflight requests return 200 OK
- [ ] No overly permissive `*` origin (security check)

## Security

- [ ] No `API_FOOTBALL_KEY` in Unity source code
- [ ] No `API_FOOTBALL_KEY` visible in WebGL network requests
- [ ] No hardcoded backend URLs in production builds
- [ ] `.env` file is local-only (in `.gitignore`)
- [ ] Sensitive environment variables only on deployment platform
- [ ] No git history exposes API keys

## Final Sanity

- [ ] No compile errors (C# and Python)
- [ ] No critical console errors
- [ ] Backend logs are useful, not noisy (check log levels)
- [ ] Production build has verbose logs disabled
- [ ] Performance acceptable on target hardware
- [ ] All API endpoints timeout gracefully (no hanging requests)
- [ ] Deployment can be repeated without manual steps
- [ ] Monitoring/health checks active on production

## Deployment Documentation

- [ ] `docs/deployment.md` reviewed and accurate
- [ ] Render setup instructions tested
- [ ] Railway setup instructions tested
- [ ] Environment variable list complete and documented
- [ ] Health check configuration verified
- [ ] Frontend deployment options documented
- [ ] Troubleshooting section covers common issues
- [ ] README.md references deployment.md for setup

## Sign-Off

- [ ] All items checked and verified
- [ ] No blocking issues remain
- [ ] Ready for user acceptance testing (UAT) or production
- [ ] Deployment runbook reviewed by team (if applicable)
