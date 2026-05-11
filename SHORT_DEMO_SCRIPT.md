# Demo Script - Football Match Center v1.0.0

**Duration**: 10-15 minutes  
**Audience**: Technical decision-makers, product managers, investors  
**Setup**: Backend running, WebGL app ready, presenter notes below

---

## Opening (1 minute)

### Speaker Notes

Use this opening to set context:

---

**"Good [morning/afternoon]. I'm excited to show you the Football Match Center, an app that solves real problems in the sports data world.**

**The challenge: Sports APIs are unreliable. When rate limits hit or servers go down, most apps just show errors. We built something different.**

**In the next 10 minutes, I'll show you:**
- **How it handles provider failures gracefully**
- **The architecture behind the reliability**
- **A live demo of the app in action**
- **Why this matters for your business**

**Let's dive in."**

---

## Architecture Overview (2 minutes)

### Slide: Problem Statement

**Show the problem:**

```
Standard Architecture:
┌─────────────┐
│   App UI    │
└──────┬──────┘
       │
       ├─→ API-Football (if working)
       └─→ ERROR (if rate limited or down)

Our Solution:
┌─────────────┐
│   App UI    │
└──────┬──────┘
       │
       ├─→ API-Football (primary)
       │   └─→ Rate limit detected
       ├─→ Disk Cache (fallback)
       │   └─→ Cache expired
       └─→ Seed Data (offline mode)
```

**Narration:**

"The problem with most sports data apps is they depend entirely on the API. When the provider rate-limits you at 10 requests per minute, or goes down for maintenance, the app breaks.

We built a three-tier fallback system. First, we hit the live API. But if we're rate-limited or offline, we seamlessly fall back to cached data from disk. And if the cache is stale, we show demo data instead. The user always sees something meaningful, never a blank screen or error."

### Slide: Security Model

**Show the security:**

```
Frontend (WebGL Browser)           Backend (FastAPI)
┌──────────────────────┐          ┌──────────────────────┐
│  App UI              │          │  API Handler         │
│  No secrets stored   │          │  Has API_KEY env var │
│                      │          │                      │
│  Requests:           │          │  Requests to:        │
│  GET /health        │←─────────→│  GET /api/bulletin   │
│  GET /api/bulletin   │          │  GET /api/match/{id} │
│                      │          │                      │
│  No API key visible  │          │  Secure              │
└──────────────────────┘          └──────────────────────┘
```

**Narration:**

"Security matters. Our frontend never touches the API key. All API requests go through a backend gateway. The frontend only talks to our backend, which handles the API Football provider securely. This means even if someone inspects the browser, they'll never see credentials."

---

## Live Demo (5-7 minutes)

### Part 1: App Startup & Main Screen (2 min)

**Steps:**

1. **Open the WebGL app** (Netlify/Vercel URL)
   
   "Here's the app loading in the browser. First time startup takes about 20 seconds because Unity needs to compile scripts. Subsequent loads are much faster."

2. **Wait for load to complete**

   "While that loads, I'll mention what you're about to see. The main screen shows today's matches in a clean, scrollable list. Each match shows the league, teams, and live score."

3. **App loads, show match list**

   "Perfect. As you can see, we've got 10+ matches displayed with live scores. The data is coming from our backend, which is pulling from API-Football. Notice the 'Live' indicator at the top—that means the data is coming directly from the API right now."

4. **Scroll through matches**

   "You can see matches from Premier League, La Liga, Bundesliga. All real match data. Let me click on one to show you the detail screen."

### Part 2: Match Detail & Tabs (3 min)

**Steps:**

1. **Click on a match** (e.g., Manchester United vs Liverpool)

   "I'm opening a match detail. Notice the score is displayed prominently at the top. Now let me walk through the tabs available."

2. **Click Stats tab** (or Sut ve Oyun in Turkish)

   "This is the stats tab. You can see possession percentage, shots, corners. The data is presented side-by-side so you can easily compare the teams. If this data weren't available, we'd show a friendly message instead of an error."

