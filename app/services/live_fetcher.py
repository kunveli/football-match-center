import json
import time
from ast import literal_eval
from datetime import datetime
from pathlib import Path
from threading import Thread

import requests
from app.services.api_football_provider import get_live_fixtures, get_today_fixtures

CACHE_FILE = "app/data/bulletin_cache.json"
LOCAL_LEAGUE_LOOKUP_FILE = Path(__file__).resolve().parent.parent / "data" / "league_lookup.json"

MAX_PAGES = 5
MAX_MATCHES = 300

LEAGUE_PATHS = (
    "league.name",
    "league.longName",
    "league.shortName",
    "competition.name",
    "competition.longName",
    "tournament.name",
    "tournament.uniqueTournament.name",
    "tournament.category.name",
    "tournament.category.country.name",
    "event.tournament.name",
    "event.tournament.uniqueTournament.name",
    "event.tournament.category.name",
    "event.tournament.category.country.name",
    "country.name",
    "category.name",
    "season.name",
)

STATUS_PATHS = (
    "fixture.status.short",
    "fixture.status.long",
    "status.short",
    "status.long",
    "status.type",
    "status.description",
    "event.status.type",
    "event.status.description",
    "time.status",
    "matchStatus",
    "state",
)

_LEAGUE_LOOKUP = {}
_LEAGUE_LOOKUP_UPDATED_AT = None


def _is_valid_live_match(match):
    if not isinstance(match, dict):
        return False

    match_id = _pick_text(match.get("matchId"), match.get("id"))
    home = _pick_text(match.get("home"), match.get("home_team"))
    away = _pick_text(match.get("away"), match.get("away_team"))
    if not match_id or not home or not away:
        return False
    if home.lower() == away.lower():
        return False

    # Never let seed/demo entries be persisted as live cache.
    if str(match_id).strip().lower().startswith("seed-"):
        return False

    return True


def _load_local_league_lookup():
    try:
        if not LOCAL_LEAGUE_LOOKUP_FILE.exists():
            return {}

        with LOCAL_LEAGUE_LOOKUP_FILE.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        if not isinstance(payload, dict):
            return {}

        normalized = {}
        for key, value in payload.items():
            league_id = _pick_text(key)
            league_name = _pick_text(value)
            if league_id and league_name:
                normalized[league_id] = league_name
        return normalized
    except Exception:
        return {}


def _pick_text(*values):
    for value in values:
        if value is None:
            continue
        if isinstance(value, (dict, list, tuple, set)):
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _as_mapping(value):
    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        return {}

    raw = value.strip()
    if not raw:
        return {}

    for parser in (json.loads, literal_eval):
        try:
            parsed = parser(raw)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            continue

    return {}


def _to_int(value):
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    text = _pick_text(value)
    if not text:
        return None

    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None

    try:
        return int(digits)
    except Exception:
        return None


def pick(obj, *paths):
    for path in paths:
        if not path:
            continue

        current = obj
        ok = True
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current.get(part)
            else:
                ok = False
                break

        if not ok:
            continue

        if current is None:
            continue

        if isinstance(current, str):
            if current.strip():
                return current
            continue

        return current

    return None


def _all_path_values(obj, *paths):
    values = []
    for path in paths:
        value = pick(obj, path)
        if value is not None:
            values.append(value)
    return values


def team_name(value):
    if isinstance(value, dict):
        return _pick_text(value.get("name"), value.get("longName"), value.get("shortName"))
    if isinstance(value, str):
        parsed = _as_mapping(value)
        if parsed:
            return _pick_text(parsed.get("name"), parsed.get("longName"), parsed.get("shortName"))
        return value.strip()
    return ""


def team_id(value):
    if isinstance(value, dict):
        return _pick_text(value.get("id"))
    return ""


def _format_time(value):
    raw = _pick_text(value)
    if not raw:
        return ""

    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed.strftime("%H:%M")
        except ValueError:
            continue

    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed.strftime("%H:%M")
    except Exception:
        return raw


