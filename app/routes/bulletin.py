from fastapi import APIRouter
from app.schemas.response import ApiResponse
from typing import List
from app.models.bulletin import BulletinMatch
import json
from pathlib import Path

router = APIRouter()

CACHE_FILE = "app/data/bulletin_cache.json"
SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "bulletin_seed.json"


def _is_seed_match(item):
    match_id = str(item.get("matchId") or item.get("id") or "").strip().lower()
    if match_id.startswith("seed-"):
        return True

    source = str(item.get("source") or "").strip().lower()
    return source.startswith("seed")


def is_valid_match(item, allow_seed=False):
    if not isinstance(item, dict):
        return False

    match_id = str(item.get("matchId") or item.get("id") or "").strip()
    home = str(item.get("home") or item.get("home_team") or "").strip()
    away = str(item.get("away") or item.get("away_team") or "").strip()

    if not match_id or not home or not away:
        return False

    if home.lower() == away.lower():
        return False

    if not allow_seed and _is_seed_match(item):
        return False

    return True


def _to_elapsed(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)

    text = str(value).strip()
    if not text:
        return None

    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None

    try:
        return int(digits)
    except Exception:
        return None


def _to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _infer_coverage(item):
    status = str(item.get("status") or "").strip().upper()
    elapsed = _to_elapsed(item.get("elapsed"))

    if status in {"NS", "TBD", "POSTPONED"}:
        return False, False, False
    if status in {"LIVE", "FT"}:
        return True, True, True
    if elapsed is not None and elapsed > 0:
        return True, True, True
    return False, False, False


def _read_payload(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
            if isinstance(payload, list):
                return payload, None
            if isinstance(payload, dict):
                if isinstance(payload.get("data"), list):
                    return payload["data"], str(payload.get("origin") or payload.get("source") or "")
                if isinstance(payload.get("matches"), list):
                    return payload["matches"], str(payload.get("origin") or payload.get("source") or "")
            return [], None
    except Exception:
        return [], None


def _source_from_origin(origin, fallback="LIVE_CACHE"):
    text = str(origin or "").strip().lower()
    if text.startswith("seed"):
        return "SEED_FALLBACK"
    if text in {"upstream", "real_api", "cache", "live_cache"}:
        return "REAL_API_CACHE"
    return fallback


def _load_seed_fallback_matches():
    if not SEED_FILE.exists():
        return []

    seed_matches, _origin = _read_payload(str(SEED_FILE))
    return [item for item in seed_matches if is_valid_match(item, allow_seed=True)]

@router.get("/today", response_model=ApiResponse[List[BulletinMatch]])
async def get_today_bulletin():
    try:
        print("[REAL] bulletin route called")

        raw_matches, origin = _read_payload(CACHE_FILE)
        valid_live_matches = [item for item in raw_matches if is_valid_match(item, allow_seed=False)]

        source = _source_from_origin(origin, fallback="LIVE_CACHE")
        if valid_live_matches:
            print(f"[REAL] serving live/cache bulletin: {len(valid_live_matches)} matches")
            if SEED_FILE.exists():
                print("[REAL] seed fallback blocked because live cache exists")
            raw_matches = valid_live_matches
        else:
            seed_matches = _load_seed_fallback_matches()
            if seed_matches:
                raw_matches = seed_matches
                source = "SEED_FALLBACK"
                print("[REAL] seed fallback used because cache missing/empty")
            else:
                raw_matches = []
                source = "LIVE_CACHE"

        data = []
        for i, item in enumerate(raw_matches or [], start=1):
            inferred_has_stats, inferred_has_events, inferred_has_lineups = _infer_coverage(item)
            data.append(BulletinMatch(
                matchId=str(item.get("matchId") or item.get("id") or i),
                league=str(item.get("league") or ""),
                leagueId=(str(item.get("leagueId")) if item.get("leagueId") is not None else None),
                time=str(item.get("time") or item.get("date") or ""),
                home=str(item.get("home") or item.get("home_team") or ""),
                away=str(item.get("away") or item.get("away_team") or ""),
                homeId=(str(item.get("homeId")) if item.get("homeId") is not None else None),
                awayId=(str(item.get("awayId")) if item.get("awayId") is not None else None),
                homeScore=item.get("homeScore") if isinstance(item.get("homeScore"), int) else _to_elapsed(item.get("homeScore")),
                awayScore=item.get("awayScore") if isinstance(item.get("awayScore"), int) else _to_elapsed(item.get("awayScore")),
                score=(str(item.get("score")) if item.get("score") is not None else None),
                status=(str(item.get("status")) if item.get("status") is not None else None),
                elapsed=_to_elapsed(item.get("elapsed")),
                hasStats=_to_bool(item.get("hasStats"), default=inferred_has_stats),
                hasEvents=_to_bool(item.get("hasEvents"), default=inferred_has_events),
                hasLineups=_to_bool(item.get("hasLineups"), default=inferred_has_lineups),
            ))

        print(f"[REAL] matches count: {len(data)}")
        return ApiResponse(success=True, data=data, error=None, source=source)
    except Exception as e:
        print(f"[REAL] exception: {e}")
        return ApiResponse(success=False, data=[], error=str(e), source="ERROR")