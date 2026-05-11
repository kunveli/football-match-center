# Football Match Center App

Modern football match center project built for live data consumption, clean UI delivery, and production-ready client-server architecture.

Unity handles presentation and interaction, while FastAPI securely handles provider communication and caching.

## Screenshots

Place screenshots under docs/screenshots/ and update links:

- Main Match Center: docs/screenshots/main-match-center.png
- Match Detail: docs/screenshots/match-detail.png
- Settings / Localization: docs/screenshots/settings-localization.png
- WebGL Build: docs/screenshots/webgl-build.png

## Features

- Live fixtures
- Live scores
- League filters
- Match details
- Stats
- Events timeline
- Lineups
- Odds placeholder
- TR/EN localization
- WebGL-ready architecture

## Tech Stack

- Unity 6
- C#
- UI Toolkit
- FastAPI
- Python
- API-Football

## Architecture

- Unity client never stores API key.
- FastAPI backend handles external API calls.
- Cache layer protects rate limits.

High-level flow:

1. Unity client requests backend endpoints.
2. FastAPI backend validates and resolves data.
3. Backend fetches API-Football provider data.
4. Cache/fallback layers reduce provider pressure and improve stability.
5. Backend returns normalized payloads to Unity.

For details, see docs/architecture.md.

## Setup

1. Create local environment file:

```bash
copy .env.example .env
```

2. Configure backend environment variables in .env (do not commit).

3. Install requirements:

```bash
pip install -r requirements.txt
```

4. Run backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

5. Start Unity project and run Play Mode.

## API Endpoints

- /api/bulletin/today
- /api/match/{id}
- /api/match/{id}/stats
- /api/match/{id}/events
- /api/match/{id}/lineups
- /api/match/{id}/odds

## Environment Variables

- API_FOOTBALL_KEY: provider key (backend only)
- API_FOOTBALL_BASE: provider base URL
- API_FOOTBALL_HOST: provider host
- CORS_ALLOW_ORIGINS: comma-separated allowed origins

Unity-side profile examples are available in:

- ../İstatistik/BuildProfiles/Development.env.example
- ../İstatistik/BuildProfiles/Production.env.example

## Known Limitations

- Stats/events/lineups depend on provider coverage.
- Odds provider is not connected yet.

## Future Roadmap

- Mobile build
- Authentication
- Favorites sync
- Push notifications
- Advanced analytics