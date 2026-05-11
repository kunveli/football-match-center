# QA Test Plan - Unity Football Match Center v1.0.0

**Project**: Unity Football Match Center  
**Version**: v1.0.0  
**Date**: May 11, 2026  
**Platform**: Backend (FastAPI) + Frontend (Unity WebGL)  

---

## Table of Contents

1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Backend API Tests](#backend-api-tests)
4. [Unity Main Screen Tests](#unity-main-screen-tests)
5. [Match Detail Screen Tests](#match-detail-screen-tests)
6. [Rate Limit & Offline Tests](#rate-limit--offline-tests)
7. [WebGL Build Tests](#webgl-build-tests)
8. [Release Approval Checklist](#release-approval-checklist)
9. [Test Results Summary](#test-results-summary)

---

## Overview

### Scope

This QA test plan covers:
- ✅ Backend API endpoints
- ✅ Unity main UI screen
- ✅ Match detail screen
- ✅ Error handling & fallbacks
- ✅ WebGL build configuration
- ✅ Release readiness

### Test Platforms

| Component | Platform | Version |
|-----------|----------|---------|
| Backend | Render / Railway | FastAPI + Uvicorn |
| Frontend (Play Mode) | Windows / Mac | Unity 6.0+ |
| Frontend (WebGL) | Chrome / Firefox | Latest |

### Pass Criteria

- ✅ All test cases pass
- ✅ No critical console errors
- ✅ No API key exposed
- ✅ User-friendly error messages
- ✅ Responsive UI at target resolutions

---

## Test Environment Setup

### Prerequisites

Before running tests, ensure:

1. **Backend Running**
   ```bash
   # Local or deployed
   uvicorn app.main:app --reload
   # Should start at http://localhost:8000 or deployed URL
   ```

2. **Unity Project Open**
   - Open `İstatistik/` project in Unity 6.0+
   - Open Play Mode ready

3. **Browser DevTools**
   - F12 to open DevTools for WebGL testing
   - Watch Console tab for errors

4. **Test Tools**
   - `curl` or Postman for backend API tests
   - Browser for WebGL tests
   - Unity Editor for Play Mode tests

### Environment Variables (Test)

For local testing, create `.env.test`:

```
API_FOOTBALL_KEY=your_test_key_here
API_FOOTBALL_BASE=https://v3.football.api-sports.io
API_FOOTBALL_HOST=v3.football.api-sports.io
CORS_ALLOW_ORIGINS=http://localhost,http://127.0.0.1,http://localhost:8080,http://localhost:3000
```

---

## Backend API Tests

### Test 1.1: Health Endpoint

**Endpoint**: `GET /health`

**Test Steps**:
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response**:
```json
{"status": "ok"}
```

**Expected Status Code**: `200 OK`

**Pass Criteria**:
- [ ] Returns 200 status code
- [ ] Response is valid JSON
- [ ] Contains `"status": "ok"`

**Notes**: This endpoint is critical for deployment platforms (Render, Railway, K8s).

---

### Test 1.2: Bulletin Today Endpoint

**Endpoint**: `GET /api/bulletin/today`

**Test Steps**:
```bash
curl -X GET http://localhost:8000/api/bulletin/today
```

**Expected Response** (example):
```json
[
  {
    "id": 1234567,
    "league_name": "Premier League",
    "match_date": "2026-05-11",
    "status": "LIVE",
    "home_team": "Manchester United",
    "away_team": "Liverpool",
    "home_score": 1,
    "away_score": 2,
    "live_time": "45+2",
    "season": 2025,
    "round": "38",
    "referee": "John Moss",
    "venue": "Old Trafford",
    "attendance": 75000
  }
]
```

**Expected Status Code**: `200 OK`

**Pass Criteria**:
- [ ] Returns 200 status code
- [ ] Response is array of match objects
- [ ] Each match has: `id`, `league_name`, `match_date`, `home_team`, `away_team`, `home_score`, `away_score`
- [ ] Contains at least 1 match
- [ ] Scores are non-negative integers

**Notes**: Data can come from live API, cache, or seed file. Any source is acceptable if data is valid.

---

### Test 1.3: Match Stats Endpoint

**Endpoint**: `GET /api/match/{match_id}/stats`

**Test Steps**:
1. Get a valid match ID from Test 1.2
2. Replace `{match_id}` in URL
3. Run:
```bash
curl -X GET http://localhost:8000/api/match/1234567/stats
```

**Expected Response** (if available):
```json
{
  "match_id": 1234567,
  "home_team": "Manchester United",
  "away_team": "Liverpool",
  "home_stats": [
    {"stat_type": "shots", "value": 15},
    {"stat_type": "possession", "value": 42}
  ],
  "away_stats": [
    {"stat_type": "shots", "value": 18},
    {"stat_type": "possession", "value": 58}
  ]
}
```

**Expected Status Code**: `200 OK` (with data) or `200 OK` (empty/unavailable)

**Pass Criteria**:
- [ ] Returns 200 status code
- [ ] If data available: contains stats array
- [ ] If unavailable: returns graceful empty response (not 500 error)
- [ ] No server crash
- [ ] Response time < 2 seconds

**Fallback Behavior**: If API doesn't return stats, should return:
```json
{"message": "Stats unavailable for this match"}
```

---

### Test 1.4: Match Events Endpoint

**Endpoint**: `GET /api/match/{match_id}/events`

**Test Steps**:
1. Use same `match_id` from Test 1.3
2. Run:
```bash
curl -X GET http://localhost:8000/api/match/1234567/events
```

**Expected Response** (if available):
```json
{
  "match_id": 1234567,
  "events": [
    {
      "elapsed": 23,
      "type": "Goal",
      "team": "Manchester United",
      "player": "Marcus Rashford",
      "assist": "Luke Shaw"
    },
    {
      "elapsed": 45,
      "type": "Yellow Card",
      "team": "Liverpool",
      "player": "Mohamed Salah"
    }
  ]
}
```

**Expected Status Code**: `200 OK`

**Pass Criteria**:
- [ ] Returns 200 status code
- [ ] If data available: contains events array
- [ ] If unavailable: returns empty array gracefully (not error)
- [ ] No server crash
- [ ] Response time < 2 seconds

**Fallback Behavior**: If no events:
```json
{"events": []}
```

---

### Test 1.5: Match Lineups Endpoint

**Endpoint**: `GET /api/match/{match_id}/lineups`

**Test Steps**:
1. Use same `match_id` from Test 1.3
2. Run:
```bash
curl -X GET http://localhost:8000/api/match/1234567/lineups
```

**Expected Response** (if available):
```json
{
  "match_id": 1234567,
  "home_team": "Manchester United",
  "away_team": "Liverpool",
  "home_formation": "4-3-3",
  "away_formation": "4-2-3-1",
  "home_players": [
    {
      "position": "G",
      "number": 1,
      "name": "David de Gea"
    }
  ],
  "away_players": [
    {
      "position": "G",
      "number": 1,
      "name": "Alisson"
    }
  ]
}
```

**Expected Status Code**: `200 OK`

**Pass Criteria**:
- [ ] Returns 200 status code
- [ ] If data available: contains home/away formation and players
- [ ] If unavailable: returns graceful empty response
- [ ] No server crash
- [ ] Response time < 2 seconds

---

### Test 1.6: API Key Security

**Purpose**: Verify API key is never exposed in responses

**Test Steps**:
1. Make requests to all endpoints (Tests 1.1-1.5)
2. In each response, search for:
   - `API_FOOTBALL_KEY`
   - `api_key=`
   - `X-RapidAPI-Key`
   - Any string matching API key pattern

**Expected**: API key should NOT appear anywhere

**Pass Criteria**:
- [ ] No API key in `/health` response
- [ ] No API key in `/api/bulletin/today` response
- [ ] No API key in `/api/match/{id}/stats` response
- [ ] No API key in `/api/match/{id}/events` response
- [ ] No API key in `/api/match/{id}/lineups` response
- [ ] No API key in HTTP response headers

**Security Note**: Keys are kept on backend only. Frontend makes requests to backend, never to API-Football directly.

---

## Unity Main Screen Tests

### Prerequisites

- Unity project open
- Play Mode ready
- Backend running and accessible
- Console panel visible in Unity

### Test 2.1: App Loads Without Errors

**Test Steps**:
1. Open `Assets/Scenes/MainScene.unity`
2. Click **Play** button in Unity Editor
3. Watch Console tab for errors
4. Wait 5 seconds for app initialization

**Expected**:
- No red errors in Console
- App UI visible
- No exceptions thrown

**Pass Criteria**:
- [ ] Play Mode starts successfully
- [ ] Console shows no red error messages
- [ ] Console shows startup logs (e.g., "[STARTUP] fetcher started")
- [ ] UI is responsive (not frozen)

**Notes**: Yellow warnings are acceptable (e.g., deprecated API warnings).

---

### Test 2.2: Match List Renders

**Test Steps**:
1. From Test 2.1, app should be running
2. Look at **Bulletin** tab (should be selected by default)
3. Wait 2-3 seconds for data to load
4. Observe the match list

**Expected**:
- Match list displays 5+ matches
- Each match shows: home team, score, away team
- Scores are visible and correct
- No placeholder text visible

**Pass Criteria**:
- [ ] Match list is not empty
- [ ] At least 5 matches visible
- [ ] Each match has home/away team names
- [ ] Each match has score (even if 0-0)
- [ ] Match dates are displayed
- [ ] No "Loading..." or placeholder text after 3 seconds

**Example Visual**:
```
[Premier League]
Manchester United 1 - 2 Liverpool
May 11, 2026 | 20:00

[La Liga]
Barcelona 2 - 0 Valencia
May 11, 2026 | 19:00

... more matches
```

---

### Test 2.3: Live Scores Show Correctly

**Test Steps**:
1. From Test 2.2, observe match list
2. Look for scores in the main display
3. Click on one match to see score in detail

**Expected**:
- Current scores visible in list view
- Scores update dynamically if match is LIVE (within a few seconds)
- Score format: `home_score - away_score`

**Pass Criteria**:
- [ ] Scores displayed in correct format
- [ ] Scores are integers (not floating point)
- [ ] LIVE status shows for ongoing matches
- [ ] Scores don't show as negative

**Notes**: Scores are read-only for this release. No scoring buttons/input.

---

### Test 2.4: League Filter Works

**Test Steps**:
1. From Test 2.2, look for league filter dropdown
2. Click on league filter
3. Select different leagues (e.g., "Premier League", "La Liga", "Bundesliga")
4. Observe list updates

**Expected**:
- List updates immediately
- Only selected league matches shown
- Filter is intuitive and responsive

**Pass Criteria**:
- [ ] League dropdown is visible
- [ ] Selecting a league filters the list
- [ ] Selected league persists while viewing
- [ ] All matches shown are from selected league
- [ ] Filter updates instantly (no delay > 1 second)

---

### Test 2.5: Favorites Feature Works

**Test Steps**:
1. Click on a match in the list
2. Look for **favorite/star icon** in detail screen
3. Click the star icon
4. Go back to main list
5. Look for **Favorites** tab or filter

**Expected**:
- Star icon toggles between filled/empty
- Favorited matches are marked
- Favorites tab shows saved matches
- Favorites persist on app restart

**Pass Criteria**:
- [ ] Star icon visible in detail screen
- [ ] Clicking star toggles favorite status
- [ ] Favorites tab shows only favorited matches
- [ ] Favorite count is accurate
- [ ] Favorites persist in PlayerPrefs

---

### Test 2.6: Source Banner Shows Correctly

**Test Steps**:
1. From Test 2.1, look at top of app
2. Observe the data source indicator (e.g., "Live", "Cached", "Demo")
3. Note which source is being used

**Expected**:
- Banner shows current data source
- "Live" if using API-Football
- "Cached" if using disk cache
- "Demo" if using seed data

**Pass Criteria**:
- [ ] Source banner visible
- [ ] Source matches actual data origin
- [ ] Banner updates if data source changes
- [ ] No misleading information

---

### Test 2.7: Language Switch Works

**Test Steps**:
1. Click **Settings** (Ayarlar) tab
2. Find **Language** dropdown
3. Select **TR** (Turkish)
4. Observe UI text changes
5. Select **EN** (English)
6. Observe UI text changes back

**Expected**:
- All UI text updates immediately
- Language persists on app restart
- Both TR and EN are complete translations
- No untranslated placeholders visible

**Pass Criteria**:
- [ ] Language dropdown visible in Settings
- [ ] Selecting TR translates UI to Turkish
- [ ] Selecting EN translates UI to English
- [ ] All buttons/tabs translated (not mix of languages)
- [ ] Translation changes instantly (no reload)
- [ ] Language persists across sessions

**Key Areas to Check**:
- Tab labels (Bulten, Favori, Ayarlar)
- Match detail tab names (Genel, Sut ve Oyun, Olaylar, Kadro, H2H, Oranlar)
- Error messages
- Empty state messages

---

## Match Detail Screen Tests

### Test 3.1: Selected Match Opens Correctly

**Test Steps**:
1. From Test 2.2, click any match in list
2. Wait for detail screen to load
3. Observe match information displayed

**Expected**:
- Detail screen opens without lag
- Correct match is displayed (verify by team names, date, score)
- Header shows match info clearly

**Pass Criteria**:
- [ ] Detail screen loads within 2 seconds
- [ ] Correct match displayed (team names match)
- [ ] No console errors
- [ ] Back button visible and functional

---

### Test 3.2: Score & Header Correct

**Test Steps**:
1. From Test 3.1, observe header section
2. Verify score matches what was shown in list
3. Check team names, logo placeholders, date

**Expected**:
- Header shows:
  - Home team name and score
  - Away team name and score
  - Match date and time
  - League name
  - Match status (LIVE, FINISHED, etc.)

**Pass Criteria**:
- [ ] Home score correct
- [ ] Away score correct
- [ ] Team names correct (not swapped)
- [ ] Date/time displayed
- [ ] League name shown
- [ ] Status indicator correct

---

### Test 3.3: Stats Tab Works

**Test Steps**:
1. From Test 3.1, find **Stats** tab (or **Sut ve Oyun** in Turkish)
2. Click the tab
3. Wait for data to load
4. Observe stats display

**Expected**:
- Tab loads without error
- Shows stats if available (possession, shots, corners, etc.)
- Or shows graceful "unavailable" message

**Pass Criteria**:
- [ ] Tab loads without crashing
- [ ] If stats available: displays stat categories and values
- [ ] If unavailable: shows friendly "Data not available" message
- [ ] No raw error text (e.g., "500 Internal Server Error")
- [ ] Response time < 2 seconds

**Example Stats Display**:
```
Manchester United vs Liverpool

Possession: 42% vs 58%
Shots: 15 vs 18
Shots on Target: 7 vs 9
Corners: 4 vs 6
Fouls: 12 vs 10
```

---

### Test 3.4: Timeline Tab Works

**Test Steps**:
1. From Test 3.1, find **Timeline** tab (or **Olaylar** in Turkish)
2. Click the tab
3. Wait for data to load
4. Observe events chronologically

**Expected**:
- Tab loads without error
- Shows events (goals, cards, substitutions) if available
- Events listed by minute (chronological order)
- Or shows "No events" gracefully

**Pass Criteria**:
- [ ] Tab loads without crashing
- [ ] If events available: displays goals, cards, substitutions
- [ ] Events shown in correct order (oldest first)
- [ ] Each event shows minute, type, player, team
- [ ] If no events: shows "No events in this match"
- [ ] Response time < 2 seconds

**Example Timeline Display**:
```
23' Goal - Marcus Rashford (Manchester United)
     Assist: Luke Shaw

45' Yellow Card - Mohamed Salah (Liverpool)

48' Substitution - Jadon Sancho in, Antony out (Manchester United)
```

---

### Test 3.5: Lineups Tab Works

**Test Steps**:
1. From Test 3.1, find **Lineups** tab (or **Kadro** in Turkish)
2. Click the tab
3. Wait for data to load
4. Observe formation and player lists

**Expected**:
- Tab loads without error
- Shows formation (e.g., 4-3-3)
- Shows player lists for each team
- Or shows "unavailable" gracefully

**Pass Criteria**:
- [ ] Tab loads without crashing
- [ ] If lineups available: shows formations
- [ ] Player names and positions displayed
- [ ] Team colors/logos distinguish sides (visual design)
- [ ] If unavailable: shows friendly message
- [ ] Response time < 2 seconds

**Example Lineups Display**:
```
Manchester United (4-3-3)
[Goalkeeper]
1. David de Gea

[Defenders]
2. Aaron Wan-Bissaka
3. Harry Maguire
...

Liverpool (4-2-3-1)
[Goalkeeper]
1. Alisson
...
```

---

### Test 3.6: Odds Placeholder Works

**Test Steps**:
1. From Test 3.1, find **Odds** tab (or **Oranlar** in Turkish)
2. Click the tab
3. Observe placeholder display

**Expected**:
- Tab loads without error
- Shows placeholder message (e.g., "Odds data coming soon")
- Or shows mock odds if available

**Pass Criteria**:
- [ ] Tab is clickable
- [ ] Tab loads without crash
- [ ] Shows appropriate placeholder or data
- [ ] No "Not Implemented" error

**Note**: Odds tab is placeholder for v1.0.0. Full odds data available in future versions.

---

### Test 3.7: No Fake/Demo Data Shown

**Test Steps**:
1. Go through all detail tabs (Stats, Timeline, Lineups)
2. Look for:
   - Hardcoded test names (e.g., "Test Player", "Demo Team")
   - Lorem ipsum placeholders
   - Inconsistent data with list view
   - Example data labeled as such

**Expected**:
- All data matches actual match information
- No demo/test data visible
- Data is either real from API or clearly marked as unavailable

**Pass Criteria**:
- [ ] No test/demo player names
- [ ] No placeholder text (except for genuine unavailable sections)
- [ ] All data consistent with bulletin list
- [ ] No hardcoded example stats

---

## Rate Limit & Offline Tests

### Test 4.1: Cache Used on Provider Failure

**Test Steps**:
1. Ensure backend is running with cache file: `app/data/bulletin_cache.json`
2. (Optional) Manually trigger API failure:
   - Stop backend, delete API key from environment
   - Restart backend
3. Open app in Play Mode
4. Observe data source banner

**Expected**:
- If API fails, app still shows matches from cache
- Banner shows "Cached" instead of "Live"
- User sees old but valid data

**Pass Criteria**:
- [ ] App does not crash when API fails
- [ ] Matches displayed even when API unavailable
- [ ] Source banner shows "Cached"
- [ ] Error message is friendly (not raw HTTP error)

**Cache Behavior**:
- Cache TTL: 5 minutes (300 seconds)
- If cache expired: fall through to seed data

---

### Test 4.2: Seed Fallback Only If Cache Unavailable

**Test Steps**:
1. Delete or corrupt `app/data/bulletin_cache.json`
2. Set API key to invalid value
3. Restart backend
4. Open app in Play Mode
5. Observe data source

**Expected**:
- If cache unavailable AND API fails, app shows seed data
- Banner shows "Demo"
- Data is clearly marked as demo/offline data

**Pass Criteria**:
- [ ] Seed data loads if cache not found
- [ ] Banner shows "Demo"
- [ ] Matches displayed (even if old demo data)
- [ ] App does not crash

**Priority Order** (enforced in backend):
1. Live API (if valid key and API online)
2. Cached data (if cache exists and not expired)
3. Seed data (fallback for offline/demo)

---

### Test 4.3: User-Friendly Error Messages

**Test Steps**:
1. Trigger various error conditions:
   - Disconnect internet while app loading
   - Set backend URL to invalid address
   - Stop backend server
2. Observe error messages shown to user

**Expected**:
- Error messages are clear and non-technical
- No raw HTTP errors (404, 500, etc.)
- Messages like: "Unable to connect. Showing cached data."
- Suggestions for action if needed

**Pass Criteria**:
- [ ] No raw JSON error responses shown
- [ ] No stack traces visible
- [ ] No "Internal Server Error 500" in UI
- [ ] Messages are user-friendly (TR/EN appropriately)
- [ ] Errors don't crash app

**Example Good Error Messages**:
```
❌ Bad:
  "HTTPConnectionError: Failed to establish connection to 127.0.0.1:8000"

✅ Good:
  "Unable to connect to server. Showing cached matches."
```

---

### Test 4.4: App Does Not Crash

**Test Steps**:
1. Run through all error scenarios (Tests 4.1-4.3)
2. Perform stress tests:
   - Rapidly click buttons
   - Switch tabs while loading
   - Click back/forward multiple times
   - Toggle language rapidly
3. Monitor Console for exceptions

**Expected**:
- App remains responsive
- No crashes or freezes
- Error states handled gracefully

**Pass Criteria**:
- [ ] No UnityEngine.Exception thrown
- [ ] No NullReferenceException
- [ ] No OutOfMemoryException
- [ ] App recovers from errors
- [ ] Can click buttons even after error

---

## WebGL Build Tests

### Prerequisites

- WebGL build completed: `WebGL_Build/` folder exists
- Backend deployed and accessible
- Modern browser (Chrome, Firefox, Edge)

### Test 5.1: Backend URL Points to Production

**Test Steps**:
1. Open `Assets/Scripts/Core/AppConfig.cs`
2. Find `ProductionBackendPlaceholder` constant
3. Verify it contains production domain (not localhost)

**Expected**:
```csharp
private const string ProductionBackendPlaceholder = "https://unity-stats-api.onrender.com";
// NOT "http://localhost:8000"
```

**Pass Criteria**:
- [ ] Production URL is set
- [ ] URL is HTTPS (not HTTP)
- [ ] URL points to actual deployed backend
- [ ] No localhost addresses

---

### Test 5.2: CORS Works

**Test Steps**:
1. Deploy WebGL to production (Netlify/Vercel)
2. Open WebGL app in browser
3. Watch Network tab in DevTools
4. Look for CORS preflight requests (OPTIONS)

**Expected**:
- Preflight requests return 200 OK
- Response includes `Access-Control-Allow-Origin` header
- Frontend domain is in allowed origins

**Pass Criteria**:
- [ ] No CORS errors in Console
- [ ] Preflight requests succeed
- [ ] `Access-Control-Allow-Origin` header present
- [ ] WebGL domain matches backend CORS config

**Debug CORS Issues**:
- Check backend `CORS_ALLOW_ORIGINS` env var
- Verify WebGL domain is in the list
- Restart backend after updating CORS

---

### Test 5.3: App Loads in Browser

**Test Steps**:
1. Navigate to WebGL URL in Chrome/Firefox/Edge
2. Wait 15-20 seconds for app to initialize
3. Observe loading progress

**Expected**:
- Page loads without 404/500
- Loading bar progresses
- App initializes after ~20 seconds
- UI appears and is responsive

**Pass Criteria**:
- [ ] Page loads (HTTP 200)
- [ ] Loading screen visible
- [ ] App initializes and shows UI
- [ ] No blank white screen or error page
- [ ] Response time acceptable (< 30 seconds)

**Note**: First load is slower (~20s). Subsequent loads are faster (~5s).

---

### Test 5.4: No API Key Visible in Browser

**Test Steps**:
1. Open WebGL app in browser
2. Open DevTools (F12)
3. Go to **Network** tab
4. Reload the page
5. Go through all network requests
6. Search for "API" or "key" in:
   - Request headers
   - Request body
   - Request URL
   - Response headers
   - Response body

**Expected**:
- No `API_FOOTBALL_KEY` visible anywhere
- No API key in localStorage or sessionStorage
- No API key in HTML source

**Pass Criteria**:
- [ ] No API key in Network requests
- [ ] No API key in localStorage (check Console: `localStorage`)
- [ ] No API key in response bodies
- [ ] All API requests go to backend (not API-Football directly)

**Verification in Console**:
```javascript
// Check if any key material is stored
localStorage
sessionStorage
```

Should not contain sensitive data.

---

### Test 5.5: UI Responsive at Target Resolutions

**Test Steps**:
1. Open WebGL app in browser
2. Open DevTools
3. Use Device Toolbar to test resolutions:
   - 1366x768 (target)
   - 1920x1080 (target)
   - 768x1024 (tablet)
   - 375x667 (mobile, for reference)

**Expected**:
- UI is usable at 1366x768
- UI is usable at 1920x1080
- No critical overflow/cutoff
- Buttons are clickable
- Text is readable

**Pass Criteria**:
- [ ] 1366x768: All UI visible and clickable
- [ ] 1920x1080: All UI visible and clickable
- [ ] No horizontal scrollbars needed
- [ ] No text cutoff
- [ ] Buttons have adequate touch targets (≥ 44x44 px)

---

## Release Approval Checklist

### Test 6.1: No Compile Errors

**Test Steps**:
1. Open Unity project
2. Click **Window** → **General** → **Console**
3. In Console, filter by error level
4. Check for red error messages

**Expected**:
- 0 red compiler errors
- Project builds successfully

**Pass Criteria**:
- [ ] No C# compilation errors
- [ ] No asset import errors
- [ ] No build pipeline errors
- [ ] Console shows no red errors at startup

---

### Test 6.2: No Critical Console Errors

**Test Steps**:
1. Run Play Mode
2. Navigate through all screens:
   - Main screen (match list)
   - Detail screen (all tabs)
   - Settings screen
3. Open Console
4. Look for critical errors

**Expected**:
- No red errors
- Only informational logs or yellow warnings

**Pass Criteria**:
- [ ] Console has 0 red error messages
- [ ] No exceptions thrown
- [ ] No null reference errors
- [ ] Warnings are OK (e.g., deprecated APIs)

---

### Test 6.3: README Completed

**Test Steps**:
1. Open `backend-service/README.md`
2. Check for required sections:
   - Project overview
   - Features list
   - Tech stack
   - Setup instructions
   - API endpoints
   - Deployment info
   - Troubleshooting

**Expected**:
- All sections filled with relevant content
- No placeholder text ("TODO", "COMING SOON")
- Links are working (at least syntactically correct)

**Pass Criteria**:
- [ ] Project overview present
- [ ] Features list complete
- [ ] Tech stack documented
- [ ] Setup instructions clear
- [ ] API endpoints listed
- [ ] Deployment section filled
- [ ] No "TODO" placeholders

---

### Test 6.4: Release Guide Completed

**Test Steps**:
1. Open `docs/final_release_guide.md`
2. Check for required sections:
   - Backend deployment (Render/Railway)
   - WebGL build steps
   - Verification checklist
   - Troubleshooting guide
   - Release notes template

**Expected**:
- All sections detailed and complete
- Step-by-step instructions are clear
- Code examples provided
- No missing steps

**Pass Criteria**:
- [ ] Render deployment steps complete
- [ ] Railway deployment steps complete
- [ ] WebGL build process documented
- [ ] Verification checklist detailed
- [ ] Troubleshooting covers common issues
- [ ] Release notes template provided

---

### Test 6.5: Screenshots Added

**Test Steps**:
1. Open `docs/screenshots/` directory
2. Check for:
   - Main screen screenshot
   - Match detail screenshot
   - Error state screenshot (optional)

**Expected**:
- At least 2 representative screenshots
- Screenshots show the app in use
- Image quality is reasonable (≥ 1366x768)

**Pass Criteria**:
- [ ] `docs/screenshots/` directory exists
- [ ] At least 1 main screen screenshot
- [ ] At least 1 detail screen screenshot
- [ ] Screenshots are clear and representative
- [ ] File format is .png or .jpg

---

### Test 6.6: Release Notes Ready

**Test Steps**:
1. Check `docs/final_release_guide.md` for release notes template
2. Verify v1.0.0 section includes:
   - Features summary
   - Tech stack
   - Known limitations
   - Getting started
   - Credits

**Expected**:
- Release notes are complete and professional
- No placeholder text
- All sections filled

**Pass Criteria**:
- [ ] Release notes have title "v1.0.0"
- [ ] Features section populated
- [ ] Tech stack listed
- [ ] Known limitations documented
- [ ] Getting started instructions included
- [ ] Professional tone and formatting

---

## Test Results Summary

### Overall Test Execution

| Test Category | Tests | Passed | Failed | Status |
|---------------|-------|--------|--------|--------|
| Backend API | 6 | ___ / 6 | ___ | ☐ PASS ☐ FAIL |
| Main Screen | 7 | ___ / 7 | ___ | ☐ PASS ☐ FAIL |
| Detail Screen | 7 | ___ / 7 | ___ | ☐ PASS ☐ FAIL |
| Rate Limit | 4 | ___ / 4 | ___ | ☐ PASS ☐ FAIL |
| WebGL Build | 5 | ___ / 5 | ___ | ☐ PASS ☐ FAIL |
| Release | 6 | ___ / 6 | ___ | ☐ PASS ☐ FAIL |
| **TOTAL** | **35** | **___ / 35** | **___** | **☐ PASS ☐ FAIL** |

### Sign-Off

**QA Tester Name**: _____________________

**Date**: _____________________

**Backend URL Tested**: _____________________

**WebGL URL Tested**: _____________________

**Result**:
- ☐ **APPROVED** - All tests passed, ready for production
- ☐ **APPROVED WITH NOTES** - Minor issues documented below
- ☐ **REJECTED** - Critical issues found, see below

### Critical Issues Found

(If any, document here)

```
Issue 1:
  - Test: [Test number]
  - Description: [What went wrong]
  - Impact: [How it affects users]
  - Fix: [How to resolve]
  - Status: ☐ Fixed ☐ Documented as Known Limitation

Issue 2:
  [etc.]
```

### Minor Issues / Observations

(Non-blocking issues, nice-to-haves for future)

```
- Observation 1: [Description]
- Observation 2: [Description]
```

---

## Test Execution Tips

### Running Tests Efficiently

1. **Batch Backend Tests**: Run all API tests in sequence (Tests 1.1-1.6)
2. **Play Mode Tests**: Run all Unity tests in one session (Tests 2.1-3.7)
3. **Error Tests**: Leave for end (tests that intentionally break things)
4. **WebGL Tests**: Use different browser tabs to avoid cache confusion

### Environment Notes

- **API Latency**: Response times may vary based on:
  - Network speed
  - API-Football rate limits
  - Backend hosting (free tier may be slow)
  - Browser cache state

- **Expected Variability**:
  - First load: 20 seconds (script parsing, shader compilation)
  - Subsequent loads: 5-10 seconds
  - API responses: 500ms - 2 seconds

### Debugging

Enable verbose logging:
1. In AppConfig.cs: Set `EnableVerboseLogs = true`
2. Restart app
3. Console will show detailed timing and error info

---

## Appendix: Quick Reference

### Pass Thresholds

- **Backend**: 6/6 tests must pass
- **Main Screen**: 7/7 tests must pass
- **Detail Screen**: 7/7 tests must pass
- **Rate Limit**: 4/4 tests must pass
- **WebGL**: 5/5 tests must pass
- **Release**: 6/6 tests must pass

### Go/No-Go Decision

**GO TO PRODUCTION** if:
- ✅ All 35 tests pass
- ✅ No critical issues
- ✅ All documentation complete
- ✅ Security verified (no API key exposed)
- ✅ Performance acceptable

**NO-GO** if:
- ❌ Any critical issue found
- ❌ API key exposed
- ❌ App crashes in main flows
- ❌ CORS misconfigured
- ❌ Documentation incomplete

---

**Version**: v1.0.0  
**Last Updated**: May 11, 2026  
**Next Review**: After each major feature addition
