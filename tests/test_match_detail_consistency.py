import asyncio
import importlib
import threading
import unittest
from datetime import datetime, timedelta

from app import rapid_service

match_module = importlib.import_module("app.routes.match")


class MatchDetailConsistencyTests(unittest.TestCase):
    def setUp(self):
        rapid_service._LEAGUE_LOOKUP = {}
        rapid_service._LEAGUE_LOOKUP_UPDATED_AT = None
        rapid_service._BULLETIN_CACHE = None
        rapid_service._BULLETIN_DISK_CACHE = None
        rapid_service._RATE_LIMITED_UNTIL = None
        rapid_service._BULLETIN_FETCH_LOCK = threading.Lock()
        rapid_service._LAST_BULLETIN_SOURCE = "REAL_API"
        rapid_service._LAST_BULLETIN_ERROR = None
        rapid_service._LAST_BULLETIN_REQUEST_AT = None
        match_module.ENABLE_DEMO_DATA = False

    def test_build_match_id_is_string_and_stable(self):
        item = {
            "time": "2099-01-01 20:00:00",
            "timeTS": 4070904000,
            "home": {"name": "Galatasaray", "id": 1},
            "away": {"name": "Fenerbahçe", "id": 2},
            "league": {"id": 71, "name": "Süper Lig"},
            "fixture": {"status": {"short": "NS", "elapsed": 0}},
            "status": {"started": False, "ongoing": False},
        }

        first = rapid_service._build_match(item, {})
        second = rapid_service._build_match(item, {})

        self.assertIsNotNone(first)
        self.assertEqual(first["matchId"], second["matchId"])
        self.assertIsInstance(first["matchId"], str)
        self.assertNotEqual(first["matchId"], "")

    def test_detail_endpoint_does_not_return_fake_stats(self):
        rapid_service._BULLETIN_CACHE = {
            "data": [
                {
                    "matchId": "fixture-123",
                    "league": "Süper Lig",
                    "time": "20:00",
                    "home": "Galatasaray",
                    "away": "Fenerbahçe",
                    "homeId": "gal",
                    "awayId": "fen",
                }
            ],
            "fetched_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=5),
            "origin": "upstream",
        }

        response = asyncio.run(match_module.get_match_detail("fixture-123"))

        self.assertFalse(response.success)
        self.assertIsNone(response.data)
        self.assertEqual(response.source, "NO_REAL_DETAIL")
        self.assertEqual(response.error, "Bu mac icin ayrintili istatistikler henuz alinamadi.")

    def test_detail_lookup_matches_even_if_cached_id_is_not_string(self):
        rapid_service._BULLETIN_CACHE = {
            "data": [
                {
                    "matchId": 98765,
                    "league": "Premier League",
                    "time": "21:00",
                    "home": "Arsenal",
                    "away": "Chelsea",
                    "homeId": "ars",
                    "awayId": "che",
                }
            ],
            "fetched_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=5),
            "origin": "upstream",
        }

        response = asyncio.run(match_module.get_match_detail("98765"))

        self.assertFalse(response.success)
        self.assertIsNone(response.data)
        self.assertEqual(response.source, "NO_REAL_DETAIL")
        self.assertEqual(response.error, "Bu mac icin ayrintili istatistikler henuz alinamadi.")


if __name__ == "__main__":
    unittest.main()
