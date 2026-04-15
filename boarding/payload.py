"""Payload building utilities — resolves Postman-style {{variable}} placeholders."""

import copy
import hashlib
import json
import random
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional


def load_json(path: Path) -> dict:
    """Load and parse a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def eastern_now() -> str:
    """Return the current Eastern-time timestamp in ISO-like format."""
    eastern_offset = timedelta(hours=-4)
    now = datetime.now(timezone(eastern_offset))
    return now.strftime("%Y-%m-%dT%H:%M:%S.000%z")


def random_notification_id(length: int = 8) -> str:
    """Generate a zero-padded random numeric notification ID."""
    return str(random.randint(0, 10**length - 1)).zfill(length)


def random_eight_digit_terminal_id() -> str:
    """Random 8-digit numeric string (zero-padded), for unique vendorTerminalId per request."""
    return random_notification_id(8)


def generate_worldpay_mid(merchant_name: str) -> str:
    """Deterministically derive a 16-digit Worldpay MID from a merchant name."""
    md5 = hashlib.md5(merchant_name.encode()).hexdigest()
    unique_number = int(md5[:16], 16) % (10**16)
    return str(unique_number)

def generate_terminal_mid(merchant_name: str) -> str:
    """Deterministically derive a 16-digit Worldpay MID from a merchant name."""
    md5 = hashlib.md5(merchant_name.encode()).hexdigest()
    unique_number = int(md5[:16], 16) % (10**16)
    return str(unique_number)


def _terminal_id_from_test_data(td: dict) -> Optional[str]:
    """Non-empty ``test_data.terminal_id`` from config, else ``None`` (caller will randomize)."""
    raw = td.get("terminal_id")
    if raw is None:
        return None
    s = str(raw).strip()
    return s if s else None


class PayloadBuilder:
    """Build event payloads by resolving Postman-style template variables."""

    def __init__(self, config: dict):
        self.config = config
        td = config.get("test_data", {})
        self.merchant_name = td.get("merchant_name", "Test Merchant")
        self.config_terminal_id = _terminal_id_from_test_data(td)
        self.model = td.get("model", "A920Pro")
        self.reseller_name = td.get("reseller_name", "Worldpay")

    def resolve(
        self,
        payload: dict,
        *,
        merchant_name: Optional[str] = None,
        terminal_id: Optional[str] = None,
        model: Optional[str] = None,
        reseller_name: Optional[str] = None,
        notification_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> dict:
        """Deep-copy payload and replace {{variable}} placeholders.

        Omit optional kwargs to use values from config ``test_data``.
        If ``terminal_id`` is omitted and config has no ``terminal_id``, a random
        8-digit id is generated (see ``random_eight_digit_terminal_id``).
        """
        resolved = copy.deepcopy(payload)
        mn = self.merchant_name if merchant_name is None else merchant_name
        if terminal_id is not None:
            tid = terminal_id
        elif self.config_terminal_id is not None:
            tid = self.config_terminal_id
        else:
            tid = random_eight_digit_terminal_id()
        mo = self.model if model is None else model
        rn = self.reseller_name if reseller_name is None else reseller_name
        variables = {
            "notificationId": random_notification_id() if notification_id is None else notification_id,
            "createdAt": eastern_now() if created_at is None else created_at,
            "merchantName": mn,
            "worldpayMID": generate_worldpay_mid(mn),
            "terminalId": tid,
            "model": mo,
            "resellerName": rn,
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
