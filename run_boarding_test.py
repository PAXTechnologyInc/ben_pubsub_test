"""
WORLDPAY_PAXSTORE_BRIDGE Boarding Automation Test Framework
===========================================================
Data-driven test suite for the /MerchantSolution/notification webhook endpoint.
Reads payloads from boarding_payload.json, config from config.json.

Supported event types:
  - equipment.terminals.created
  - equipment.terminals.updated
  - equipment.terminals.reactivated
  - equipment.terminals.deactivated
  - equipment.terminals.deleted
  - merchant.accounts.updated
  - merchant.accounts.created  (payload-level only; server returns unsupported)
"""

import copy
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

import pytest
import requests
from colorama import Fore, Style, init as colorama_init

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
DEFAULT_PAYLOAD_FILE = SCRIPT_DIR / "boarding_payload.json"

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "httpStatusCode": {"type": "string"},
        "httpStatusMessage": {"type": "string"},
        "errors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "errorCode": {"type": "string"},
                    "errorMessage": {"type": "string"},
                    "target": {"type": "string"},
                },
                "required": ["errorCode", "errorMessage"],
            },
        },
    },
    "required": ["httpStatusCode", "httpStatusMessage"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

colorama_init(autoreset=True)


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _eastern_now() -> str:
    eastern_offset = timedelta(hours=-4)
    now = datetime.now(timezone(eastern_offset))
    return now.strftime("%Y-%m-%dT%H:%M:%S.000%z")


def _random_notification_id(length: int = 8) -> str:
    return str(random.randint(0, 10**length - 1)).zfill(length)


def _generate_worldpay_mid(merchant_name: str) -> str:
    md5 = hashlib.md5(merchant_name.encode()).hexdigest()
    unique_number = int(md5[:16], 16) % (10**16)
    return str(unique_number)


class PayloadBuilder:
    """Build event payloads by resolving Postman-style template variables."""

    def __init__(self, config: dict):
        self.config = config
        td = config.get("test_data", {})
        self.merchant_name = td.get("merchant_name", "Test Merchant")
        self.terminal_id = td.get("terminal_id", "PAX12345678")
        self.model = td.get("model", "A920Pro")
        self.reseller_name = td.get("reseller_name", "Worldpay")

    def resolve(self, payload: dict) -> dict:
        """Deep-copy payload and replace {{variable}} placeholders."""
        resolved = copy.deepcopy(payload)
        variables = {
            "notificationId": _random_notification_id(),
            "createdAt": _eastern_now(),
            "merchantName": self.merchant_name,
            "worldpayMID": _generate_worldpay_mid(self.merchant_name),
            "terminalId": self.terminal_id,
            "model": self.model,
            "resellerName": self.reseller_name,
        }
        return self._substitute(resolved, variables)

    @staticmethod
    def _substitute(obj: Any, variables: dict) -> Any:
        if isinstance(obj, str):
            pattern = re.compile(r"\{\{(\w+)\}\}")
            return pattern.sub(lambda m: str(variables.get(m.group(1), m.group(0))), obj)
        if isinstance(obj, dict):
            return {k: PayloadBuilder._substitute(v, variables) for k, v in obj.items()}
        if isinstance(obj, list):
            return [PayloadBuilder._substitute(item, variables) for item in obj]
        return obj


# ---------------------------------------------------------------------------
# Logger Setup
# ---------------------------------------------------------------------------


def setup_logger(config: dict) -> logging.Logger:
    log_cfg = config.get("logging", {})
    log_dir = SCRIPT_DIR / log_cfg.get("log_dir", "logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / log_cfg.get("log_file", "boarding_test_{timestamp}.log").replace(
        "{timestamp}", timestamp
    )

    logger = logging.getLogger("boarding_test")
    logger.setLevel(getattr(logging, log_cfg.get("level", "DEBUG")))
    logger.handlers.clear()

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    if log_cfg.get("console_output", True):
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    return logger


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------


class BoardingApiClient:
    """HTTP client wrapping the /MerchantSolution/notification endpoint."""

    def __init__(self, config: dict, logger: logging.Logger):
        svc = config["service"]
        self.base_url = svc["base_url"].rstrip("/")
        self.notification_url = self.base_url + svc["notification_endpoint"]
        self.health_url = self.base_url + svc["health_endpoint"]
        self.timeout = svc.get("request_timeout_seconds", 30)
        self.auth_cfg = config.get("auth", {})
        self.retry_cfg = config.get("retry", {})
        self.logger = logger

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        mode = self.auth_cfg.get("mode", "ip")
        if mode == "ip":
            forwarded = self.auth_cfg.get("x_forwarded_for", "127.0.0.1")
            headers["X-Forwarded-For"] = forwarded
        elif mode == "jwt":
            token = self.auth_cfg.get("jwt_token", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    def health_check(self) -> requests.Response:
        self.logger.info("GET %s", self.health_url)
        resp = requests.get(self.health_url, timeout=self.timeout)
        self.logger.info("Health check -> %s %s", resp.status_code, resp.text[:200])
        return resp

    def send_notification(self, payload: dict) -> requests.Response:
        headers = self._headers()
        body_str = json.dumps(payload, ensure_ascii=False)
        self.logger.debug("POST %s", self.notification_url)
        self.logger.debug("Headers: %s", json.dumps(headers))
        self.logger.debug("Payload: %s", body_str[:2000])

        resp = requests.post(
            self.notification_url,
            headers=headers,
            data=body_str,
            timeout=self.timeout,
        )
        self.logger.info(
            "Response [%s]: %s", resp.status_code, resp.text[:2000]
        )
        return resp


# ---------------------------------------------------------------------------
# Pytest Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def config():
    return _load_json(CONFIG_PATH)


@pytest.fixture(scope="session")
def logger(config):
    return setup_logger(config)


@pytest.fixture(scope="session")
def api(config, logger):
    return BoardingApiClient(config, logger)


@pytest.fixture(scope="session")
def builder(config):
    return PayloadBuilder(config)


@pytest.fixture(scope="session")
def base_payload(config):
    payload_path = SCRIPT_DIR / config["test_data"].get("payload_file", "boarding_payload.json")
    return _load_json(payload_path)


# ---------------------------------------------------------------------------
# Helper assertions
# ---------------------------------------------------------------------------


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


# ===========================================================================
# TEST SUITE: Health Check
# ===========================================================================


class TestHealthCheck:
    """Verify service is alive before running boarding tests."""

    def test_health_endpoint(self, api, logger):
        logger.info("=" * 60)
        logger.info("TEST: Health Check")
        logger.info("=" * 60)
        resp = api.health_check()
        assert resp.status_code == 200
        assert "Healthy" in resp.text


# ===========================================================================
# TEST SUITE: Terminal Created Event (equipment.terminals.created)
# ===========================================================================


class TestTerminalCreated:
    """Tests for the equipment.terminals.created event type."""

    def _make_payload(self, builder: PayloadBuilder, base_payload: dict, **overrides) -> dict:
        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.created"
        for k, v in overrides.items():
            if k in payload:
                payload[k] = v
        return payload

    def test_tc01_create_terminal_success(self, api, builder, base_payload, logger):
        """TC-01: Send a valid terminal-created event and expect 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-01: Create Terminal - Happy Path")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        logger.info("eventType=%s, notificationId=%s", payload["eventType"], payload["notificationId"])

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-01 PASSED")

    def test_tc02_create_terminal_missing_notification_id(self, api, builder, base_payload, logger):
        """TC-02: Missing notificationId should return 400 immediately."""
        logger.info("=" * 60)
        logger.info("TC-02: Create Terminal - Missing notificationId")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        del payload["notificationId"]

        resp = api.send_notification(payload)
        assert_ack_bad_request(resp)
        assert_response_schema(resp)
        assert_error_contains(resp, expected_code="PARAMETER_VALIDATION_ERROR", expected_target="notificationId")
        logger.info("TC-02 PASSED")

    def test_tc03_create_terminal_missing_event_type(self, api, builder, base_payload, logger):
        """TC-03: Missing eventType should still return 200 ACK (error sent via PATCH)."""
        logger.info("=" * 60)
        logger.info("TC-03: Create Terminal - Missing eventType")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        del payload["eventType"]

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-03 PASSED (error will be sent async via PATCH)")

    def test_tc04_create_terminal_missing_data(self, api, builder, base_payload, logger):
        """TC-04: Missing data field should return 200 ACK (error sent via PATCH)."""
        logger.info("=" * 60)
        logger.info("TC-04: Create Terminal - Missing data")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        del payload["data"]

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-04 PASSED (error will be sent async via PATCH)")

    def test_tc05_create_terminal_empty_equipment_data(self, api, builder, base_payload, logger):
        """TC-05: Empty equipmentData array should return 200 ACK (error via PATCH)."""
        logger.info("=" * 60)
        logger.info("TC-05: Create Terminal - Empty equipmentData")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        payload["data"]["equipmentData"] = []

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-05 PASSED")

    def test_tc06_create_terminal_missing_hierarchy(self, api, builder, base_payload, logger):
        """TC-06: Missing hierarchy in equipmentData should return 200 ACK (validation error via PATCH)."""
        logger.info("=" * 60)
        logger.info("TC-06: Create Terminal - Missing hierarchy")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            eq.pop("hierarchy", None)

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-06 PASSED")

    def test_tc07_create_terminal_missing_hierarchy_merchant_id(self, api, builder, base_payload, logger):
        """TC-07: Missing merchantId under hierarchy should trigger validation error."""
        logger.info("=" * 60)
        logger.info("TC-07: Create Terminal - Missing hierarchy.merchantId")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            if eq.get("hierarchy"):
                eq["hierarchy"]["merchantId"] = None

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-07 PASSED")

    def test_tc08_create_terminal_missing_location(self, api, builder, base_payload, logger):
        """TC-08: Missing location in equipmentData."""
        logger.info("=" * 60)
        logger.info("TC-08: Create Terminal - Missing location")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            eq.pop("location", None)

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-08 PASSED")

    def test_tc09_create_terminal_missing_business(self, api, builder, base_payload, logger):
        """TC-09: Missing business in equipmentData."""
        logger.info("=" * 60)
        logger.info("TC-09: Create Terminal - Missing business")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            eq.pop("business", None)

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-09 PASSED")

    def test_tc10_create_terminal_missing_terminals_array(self, api, builder, base_payload, logger):
        """TC-10: Missing terminals array inside equipmentData."""
        logger.info("=" * 60)
        logger.info("TC-10: Create Terminal - Missing terminals")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            eq.pop("terminals", None)

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-10 PASSED")

    def test_tc11_create_terminal_missing_location_store_name(self, api, builder, base_payload, logger):
        """TC-11: Missing storeName under location triggers LOCATION_STORE_NAME_IS_MISSING."""
        logger.info("=" * 60)
        logger.info("TC-11: Create Terminal - Missing location.storeName")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            if eq.get("location"):
                eq["location"]["storeName"] = None

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-11 PASSED")

    def test_tc12_create_terminal_missing_physical_address_country(self, api, builder, base_payload, logger):
        """TC-12: Missing country under physicalAddress triggers LOCATION_PHYSICAL_ADDRESS_NOT_VALID."""
        logger.info("=" * 60)
        logger.info("TC-12: Create Terminal - Missing physicalAddress.country")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            loc = eq.get("location", {})
            addr = loc.get("physicalAddress", {})
            if addr:
                addr["country"] = None

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-12 PASSED")

    def test_tc13_create_terminal_missing_primary_contact(self, api, builder, base_payload, logger):
        """TC-13: Missing primaryContact under location triggers LOCATION_PRIMARY_CONTACT_NOT_VALID."""
        logger.info("=" * 60)
        logger.info("TC-13: Create Terminal - Missing location.primaryContact")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            if eq.get("location"):
                eq["location"]["primaryContact"] = None

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-13 PASSED")

    def test_tc14_create_terminal_missing_vendor_terminal_id(self, api, builder, base_payload, logger):
        """TC-14: Missing vendorTerminalId in terminal object."""
        logger.info("=" * 60)
        logger.info("TC-14: Create Terminal - Missing vendorTerminalId")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        for eq in payload["data"]["equipmentData"]:
            for term in eq.get("terminals", []):
                term["vendorTerminalId"] = None

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-14 PASSED")


# ===========================================================================
# TEST SUITE: Terminal Updated Event (equipment.terminals.updated)
# ===========================================================================


class TestTerminalUpdated:
    """Tests for the equipment.terminals.updated event type."""

    def _make_payload(self, builder: PayloadBuilder, base_payload: dict) -> dict:
        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.updated"
        return payload

    def test_tc20_update_terminal_success(self, api, builder, base_payload, logger):
        """TC-20: Valid update event should return 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-20: Update Terminal - Happy Path")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-20 PASSED")


# ===========================================================================
# TEST SUITE: Terminal Deactivated Event (equipment.terminals.deactivated)
# ===========================================================================


class TestTerminalDeactivated:
    """Tests for the equipment.terminals.deactivated event type."""

    def _make_payload(self, builder: PayloadBuilder, base_payload: dict) -> dict:
        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.deactivated"
        return payload

    def test_tc30_deactivate_terminal_success(self, api, builder, base_payload, logger):
        """TC-30: Valid deactivation event should return 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-30: Deactivate Terminal - Happy Path")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-30 PASSED")


# ===========================================================================
# TEST SUITE: Terminal Reactivated Event (equipment.terminals.reactivated)
# ===========================================================================


class TestTerminalReactivated:
    """Tests for the equipment.terminals.reactivated event type."""

    def _make_payload(self, builder: PayloadBuilder, base_payload: dict) -> dict:
        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.reactivated"
        return payload

    def test_tc40_reactivate_terminal_success(self, api, builder, base_payload, logger):
        """TC-40: Valid reactivation event should return 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-40: Reactivate Terminal - Happy Path")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-40 PASSED")


