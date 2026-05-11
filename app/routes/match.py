import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter
from app.schemas.response import ApiResponse
from app.models.match import MatchDetail
from app.services.api_football_provider import get_fixture_statistics, get_fixture_events, get_fixture_lineups

_CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "bulletin_cache.json"


def _get_bulletin_match_by_id(match_id: str) -> Optional[Dict[str, Any]]:
    """Read match from local bulletin cache by matchId."""
    try:
        # Prefer in-memory cache from rapid_service when available.
        from app import rapid_service

        memory_cache = getattr(rapid_service, "_BULLETIN_CACHE", None)
        if isinstance(memory_cache, dict):
            memory_items = memory_cache.get("data") or memory_cache.get("matches") or []
            for item in memory_items:
                if isinstance(item, dict) and str(item.get("matchId") or item.get("id") or "") == str(match_id):
                    return item

        if not _CACHE_FILE.exists():
            return None
        with _CACHE_FILE.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        items = payload if isinstance(payload, list) else payload.get("data") or payload.get("matches") or []
        for item in items:
            if isinstance(item, dict) and str(item.get("matchId") or item.get("id") or "") == str(match_id):
                return item
    except Exception:
        pass
    return None

router = APIRouter()
ENABLE_DEMO_DATA = os.getenv("ENABLE_DEMO_DATA", "").strip().lower() in {"1", "true", "yes", "on"}
MATCH_STATS_PROVIDER_URL = os.getenv("MATCH_STATS_PROVIDER_URL", "").strip()


def _make_stats_unavailable(match_id: str, source: str, error: str) -> ApiResponse[Dict[str, Any]]:
    """Return a success=True wrapper with stats=null payload so Unity can always read .data."""
    return ApiResponse(
        success=True,
        data={
            "success": False,
            "matchId": str(match_id),
            "source": source,
            "error": error,
            "stats": None,
        },
        error=None,
        source=source,
    )


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _normalize_stat_key(value: str) -> str:
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def _normalize_event_type(value: str) -> str:
    t = str(value or "").strip().lower()
    if t == "goal":
        return "Goal"
    if t == "card":
        return "Card"
    if t == "subst":
        return "subst"
    if t == "var":
        return "Var"
    return str(value or "")