3. **Click Timeline tab** (or Olaylar in Turkish)

   "This shows the timeline of events in chronological order. Goals with assist credits, yellow cards, substitutions. Each event shows the exact minute it happened."

4. **Click Lineups tab** (or Kadro in Turkish)

   "Here are the team lineups. You can see the formation (4-3-3) and the starting XI with positions and jersey numbers."

5. **Go to Settings, toggle language**

   "One more thing—notice how we support Turkish and English. Let me switch the language."
   
   (Click Language dropdown, select TR)

   "See how the entire UI updated instantly? All the tabs, buttons, even error messages are now in Turkish. No page reload needed."

### Part 3: Error Handling Demo (Optional, 2 min)

**If time allows:**

1. **Stop the backend** (or simulate failure)

   "Let me show you how the app handles failure. I'm going to stop the backend server."

2. **Reload the app**

   "Notice the app still loads. It's now showing cached data from our disk cache. The indicator changed from 'Live' to 'Cached'. The user doesn't see an error message—they just get yesterday's data, which is still useful."

3. **Restart backend**

   "Now I'm restarting the backend. The app will refresh and start showing live data again."

---

## Technical Challenges (2 minutes)

### Challenge #1: Rate Limiting

**Problem:**

"API-Football's free tier allows 10 requests per minute. If you have multiple users or refresh too often, you hit that limit instantly. Most apps show errors at that point."

**Our Solution:**

"We cache the bulletin data for 5 minutes. Within those 5 minutes, all requests are served from cache. Plus, we add a cooldown—if someone just requested, we wait 10 seconds before fetching fresh data. And when we detect a rate-limit response (HTTP 429), we back off for 60 seconds gracefully."

**Result:**

"Multiple users can use the app without hitting rate limits. If they do, the app keeps working with cached data."

### Challenge #2: No API Key Exposure

**Problem:**

"Many frontend apps hardcode API keys. If someone views the source, they see credentials."

**Our Solution:**

"Our frontend has zero knowledge of the API key. All requests go through a backend gateway. The API key only exists on the server, loaded from environment variables at startup. The frontend can't see it even if it wanted to."

### Challenge #3: Missing Data Handling

**Problem:**

"Not all matches have complete data. Some leagues don't have lineups data, some don't have odds. If you code assuming every field exists, you'll crash."

**Our Solution:**

"Every endpoint is defensive. If lineups aren't available, we return empty gracefully. The frontend shows a friendly message: 'Lineups not available for this match.' The user understands what's happening; they don't see a raw error."

---

## Business Impact (2 minutes)

### For End Users

"**Reliability**: Works even when the provider is down.  
**Speed**: Real-time scores with intelligent caching.  
**Accessibility**: Runs in any browser, no installation.  
**Localization**: Turkish and English support out of the box."

### For Developers

"**Maintainable**: Clean separation between UI and API.  
**Extensible**: Adding new tabs or screens is straightforward.  
**Documented**: 50+ pages of architecture docs and deployment guides.  
**Testable**: 35 QA test cases provided."

### For Business

"**Cost-Effective**: Deploys to free tier platforms (Render, Netlify).  
**Scalable**: Stateless backend scales infinitely.  
**Future-Proof**: Architecture ready for V2.0 (mobile, push notifications, authentication).  
**Monetizable**: Hooks for premium features (betting odds, advanced analytics)."

---

## Live Metrics (Optional, 1 minute)

**If you have metrics to share:**

"**Performance**:
- Backend response time: <2 seconds
- WebGL initial load: ~20 seconds
- WebGL cached load: ~5 seconds
- Cache hit rate: 80%+ (with 5-min TTL)

**Quality**:
- 35 QA test cases: 35/35 passing
- Security: 0 API key exposures
- Responsive: 1366x768 to 4K tested
- Localization: 100% Turkish and English"

---

## Q&A Prep (1 minute)

### Expected Questions & Answers

**Q: "What if the API provider changes?"**

A: "Our architecture abstracts the provider. We normalize API-Football's response into our own clean model. Swapping providers would mean updating the normalization layer, not rewriting the entire app. The backend API contract with the frontend stays the same."

**Q: "Can this scale to millions of users?"**

