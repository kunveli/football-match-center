import json
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path

import requests

API_KEY = os.getenv("RAPIDAPI_KEY", "").strip()
API_HOST = os.getenv("RAPIDAPI_HOST", "free-api-live-football-data.p.rapidapi.com").strip()
BULLETIN_CACHE_TTL_SECONDS = 300
BULLETIN_REQUEST_COOLDOWN_SECONDS = 10
BULLETIN_BACKOFF_AFTER_429_SECONDS = 60

_BULLETIN_DISK_CACHE_PATH = Path(__file__).resolve().parent / "data" / "bulletin_cache.json"
_BULLETIN_SEED_PATH = Path(__file__).resolve().parent / "data" / "bulletin_seed.json"

_LEAGUE_LOOKUP = {}
_LEAGUE_LOOKUP_UPDATED_AT = None
_BULLETIN_CACHE = None
_BULLETIN_DISK_CACHE = None
_RATE_LIMITED_UNTIL = None
_BULLETIN_FETCH_LOCK = threading.Lock()
_LAST_BULLETIN_REQUEST_AT = None
_LAST_BULLETIN_SOURCE = "REAL_API"
_LAST_BULLETIN_ERROR = None


def _request_headers():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    return {k: v for k, v in headers.items() if v}


def _clone_matches(matches):
    return [dict(item) for item in (matches or [])]


def _serialize_cache_entry(cache_entry):
    if not isinstance(cache_entry, dict):
        return None

    fetched_at = cache_entry.get("fetched_at")
    if fetched_at is None:
        return None

    expires_at = cache_entry.get("expires_at")
    return {
        "data": _clone_matches(cache_entry.get("data")),
        "fetched_at": fetched_at.isoformat() if isinstance(fetched_at, datetime) else str(fetched_at),
        "expires_at": (
            expires_at.isoformat()
            if isinstance(expires_at, datetime)
            else (str(expires_at) if expires_at is not None else None)
        ),
        "origin": _pick_text(cache_entry.get("origin")) or "upstream",
    }


def _hydrate_cache_entry(payload):
    if not isinstance(payload, dict):
        return None

    fetched_at = _parse_time(payload.get("fetched_at"))
    if fetched_at is None:
        return None

    return {
        "data": _clone_matches(payload.get("data")),
        "fetched_at": fetched_at,
        "expires_at": _parse_time(payload.get("expires_at")),
        "origin": _pick_text(payload.get("origin")) or "upstream",
    }


def _get_cache_entry(cache_store=None):
    if cache_store is None:
        cache_store = _BULLETIN_CACHE

    if not isinstance(cache_store, dict):
        return None

    fetched_at = cache_store.get("fetched_at")
    expires_at = cache_store.get("expires_at")
    if fetched_at is None:
        return None

    return {
        "data": _clone_matches(cache_store.get("data")),
        "fetched_at": fetched_at,
        "expires_at": expires_at,
        "origin": _pick_text(cache_store.get("origin")) or "upstream",
    }


def _get_disk_cache_entry():
    return _get_cache_entry(_BULLETIN_DISK_CACHE)


def _is_seed_cache_entry(cache_entry):
    return isinstance(cache_entry, dict) and _pick_text(cache_entry.get("origin")).lower() == "seed"


def _get_cache_result_source(cache_entry, storage="memory", after_rate_limit=False):
    if _is_seed_cache_entry(cache_entry):
        return "SEED_CACHE_AFTER_RATE_LIMIT" if after_rate_limit else "SEED_CACHE"

    if storage == "disk":
        return "DISK_CACHE_AFTER_RATE_LIMIT" if after_rate_limit else "DISK_CACHE_HIT"

    return "CACHE_AFTER_RATE_LIMIT" if after_rate_limit else "CACHE_HIT"


def _log_cache_usage(cache_entry, storage="memory", after_rate_limit=False):
    if _is_seed_cache_entry(cache_entry):
        if after_rate_limit:
            print("[REAL] using seed cache after 429")
        else:
            print("[REAL] serving from seed cache")
        return

    if storage == "disk":
        if after_rate_limit:
            print("[REAL] using disk cache after 429")
        else:
            print("[REAL] serving from disk cache")
        return

    if after_rate_limit:
        print("[REAL] using cache after 429")
    else:
        print("[REAL] serving from cache")


