import os
from fastapi import APIRouter
from app.schemas.response import ApiResponse
from app.services.mock_data import get_mock_h2h
from app.models.h2h import H2HSummary

router = APIRouter()
ENABLE_DEMO_DATA = os.getenv("ENABLE_DEMO_DATA", "").strip().lower() in {"1", "true", "yes", "on"}

@router.get("/h2h/{home_team}/{away_team}", response_model=ApiResponse[H2HSummary])
async def get_h2h_summary(home_team: str, away_team: str):
    try:
        print(f"[REAL] h2h request: {home_team} vs {away_team}")

        if ENABLE_DEMO_DATA:
            print("[REAL] h2h demo mode enabled")
            data = get_mock_h2h(home_team, away_team)
            return ApiResponse(success=True, data=data, error=None, source="DEMO")

        print("[REAL] h2h fallback blocked")
        return ApiResponse(
            success=False,
            data=None,
            error="Real h2h payload unavailable",
            source="NO_REAL_DATA",
        )
    except Exception as e:
        print(f"[REAL] h2h exception: {e}")
        return ApiResponse.error_response(str(e))