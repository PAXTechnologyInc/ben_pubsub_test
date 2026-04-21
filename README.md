# WORLDPAY_PAXSTORE_BRIDGE Boarding Automation Test Framework

## Overview

This is a **data-driven** Python automation test framework for the **WORLDPAY_PAXSTORE_BRIDGE** Boarding microservice. It translates the Postman collection (BEN.postman_collection.json) into executable pytest-based test cases that target the `/MerchantSolution/notification` webhook endpoint.

## Project Structure

```
ben_pubsub_test/
├── run_boarding_test.py            # Entry point — runs full suite with HTML report
├── pytest.ini                      # Pytest discovery configuration
├── config.json                     # Environment & test configuration
├── boarding_payload.json           # External data file (Pub/Sub message template)
├── paxstore_config.yml             # Paxstore API credentials
├── pom.xml                         # Maven project for Paxstore SDK
├── requirements.txt                # Python dependencies
├── README.md                       # This document
│
├── boarding/                       # Core library package
│   ├── __init__.py                 # Package exports
│   ├── constants.py                # Shared constants & JSON schemas
│   ├── client.py                   # BoardingApiClient (HTTP client)
│   ├── payload.py                  # PayloadBuilder & utility functions
│   ├── logger.py                   # Logging configuration
│   ├── assertions.py               # Reusable assertion helpers
│   └── paxstore_bridge.py          # Python-to-Java bridge for Paxstore SDK
│
├── src/main/kotlin/com/pax/test/   # Kotlin Paxstore SDK wrapper
│   ├── PaxstoreConfig.kt           # YAML config loader
│   ├── PaxstoreClient.kt           # SDK wrapper client
│   ├── SearchTerminalJson.kt       # Terminal search (JSON output)
│   └── SearchTerminalApkJson.kt    # APK search (JSON output)
│
├── tests/                          # Test suite (pytest-discovered)
│   ├── conftest.py                 # Shared fixtures (config, api, builder, logger, paxstore)
│   ├── test_health.py              # Service liveness check
│   ├── test_terminal_created.py    # TC-01 to TC-14: equipment.terminals.created
│   ├── test_terminal_lifecycle.py  # TC-20 to TC-50: updated/deactivated/reactivated/deleted
│   ├── test_merchant.py            # TC-60 to TC-71: merchant events
│   ├── test_edge_cases.py          # TC-80 to TC-91: unsupported events & security
│   ├── test_postman_logic.py       # Unit tests for Postman variable resolution
│   └── test_e2e.py                 # TC-100: full terminal lifecycle E2E
│
└── logs/                           # Auto-generated test logs & HTML reports
    ├── boarding_test_YYYYMMDD_HHMMSS.log
    └── report.html
```

### Layer Architecture

| Layer | Package / File | Responsibility |
|-------|---------------|----------------|
| **Entry Point** | `run_boarding_test.py` | CLI runner — invokes pytest with HTML report |
| **Test Layer** | `tests/` | All test classes and fixtures; depends on `boarding` |
| **Core Library** | `boarding/` | Reusable, test-independent components |
| ↳ API Client | `boarding/client.py` | HTTP requests to the bridge service |
| ↳ Payload | `boarding/payload.py` | Template resolution & data generation |
| ↳ Assertions | `boarding/assertions.py` | Schema & status validation |
| ↳ Logger | `boarding/logger.py` | Dual-output logging setup |
| ↳ Constants | `boarding/constants.py` | Paths, schemas, shared values |
| **Config** | `config.json` | Environment, auth, retry settings |
| **Test Data** | `boarding_payload.json` | Pub/Sub message template with `{{variables}}` |

## Quick Start

### 1. Install Dependencies

**Python dependencies:**

```bash
pip install -r requirements.txt
```

**Maven/Kotlin dependencies (for Paxstore SDK):**

```bash
mvn compile
```

### 2. Configure the Environment

Edit `config.json` to match your target environment:

```json
{
    "service": {
        "base_url": "http://localhost:80",
        "notification_endpoint": "/MerchantSolution/notification",
        "health_endpoint": "/health"
    },
    "auth": {
        "mode": "ip",
        "x_forwarded_for": "127.0.0.1"
    },
    "test_data": {
        "payload_file": "boarding_payload.json",
        "merchant_name": "THORNTONS #0304",
        "terminal_id": "PAX12345678",
        "model": "A920Pro",
        "reseller_name": "Worldpay"
    }
}
```

**Key configuration options:**

| Field | Description |
|---|---|
| `service.base_url` | The running service URL (e.g., `http://localhost:80` for local, or the ALB/ECS URL) |
| `auth.mode` | `ip` (send X-Forwarded-For) or `jwt` (send Bearer token) |
| `test_data.payload_file` | Path to the Pub/Sub message template |
| `test_data.merchant_name` | Merchant name injected into `{{merchantName}}` |
| `test_data.terminal_id` | Terminal ID injected into `{{terminalId}}` |
| `test_data.model` | Terminal model injected into `{{model}}` |
| `test_data.reseller_name` | Reseller name injected into `{{resellerName}}` |