def _extract_name_from_nested(value):
    mapping = _as_mapping(value)
    if not mapping:
        return ""

    direct = _pick_text(mapping.get("name"), mapping.get("longName"), mapping.get("shortName"))
    if direct:
        return direct

    for nested_key in ("league", "competition", "tournament", "uniqueTournament", "category", "country", "season"):
        nested = _as_mapping(mapping.get(nested_key))
        nested_name = _pick_text(nested.get("name"), nested.get("longName"), nested.get("shortName"))
        if nested_name:
            return nested_name

    return ""


def _is_low_confidence_league_name(value):
    text = _pick_text(value)
    if not text:
        return True

    lowered = text.strip().lower()
    if lowered in {"unknown", "unknown league", "other", "league", "competition", "tournament"}:
        return True
    if lowered.startswith("league "):
        return True
    if lowered.isdigit():
        return True
    return False


def _clean_league_name(value):
    text = _pick_text(value)
    if _is_low_confidence_league_name(text):
        return ""
    return text


def _probe_coverage(item, status, elapsed):
    short_code = _pick_text(pick(item, "fixture.status.short"), pick(item, "status.short")).upper()
    normalized_status = _pick_text(status).upper()

    not_started_codes = {"NS", "TBD", "PST", "CANC", "ABD", "SUSP", "AWD", "WO"}
    live_like_codes = {"1H", "HT", "2H", "ET", "BT", "P", "LIVE"}
    finished_codes = {"FT", "AET", "PEN"}

    if short_code in not_started_codes or normalized_status in {"NS", "POSTPONED"}:
        return {"hasStats": False, "hasEvents": False, "hasLineups": False}

    if short_code in live_like_codes or normalized_status == "LIVE":
        return {"hasStats": True, "hasEvents": True, "hasLineups": True}

    if short_code in finished_codes or normalized_status == "FT":
        return {"hasStats": True, "hasEvents": True, "hasLineups": True}

    elapsed_min = _to_int(elapsed)
    if elapsed_min is not None and elapsed_min > 0:
        return {"hasStats": True, "hasEvents": True, "hasLineups": True}

    return {"hasStats": False, "hasEvents": False, "hasLineups": False}

def _load_league_lookup(_headers=None):
    global _LEAGUE_LOOKUP
    global _LEAGUE_LOOKUP_UPDATED_AT

    now = datetime.now()
    local_lookup = _load_local_league_lookup()

    if _LEAGUE_LOOKUP and _LEAGUE_LOOKUP_UPDATED_AT and (now - _LEAGUE_LOOKUP_UPDATED_AT).total_seconds() < 6 * 3600:
        if local_lookup:
            merged = dict(local_lookup)
            merged.update(_LEAGUE_LOOKUP)
            return merged
        return _LEAGUE_LOOKUP

    if local_lookup:
        _LEAGUE_LOOKUP = dict(local_lookup)
        _LEAGUE_LOOKUP_UPDATED_AT = now
        return _LEAGUE_LOOKUP

    return _LEAGUE_LOOKUP


def _normalize_league(item, league_lookup):
    league_id = _pick_text(pick(item, "leagueId"), pick(item, "league.id"), pick(item, "fixture.league.id"))

    # 1) fixture.league.name (highest confidence)
    fixture_league_name = _clean_league_name(pick(item, "fixture.league.name", "league.name"))
    if fixture_league_name:
        print(f"[LEAGUE] exact name hit: {fixture_league_name}")
        return fixture_league_name, league_id

    # 2) fixture.league.id lookup
    if league_id and isinstance(league_lookup, dict):
        lookup_name = _clean_league_name(league_lookup.get(league_id))
        if lookup_name:
            print(f"[LEAGUE] exact id hit: {league_id} -> {lookup_name}")
            return lookup_name, league_id

    # 3) country + league pair
    country_name = _pick_text(
        pick(item, "league.country"),
        pick(item, "fixture.league.country"),
        pick(item, "tournament.category.country.name"),
        pick(item, "event.tournament.category.country.name"),
        pick(item, "country.name"),
    )
    pair_league = _clean_league_name(
        _pick_text(
            pick(item, "league.name"),
            pick(item, "fixture.league.name"),
            pick(item, "competition.name"),
            pick(item, "tournament.name"),
        )
    )
    if country_name and pair_league:
        if country_name.lower() in pair_league.lower():
            print(f"[LEAGUE] exact name hit: {pair_league}")
            return pair_league, league_id
        pair_name = f"{country_name} - {pair_league}"
        print(f"[LEAGUE] exact name hit: {pair_name}")
        return pair_name, league_id

    # 4) competition name
    competition_name = _clean_league_name(pick(item, "competition.name", "competition.longName"))
    if competition_name:
        print(f"[LEAGUE] exact name hit: {competition_name}")
        return competition_name, league_id

    # 5) tournament name
    tournament_name = _clean_league_name(pick(item, "tournament.name", "event.tournament.name", "tournament.uniqueTournament.name"))
    if tournament_name:
        print(f"[LEAGUE] exact name hit: {tournament_name}")
        return tournament_name, league_id

    print("[LEAGUE] low confidence fallback -> Other")
    return "Other", league_id


