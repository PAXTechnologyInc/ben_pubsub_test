"""Shared constants and JSON schemas used across the test framework."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
DEFAULT_PAYLOAD_FILE = PROJECT_ROOT / "boarding_payload.json"

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