# ===========================================================================
# TEST SUITE: Terminal Deleted Event (equipment.terminals.deleted)
# ===========================================================================


class TestTerminalDeleted:
    """Tests for the equipment.terminals.deleted event type."""

    def _make_payload(self, builder: PayloadBuilder, base_payload: dict) -> dict:
        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.deleted"
        return payload

    def test_tc50_delete_terminal_success(self, api, builder, base_payload, logger):
        """TC-50: Valid deletion event should return 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-50: Delete Terminal - Happy Path")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-50 PASSED")


# ===========================================================================
# TEST SUITE: Merchant Created Event (merchant.accounts.created)
# ===========================================================================


class TestMerchantCreated:
    """Tests for the merchant.accounts.created event type.

    Note: In the current codebase, merchant.accounts.created is commented out
    and returns null from convertMerchantEvent(), resulting in an error.
    """

    def _make_merchant_payload(self, builder: PayloadBuilder) -> dict:
        return {
            "eventType": "merchant.accounts.created",
            "notificationId": int(_random_notification_id()),
            "eventCount": 1,
            "version": "2.0",
            "createdAt": _eastern_now(),
            "data": {
                "merchantAccounts": [
                    {
                        "hierarchy": {
                            "salesOrganizationCode": "12",
                            "salesOrganizationName": "Your Sales Organization Name",
                            "salesChannelCode": "73",
                            "salesChannelName": "Your Sales Channel Name",
                            "partnerGroupId": "41",
                            "partnerGroupName": "ABC Corp",
                            "nationalCode": "NATNL",
                            "nationalName": "DEF company",
                            "superChainCode": "DA012",
                            "superChainName": "ABC CORP",
                            "branchCode": "9999",
                            "branchName": "ABC 123",
                            "divisionCode": "DIV",
                            "divisionName": "My Division Name",
                            "chainCode": "0X1234",
                            "chainName": "My Chain Name",
                            "storeNumber": "000000001",
                            "storeName": "My Store Name",
                            "merchantId": "12345678909876",
                            "merchantName": "Merchant Name",
                        },
                        "business": {
                            "location": {
                                "storeNumber": "000000001",
                                "storeName": "Test1111",
                                "status": "ACTIVE",
                                "physicalAddress": {
                                    "addressLine1": "4355 N Coalwhipe St.",
                                    "addressLine2": "suite 104",
                                    "city": "Denver",
                                    "state": "CO",
                                    "country": "US",
                                    "postalCode": "80237",
                                },
                                "primaryContact": {
                                    "firstName": "John",
                                    "lastName": "Doe",
                                    "phoneNumber": "1234569870",
                                },
                            },
                            "primaryContact": {
                                "firstName": "John",
                                "lastName": "Doe",
                                "phoneNumber": "1234569870",
                            },
                        },
                    }
                ]
            },
        }

    def test_tc60_create_merchant_unsupported(self, api, builder, logger):
        """TC-60: merchant.accounts.created is currently unsupported; expect 200 ACK but async error."""
        logger.info("=" * 60)
        logger.info("TC-60: Create Merchant (unsupported event)")
        logger.info("=" * 60)

        payload = self._make_merchant_payload(builder)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-60 PASSED (event unsupported; async PATCH error expected)")


# ===========================================================================
# TEST SUITE: Merchant Updated Event (merchant.accounts.updated)
# ===========================================================================


class TestMerchantUpdated:
    """Tests for the merchant.accounts.updated event type."""

    def _make_merchant_updated_payload(self) -> dict:
        return {
            "eventType": "merchant.accounts.updated",
            "notificationId": int(_random_notification_id()),
            "eventCount": 1,
            "version": "2.0",
            "createdAt": _eastern_now(),
            "data": {
                "merchantAccounts": [
                    {
                        "hierarchy": {
                            "salesOrganizationCode": "12",
                            "salesOrganizationName": "Your Sales Organization Name",
                            "salesChannelCode": "73",
                            "salesChannelName": "Your Sales Channel Name",
                            "partnerGroupId": "41",
                            "partnerGroupName": "ABC Corp",
                            "nationalCode": "NATNL",
                            "nationalName": "DEF company",
                            "superChainCode": "DA012",
                            "superChainName": "ABC CORP",
                            "branchCode": "9999",
                            "branchName": "ABC 123",
                            "divisionCode": "DIV",
                            "divisionName": "My Division Name",
                            "chainCode": "0X1234",
                            "chainName": "My Chain Name",
                            "storeNumber": "000000001",
                            "storeName": "My Store Name",
                            "merchantId": "12345678909876",
                            "merchantName": "Merchant Name",
                        },
                        "business": {
                            "location": {
                                "storeNumber": "000000001",
                                "storeName": "Updated Store",
                                "status": "ACTIVE",
                                "physicalAddress": {
                                    "addressLine1": "100 Main St",
                                    "addressLine2": None,
                                    "city": "New York",
                                    "state": "NY",
                                    "country": "US",
                                    "postalCode": "10001",
                                },
                                "primaryContact": {
                                    "firstName": "Jane",
                                    "lastName": "Smith",
                                    "phoneNumber": "9876543210",
                                },
                            },
                            "primaryContact": {
                                "firstName": "Jane",
                                "lastName": "Smith",
                                "phoneNumber": "9876543210",
                            },
                        },
                    }
                ]
            },
        }

    def test_tc70_update_merchant_success(self, api, logger):
        """TC-70: Valid merchant update should return 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-70: Update Merchant - Happy Path")
        logger.info("=" * 60)

        payload = self._make_merchant_updated_payload()
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-70 PASSED")

    def test_tc71_update_merchant_missing_notification_id(self, api, logger):
        """TC-71: Missing notificationId should return 400."""
        logger.info("=" * 60)
        logger.info("TC-71: Update Merchant - Missing notificationId")
        logger.info("=" * 60)

        payload = self._make_merchant_updated_payload()
        del payload["notificationId"]
        resp = api.send_notification(payload)
        assert_ack_bad_request(resp)
        assert_response_schema(resp)
        assert_error_contains(resp, expected_code="PARAMETER_VALIDATION_ERROR", expected_target="notificationId")
        logger.info("TC-71 PASSED")