def _build_seed_cache_entry(matches):
    safe_matches = _clone_matches(matches)
    if not safe_matches:
        return None

    now = datetime.now()
    return {
        "data": safe_matches,
        "fetched_at": now,
        "expires_at": now - timedelta(seconds=1),
        "origin": "seed",
    }


def _load_bulletin_disk_cache():
    global _BULLETIN_DISK_CACHE

    try:
        if not _BULLETIN_DISK_CACHE_PATH.exists():
            _BULLETIN_DISK_CACHE = None
            return None

        with _BULLETIN_DISK_CACHE_PATH.open("r", encoding="utf-8") as cache_file:
            payload = json.load(cache_file)

        cache_entry = _hydrate_cache_entry(payload)
        if cache_entry is None or not cache_entry.get("data"):
            _BULLETIN_DISK_CACHE = None
            return None

        _BULLETIN_DISK_CACHE = cache_entry
        print("[REAL] disk cache loaded")
        return cache_entry
    except Exception as e:
        print("[REAL] disk cache load failed:", str(e))
        _BULLETIN_DISK_CACHE = None
        return None


def _load_bulletin_seed_cache():
    global _BULLETIN_DISK_CACHE
    global _BULLETIN_CACHE

    if _get_cache_entry() is not None or _get_disk_cache_entry() is not None:
        return _get_disk_cache_entry()

    try:
        if not _BULLETIN_SEED_PATH.exists():
            return None

        with _BULLETIN_SEED_PATH.open("r", encoding="utf-8") as seed_file:
            payload = json.load(seed_file)

        if not isinstance(payload, dict) or payload.get("success") is False:
            return None

        cache_entry = _build_seed_cache_entry(payload.get("data"))
        if cache_entry is None:
            return None

        # Keep seed fallback in memory only; never overwrite live disk cache with seed/demo.
        _BULLETIN_CACHE = cache_entry
        _BULLETIN_DISK_CACHE = _get_disk_cache_entry()
        print("[REAL] seed cache loaded (memory only)")
        return _get_cache_entry()
    except Exception as e:
        print("[REAL] seed cache load failed:", str(e))
        return None


def _write_bulletin_disk_cache(cache_entry):
    global _BULLETIN_DISK_CACHE

    payload = _serialize_cache_entry(cache_entry)
    if payload is None:
        return

    try:
        _BULLETIN_DISK_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _BULLETIN_DISK_CACHE_PATH.open("w", encoding="utf-8") as cache_file:
            json.dump(payload, cache_file, ensure_ascii=False)
        _BULLETIN_DISK_CACHE = _hydrate_cache_entry(payload)
        print("[REAL] disk cache updated")
    except Exception as e:
        print("[REAL] disk cache write failed:", str(e))


def _promote_disk_cache_to_memory():
    global _BULLETIN_CACHE

    disk_entry = _get_disk_cache_entry()
    if disk_entry is None:
        return None

    _BULLETIN_CACHE = {
        "data": _clone_matches(disk_entry.get("data")),
        "fetched_at": disk_entry.get("fetched_at"),
        "expires_at": disk_entry.get("expires_at"),
        "origin": _pick_text(disk_entry.get("origin")) or "upstream",
    }
    return _clone_matches(_BULLETIN_CACHE.get("data"))


def _is_cache_stale():
    cache_entry = _get_cache_entry()
    if cache_entry is None:
        return False

    expires_at = cache_entry.get("expires_at")
    return expires_at is not None and datetime.now() > expires_at


def _get_cached_bulletin_matches(allow_stale=False, log_state=True):
    cache_entry = _get_cache_entry()
    if cache_entry is None:
        return None

    expires_at = cache_entry.get("expires_at")
    if expires_at and datetime.now() <= expires_at:
        if log_state:
            print("[REAL] cache hit")
        return cache_entry["data"]

    if log_state:
        print("[REAL] cache stale")
    if allow_stale:
        return cache_entry["data"]
    return None


def _get_disk_cached_bulletin_matches(allow_stale=False, log_state=True):
    cache_entry = _get_disk_cache_entry()
    if cache_entry is None:
        return None

    expires_at = cache_entry.get("expires_at")
    if expires_at and datetime.now() <= expires_at:
        return cache_entry["data"]

    if log_state:
        print("[REAL] disk cache stale")
    if allow_stale:
        return cache_entry["data"]
    return None


