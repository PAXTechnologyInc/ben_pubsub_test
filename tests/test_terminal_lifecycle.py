"""TEST SUITE: Terminal Lifecycle Events — Updated / Deactivated / Reactivated / Deleted."""

from boarding.payload import PayloadBuilder
from boarding.assertions import assert_ack_ok, assert_response_schema


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