# ===========================================================================
# TEST SUITE: Unsupported Event Type
# ===========================================================================


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


# ===========================================================================
# TEST SUITE: Authentication & Security
# ===========================================================================


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


# ===========================================================================
# TEST SUITE: Postman Pre-request Script Logic Verification
# ===========================================================================


class TestPostmanVariableLogic:
    """Verify the Postman pre-request script logic is correctly translated."""

    def test_eastern_time_format(self):
        """The generated createdAt should be a valid ISO-like timestamp."""
        ts = _eastern_now()
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{4}", ts), f"Bad format: {ts}"

    def test_notification_id_length(self):
        """notificationId should be exactly 8 digits."""
        nid = _random_notification_id()
        assert len(nid) == 8
        assert nid.isdigit()

    def test_worldpay_mid_deterministic(self):
        """Same merchantName should always produce the same worldpayMID."""
        name = "THORNTONS #0304"
        mid1 = _generate_worldpay_mid(name)
        mid2 = _generate_worldpay_mid(name)
        assert mid1 == mid2

    def test_worldpay_mid_uniqueness(self):
        """Different merchantNames should produce different worldpayMIDs."""
        mid1 = _generate_worldpay_mid("Merchant A")
        mid2 = _generate_worldpay_mid("Merchant B")
        assert mid1 != mid2

    def test_payload_variable_resolution(self, builder, base_payload):
        """All {{variable}} placeholders should be resolved after calling resolve()."""
        payload = builder.resolve(base_payload)
        raw = json.dumps(payload)
        unresolved = re.findall(r"\{\{\w+\}\}", raw)
        assert len(unresolved) == 0, f"Unresolved variables found: {unresolved}"


