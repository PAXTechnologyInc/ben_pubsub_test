"""TEST SUITE: Terminal Created Event (equipment.terminals.created) — TC-01 to TC-14."""

from boarding.payload import PayloadBuilder
from boarding.assertions import assert_ack_ok, assert_ack_bad_request, assert_response_schema, assert_error_contains


class TestTerminalCreated:
    """Tests for the equipment.terminals.created event type."""

    def _make_payload(self, builder: PayloadBuilder, base_payload: dict, **overrides) -> dict:
        payload = builder.resolve(base_payload)
        payload["eventType"] = "equipment.terminals.created"
        for k, v in overrides.items():
            if k in payload:
                payload[k] = v
        return payload

    '''TC-01: Send a valid terminal-created event and expect 200 ACK.
    Test data:
    - merchantName: Terry test_data #0304
    - worldpayMID: 5922820006187008
    - terminalId: 7079
    - model: Valutec Only PAX A920 MAX
    - resellerName: Valutec
    - notificationId: 42379122
    - createdAt: 2026-04-15T15:48:13.000-04:00
    '''
    def test_tc01_create_terminal_success(self, api, builder, base_payload, logger):
        """TC-01: Send a valid terminal-created event and expect 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-01: Create Terminal - Happy Path")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        logger.info("eventType=%s, notificationId=%s", payload["eventType"], payload["notificationId"])
        logger.info("payload: %s", payload)

        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-01 PASSED")

    '''
    TC-02: Missing notificationId should return 400 immediately.
    Test data:
    - merchantName: Terry test_data #0304
    - worldpayMID: 5922820006187008
    - terminalId: 7079
    - model: Valutec Only PAX A920 MAX
    - resellerName: Valutec
    - notificationId: 
    - createdAt: 2026-04-15T15:48:13.000-04:00
    '''
    def test_tc02_create_terminal_missing_notification_id(self, api, builder, base_payload, logger):
        """TC-02: Missing notificationId should return 400 immediately."""
        logger.info("=" * 60)
        logger.info("TC-02: Create Terminal - Missing notificationId")
        logger.info("=" * 60)

        payload = self._make_payload(builder, base_payload)
        del payload["notificationId"] # missing notificationId

        resp = api.send_notification(payload)
        assert_ack_bad_request(resp)
        assert_response_schema(resp)
        assert_error_contains(resp, expected_code="PARAMETER_VALIDATION_ERROR", expected_target="notificationId")
        logger.info("TC-02 PASSED")


    '''
    TC-03: Missing eventType should still return 200 ACK (error sent via PATCH).
    Test data:
    - merchantName: Terry test_data #0304
    - worldpayMID: 5922820006187008
    - terminalId: 7079
    - model: Valutec Only PAX A920 MAX
    - resellerName: Valutec
    - notificationId: 42379122
    - createdAt: 2026-04-15T15:48:13.000-04:00
    '''
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

    '''
    TC-07: Missing merchantId under hierarchy should trigger validation error.
    Test data:
    - merchantName: Terry test_data #0304
    - worldpayMID: 5922820006187008
    - terminalId: 7079
    - model: Valutec Only PAX A920 MAX
    - resellerName: Valutec
    - notificationId: 42379122
    - createdAt: 2026-04-15T15:48:13.000-04:00
    '''
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
