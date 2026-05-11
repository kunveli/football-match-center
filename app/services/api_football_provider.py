import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

DEFAULT_BASE = "https://v3.football.api-sports.io"
DEFAULT_HOST = "v3.football.api-sports.io"


def _env_text(name: str, default: str = "") -> str:
    return str(os.getenv(name, default) or "").strip()


def _base_url() -> str:
    return _env_text("API_FOOTBALL_BASE", DEFAULT_BASE).rstrip("/")


def _headers() -> Dict[str, str]:
    key = _env_text("API_FOOTBALL_KEY")
    host = _env_text("API_FOOTBALL_HOST", DEFAULT_HOST)
    headers = {
        "x-apisports-key": key,
        # Compatibility with projects that still run via RapidAPI gateway.
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": host,
    }
    return {k: v for k, v in headers.items() if v}


def _request(path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 20) -> Tuple[Optional[Dict[str, Any]], int]:
    url = f"{_base_url()}{path}"
    print(f"[API_FOOTBALL] GET {url} params={params}")
    try:
        response = requests.get(url, headers=_headers(), params=params or {}, timeout=timeout)
        status = response.status_code
        print(f"[API_FOOTBALL] response: HTTP {status}")
        if status == 429:
            print("[API_FOOTBALL] rate limit hit (429)")
        if status != 200:
            return None, status
        payload = response.json() if response.content else {}
        if not isinstance(payload, dict):
            return {}, 200
        errors = payload.get("errors")
        if errors:
            print(f"[API_FOOTBALL] API errors: {errors}")
        results_count = payload.get("results")
        if results_count is not None:
            print(f"[API_FOOTBALL] results count: {results_count}")
        return payload, 200
    except Exception as exc:
        print(f"[API_FOOTBALL] request failed: {exc}")
        return None, 0


def _extract_response_list(payload: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    response_obj = payload.get("response")
    if isinstance(response_obj, list):
        return [item for item in response_obj if isinstance(item, dict)]
    return []


def get_live_fixtures() -> Tuple[List[Dict[str, Any]], int]:
    payload, status = _request("/fixtures", params={"live": "all"}, timeout=20)
    return _extract_response_list(payload), status


def get_today_fixtures() -> Tuple[List[Dict[str, Any]], int]:
    today = datetime.now().strftime("%Y-%m-%d")
    payload, status = _request("/fixtures", params={"date": today}, timeout=20)
    return _extract_response_list(payload), status


def get_fixture_statistics(fixture_id: str) -> Tuple[List[Dict[str, Any]], int]:
    payload, status = _request("/fixtures/statistics", params={"fixture": str(fixture_id)}, timeout=10)
    return _extract_response_list(payload), status


def get_fixture_events(fixture_id: str) -> Tuple[List[Dict[str, Any]], int]:
    payload, status = _request("/fixtures/events", params={"fixture": str(fixture_id)}, timeout=10)
    return _extract_response_list(payload), status


def get_fixture_lineups(fixture_id: str) -> Tuple[List[Dict[str, Any]], int]:
    payload, status = _request("/fixtures/lineups", params={"fixture": str(fixture_id)}, timeout=10)
    return _extract_response_list(payload), status
