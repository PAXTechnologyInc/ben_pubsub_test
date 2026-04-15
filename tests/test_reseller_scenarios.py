"""Reseller / product-line scenarios: Valutec, Genius, Swipe Simple.

Each request uses a fresh random 8-digit ``vendorTerminalId`` (terminalId).
"""

from boarding.assertions import assert_ack_ok, assert_response_schema
from boarding.payload import random_eight_digit_terminal_id


def _first_terminal(payload: dict) -> dict:
    return payload["data"]["equipmentData"][0]["terminals"][0]


class TestResellerScenarios:
    """branchName (reseller) and terminalType.description (model) rules per product line."""

    def test_valutec_reseller_and_model(self, api, builder, base_payload, logger):
        """Reseller Valutec; model description must contain 'Valutec Only'."""
        reseller = "Valutec"
        model = "Valutec Only PAX A920 MAX"
        tid = random_eight_digit_terminal_id()
        payload = builder.resolve(
            base_payload,
            terminal_id=tid,
            model=model,
            reseller_name=reseller,
        )
        payload["eventType"] = "equipment.terminals.created"

        assert payload["data"]["equipmentData"][0]["hierarchy"]["branchName"] == reseller
        term = _first_terminal(payload)
        assert term["vendorTerminalId"] == tid
        assert len(tid) == 8 and tid.isdigit()
        assert "Valutec Only" in term["terminalType"]["description"]

        logger.info("Valutec: notificationId=%s vendorTerminalId=%s", payload["notificationId"], tid)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)

    def test_genius_reseller_and_model(self, api, builder, base_payload, logger):
        """Reseller Genius; model description must contain 'Genius'."""
        reseller = "Genius"
        model = "Genius Integrated POS Terminal"
        tid = random_eight_digit_terminal_id()
        payload = builder.resolve(
            base_payload,
            terminal_id=tid,
            model=model,
            reseller_name=reseller,
        )
        payload["eventType"] = "equipment.terminals.created"

        assert payload["data"]["equipmentData"][0]["hierarchy"]["branchName"] == reseller
        term = _first_terminal(payload)
        assert term["vendorTerminalId"] == tid
        assert "Genius" in term["terminalType"]["description"]

        logger.info("Genius: notificationId=%s vendorTerminalId=%s", payload["notificationId"], tid)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)

    def test_swipe_simple_reseller_and_model(self, api, builder, base_payload, logger):
        """Reseller Swipe Simple; model description must contain 'Swipe Simple'."""
        reseller = "Swipe Simple"
        model = "Swipe Simple Mobile Reader"
        tid = random_eight_digit_terminal_id()
        payload = builder.resolve(
            base_payload,
            terminal_id=tid,
            model=model,
            reseller_name=reseller,
        )
        payload["eventType"] = "equipment.terminals.created"

        assert payload["data"]["equipmentData"][0]["hierarchy"]["branchName"] == reseller
        term = _first_terminal(payload)
        assert term["vendorTerminalId"] == tid
        assert "Swipe Simple" in term["terminalType"]["description"]

        logger.info("Swipe Simple: notificationId=%s vendorTerminalId=%s", payload["notificationId"], tid)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