def _store_bulletin_cache(matches):
    global _BULLETIN_CACHE

    safe_matches = _clone_matches(matches)
    if not safe_matches:
        return

    fetched_at = datetime.now()
    cache_entry = {
        "data": safe_matches,
        "fetched_at": fetched_at,
        "expires_at": fetched_at + timedelta(seconds=BULLETIN_CACHE_TTL_SECONDS),
        "origin": "upstream",
    }
    _BULLETIN_CACHE = cache_entry
    _write_bulletin_disk_cache(cache_entry)
    print("[REAL] cache updated from upstream")
    print("[REAL] cache updated")


def _set_bulletin_result(source, error, matches=None, from_cache=False):
    global _LAST_BULLETIN_SOURCE
    global _LAST_BULLETIN_ERROR

    safe_matches = _clone_matches(matches)
    if from_cache and safe_matches:
        print("[REAL] using cached bulletin data")
    print("[REAL] mapped matches:", len(safe_matches))

    _LAST_BULLETIN_SOURCE = source
    _LAST_BULLETIN_ERROR = error
    return safe_matches


def get_bulletin_fetch_meta():
    return _LAST_BULLETIN_SOURCE, _LAST_BULLETIN_ERROR


def _find_match_in_matches(matches, match_id):
    target_match_id = _pick_text(match_id)
    if not target_match_id:
        return None

    for item in matches or []:
        if not isinstance(item, dict):
            continue

        candidate_id = _pick_text(item.get("matchId"), item.get("id"))
        if candidate_id == target_match_id:
            return dict(item)

    return None


def get_bulletin_match_by_id(match_id):
    memory_entry = _get_cache_entry()
    memory_match = _find_match_in_matches(memory_entry.get("data") if memory_entry else [], match_id)
    if memory_match is not None:
        return memory_match, _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=False)

    disk_entry = _get_disk_cache_entry() or _load_bulletin_disk_cache() or _load_bulletin_seed_cache()
    disk_match = _find_match_in_matches(disk_entry.get("data") if disk_entry else [], match_id)
    if disk_match is not None:
        _promote_disk_cache_to_memory()
        return disk_match, _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=False)

    return None, None


def _is_backoff_active(now=None):
    if now is None:
        now = datetime.now()
    return _RATE_LIMITED_UNTIL is not None and now < _RATE_LIMITED_UNTIL


def _is_cooldown_active(now=None):
    if now is None:
        now = datetime.now()
    return _LAST_BULLETIN_REQUEST_AT is not None and (now - _LAST_BULLETIN_REQUEST_AT).total_seconds() < BULLETIN_REQUEST_COOLDOWN_SECONDS


def _load_league_lookup(headers):
    global _LEAGUE_LOOKUP
    global _LEAGUE_LOOKUP_UPDATED_AT

    now = datetime.now()
    if _LEAGUE_LOOKUP and _LEAGUE_LOOKUP_UPDATED_AT and (now - _LEAGUE_LOOKUP_UPDATED_AT).total_seconds() < 6 * 3600:
        return _LEAGUE_LOOKUP

    try:
        resp = requests.get(
            "https://free-api-live-football-data.p.rapidapi.com/football-get-all-leagues",
            headers=headers,
            timeout=20,
        )
        if resp.status_code != 200:
            return _LEAGUE_LOOKUP

        body = resp.json()
        response_obj = body.get("response", {}) if isinstance(body, dict) else {}
        leagues = response_obj.get("leagues", []) if isinstance(response_obj, dict) else []
        if not isinstance(leagues, list):
            return _LEAGUE_LOOKUP

        lookup = {}
        for league in leagues:
            if not isinstance(league, dict):
                continue
            league_id = _pick_text(league.get("id"))
            league_name = _pick_text(league.get("localizedName"), league.get("name"))
            if league_id and league_name:
                lookup[league_id] = league_name

        if lookup:
            _LEAGUE_LOOKUP = lookup
            _LEAGUE_LOOKUP_UPDATED_AT = now
    except Exception:
        return _LEAGUE_LOOKUP

    return _LEAGUE_LOOKUP


def _pick_text(*values):
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _pick_team_name(team_data, *fallback_values):
    values = []
    if isinstance(team_data, dict):
        values.extend(
            [
                team_data.get("name"),
                team_data.get("longName"),
                team_data.get("shortName"),
                team_data.get("localizedName"),
            ]
        )

    for value in fallback_values:
        if isinstance(value, dict):
            continue
        values.append(value)

    return _pick_text(*values)


