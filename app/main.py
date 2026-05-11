import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level above app/)
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.bulletin import router as bulletin_router
from app.routes import match, h2h
from app.services.live_fetcher import start_fetcher

app = FastAPI(title="Unity Stats API", version="1.0.0")

def _read_cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost,http://127.0.0.1,http://localhost:8080,http://127.0.0.1:8080,https://YOUR_FRONTEND_DOMAIN_HERE",
    )
    values = [item.strip() for item in (raw or "").split(",") if item.strip()]
    return values or ["http://localhost", "http://127.0.0.1"]


# CORS for Unity/WebGL (configurable and restrictive by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_read_cors_origins(),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bulletin_router, prefix="/api/bulletin", tags=["bulletin"])
app.include_router(match, prefix="/api", tags=["match"])
app.include_router(h2h, prefix="/api", tags=["h2h"])


@app.on_event("startup")
async def startup_event():
    try:
        api_key = os.getenv("API_FOOTBALL_KEY", "").strip()
        api_base = os.getenv("API_FOOTBALL_BASE", "https://v3.football.api-sports.io").strip()
        api_host = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io").strip()

        if api_key:
            masked = api_key[:6] + "****" + api_key[-4:]
            print(f"[PROVIDER] API-Football connected: key={masked} base={api_base} host={api_host}")
        else:
            print("[PROVIDER] WARNING: API_FOOTBALL_KEY not set — live data will not be fetched")

        start_fetcher()
        print("[STARTUP] fetcher started")
    except Exception as e:
        print("[STARTUP ERROR]", e)

@app.get("/")
async def root():
    return {"message": "Unity Stats API is running"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment platforms (Render, Railway, Kubernetes).
    Returns 200 OK when service is operational.
    """
    return {"status": "ok"}