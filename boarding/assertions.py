"""Reusable assertion helpers for WorldpayResponse schema validation."""

import pytest
import requests

from boarding.constants import RESPONSE_SCHEMA


def assert_ack_ok(resp: requests.Response):
    """Service should return 200 ACK with httpStatusCode=200."""
    assert resp.status_code == 200, f"Expected HTTP 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["httpStatusCode"] == "200", f"Expected ACK code 200, got {body}"
    assert body["httpStatusMessage"] == "OK"


def assert_ack_bad_request(resp: requests.Response):
    """Service should return 400 immediately."""
    assert resp.status_code == 400, f"Expected HTTP 400, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["httpStatusCode"] == "400"
    assert body["httpStatusMessage"] == "Bad Request"
    assert "errors" in body and len(body["errors"]) > 0


def assert_response_schema(resp: requests.Response):
    """Validate the response body matches the WorldpayResponse schema."""
    from jsonschema import validate, ValidationError

    body = resp.json()
    try:
        validate(instance=body, schema=RESPONSE_SCHEMA)
    except ValidationError as e:
        pytest.fail(f"Response schema validation failed: {e.message}")


def assert_error_contains(resp: requests.Response, expected_code: str = None, expected_target: str = None):
    """Check that the error list contains expected errorCode or target."""
    body = resp.json()
    errors = body.get("errors", [])
    assert len(errors) > 0, "Expected errors in response but got none"
    if expected_code:
        codes = [e["errorCode"] for e in errors]
        assert expected_code in codes, f"Expected errorCode '{expected_code}' in {codes}"
    if expected_target:
        targets = [e.get("target") for e in errors]
        assert expected_target in targets, f"Expected target '{expected_target}' in {targets}"