def _extract_scores(item):
    home_score = _to_int(
        pick(
            item,
            "home.score",
            "teams.home.score",
            "homeTeam.score",
            "score.home",
            "goals.home",
            "fixture.goals.home",
        )
    )
    away_score = _to_int(
        pick(
            item,
            "away.score",
            "teams.away.score",
            "awayTeam.score",
            "score.away",
            "goals.away",
            "fixture.goals.away",
        )
    )

    score = ""
    if home_score is not None and away_score is not None:
        score = f"{home_score}-{away_score}"

    return home_score, away_score, score


def _normalize_status(item):
    raw_values = _all_path_values(item, *STATUS_PATHS)
    raw_status = _pick_text(*raw_values)

    status_obj = _safe_dict(pick(item, "status"))
    fixture_obj = _safe_dict(pick(item, "fixture.status"))

    started = bool(status_obj.get("started") or fixture_obj.get("started"))
    ongoing = bool(status_obj.get("ongoing") or fixture_obj.get("ongoing"))
    finished = bool(status_obj.get("finished") or fixture_obj.get("finished"))
    cancelled = bool(status_obj.get("cancelled") or fixture_obj.get("cancelled"))

    normalized = ""
    lowered = raw_status.strip().lower()

    if lowered in {"1h", "2h", "et", "bt", "p", "live"}:
        normalized = "LIVE"
    elif lowered in {"ns", "tbd"}:
        normalized = "NS"
    elif lowered in {"ft", "aet", "pen"}:
        normalized = "FT"
    elif lowered in {"pst", "canc", "abd"}:
        normalized = "POSTPONED"
    else:
        live_terms = ("live", "inprogress", "in progress", "1st half", "first half", "2nd half", "second half", "ht", "playing", "ongoing")
        ns_terms = ("notstarted", "scheduled", "ns")
        ft_terms = ("finished", "ended", "ft")

        if any(term in lowered for term in live_terms):
            normalized = "LIVE"
        elif any(term in lowered for term in ns_terms):
            normalized = "NS"
        elif any(term in lowered for term in ft_terms):
            normalized = "FT"
        elif "postponed" in lowered:
            normalized = "POSTPONED"
        elif cancelled:
            normalized = "POSTPONED"
        elif ongoing:
            normalized = "LIVE"
        elif finished:
            normalized = "FT"
        elif started:
            normalized = "LIVE"
        else:
            normalized = raw_status.upper() if raw_status else "NS"

    print(f"[FETCHER] normalized status: {normalized}")
    return normalized, raw_status


def _extract_elapsed(item):
    elapsed = pick(item, "fixture.status.elapsed", "status.elapsed")
    as_int = _to_int(elapsed)
    if as_int is not None:
        return as_int

    live_time_short = pick(item, "status.liveTime.short", "fixture.status.liveTime.short")
    return _to_int(live_time_short)


def _display_time(item, status, elapsed):
    if status == "LIVE":
        if elapsed is not None:
            return f"{elapsed}'"

        live_short = _pick_text(
            pick(item, "status.liveTime.short"),
            pick(item, "fixture.status.liveTime.short"),
        )
        if live_short:
            return live_short
        return "Canli"

    return _format_time(pick(item, "fixture.date", "date", "startTime", "start_time", "time"))


def _extract_items(payload):
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    for key in ("response", "data", "matches", "events", "results", "fixtures"):
        candidate = payload.get(key)
        if isinstance(candidate, list):
            return candidate
        if isinstance(candidate, dict):
            nested = _extract_items(candidate)
            if nested:
                return nested

    for value in payload.values():
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _extract_items(value)
            if nested:
                return nested

    return []