def _parse_time(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        ts_value = float(value)
        if ts_value > 10_000_000_000:
            ts_value /= 1000
        try:
            return datetime.fromtimestamp(ts_value)
        except Exception:
            return None

    text = str(value).strip()
    if not text:
        return None

    formats = [
        "%d.%m.%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    try:
        normalized = text.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo:
            return parsed.astimezone().replace(tzinfo=None)
        return parsed
    except Exception:
        return None


def _format_match_time(item):
    date_obj = _parse_time(item.get("time")) or _parse_time(item.get("timeTS"))
    if not date_obj:
        return ""

    now = datetime.now()
    if date_obj.date() == now.date():
        return date_obj.strftime("%H:%M")
    return date_obj.strftime("%d.%m.%Y %H:%M")


def _get_league_name(item, league_lookup):
    league = _safe_dict(item.get("league"))
    fixture = _safe_dict(item.get("fixture"))
    fixture_league = _safe_dict(fixture.get("league"))
    competition = _safe_dict(item.get("competition"))
    tournament = _safe_dict(item.get("tournament"))
    country = _safe_dict(league.get("country"))

    def _clean(text):
        value = _pick_text(text)
        if not value:
            return ""
        lowered = value.lower()
        if lowered in {"other", "unknown", "unknown league", "league"}:
            return ""
        if value.isdigit():
            return ""
        return value

    league_id = _pick_text(item.get("leagueId"), league.get("id"), fixture_league.get("id"))

    # 1) fixture.league.name
    fixture_name = _clean(_pick_text(fixture_league.get("name"), league.get("name")))
    if fixture_name:
        print(f"[LEAGUE] exact name hit: {fixture_name}")
        return fixture_name

    # 2) fixture.league.id lookup
    if league_id and isinstance(league_lookup, dict):
        lookup_name = _clean(_pick_text(league_lookup.get(league_id)))
        if lookup_name:
            print(f"[LEAGUE] exact id hit: {league_id} -> {lookup_name}")
            return lookup_name

    # 3) country + league pair
    country_name = _pick_text(country.get("name"), league.get("country"), item.get("country"))
    pair_name = _clean(_pick_text(league.get("name"), competition.get("name"), tournament.get("name")))
    if country_name and pair_name:
        if country_name.lower() in pair_name.lower():
            print(f"[LEAGUE] exact name hit: {pair_name}")
            return pair_name
        combined = f"{country_name} - {pair_name}"
        print(f"[LEAGUE] exact name hit: {combined}")
        return combined

    # 4) competition name
    competition_name = _clean(_pick_text(competition.get("name"), competition.get("longName")))
    if competition_name:
        print(f"[LEAGUE] exact name hit: {competition_name}")
        return competition_name

    # 5) tournament name
    tournament_name = _clean(_pick_text(tournament.get("name"), _safe_dict(tournament.get("uniqueTournament")).get("name")))
    if tournament_name:
        print(f"[LEAGUE] exact name hit: {tournament_name}")
        return tournament_name

    print("[LEAGUE] low confidence fallback -> Other")
    return "Other"


def _build_match_id(item, home_name, away_name, time_text):
    raw_match_id = _pick_text(item.get("id"), item.get("matchId"))
    if raw_match_id:
        return str(raw_match_id)

    league = _safe_dict(item.get("league"))
    home = _safe_dict(item.get("home"))
    away = _safe_dict(item.get("away"))
    fixture = _safe_dict(item.get("fixture"))

    unique_parts = [
        _pick_text(item.get("leagueId"), league.get("id")),
        _pick_text(home.get("id"), item.get("homeId"), home_name),
        _pick_text(away.get("id"), item.get("awayId"), away_name),
        _pick_text(item.get("timeTS"), item.get("time"), fixture.get("date"), item.get("date"), time_text),
    ]
    unique_parts = [part for part in unique_parts if part]
    if unique_parts:
        return "::".join(unique_parts)

    return f"{home_name}-{away_name}-{time_text}"


def _build_match(item, league_lookup):
    home = _safe_dict(item.get("home"))
    away = _safe_dict(item.get("away"))
    fixture = _safe_dict(item.get("fixture"))
    fixture_status = _safe_dict(fixture.get("status"))

    home_name = _pick_team_name(home, item.get("homeName"), item.get("home"))
    away_name = _pick_team_name(away, item.get("awayName"), item.get("away"))

    if not home_name or not away_name:
        return None

    if home_name.lower() == away_name.lower():
        return None

    time_text = _format_match_time(item)
    if not time_text:
        return None

    status_short = _pick_text(fixture_status.get("short")).upper()
    elapsed_value = fixture_status.get("elapsed")
    has_started = status_short in {"1H", "HT", "2H", "ET", "BT", "P", "FT", "AET", "PEN", "LIVE"} or (isinstance(elapsed_value, int) and elapsed_value > 0)

    mapped_match = {
        "matchId": _build_match_id(item, home_name, away_name, time_text),
        "league": _get_league_name(item, league_lookup),
        "status": fixture_status.get("short"),
        "elapsed": fixture_status.get("elapsed"),
        "time": time_text,
        "home": home_name,
        "away": away_name,
        "homeId": _pick_text(home.get("id"), item.get("homeId")),
        "awayId": _pick_text(away.get("id"), item.get("awayId")),
        "hasStats": bool(has_started),
        "hasEvents": bool(has_started),
        "hasLineups": bool(has_started),
    }
    print(f"[REAL] match mapped: {home_name} vs {away_name}")
    return mapped_match


def _quality_score(item, mapped):
    score = 0

    if mapped.get("league") and not mapped["league"].startswith("League ") and mapped["league"] != "Unknown League":
        score += 3
    elif mapped.get("league") and mapped["league"] != "Unknown League":
        score += 1

    if mapped.get("homeId") and mapped.get("awayId"):
        score += 2
    elif mapped.get("homeId") or mapped.get("awayId"):
        score += 1

    status = _safe_dict(item.get("status"))
    if status.get("ongoing"):
        score += 3
    elif status.get("started"):
        score += 2
    elif status:
        score += 1

    if mapped.get("time"):
        score += 1

    return score

def _fetch_today_matches_from_upstream(update_meta=True):
    global _RATE_LIMITED_UNTIL
    global _LAST_BULLETIN_REQUEST_AT

    url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
    headers = _request_headers()
    _LAST_BULLETIN_REQUEST_AT = datetime.now()

    try:
        response = requests.get(url, headers=headers, timeout=20)

        print("[REAL] status:", response.status_code)

        try:
            data = response.json()
        except ValueError:
            data = {}

        print("[REAL] raw keys:", list(data.keys()) if isinstance(data, dict) else "not dict")

        if response.status_code == 429:
            _RATE_LIMITED_UNTIL = datetime.now() + timedelta(seconds=BULLETIN_BACKOFF_AFTER_429_SECONDS)
            print("[REAL] rate limited (429)")
            print("[REAL] backoff active after 429")

            memory_entry = _get_cache_entry()
            memory_cached = _get_cached_bulletin_matches(allow_stale=True, log_state=False)
            if memory_cached is not None and memory_entry is not None:
                _log_cache_usage(memory_entry, storage="memory", after_rate_limit=True)
                if update_meta:
                    return _set_bulletin_result(
                        _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=True),
                        "Rate limited by upstream API",
                        memory_cached,
                        from_cache=True,
                    )
                return memory_cached

            disk_entry = _get_disk_cache_entry()
            disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)
            if disk_cached is None or disk_entry is None:
                disk_entry = _load_bulletin_seed_cache()
                disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)

            if disk_cached is not None and disk_entry is not None:
                _promote_disk_cache_to_memory()
                _log_cache_usage(disk_entry, storage="disk", after_rate_limit=True)
                if update_meta:
                    return _set_bulletin_result(
                        _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=True),
                        "Rate limited by upstream API",
                        disk_cached,
                        from_cache=True,
                    )
                return disk_cached

            if update_meta:
                return _set_bulletin_result("RATE_LIMITED", "Rate limited by upstream API")
            return []

        if response.status_code != 200:
            memory_entry = _get_cache_entry()
            memory_cached = _get_cached_bulletin_matches(allow_stale=True, log_state=False)
            if memory_cached is not None and memory_entry is not None:
                _log_cache_usage(memory_entry, storage="memory", after_rate_limit=False)
                if update_meta:
                    return _set_bulletin_result(
                        _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=False),
                        None,
                        memory_cached,
                        from_cache=True,
                    )
                return memory_cached

            disk_entry = _get_disk_cache_entry()
            disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)
            if disk_cached is None or disk_entry is None:
                disk_entry = _load_bulletin_seed_cache()
                disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)

            if disk_cached is not None and disk_entry is not None:
                _promote_disk_cache_to_memory()
                _log_cache_usage(disk_entry, storage="disk", after_rate_limit=False)
                if update_meta:
                    return _set_bulletin_result(
                        _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=False),
                        None,
                        disk_cached,
                        from_cache=True,
                    )
                return disk_cached

            if update_meta:
                return _set_bulletin_result("ERROR", f"Upstream API returned status {response.status_code}")
            return []

        _RATE_LIMITED_UNTIL = None
        candidates = []
        league_lookup = _load_league_lookup(headers)

        raw_response = data.get("response", {}) if isinstance(data, dict) else {}
        if isinstance(raw_response, dict):
            raw_list = raw_response.get("live", [])
        else:
            raw_list = raw_response

        print("[REAL] total raw:", len(raw_list))

        for item in raw_list:
            try:
                if not isinstance(item, dict):
                    continue

                mapped = _build_match(item, league_lookup)
                if not mapped:
                    continue

                sort_time = _parse_time(item.get("time")) or _parse_time(item.get("timeTS")) or datetime.max
                candidates.append((
                    -_quality_score(item, mapped),
                    sort_time,
                    mapped.get("home", ""),
                    mapped,
                ))
            except Exception as inner_e:
                print("[REAL] item error:", inner_e)

        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        matches = [entry[3] for entry in candidates]
        _store_bulletin_cache(matches)

        if update_meta:
            return _set_bulletin_result("REAL_API", None, matches)
        return matches

    except Exception as e:
        print("[REAL] ERROR:", str(e))

        memory_entry = _get_cache_entry()
        memory_cached = _get_cached_bulletin_matches(allow_stale=True, log_state=False)
        if memory_cached is not None and memory_entry is not None:
            _log_cache_usage(memory_entry, storage="memory", after_rate_limit=False)
            if update_meta:
                return _set_bulletin_result(
                    _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=False),
                    None,
                    memory_cached,
                    from_cache=True,
                )
            return memory_cached

        disk_entry = _get_disk_cache_entry()
        disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)
        if disk_cached is None or disk_entry is None:
            disk_entry = _load_bulletin_seed_cache()
            disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)

        if disk_cached is not None and disk_entry is not None:
            _promote_disk_cache_to_memory()
            _log_cache_usage(disk_entry, storage="disk", after_rate_limit=False)
            if update_meta:
                return _set_bulletin_result(
                    _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=False),
                    None,
                    disk_cached,
                    from_cache=True,
                )
            return disk_cached

        if update_meta:
            return _set_bulletin_result("ERROR", str(e))
        return []


