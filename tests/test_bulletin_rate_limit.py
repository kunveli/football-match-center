import json
import tempfile
import threading
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from app import rapid_service


class BulletinRateLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        rapid_service._BULLETIN_DISK_CACHE_PATH = Path(self.temp_dir.name) / "bulletin_cache.json"
        rapid_service._BULLETIN_SEED_PATH = Path(self.temp_dir.name) / "bulletin_seed.json"
        rapid_service._LEAGUE_LOOKUP = {}
        rapid_service._LEAGUE_LOOKUP_UPDATED_AT = None
        rapid_service._BULLETIN_CACHE = None
        rapid_service._BULLETIN_DISK_CACHE = None
        rapid_service._RATE_LIMITED_UNTIL = None
        rapid_service._BULLETIN_FETCH_LOCK = threading.Lock()
        rapid_service._LAST_BULLETIN_SOURCE = "REAL_API"
        rapid_service._LAST_BULLETIN_ERROR = None
        rapid_service._LAST_BULLETIN_REQUEST_AT = None

    def tearDown(self):
        self.temp_dir.cleanup()

    def _response(self, status_code=200, payload=None):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = payload or {}
        return response

    def _live_response(self, match_id="match-1"):
        return self._response(
            200,
            {
                "response": {
                    "live": [
                        {
                            "id": match_id,
                            "time": "2099-01-01 12:30:00",
                            "home": {"name": "Arsenal", "id": "10"},
                            "away": {"name": "Chelsea", "id": "20"},
                            "league": {"name": "Premier League", "id": "100"},
                            "fixture": {"status": {"short": "NS", "elapsed": 0}},
                            "status": {"started": False, "ongoing": False},
                        }
                    ]
                }
            },
        )

    def _cached_match(self):
        return [{
            "matchId": "cached-1",
            "league": "Premier League",
            "time": "12:30",
            "home": "Arsenal",
            "away": "Chelsea",
            "homeId": "10",
            "awayId": "20",
        }]

    def _seed_payload(self):
        return {
            "success": True,
            "data": [
                {
                    "matchId": "seed-1",
                    "league": "Premier League",
                    "time": "20:00",
                    "home": "Arsenal",
                    "away": "Chelsea",
                    "homeId": "ars",
                    "awayId": "che",
                    "status": "NS",
                    "elapsed": None,
                }
            ],
            "error": None,
            "source": "SEED_CACHE",
        }

    def test_successful_fetch_updates_cache_metadata(self):
        with patch.object(rapid_service, "_load_league_lookup", return_value={}), patch.object(
            rapid_service.requests,
            "get",
            return_value=self._live_response(),
        ), patch("builtins.print") as mock_print:
            matches = rapid_service.get_today_matches()

        self.assertEqual(len(matches), 1)
        self.assertIsInstance(rapid_service._BULLETIN_CACHE, dict)
        self.assertEqual(rapid_service._BULLETIN_CACHE["data"], matches)
        self.assertIsNotNone(rapid_service._BULLETIN_CACHE["fetched_at"])
        self.assertIsNotNone(rapid_service._BULLETIN_CACHE["expires_at"])
        self.assertTrue(any("[REAL] cache updated" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_cache_hit_returns_immediately_and_skips_upstream(self):
        cached = self._cached_match()
        rapid_service._store_bulletin_cache(cached)

        with patch.object(rapid_service.requests, "get", side_effect=AssertionError("upstream should not be called")), patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches()
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, cached)
        self.assertEqual(source, "CACHE_HIT")
        self.assertIsNone(error)
        self.assertTrue(any("[REAL] serving from cache" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_disk_cache_can_be_loaded_from_json_file(self):
        cached = self._cached_match()
        rapid_service._store_bulletin_cache(cached)
        rapid_service._BULLETIN_CACHE = None
        rapid_service._BULLETIN_DISK_CACHE = None

        with patch("builtins.print") as mock_print:
            cache_entry = rapid_service._load_bulletin_disk_cache()

        self.assertIsNotNone(cache_entry)
        self.assertEqual(cache_entry["data"], cached)
        self.assertTrue(any("[REAL] disk cache loaded" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_disk_cache_hit_used_when_memory_cache_missing(self):
        cached = self._cached_match()
        rapid_service._store_bulletin_cache(cached)
        rapid_service._BULLETIN_CACHE = None

        with patch.object(rapid_service.requests, "get", side_effect=AssertionError("upstream should not be called")), patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches()
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, cached)
        self.assertEqual(source, "DISK_CACHE_HIT")
        self.assertIsNone(error)
        self.assertTrue(any("[REAL] serving from disk cache" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_seed_cache_bootstraps_when_disk_cache_missing(self):
        rapid_service._BULLETIN_SEED_PATH.write_text(json.dumps(self._seed_payload(), ensure_ascii=False), encoding="utf-8")

        with patch.object(rapid_service.requests, "get", side_effect=AssertionError("upstream should not be called")), patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches()
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, self._seed_payload()["data"])
        self.assertEqual(source, "SEED_CACHE")
        self.assertIsNone(error)
        self.assertIsInstance(rapid_service._BULLETIN_DISK_CACHE, dict)
        self.assertTrue(any("[REAL] seed cache loaded" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))
        self.assertTrue(any("[REAL] serving from seed cache" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_cooldown_skips_api_and_returns_cache(self):
        cached = self._cached_match()
        rapid_service._store_bulletin_cache(cached)
        rapid_service._BULLETIN_CACHE["expires_at"] = datetime.now() - timedelta(seconds=1)
        rapid_service._LAST_BULLETIN_REQUEST_AT = datetime.now()

        with patch.object(rapid_service.requests, "get", side_effect=AssertionError("upstream should not be called twice")), patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches()
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, cached)
        self.assertEqual(source, "CACHE_HIT")
        self.assertIsNone(error)
        self.assertTrue(any("[REAL] skipping API due to cooldown" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_429_returns_cached_data_with_cache_after_rate_limit_source(self):
        cached = self._cached_match()
        rapid_service._store_bulletin_cache(cached)
        rapid_service._BULLETIN_CACHE["expires_at"] = datetime.now() - timedelta(seconds=1)

        with patch.object(rapid_service, "_load_league_lookup", return_value={}), patch.object(
            rapid_service.requests,
            "get",
            return_value=self._response(429, {}),
        ), patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches(force_refresh=True)
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, cached)
        self.assertEqual(source, "CACHE_AFTER_RATE_LIMIT")
        self.assertEqual(error, "Rate limited by upstream API")
        self.assertIsNotNone(rapid_service._RATE_LIMITED_UNTIL)
        self.assertTrue(any("[REAL] using cache after 429" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_429_uses_disk_cache_when_memory_cache_missing(self):
        cached = self._cached_match()
        rapid_service._store_bulletin_cache(cached)
        rapid_service._BULLETIN_CACHE = None

        with patch.object(rapid_service, "_load_league_lookup", return_value={}), patch.object(
            rapid_service.requests,
            "get",
            return_value=self._response(429, {}),
        ), patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches(force_refresh=True)
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, cached)
        self.assertEqual(source, "DISK_CACHE_AFTER_RATE_LIMIT")
        self.assertEqual(error, "Rate limited by upstream API")
        self.assertIsNotNone(rapid_service._RATE_LIMITED_UNTIL)
        self.assertTrue(any("[REAL] using disk cache after 429" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_429_uses_seed_cache_when_no_other_cache_exists(self):
        rapid_service._BULLETIN_SEED_PATH.write_text(json.dumps(self._seed_payload(), ensure_ascii=False), encoding="utf-8")

        with patch.object(rapid_service, "_load_league_lookup", return_value={}), patch.object(
            rapid_service.requests,
            "get",
            return_value=self._response(429, {}),
        ), patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches(force_refresh=True)
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, self._seed_payload()["data"])
        self.assertEqual(source, "SEED_CACHE_AFTER_RATE_LIMIT")
        self.assertEqual(error, "Rate limited by upstream API")
        self.assertIsNotNone(rapid_service._RATE_LIMITED_UNTIL)
        self.assertTrue(any("[REAL] using seed cache after 429" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_backoff_without_cache_returns_rate_limited_error(self):
        rapid_service._RATE_LIMITED_UNTIL = datetime.now() + timedelta(seconds=30)

        with patch("builtins.print") as mock_print:
            result = rapid_service.get_today_matches(force_refresh=True)
            source, error = rapid_service.get_bulletin_fetch_meta()

        self.assertEqual(result, [])
        self.assertEqual(source, "RATE_LIMITED")
        self.assertEqual(error, "Rate limited by upstream API")
        self.assertTrue(any("[REAL] backoff active after 429" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_league_resolution_prefers_item_name(self):
        item = {"league": {"name": "Premier League", "id": "9294"}, "leagueId": "9294"}

        with patch("builtins.print") as mock_print:
            result = rapid_service._get_league_name(item, {"9294": "Lookup League"})

        self.assertEqual(result, "Premier League")
        self.assertTrue(any("[LEAGUE] exact name hit: Premier League" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_league_resolution_uses_lookup_when_name_missing(self):
        item = {"league": {"id": "9294"}, "leagueId": "9294"}

        with patch("builtins.print") as mock_print:
            result = rapid_service._get_league_name(item, {"9294": "Türkiye Süper Lig"})

        self.assertEqual(result, "Türkiye Süper Lig")
        self.assertTrue(any("[LEAGUE] exact id hit: 9294 -> Türkiye Süper Lig" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))

    def test_league_resolution_falls_back_only_as_last_resort(self):
        item = {"league": {"id": "9294"}, "leagueId": "9294"}

        with patch("builtins.print") as mock_print:
            result = rapid_service._get_league_name(item, {})

        self.assertEqual(result, "Other")
        self.assertTrue(any("[LEAGUE] low confidence fallback -> Other" in " ".join(map(str, call.args)) for call in mock_print.call_args_list))


if __name__ == "__main__":
    unittest.main()
