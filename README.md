# WORLDPAY_PAXSTORE_BRIDGE Boarding Automation Test Framework

## Overview

This is a **data-driven** Python automation test framework for the **WORLDPAY_PAXSTORE_BRIDGE** Boarding microservice. It translates the Postman collection (BEN.postman_collection.json) into executable pytest-based test cases that target the `/MerchantSolution/notification` webhook endpoint.

## Architecture

```
C:\Users\terry.liu\works\works\pubsub\code\new\
├── run_boarding_test.py        # Main test script (pytest-based)
├── config.json                 # Environment & test configuration
├── boarding_payload.json       # External data file (Pub/Sub message template)
├── requirements.txt            # Python dependencies
├── README_boarding_test.md     # This document
└── logs/                       # Auto-generated test logs & HTML reports
    ├── boarding_test_YYYYMMDD_HHMMSS.log
    └── report.html
```

### Module Breakdown

| Module / Class | Purpose |
|---|---|
| `PayloadBuilder` | Resolves Postman `{{variable}}` placeholders in the boarding_payload.json (replicates the Postman pre-request script logic) |
| `BoardingApiClient` | HTTP client wrapping the notification endpoint; handles IP/JWT auth, headers, timeouts |
| `setup_logger()` | Configures dual-output logging (file + console) with timestamps |
| `assert_ack_ok / assert_ack_bad_request` | Reusable assertion helpers for the WorldpayResponse schema |
| `TestHealthCheck` | Service liveness verification |
| `TestTerminalCreated` | 14 test cases for `equipment.terminals.created` |
| `TestTerminalUpdated` | Tests for `equipment.terminals.updated` |
| `TestTerminalDeactivated` | Tests for `equipment.terminals.deactivated` |
| `TestTerminalReactivated` | Tests for `equipment.terminals.reactivated` |
| `TestTerminalDeleted` | Tests for `equipment.terminals.deleted` |
| `TestMerchantCreated` | Tests for `merchant.accounts.created` (currently unsupported) |
| `TestMerchantUpdated` | Tests for `merchant.accounts.updated` |
| `TestUnsupportedEvent` | Edge cases: unknown types, empty body, malformed JSON |
| `TestSecurity` | Authentication & IP-based access control tests |
| `TestPostmanVariableLogic` | Unit-level validation of Postman pre-request script logic |
| `TestBoardingE2EFlow` | Full lifecycle: create -> update -> deactivate -> reactivate -> delete |

## Quick Start

### 1. Install Dependencies

```bash
cd C:\Users\terry.liu\works\works\pubsub\code\new
pip install -r requirements.txt
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

QA personnel only need to modify `boarding_payload.json` to change test data. This file is the Pub/Sub message template with `{{variable}}` placeholders that get resolved at runtime.

The `{{variable}}` placeholders are resolved automatically using the same logic as the Postman pre-request script:

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

**Run all tests:**

```bash
python run_boarding_test.py
```

**Run specific test class:**

```bash
pytest run_boarding_test.py::TestTerminalCreated -v
```

**Run a single test:**

```bash
pytest run_boarding_test.py::TestTerminalCreated::test_tc01_create_terminal_success -v
```

**Generate HTML report only:**

```bash
pytest run_boarding_test.py -v --html=logs/report.html --self-contained-html
```

**Run with keyword filter:**

```bash
pytest run_boarding_test.py -v -k "missing_notification"
```

## Test Case Catalog

### Terminal Created (TC-01 to TC-14)

| ID | Test Name | Description | Expected |
|---|---|---|---|
| TC-01 | `test_tc01_create_terminal_success` | Valid terminal created event | 200 ACK |
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

## Boarding Flow (Terminal Created)

```
1. Receive POST /MerchantSolution/notification
2. Extract notificationId, eventType, data
3. Convert data to TerminalCreatedEventData
4. For each equipmentData:
   a. Validate: hierarchy, business, location, terminals
   b. Determine reseller (Worldpay / Swipe Simple / Valutec / Genius)
   c. Search/Create Merchant in PAXSTORE
   d. Validate terminal not already exists
   e. Create Terminal in PAXSTORE
   f. Push Terminal APK (BroadPOS Vantiv / Valutec / SwipeSimple / Genius)
   g. Push RKI Key (if not Valutec)
5. Return 200 ACK (or PATCH error on failure)
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `ConnectionRefusedError` | Ensure the bridge service is running on the configured `base_url` |
| 401 Unauthorized | Check `auth.mode` and `x_forwarded_for` in config.json |
| Tests pass but PAXSTORE operations fail | Check the service logs; async errors are sent via PATCH |
| `boarding_payload.json` not found | Verify `test_data.payload_file` path in config.json |
| Unresolved `{{variables}}` | Check that `test_data.*` fields in config.json match the placeholders |
