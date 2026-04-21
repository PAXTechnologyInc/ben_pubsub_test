"""Pytest fixtures shared across all boarding test modules."""

import pytest

from boarding.constants import CONFIG_PATH, PROJECT_ROOT
from boarding.payload import load_json, PayloadBuilder
from boarding.client import BoardingApiClient
from boarding.logger import setup_logger
from boarding.paxstore_bridge import PaxstoreBridge


@pytest.fixture(scope="session")
def config():
    return load_json(CONFIG_PATH)


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
    payload_path = PROJECT_ROOT / config["test_data"].get("payload_file", "boarding_payload.json")
    return load_json(payload_path)


@pytest.fixture(scope="session")
def paxstore():
    """Paxstore SDK bridge for calling Java API from Python."""
    return PaxstoreBridge(str(PROJECT_ROOT))
