"""TEST SUITE: Postman Pre-request Script Logic Verification."""

import json
import re

from boarding.payload import (
    eastern_now,
    random_notification_id,
    random_eight_digit_terminal_id,
    generate_worldpay_mid,
)


class TestPostmanVariableLogic:
    """Verify the Postman pre-request script logic is correctly translated."""

    def test_eastern_time_format(self):
        """The generated createdAt should be a valid ISO-like timestamp."""
        ts = eastern_now()
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{4}", ts), f"Bad format: {ts}"

    def test_notification_id_length(self):
        """notificationId should be exactly 8 digits."""
        nid = random_notification_id()
        assert len(nid) == 8
        assert nid.isdigit()

    def test_eight_digit_terminal_id(self):
        """vendorTerminalId-style ID should be 8 numeric characters."""
        tid = random_eight_digit_terminal_id()
        assert len(tid) == 8
        assert tid.isdigit()

    def test_worldpay_mid_deterministic(self):
        """Same merchantName should always produce the same worldpayMID."""
        name = "THORNTONS #0304"
        mid1 = generate_worldpay_mid(name)
        mid2 = generate_worldpay_mid(name)
        assert mid1 == mid2

    def test_worldpay_mid_uniqueness(self):
        """Different merchantNames should produce different worldpayMIDs."""
        mid1 = generate_worldpay_mid("Merchant A")
        mid2 = generate_worldpay_mid("Merchant B")
        assert mid1 != mid2

    def test_payload_variable_resolution(self, builder, base_payload):
        """All {{variable}} placeholders should be resolved after calling resolve()."""
        payload = builder.resolve(base_payload)
        raw = json.dumps(payload)
        unresolved = re.findall(r"\{\{\w+\}\}", raw)
        assert len(unresolved) == 0, f"Unresolved variables found: {unresolved}"