### 3. Modify Test Data

QA personnel only need to modify `boarding_payload.json` to change test data. The `{{variable}}` placeholders are resolved automatically:

| Variable | Source | Description |
|---|---|---|
| `{{notificationId}}` | Auto-generated | Random 8-digit number |
| `{{createdAt}}` | Auto-generated | Current Eastern time in ISO format |
| `{{merchantName}}` | config.json | `test_data.merchant_name` |
| `{{worldpayMID}}` | Auto-generated | MD5-based unique ID from merchantName |
| `{{terminalId}}` | config.json | `test_data.terminal_id` |
| `{{model}}` | config.json | `test_data.model` |
| `{{resellerName}}` | config.json | `test_data.reseller_name` |

### 4. Run Tests

**Run all tests (with banner & HTML report):**

```bash
python run_boarding_test.py
```

**Run all tests via pytest directly:**

```bash
pytest -v
```

**Run specific test module:**

```bash
pytest tests/test_terminal_created.py -v
```

**Run a single test:**

```bash
pytest tests/test_terminal_created.py::TestTerminalCreated::test_tc01_create_terminal_success -v
```

**Run with keyword filter:**

```bash
pytest -v -k "missing_notification"
```

**Generate HTML report only:**

```bash
pytest -v --html=logs/report.html --self-contained-html
```

## Test Case Catalog

### Terminal Created (TC-01 to TC-14)

| ID | Test Name | Description | Expected |
|---|---|---|---|
| TC-01 | `test_tc01_create_terminal_success` | Valid terminal created event + Paxstore APK verification | 200 ACK + APK count check |
| TC-02 | `test_tc02_create_terminal_missing_notification_id` | Missing notificationId | 400 BAD_REQUEST |
| TC-03 | `test_tc03_create_terminal_missing_event_type` | Missing eventType | 200 ACK (async PATCH error) |
| TC-04 | `test_tc04_create_terminal_missing_data` | Missing data field | 200 ACK (async PATCH error) |
| TC-05 | `test_tc05_create_terminal_empty_equipment_data` | Empty equipmentData[] | 200 ACK (async PATCH error) |
| TC-06 | `test_tc06_create_terminal_missing_hierarchy` | Missing hierarchy | 200 ACK (validation error) |
| TC-07 | `test_tc07_create_terminal_missing_hierarchy_merchant_id` | Missing hierarchy.merchantId | 200 ACK (validation error) |
| TC-08 | `test_tc08_create_terminal_missing_location` | Missing location | 200 ACK (validation error) |
| TC-09 | `test_tc09_create_terminal_missing_business` | Missing business | 200 ACK (validation error) |
| TC-10 | `test_tc10_create_terminal_missing_terminals_array` | Missing terminals[] | 200 ACK (validation error) |
| TC-11 | `test_tc11_create_terminal_missing_location_store_name` | Missing location.storeName | 200 ACK (validation error) |
| TC-12 | `test_tc12_create_terminal_missing_physical_address_country` | Missing physicalAddress.country | 200 ACK (validation error) |
| TC-13 | `test_tc13_create_terminal_missing_primary_contact` | Missing location.primaryContact | 200 ACK (validation error) |
| TC-14 | `test_tc14_create_terminal_missing_vendor_terminal_id` | Missing vendorTerminalId | 200 ACK (validation error) |

### Terminal Lifecycle (TC-20 to TC-50)

| ID | Test Name | Description | Expected |
|---|---|---|---|
| TC-20 | `test_tc20_update_terminal_success` | Valid terminal update | 200 ACK |
| TC-30 | `test_tc30_deactivate_terminal_success` | Valid terminal deactivation | 200 ACK |
| TC-40 | `test_tc40_reactivate_terminal_success` | Valid terminal reactivation | 200 ACK |
| TC-50 | `test_tc50_delete_terminal_success` | Valid terminal deletion | 200 ACK |

### Merchant Events (TC-60 to TC-71)

| ID | Test Name | Description | Expected |
|---|---|---|---|
| TC-60 | `test_tc60_create_merchant_unsupported` | merchant.accounts.created (disabled) | 200 ACK + async error |
| TC-70 | `test_tc70_update_merchant_success` | Valid merchant update | 200 ACK |
| TC-71 | `test_tc71_update_merchant_missing_notification_id` | Missing notificationId | 400 BAD_REQUEST |

### Edge Cases & Security (TC-80 to TC-91)

| ID | Test Name | Description | Expected |
|---|---|---|---|
| TC-80 | `test_tc80_unsupported_event_type` | Unknown eventType string | 200 ACK + async error |
| TC-81 | `test_tc81_empty_body` | Empty JSON body {} | 400 BAD_REQUEST |
| TC-82 | `test_tc82_malformed_json` | Invalid JSON payload | 400 or 500 |
| TC-90 | `test_tc90_access_without_auth` | No auth header | 401 |
| TC-91 | `test_tc91_access_with_blocked_ip` | Non-allowed IP | 401 |

### Postman Logic & E2E (TC-100)

