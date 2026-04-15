"""TEST SUITE: Edge Cases & Security — unsupported events, malformed input, auth checks."""

import json

import requests

from boarding.assertions import assert_ack_ok, assert_response_schema


class TestUnsupportedEvent:
    """Tests for unsupported or malformed event types."""

    def test_tc80_unsupported_event_type(self, api, builder, base_payload, logger):
        """TC-80: An unknown eventType should return 200 ACK (async error)."""
        logger.info("=" * 60)
        logger.info("TC-80: Unsupported Event Type")
        logger.info("=" * 60)

        payload = builder.resolve(base_payload)
        payload["eventType"] = "unknown.event.type"

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-80 PASSED (async PATCH error expected for unsupported type)")

    def test_tc81_empty_body(self, api, logger):
        """TC-81: Sending an empty body should return an error."""
        logger.info("=" * 60)
        logger.info("TC-81: Empty Request Body")
        logger.info("=" * 60)

        headers = {"Content-Type": "application/json", "X-Forwarded-For": "127.0.0.1"}
        resp = requests.post(
            api.notification_url,
            headers=headers,
            data="{}",
            timeout=api.timeout,
        )
        logger.info("Response [%s]: %s", resp.status_code, resp.text[:500])
        assert resp.status_code == 400
        logger.info("TC-81 PASSED")

    def test_tc82_malformed_json(self, api, logger):
        """TC-82: Malformed JSON body should return 400 or 500."""
        logger.info("=" * 60)
        logger.info("TC-82: Malformed JSON Body")
        logger.info("=" * 60)

        headers = {"Content-Type": "application/json", "X-Forwarded-For": "127.0.0.1"}
        resp = requests.post(
            api.notification_url,
            headers=headers,
            data="{this is not valid json",
            timeout=api.timeout,
        )
        logger.info("Response [%s]: %s", resp.status_code, resp.text[:500])
        assert resp.status_code in (400, 500)
        logger.info("TC-82 PASSED")


class TestSecurity:
    """Tests for authentication and IP-based access control."""

    def test_tc90_access_without_auth(self, api, builder, base_payload, logger):
        """TC-90: Request without X-Forwarded-For or JWT should be rejected (401)."""
        logger.info("=" * 60)
        logger.info("TC-90: No Authentication Header")
        logger.info("=" * 60)

        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.created"
        headers = {"Content-Type": "application/json"}

        resp = requests.post(
            api.notification_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=api.timeout,
        )
        logger.info("Response [%s]: %s", resp.status_code, resp.text[:500])
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        logger.info("TC-90 PASSED")

    def test_tc91_access_with_blocked_ip(self, api, builder, base_payload, logger):
        """TC-91: Request from non-allowed IP should be rejected."""
        logger.info("=" * 60)
        logger.info("TC-91: Blocked IP Access")
        logger.info("=" * 60)

        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.created"
        headers = {
            "Content-Type": "application/json",
            "X-Forwarded-For": "192.168.99.99",
        }

        resp = requests.post(
            api.notification_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=api.timeout,
        )
        logger.info("Response [%s]: %s", resp.status_code, resp.text[:500])
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        logger.info("TC-91 PASSED")
