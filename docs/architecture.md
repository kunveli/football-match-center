# Architecture

## Overview

Football Match Center App follows a client-server architecture designed for security, resilience, and WebGL compatibility.

1. Unity client renders UI and handles user interaction.
2. FastAPI backend acts as the single integration layer.
3. API-Football provider is called only by backend.
4. Cache system reduces external API pressure and rate-limit impact.

## Unity Client

Responsibilities:

- Render match center UI (bulletin, filters, details).
- Show live scores and match detail sections.
- Handle TR/EN localization in UI.
- Call backend endpoints only.

Security model:

- No API provider key is stored in Unity.
- Unity does not call API-Football directly.

## FastAPI Backend

Responsibilities:

- Expose stable REST endpoints for Unity.
- Read provider credentials from environment variables.
- Perform external API-Football requests.
- Normalize and return data for client consumption.

CORS:

- Configurable through CORS_ALLOW_ORIGINS.
- Local origins and production placeholder are supported.

## API-Football Provider

- Used as upstream live data source.
- Called only from backend service layer.
- Provider coverage may vary by league/match.

## Cache System

Cache layer is used to protect against provider instability and rate limits.

Typical behavior:

1. Try live provider data.
2. Use cache when applicable.
3. Return safe/fallback response patterns without exposing raw upstream details.

## Localization

- Central localization manager supports TR/EN.
- UI labels and state messages update at runtime.
- Architecture is ready for additional languages.

## WebGL Deployment Plan

1. Build Unity WebGL client.
2. Host WebGL output on static hosting or CDN.
3. Configure backend with HTTPS and proper CORS origins.
4. Set production BACKEND_BASE_URL for Unity profile.
5. Keep all provider keys in backend environment only.

## Deployment Notes

- Keep .env local/private on backend host.
- Do not commit secrets.
- Monitor backend logs and provider rate-limit behavior during production rollout.
