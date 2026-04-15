"""HTTP client wrapping the /MerchantSolution/notification endpoint."""

import json
import logging

import requests


class BoardingApiClient:
    """Send boarding notifications and perform health checks against the bridge service."""

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
        # "none": only Content-Type (matches Postman / open dev endpoints without spoofed client IP).
        if mode == "none":
            pass
        elif mode == "ip":
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
        self.logger.info("Health check -> %s %s", resp.status_code, resp.text)
        return resp

    def send_notification(self, payload: dict) -> requests.Response:
        headers = self._headers()
        body_str = json.dumps(payload, ensure_ascii=False)
        self.logger.debug("POST %s", self.notification_url)
        self.logger.debug("Headers: %s", json.dumps(headers))
        # self.logger.debug("Payload: %s", body_str)

        resp = requests.post(
            self.notification_url,
            headers=headers,
            data=body_str,
            timeout=self.timeout,
        )
        self.logger.info("Response [%s]: %s", resp.status_code, resp.text)
        return resp