def _background_refresh_cache():
    if not _BULLETIN_FETCH_LOCK.acquire(blocking=False):
        print("[REAL] coalesced concurrent request")
        return

    try:
        _fetch_today_matches_from_upstream(update_meta=False)
    finally:
        _BULLETIN_FETCH_LOCK.release()


def _maybe_refresh_cache_in_background(now=None):
    if now is None:
        now = datetime.now()

    if _is_backoff_active(now):
        print("[REAL] backoff active after 429")
        return

    if _is_cooldown_active(now):
        print("[REAL] cooldown active")
        print("[REAL] skipping API due to cooldown")
        return

    print("[REAL] refreshing cache in background")
    threading.Thread(target=_background_refresh_cache, daemon=True).start()


def get_today_matches(force_refresh=False):
    now = datetime.now()
    memory_entry = _get_cache_entry()
    cached = _get_cached_bulletin_matches(allow_stale=True)

    if cached is not None and not force_refresh and memory_entry is not None:
        if _is_backoff_active(now):
            print("[REAL] backoff active after 429")
            _log_cache_usage(memory_entry, storage="memory", after_rate_limit=True)
            return _set_bulletin_result(
                _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=True),
                "Rate limited by upstream API",
                cached,
                from_cache=True,
            )

        _log_cache_usage(memory_entry, storage="memory", after_rate_limit=False)
        if _is_cache_stale():
            _maybe_refresh_cache_in_background(now)
        return _set_bulletin_result(
            _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=False),
            None,
            cached,
            from_cache=True,
        )

    disk_entry = _get_disk_cache_entry()
    disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True)
    if disk_cached is None or disk_entry is None:
        disk_entry = _load_bulletin_seed_cache()
        disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True)

    if disk_cached is not None and not force_refresh and disk_entry is not None:
        _promote_disk_cache_to_memory()
        if _is_backoff_active(now):
            print("[REAL] backoff active after 429")
            _log_cache_usage(disk_entry, storage="disk", after_rate_limit=True)
            return _set_bulletin_result(
                _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=True),
                "Rate limited by upstream API",
                disk_cached,
                from_cache=True,
            )

        _log_cache_usage(disk_entry, storage="disk", after_rate_limit=False)
        if _is_cache_stale():
            _maybe_refresh_cache_in_background(now)
        return _set_bulletin_result(
            _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=False),
            None,
            disk_cached,
            from_cache=True,
        )

    if _BULLETIN_FETCH_LOCK.locked():
        print("[REAL] coalesced concurrent request")

    _BULLETIN_FETCH_LOCK.acquire()
    try:
        now = datetime.now()
        memory_entry = _get_cache_entry()
        cached = _get_cached_bulletin_matches(allow_stale=True, log_state=False)

        if cached is not None and not force_refresh and memory_entry is not None:
            if _is_backoff_active(now):
                print("[REAL] backoff active after 429")
                _log_cache_usage(memory_entry, storage="memory", after_rate_limit=True)
                return _set_bulletin_result(
                    _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=True),
                    "Rate limited by upstream API",
                    cached,
                    from_cache=True,
                )

            _log_cache_usage(memory_entry, storage="memory", after_rate_limit=False)
            if _is_cache_stale():
                _maybe_refresh_cache_in_background(now)
            return _set_bulletin_result(
                _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=False),
                None,
                cached,
                from_cache=True,
            )

        disk_entry = _get_disk_cache_entry()
        disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)
        if disk_cached is None or disk_entry is None:
            disk_entry = _load_bulletin_seed_cache()
            disk_cached = _get_disk_cached_bulletin_matches(allow_stale=True, log_state=False)

        if disk_cached is not None and not force_refresh and disk_entry is not None:
            _promote_disk_cache_to_memory()
            if _is_backoff_active(now):
                print("[REAL] backoff active after 429")
                _log_cache_usage(disk_entry, storage="disk", after_rate_limit=True)
                return _set_bulletin_result(
                    _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=True),
                    "Rate limited by upstream API",
                    disk_cached,
                    from_cache=True,
                )

            _log_cache_usage(disk_entry, storage="disk", after_rate_limit=False)
            if _is_cache_stale():
                _maybe_refresh_cache_in_background(now)
            return _set_bulletin_result(
                _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=False),
                None,
                disk_cached,
                from_cache=True,
            )

        if _is_backoff_active(now):
            print("[REAL] backoff active after 429")
            if cached is not None and memory_entry is not None:
                _log_cache_usage(memory_entry, storage="memory", after_rate_limit=True)
                return _set_bulletin_result(
                    _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=True),
                    "Rate limited by upstream API",
                    cached,
                    from_cache=True,
                )
            if disk_cached is not None and disk_entry is not None:
                _promote_disk_cache_to_memory()
                _log_cache_usage(disk_entry, storage="disk", after_rate_limit=True)
                return _set_bulletin_result(
                    _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=True),
                    "Rate limited by upstream API",
                    disk_cached,
                    from_cache=True,
                )
            return _set_bulletin_result("RATE_LIMITED", "Rate limited by upstream API")

        if _is_cooldown_active(now) and not force_refresh:
            print("[REAL] cooldown active")
            print("[REAL] skipping API due to cooldown")
            if cached is not None and memory_entry is not None:
                return _set_bulletin_result(
                    _get_cache_result_source(memory_entry, storage="memory", after_rate_limit=False),
                    None,
                    cached,
                    from_cache=True,
                )
            if disk_cached is not None and disk_entry is not None:
                _promote_disk_cache_to_memory()
                _log_cache_usage(disk_entry, storage="disk", after_rate_limit=False)
                return _set_bulletin_result(
                    _get_cache_result_source(disk_entry, storage="disk", after_rate_limit=False),
                    None,
                    disk_cached,
                    from_cache=True,
                )
            return _set_bulletin_result("ERROR", "Bulletin refresh cooldown is active")

        return _fetch_today_matches_from_upstream(update_meta=True)
    finally:
        _BULLETIN_FETCH_LOCK.release()


_load_bulletin_disk_cache() or _load_bulletin_seed_cache()