def _fetch_provider_stats(match_id: str) -> ApiResponse[Dict[str, Any]]:
    if not MATCH_STATS_PROVIDER_URL and not os.getenv("API_FOOTBALL_KEY", "").strip():
        return _make_stats_unavailable(match_id, "API_FOOTBALL", "Stats provider endpoint not configured")

    try:
        stats_rows, status_code = get_fixture_statistics(str(match_id))
        if status_code == 429:
            print(f"[API_FOOTBALL] stats unavailable for fixture: {match_id}")
            return _make_stats_unavailable(match_id, "API_FOOTBALL", "Rate limited while fetching live statistics")
        if status_code != 200:
            print(f"[API_FOOTBALL] stats unavailable for fixture: {match_id}")
            return _make_stats_unavailable(match_id, "API_FOOTBALL", f"Provider returned HTTP {status_code}")

        if not isinstance(stats_rows, list) or len(stats_rows) < 2:
            print(f"[API_FOOTBALL] stats unavailable for fixture: {match_id}")
            return _make_stats_unavailable(match_id, "API_FOOTBALL", "Live statistics are not available from the current provider")

        def _stat_map(team_stats: Dict[str, Any]) -> Dict[str, Any]:
            mapped = {}
            for row in team_stats.get("statistics", []) or []:
                if not isinstance(row, dict):
                    continue
                t = _normalize_stat_key(str(row.get("type") or ""))
                if t:
                    mapped[t] = row.get("value")
            return mapped

        def _pick_stat(values: Dict[str, Any], *keys: str) -> Any:
            for key in keys:
                normalized_key = _normalize_stat_key(key)
                if normalized_key in values:
                    return values[normalized_key]
            return None

        def _to_display(value: Any) -> Optional[str]:
            if value is None:
                return None
            text = str(value).strip()
            return text if text else None

        home_row = _safe_dict(stats_rows[0])
        away_row = _safe_dict(stats_rows[1])
        home_stats = _stat_map(home_row)
        away_stats = _stat_map(away_row)

        normalized = {
            "home": {
                "possession": _to_display(_pick_stat(home_stats, "ball possession")),
                "shots": _to_display(_pick_stat(home_stats, "total shots")),
                "shotsOnTarget": _to_display(_pick_stat(home_stats, "shots on goal", "shots on target")),
                "corners": _to_display(_pick_stat(home_stats, "corner kicks", "corners")),
                "yellowCards": _to_display(_pick_stat(home_stats, "yellow cards")),
                "redCards": _to_display(_pick_stat(home_stats, "red cards")),
                "fouls": _to_display(_pick_stat(home_stats, "fouls", "fouls committed")),
                "offsides": _to_display(_pick_stat(home_stats, "offsides", "offsides")),
                "goalkeeperSaves": _to_display(_pick_stat(home_stats, "goalkeeper saves")),
                "passes": _to_display(_pick_stat(home_stats, "total passes", "passes")),
                "passAccuracy": _to_display(_pick_stat(home_stats, "passes accurate", "passes %", "passes accuracy %", "pass accuracy")),
            },
            "away": {
                "possession": _to_display(_pick_stat(away_stats, "ball possession")),
                "shots": _to_display(_pick_stat(away_stats, "total shots")),
                "shotsOnTarget": _to_display(_pick_stat(away_stats, "shots on goal", "shots on target")),
                "corners": _to_display(_pick_stat(away_stats, "corner kicks", "corners")),
                "yellowCards": _to_display(_pick_stat(away_stats, "yellow cards")),
                "redCards": _to_display(_pick_stat(away_stats, "red cards")),
                "fouls": _to_display(_pick_stat(away_stats, "fouls", "fouls committed")),
                "offsides": _to_display(_pick_stat(away_stats, "offsides", "offsides")),
                "goalkeeperSaves": _to_display(_pick_stat(away_stats, "goalkeeper saves")),
                "passes": _to_display(_pick_stat(away_stats, "total passes", "passes")),
                "passAccuracy": _to_display(_pick_stat(away_stats, "passes accurate", "passes %", "passes accuracy %", "pass accuracy")),
            },
        }

        if all(v is None for v in normalized["home"].values()) and all(v is None for v in normalized["away"].values()):
            print(f"[API_FOOTBALL] stats unavailable for fixture: {match_id}")
            return _make_stats_unavailable(match_id, "API_FOOTBALL", "Live statistics are not available from the current provider")

        print(f"[API_FOOTBALL] stats loaded for fixture: {match_id}")
        return ApiResponse(
            success=True,
            data={
                "success": True,
                "matchId": str(match_id),
                "source": "API_FOOTBALL",
                "error": None,
                "stats": normalized,
            },
            error=None,
            source="API_FOOTBALL",
        )
    except Exception as e:
        print(f"[API_FOOTBALL] stats unavailable for fixture: {match_id}")
        return _make_stats_unavailable(match_id, "API_FOOTBALL", f"Stats fetch failed: {str(e)}")

@router.get("/match/{match_id}", response_model=ApiResponse[MatchDetail])
async def get_match_detail(match_id: str):
    try:
        requested_match_id = str(match_id)
        print(f"[REAL] detail request: {requested_match_id}")

        match_data = _get_bulletin_match_by_id(requested_match_id)
        if match_data is not None:
            resolved_match_id = str(match_data.get("matchId") or requested_match_id)
            print(f"[REAL] detail match found: matchId={resolved_match_id}")
            return ApiResponse(
                success=False,
                data=None,
                error="Bu mac icin ayrintili istatistikler henuz alinamadi.",
                source="NO_REAL_DETAIL",
            )

        if ENABLE_DEMO_DATA:
            print("[REAL] detail demo mode ignored to prevent fake stats")

        print("[REAL] detail fallback blocked")
        return ApiResponse(
            success=False,
            data=None,
            error="Match detail not found for the given matchId",
            source="NO_REAL_DATA",
        )
    except Exception as e:
        print(f"[REAL] detail exception: {e}")
        return ApiResponse.error_response(str(e))


@router.get("/match/{match_id}/stats", response_model=ApiResponse[Dict[str, Any]])
async def get_match_stats(match_id: str):
    try:
        requested_match_id = str(match_id)
        print(f"[REAL] stats request: {requested_match_id}")
        return _fetch_provider_stats(requested_match_id)
    except Exception as e:
        print(f"[REAL] stats exception: {e}")
        return _make_stats_unavailable(str(match_id), "UNAVAILABLE", str(e))


