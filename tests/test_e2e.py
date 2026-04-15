"""TEST SUITE: Data-Driven Boarding End-to-End Flow."""

import time

from boarding.assertions import assert_ack_ok, assert_response_schema


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