| ID | Test Name | Description |
|---|---|---|
| - | `test_eastern_time_format` | Validates createdAt ISO format |
| - | `test_notification_id_length` | Validates 8-digit notificationId |
| - | `test_worldpay_mid_deterministic` | Same name -> same MID |
| - | `test_worldpay_mid_uniqueness` | Different name -> different MID |
| - | `test_payload_variable_resolution` | All {{vars}} resolved |
| TC-100 | `test_tc100_full_terminal_lifecycle` | Full E2E: create -> update -> deactivate -> reactivate -> delete |

## Paxstore SDK Integration

### Overview

TC-01 (`test_tc01_create_terminal_success`) includes **end-to-end verification** via the Paxstore SDK. After sending the terminal creation notification to the Bridge service, the test verifies that the terminal was correctly provisioned in Paxstore by checking the APK push count.

### TC-01 Test Flow

```
Step 1: Send Notification
├── POST /MerchantSolution/notification
├── Payload includes vendorTerminalId (from boarding_payload.json)
└── Assert: HTTP 200 ACK

Step 2: Wait for Async Processing
└── Sleep 5 seconds (backend processes notification asynchronously)

Step 3: Verify APK Count via Paxstore SDK
├── Calculate Paxstore TID from vendorTerminalId
├── Call Paxstore searchTerminalApk API
└── Assert: APK count matches expected value based on model
```

### TID Calculation Rule

The Paxstore TID is calculated from the `vendorTerminalId` in the payload:

```
Paxstore TID = "00000022" + vendorTerminalId
```

**Examples:**

| vendorTerminalId | Paxstore TID |
|------------------|--------------|
| `7080` | `000000227080` |
| `76650438` | `0000002276650438` |

### Expected APK Count by Model

The expected APK count is determined by the `model` field in `config.json`:

| Model Contains | Expected APK Count | Log Output |
|----------------|-------------------|------------|
| `valutec` or `vantiv` | 1 | `Model matched [Valutec/Vantiv], expected_count=1` |
| `swipe simple` or `genius` | 2 | `Model matched [Swipe Simple/Genius], expected_count=2` |
| Other (unknown) | 1 (default) | `WARNING: Unknown model '...', using DEFAULT expected_count=1` |

### Paxstore Configuration

Edit `paxstore_config.yml` with your Paxstore API credentials:

```yaml
paxstore:
  baseUrl: "https://api.paxstores.com/p-market-api"
  apiKey: "YOUR_API_KEY"
  token: "YOUR_API_TOKEN"
```

### Architecture

The Paxstore SDK integration uses a **Python-to-Java bridge** architecture:

```
Python Test (pytest)
    │
    ├── boarding/paxstore_bridge.py  (Python wrapper)
    │       │
    │       └── subprocess call ──────────────────┐
    │                                             │
    │                                             ▼
    │                              Kotlin/Maven Project
    │                              ├── SearchTerminalApkJson.kt
    │                              └── Paxstore Java SDK
    │                                     │
    │                                     ▼
    │                              Paxstore API
    │                                     │
    ◄─────────────── JSON Response ───────┘
```

## Service API Reference

### Endpoint: POST /MerchantSolution/notification

**Request:**

```json
{
  "eventType": "equipment.terminals.created",
  "notificationId": "12345678",
  "eventCount": 1,
  "version": 2.0,
  "createdAt": "2025-04-10T12:30:00.000-0400",
  "data": {
    "equipmentData": [{ ... }]
  }
}
```

**Success Response (200):**

```json
{
  "httpStatusCode": "200",
  "httpStatusMessage": "OK"
}
```

**Error Response (400):**

```json
{
  "httpStatusCode": "400",
  "httpStatusMessage": "Bad Request",
  "errors": [
    {
      "errorCode": "PARAMETER_VALIDATION_ERROR",
      "errorMessage": "Notification Id is missing",
      "target": "notificationId"
    }
  ]
}
```

### Key Behavior Notes

1. **Immediate 400**: Only returned when `notificationId` is missing (cannot send PATCH without it).
2. **Async Error Reporting**: For all other validation failures (missing eventType, data, equipmentData fields), the service returns **200 ACK immediately** and reports errors asynchronously via a PATCH request to the Worldpay callback URL.
3. **Security**: Requests must include either a valid JWT token (OAuth2) or come from an allowed IP address (checked via `X-Forwarded-For` header). Local addresses (127.0.0.1, ::1) are always accepted.

## Troubleshooting

| Issue | Solution |
|---|---|
| `ConnectionRefusedError` | Ensure the bridge service is running on the configured `base_url` |
| 401 Unauthorized | Check `auth.mode` and `x_forwarded_for` in config.json |
| Tests pass but PAXSTORE operations fail | Check the service logs; async errors are sent via PATCH |
| `boarding_payload.json` not found | Verify `test_data.payload_file` path in config.json |
| Unresolved `{{variables}}` | Check that `test_data.*` fields in config.json match the placeholders |
| `ModuleNotFoundError: boarding` | Run from the project root, or add it to PYTHONPATH |