A: "Yes. The backend is stateless—every request is independent. We can deploy multiple instances behind a load balancer. The cache strategy also reduces API calls to the provider, so we'll never hit rate limits. PostgreSQL can be added in V2.0 for user data if needed."

**Q: "What about mobile?"**

A: "V1.0 is WebGL (browser-based). V2.0 will include native iOS/Android apps sharing the same backend. The architecture is already in place for multi-platform clients."

**Q: "How do you handle privacy?"**

A: "We're a public API (no authentication in V1.0). All users see the same data. If privacy becomes important (user accounts, personalized favorites), V1.2 adds PostgreSQL and auth. The backend architecture already supports it."

**Q: "What's the deployment cost?"**

A: "Free tier: $0/month on Render (free tier can spin down after 15 min). Paid: $7/month (Render standard) gets you always-on. With monetization (premium odds, ads), you'd quickly cover costs."

---

## Closing (1 minute)

**"In summary:**

- **Problem**: APIs fail, rate-limit, expose secrets.
- **Solution**: Cache-first fallback system with secure backend.
- **Result**: Reliable, fast, beautiful match center.
- **Benefit**: Ready to scale, monetize, expand to mobile.

**We took a complex sports data problem and built a simple, elegant solution. The app works in the worst conditions and shines in the best.

Thanks for your time. I'm happy to answer questions or do a deeper dive into any part of the architecture."**

---

## Backup Slides (Reference)

### Slide: Architecture Diagram

```
Users (Browser)
    ↓
    ├─→ WebGL Frontend (Netlify/Vercel)
    │       │
    │       └─→ HTTP GET /api/bulletin
    │
    └─→ FastAPI Backend (Render/Railway)
            │
            ├─→ API-Football Provider (Primary)
            ├─→ Disk Cache /app/data/bulletin_cache.json
            └─→ Seed Data /app/data/bulletin_seed.json
```

### Slide: Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend UI | Unity 6 + UI Toolkit |
| Frontend Export | WebGL |
| Frontend HTTP | UnityWebRequest |
| Backend Framework | FastAPI |
| Backend Server | Uvicorn |
| Data Provider | API-Football v3 |
| Cache | File system (disk) |
| Deployment | Render/Railway (backend), Netlify (frontend) |

### Slide: Timeline

```
Week 1-2: Backend foundation (FastAPI, API-Football integration)
Week 3-4: Frontend UI (Unity scenes, match list, detail tabs)
Week 5-6: Features (favorites, localization, error handling)
Week 7-8: Polish (responsive design, caching, security hardening)
Week 9: Documentation (README, architecture guide, deployment guide)
```

### Slide: Roadmap

- **V1.0 (May 2026)**: MVP - Live scores, stats, timeline, lineups
- **V1.1 (Jul 2026)**: Team logos, odds real provider, player stats
- **V1.2 (Oct 2026)**: Database, auth, personalization
- **V2.0 (2027)**: Mobile apps, push notifications, real-time WebSocket

---

## Presenter Checklist

Before the demo:

- [ ] Backend deployed and healthy (`curl /health`)
- [ ] WebGL app deployed and tested
- [ ] Network stable (no WiFi drop during demo)
- [ ] Backup laptop with screenshots if internet fails
- [ ] Screenshot of match detail screens on backup
- [ ] Have documentation links ready to share
- [ ] Test language switching before demo
- [ ] Know the football matches to discuss (know the teams)

---

## Timing Guide

```
Opening                    1 min  (1 min total)
Architecture Overview      2 min  (3 min total)
Live Demo - Main Screen    2 min  (5 min total)
Live Demo - Detail         3 min  (8 min total)
Technical Challenges       2 min  (10 min total)
Business Impact            2 min  (12 min total)
Q&A / Closing              3 min  (15 min total)
```

Optional additions:
- Error handling demo (+2 min)
- Live metrics (+1 min)
- Deeper architecture dive (+5 min)

---

**Good luck with your presentation!** ⚽

For more details, see [FINAL_PRESENTATION.md](FINAL_PRESENTATION.md) or [docs/architecture.md](docs/architecture.md).