def _extract_pagination(payload):
    if not isinstance(payload, dict):
        return {}

    response_obj = _safe_dict(payload.get("response"))
    candidates = [
        payload,
        _safe_dict(payload.get("pagination")),
        _safe_dict(payload.get("paging")),
        _safe_dict(payload.get("meta")),
        response_obj,
        _safe_dict(response_obj.get("pagination")),
        _safe_dict(response_obj.get("paging")),
        _safe_dict(response_obj.get("meta")),
    ]

    merged = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        merged.update(candidate)

    return {
        "page": merged.get("page") or merged.get("currentPage"),
        "next": merged.get("next"),
        "hasMore": merged.get("hasMore"),
        "totalPages": merged.get("totalPages"),
        "limit": merged.get("limit"),
        "offset": merged.get("offset"),
        "cursor": merged.get("cursor"),
    }


def _build_next_params(params, pagination):
    next_params = dict(params)

    cursor = _pick_text(pagination.get("cursor"))
    if cursor and cursor != _pick_text(params.get("cursor")):
        next_params["cursor"] = cursor
        return next_params

    next_raw = pagination.get("next")
    if isinstance(next_raw, dict):
        page_val = _pick_text(next_raw.get("page"))
        cursor_val = _pick_text(next_raw.get("cursor"))
        if page_val:
            next_params["page"] = page_val
            return next_params
        if cursor_val:
            next_params["cursor"] = cursor_val
            return next_params

    next_page = _to_int(next_raw)
    if next_page is not None:
        next_params["page"] = next_page
        return next_params

    has_more = pagination.get("hasMore")
    if isinstance(has_more, str):
        has_more = has_more.strip().lower() in {"1", "true", "yes", "on"}

    current_page = _to_int(pagination.get("page"))
    total_pages = _to_int(pagination.get("totalPages"))

    if bool(has_more) and current_page is not None:
        next_params["page"] = current_page + 1
        return next_params

    if current_page is not None and total_pages is not None and current_page < total_pages:
        next_params["page"] = current_page + 1
        return next_params

    return None


def _fetch_paginated_items(headers, url=None, base_params=None):
    all_items = []
    page_num = 1
    params = dict(base_params or {})
    request_signatures = set()
    pagination_available = False
    pagination_logged = False

    while page_num <= MAX_PAGES:
        signature = json.dumps(params, sort_keys=True, ensure_ascii=True)
        if signature in request_signatures:
            break
        request_signatures.add(signature)

        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code == 429:
            return None, 429
        if response.status_code != 200:
            return None, response.status_code

        raw = response.json()
        items = _extract_items(raw)
        all_items.extend(items)
        print(f"[FETCHER] fetched page {page_num}")

        if page_num == 1 and isinstance(items, list) and items:
            print(f"[FETCHER] sample item: {json.dumps(items[0], ensure_ascii=True)}")

        pagination = _extract_pagination(raw)
        next_params = _build_next_params(params, pagination)
        if next_params is None:
            if page_num == 1:
                print("[FETCHER] pagination not available from provider")
                pagination_logged = True
            break

        pagination_available = True
        params = next_params
        page_num += 1

    if not pagination_available and not pagination_logged:
        print("[FETCHER] pagination not available from provider")

    return all_items, 200


