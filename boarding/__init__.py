"""
WORLDPAY_PAXSTORE_BRIDGE Boarding Core Library
===============================================
Reusable components: API client, payload builder, logger, assertions.
"""

from boarding.client import BoardingApiClient
from boarding.payload import PayloadBuilder
from boarding.logger import setup_logger
from boarding.assertions import (
    assert_ack_ok,
    assert_ack_bad_request,
    assert_response_schema,
    assert_error_contains,
    assert_paxstore_success,
    assert_paxstore_total_count,
)
from boarding.paxstore_bridge import (
    PaxstoreBridge, 
    SearchTerminalApkResult, 
    TerminalApkInfo,
    SearchTerminalResult,
    TerminalInfo
)

__all__ = [
    "BoardingApiClient",
    "PayloadBuilder",
    "setup_logger",
    "assert_ack_ok",
    "assert_ack_bad_request",
    "assert_response_schema",
    "assert_error_contains",
    "assert_paxstore_success",
    "assert_paxstore_total_count",
    "PaxstoreBridge",
    "SearchTerminalApkResult",
    "TerminalApkInfo",
    "SearchTerminalResult",
    "TerminalInfo",
]
