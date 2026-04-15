"""Logging configuration — dual-output (file + console) with timestamps."""

import logging
import sys
from datetime import datetime

from boarding.constants import PROJECT_ROOT


def setup_logger(config: dict) -> logging.Logger:
    """Create and configure the boarding_test logger based on config."""
    log_cfg = config.get("logging", {})
    log_dir = PROJECT_ROOT / log_cfg.get("log_dir", "logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / log_cfg.get("log_file", "boarding_test_{timestamp}.log").replace(
        "{timestamp}", timestamp
    )

    logger = logging.getLogger("boarding_test")
    logger.setLevel(getattr(logging, log_cfg.get("level", "DEBUG")))
    logger.handlers.clear()

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    if log_cfg.get("console_output", True):
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    return logger