@router.get("/match/{match_id}/events", response_model=ApiResponse[Dict[str, Any]])
async def get_match_events(match_id: str):
    try:
        fixture_id = str(match_id)
        print(f"[REAL] events request: {fixture_id}")
        rows, status_code = get_fixture_events(fixture_id)

        if status_code == 429:
            return ApiResponse(success=True, data={"success": False, "matchId": fixture_id, "source": "API_FOOTBALL", "error": "Rate limited", "events": []}, error=None, source="API_FOOTBALL")
        if status_code != 200:
            return ApiResponse(success=True, data={"success": False, "matchId": fixture_id, "source": "API_FOOTBALL", "error": f"HTTP {status_code}", "events": []}, error=None, source="API_FOOTBALL")

        events = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            time_obj = row.get("time") or {}
            player_obj = row.get("player") or {}
            assist_obj = row.get("assist") or {}
            team_obj = row.get("team") or {}
            events.append({
                "time": time_obj.get("elapsed") if isinstance(time_obj, dict) else None,
                "extra": time_obj.get("extra") if isinstance(time_obj, dict) else None,
                "team": team_obj.get("name") if isinstance(team_obj, dict) else str(team_obj or ""),
                "player": player_obj.get("name") if isinstance(player_obj, dict) else str(player_obj or ""),
                "assist": assist_obj.get("name") if isinstance(assist_obj, dict) else None,
                "type": _normalize_event_type(str(row.get("type") or "")),
                "detail": str(row.get("detail") or ""),
            })

        print(f"[REAL] events loaded: {len(events)} events for fixture {fixture_id}")
        return ApiResponse(
            success=True,
            data={"success": True, "matchId": fixture_id, "source": "API_FOOTBALL", "error": None, "events": events},
            error=None,
            source="API_FOOTBALL",
        )
    except Exception as e:
        print(f"[REAL] events exception: {e}")
        return ApiResponse(success=True, data={"success": False, "matchId": str(match_id), "source": "UNAVAILABLE", "error": str(e), "events": []}, error=None, source="UNAVAILABLE")


@router.get("/match/{match_id}/lineups", response_model=ApiResponse[Dict[str, Any]])
async def get_match_lineups(match_id: str):
    try:
        fixture_id = str(match_id)
        print(f"[REAL] lineups request: {fixture_id}")
        rows, status_code = get_fixture_lineups(fixture_id)

        if status_code == 429:
            return ApiResponse(success=True, data={"success": False, "matchId": fixture_id, "source": "API_FOOTBALL", "error": "Rate limited", "lineups": []}, error=None, source="API_FOOTBALL")
        if status_code != 200:
            return ApiResponse(success=True, data={"success": False, "matchId": fixture_id, "source": "API_FOOTBALL", "error": f"HTTP {status_code}", "lineups": []}, error=None, source="API_FOOTBALL")

        lineups = []
        for team_block in rows:
            if not isinstance(team_block, dict):
                continue
            team_obj = team_block.get("team") or {}
            coach_obj = team_block.get("coach") or {}
            formation = str(team_block.get("formation") or "")
            start_xi = []
            for entry in (team_block.get("startXI") or []):
                if not isinstance(entry, dict):
                    continue
                p = entry.get("player") or {}
                if isinstance(p, dict):
                    start_xi.append({"id": p.get("id"), "name": p.get("name"), "number": p.get("number"), "pos": p.get("pos"), "grid": p.get("grid")})
            subs = []
            for entry in (team_block.get("substitutes") or []):
                if not isinstance(entry, dict):
                    continue
                p = entry.get("player") or {}
                if isinstance(p, dict):
                    subs.append({"id": p.get("id"), "name": p.get("name"), "number": p.get("number"), "pos": p.get("pos"), "grid": p.get("grid")})
            lineups.append({
                "team": team_obj.get("name") if isinstance(team_obj, dict) else str(team_obj or ""),
                "formation": formation,
                "coach": coach_obj.get("name") if isinstance(coach_obj, dict) else str(coach_obj or ""),
                "startXI": start_xi,
                "substitutes": subs,
            })

        print(f"[REAL] lineups loaded: {len(lineups)} teams for fixture {fixture_id}")
        return ApiResponse(
            success=True,
            data={"success": True, "matchId": fixture_id, "source": "API_FOOTBALL", "error": None, "lineups": lineups},
            error=None,
            source="API_FOOTBALL",
        )
    except Exception as e:
        print(f"[REAL] lineups exception: {e}")
        return ApiResponse(success=True, data={"success": False, "matchId": str(match_id), "source": "UNAVAILABLE", "error": str(e), "lineups": []}, error=None, source="UNAVAILABLE")


@router.get("/match/{match_id}/odds", response_model=ApiResponse[Dict[str, Any]])
async def get_match_odds(match_id: str):
    """Odds provider not yet configured. Returns unavailable placeholder."""
    fixture_id = str(match_id)
    print(f"[REAL] odds request: {fixture_id} — provider not configured")
    return ApiResponse(
        success=True,
        data={"success": False, "matchId": fixture_id, "source": "UNAVAILABLE", "error": "Odds provider not configured", "odds": None},
        error=None,
        source="UNAVAILABLE",
    )