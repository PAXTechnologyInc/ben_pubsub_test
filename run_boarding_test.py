"""
WORLDPAY_PAXSTORE_BRIDGE Boarding Automation Test Runner
========================================================
Entry point for running the full boarding test suite.

Usage:
    python run_boarding_test.py          # run all tests with HTML report
    pytest tests/ -v                     # run via pytest directly
    pytest tests/test_terminal_created.py -v   # run a single module
"""

import sys
from pathlib import Path

import pytest
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

PROJECT_ROOT = Path(__file__).resolve().parent


def _print_banner():
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print("  WORLDPAY_PAXSTORE_BRIDGE - Boarding Automation Test Suite")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")


def _print_summary(result: int):
    color = Fore.GREEN if result == 0 else Fore.RED
    status = "ALL TESTS PASSED" if result == 0 else "SOME TESTS FAILED"
    print(f"\n{color}{'=' * 70}")
    print(f"  {status}")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    _print_banner()

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    args = [
        str(PROJECT_ROOT / "tests"),
        "-v",
        "--tb=short",
        f"--html={log_dir / 'report.html'}",
        "--self-contained-html",
    ]
    exit_code = pytest.main(args)
    _print_summary(exit_code)
    sys.exit(exit_code)