def _normalize_matches(items, league_lookup=None):
    valid_matches = []
    seen_match_ids = set()

    for item in items or []:
        if not isinstance(item, dict):
            continue

        home_obj = pick(item, "teams.home", "home", "homeTeam", "home_team")
        away_obj = pick(item, "teams.away", "away", "awayTeam", "away_team")

        home = team_name(home_obj)
        away = team_name(away_obj)

        home_id = str(team_id(home_obj) or pick(item, "teams.home.id", "homeId", "home_team_id") or "")
        away_id = str(team_id(away_obj) or pick(item, "teams.away.id", "awayId", "away_team_id") or "")

        league, league_id = _normalize_league(item, league_lookup or {})
        if league == "Unknown League":
            print("[FETCHER] league missing, using Unknown League")

        match_id = _pick_text(pick(item, "fixture.id", "id", "matchId", "match_id"))
        status, _raw_status = _normalize_status(item)
        elapsed = _extract_elapsed(item)
        match_time = _display_time(item, status, elapsed)
        home_score, away_score, score = _extract_scores(item)
        coverage = _probe_coverage(item, status, elapsed)

        if home_score is not None and away_score is not None:
            print(f"[FETCHER] score parsed: {home} {home_score}-{away_score} {away}")

        if not match_id or not home or not away:
            print(
                f"[FETCHER] skipped invalid match: matchId={match_id or 'EMPTY'}, home={home or 'EMPTY'}, away={away or 'EMPTY'}"
            )
            continue

        if match_id in seen_match_ids:
            continue
        seen_match_ids.add(match_id)

        mapped = {
            "matchId": str(match_id),
            "league": str(league),
            "leagueId": str(league_id) if league_id else "",
            "time": str(match_time),
            "home": str(home),
            "away": str(away),
            "homeId": home_id,
            "awayId": away_id,
            "homeScore": home_score,
            "awayScore": away_score,
            "score": score,
            "status": str(status),
            "elapsed": elapsed,
            "hasStats": bool(coverage.get("hasStats")),
            "hasEvents": bool(coverage.get("hasEvents")),
            "hasLineups": bool(coverage.get("hasLineups")),
        }

        print(f"[FETCHER] normalized: {mapped['home']} vs {mapped['away']} / {mapped['league']}")
        if status == "LIVE":
            print(f"[FETCHER] live match detected: {mapped['home']} vs {mapped['away']}")
        if _is_valid_live_match(mapped):
            valid_matches.append(mapped)

    print(f"[FETCHER] total normalized matches: {len(valid_matches)}")
    return valid_matches


def _merge_matches(match_lists):
    merged = {}
    for matches in match_lists:
        for match in matches:
            mid = match.get("matchId")
            if not mid:
                continue
            if mid not in merged:
                merged[mid] = match
            else:
                existing = merged[mid]
                # LIVE always wins over any non-LIVE status
                if match.get("status") == "LIVE" and existing.get("status") != "LIVE":
                    merged[mid] = match
                elif match.get("status") == existing.get("status"):
                    # Same status: prefer more descriptive league name
                    ex_league = existing.get("league", "Other")
                    new_league = match.get("league", "Other")
                    if ex_league in ("Other", "Unknown League") and new_league not in ("Other", "Unknown League"):
                        merged[mid] = match

    return list(merged.values())[:MAX_MATCHES]


def fetch_and_store():
    time.sleep(2)
    while True:
        try:
            print("[FETCHER] starting daily bulletin fetch...")

            league_lookup = _load_league_lookup(None)

            live_items, live_status = get_live_fixtures()
            today_items, today_status = get_today_fixtures()

            print(f"[API_FOOTBALL] live fixtures: {len(live_items)}")
            print(f"[API_FOOTBALL] today fixtures: {len(today_items)}")

            all_normalized = []

            if live_status == 200:
                all_normalized.append(_normalize_matches(live_items, league_lookup=league_lookup))
            elif live_status:
                print(f"[FETCHER] endpoint live: status {live_status}, skipping")

            if today_status == 200:
                all_normalized.append(_normalize_matches(today_items, league_lookup=league_lookup))
            elif today_status:
                print(f"[FETCHER] endpoint today: status {today_status}, skipping")

            if not all_normalized:
                print("[FETCHER] all endpoints failed, preserving existing live cache")
                time.sleep(60)
                continue

            merged = _merge_matches(all_normalized)
            merged = [m for m in merged if _is_valid_live_match(m)]
            print(f"[API_FOOTBALL] merged fixtures: {len(merged)}")
            live_count = sum(1 for m in merged if m.get("status") == "LIVE")
            print(f"[FETCHER] total merged matches: {len(merged)}")
            print(f"[FETCHER] live matches: {live_count}")

            if not merged:
                print("[FETCHER] cache update skipped, no valid live matches")
                time.sleep(60)
                continue

            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(merged, f)

            print(f"[FETCHER] live cache updated: {len(merged)} matches")

        except Exception as e:
            print("[FETCHER] error, keeping existing cache")
            print(f"[FETCHER] error detail: {e}")

        time.sleep(60)


def start_fetcher():
    t = Thread(target=fetch_and_store, daemon=True)
    t.start()