# ===========================================================================
# TEST SUITE: Data-Driven Boarding End-to-End Flow
# ===========================================================================


class TestBoardingE2EFlow:
    """End-to-end boarding flow: create -> update -> deactivate -> reactivate -> delete."""

    def test_tc100_full_terminal_lifecycle(self, api, builder, base_payload, logger):
        """TC-100: Full terminal lifecycle flow."""
        logger.info("=" * 60)
        logger.info("TC-100: Full Terminal Lifecycle (E2E)")
        logger.info("=" * 60)

        events = [
            "equipment.terminals.created",
            "equipment.terminals.updated",
            "equipment.terminals.deactivated",
            "equipment.terminals.reactivated",
            "equipment.terminals.deleted",
        ]

        for event_type in events:
            logger.info("-" * 40)
            logger.info("Step: %s", event_type)
            payload = builder.resolve(base_payload)
            payload["eventType"] = event_type

            resp = api.send_notification(payload)
            assert_ack_ok(resp)
            assert_response_schema(resp)
            logger.info("  -> %s: OK", event_type)

            time.sleep(2)

        logger.info("TC-100 PASSED (full lifecycle)")


# ===========================================================================
# Standalone Runner
# ===========================================================================


def _print_banner():
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print("  WORLDPAY_PAXSTORE_BRIDGE - Boarding Automation Test Suite")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")


def _print_summary(result: int):
    color = Fore.GREEN if result == 0 else Fore.RED
    status = "ALL TESTS PASSED" if result == 0 else "SOME TESTS FAILED"
    print(f"\n{color}{'=' * 70}")
    print(f"  {status}")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    _print_banner()
    args = [
        __file__,
        "-v",
        "--tb=short",
        f"--html={SCRIPT_DIR / 'logs' / 'report.html'}",
        "--self-contained-html",
    ]
    exit_code = pytest.main(args)
    _print_summary(exit_code)
    sys.exit(exit_code)
