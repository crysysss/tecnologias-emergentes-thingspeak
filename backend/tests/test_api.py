from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.config import load_settings


class ApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["THINGSPEAK_ALLOW_LIVE_READS"] = "false"
        os.environ["THINGSPEAK_ALLOW_WRITE"] = "false"
        load_settings.cache_clear()
        from backend.main import app

        self.client = TestClient(app)

    def tearDown(self) -> None:
        os.environ.pop("THINGSPEAK_ALLOW_LIVE_READS", None)
        os.environ.pop("THINGSPEAK_ALLOW_WRITE", None)
        load_settings.cache_clear()

    def test_history_uses_fixture_when_live_reads_disabled(self) -> None:
        response = self.client.get("/api/telemetry/history?limit=3")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["source"], "fixture")
        self.assertEqual(payload["channel_state"], "fixture_only")
        self.assertEqual(payload["count"], 3)
        self.assertEqual(len(payload["measurements"]), 3)

    def test_history_reports_live_empty_when_channel_has_no_feed_entries(self) -> None:
        os.environ["THINGSPEAK_ALLOW_LIVE_READS"] = "true"
        load_settings.cache_clear()

        with patch(
            "backend.thingspeak_client.ThingSpeakClient.read_history",
            return_value={"channel": {"id": 3353980}, "feeds": []},
        ):
            response = self.client.get("/api/telemetry/history?limit=3")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["source"], "live")
        self.assertEqual(payload["channel_state"], "live_empty")
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["measurements"], [])

    def test_preview_endpoint_returns_payload_without_write(self) -> None:
        response = self.client.post(
            "/api/telemetry/preview",
            json={
                "cognitive_load_pct": 52.4,
                "coherence_level_pct": 96.8,
                "emotional_intensity_pct": 35.2,
                "inference_latency_ms": 118.6,
                "power_consumption_w": 42.3,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["writes_enabled"])
        self.assertEqual(payload["payload"]["field1"], "52.4")
        self.assertEqual(payload["heuristic_state"], "stable")

    def test_write_endpoint_returns_409_when_write_is_disabled(self) -> None:
        response = self.client.post(
            "/api/telemetry/write",
            json={
                "cognitive_load_pct": 52.4,
                "coherence_level_pct": 96.8,
                "emotional_intensity_pct": 35.2,
                "inference_latency_ms": 118.6,
                "power_consumption_w": 42.3,
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("deshabilitadas por configuracion", response.json()["detail"])

    def test_write_endpoint_returns_entry_id_when_live_write_succeeds(self) -> None:
        os.environ["THINGSPEAK_ALLOW_WRITE"] = "true"
        load_settings.cache_clear()

        with patch(
            "backend.thingspeak_client.ThingSpeakClient.write_fields",
            return_value=77,
        ):
            response = self.client.post(
                "/api/telemetry/write",
                json={
                    "cognitive_load_pct": 52.4,
                    "coherence_level_pct": 96.8,
                    "emotional_intensity_pct": 35.2,
                    "inference_latency_ms": 118.6,
                    "power_consumption_w": 42.3,
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["writes_enabled"])
        self.assertEqual(payload["entry_id"], 77)
        self.assertEqual(payload["payload"]["field5"], "42.3")


if __name__ == "__main__":
    unittest.main()
