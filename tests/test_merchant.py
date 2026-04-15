"""TEST SUITE: Merchant Events — Created (unsupported) / Updated."""

from boarding.payload import eastern_now, random_notification_id
from boarding.assertions import (
    assert_ack_ok,
    assert_ack_bad_request,
    assert_response_schema,
    assert_error_contains,
)


class TestMerchantCreated:
    """Tests for the merchant.accounts.created event type.

    Note: In the current codebase, merchant.accounts.created is commented out
    and returns null from convertMerchantEvent(), resulting in an error.
    """

    def _make_merchant_payload(self, builder) -> dict:
        return {
            "eventType": "merchant.accounts.created",
            "notificationId": int(random_notification_id()),
            "eventCount": 1,
            "version": "2.0",
            "createdAt": eastern_now(),
            "data": {
                "merchantAccounts": [
                    {
                        "hierarchy": {
                            "salesOrganizationCode": "12",
                            "salesOrganizationName": "Your Sales Organization Name",
                            "salesChannelCode": "73",
                            "salesChannelName": "Your Sales Channel Name",
                            "partnerGroupId": "41",
                            "partnerGroupName": "ABC Corp",
                            "nationalCode": "NATNL",
                            "nationalName": "DEF company",
                            "superChainCode": "DA012",
                            "superChainName": "ABC CORP",
                            "branchCode": "9999",
                            "branchName": "ABC 123",
                            "divisionCode": "DIV",
                            "divisionName": "My Division Name",
                            "chainCode": "0X1234",
                            "chainName": "My Chain Name",
                            "storeNumber": "000000001",
                            "storeName": "My Store Name",
                            "merchantId": "12345678909876",
                            "merchantName": "Merchant Name",
                        },
                        "business": {
                            "location": {
                                "storeNumber": "000000001",
                                "storeName": "Test1111",
                                "status": "ACTIVE",
                                "physicalAddress": {
                                    "addressLine1": "4355 N Coalwhipe St.",
                                    "addressLine2": "suite 104",
                                    "city": "Denver",
                                    "state": "CO",
                                    "country": "US",
                                    "postalCode": "80237",
                                },
                                "primaryContact": {
                                    "firstName": "John",
                                    "lastName": "Doe",
                                    "phoneNumber": "1234569870",
                                },
                            },
                            "primaryContact": {
                                "firstName": "John",
                                "lastName": "Doe",
                                "phoneNumber": "1234569870",
                            },
                        },
                    }
                ]
            },
        }

    def test_tc60_create_merchant_unsupported(self, api, builder, logger):
        """TC-60: merchant.accounts.created is currently unsupported; expect 200 ACK but async error."""
        logger.info("=" * 60)
        logger.info("TC-60: Create Merchant (unsupported event)")
        logger.info("=" * 60)

        payload = self._make_merchant_payload(builder)
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-60 PASSED (event unsupported; async PATCH error expected)")


class TestMerchantUpdated:
    """Tests for the merchant.accounts.updated event type."""

    def _make_merchant_updated_payload(self) -> dict:
        return {
            "eventType": "merchant.accounts.updated",
            "notificationId": int(random_notification_id()),
            "eventCount": 1,
            "version": "2.0",
            "createdAt": eastern_now(),
            "data": {
                "merchantAccounts": [
                    {
                        "hierarchy": {
                            "salesOrganizationCode": "12",
                            "salesOrganizationName": "Your Sales Organization Name",
                            "salesChannelCode": "73",
                            "salesChannelName": "Your Sales Channel Name",
                            "partnerGroupId": "41",
                            "partnerGroupName": "ABC Corp",
                            "nationalCode": "NATNL",
                            "nationalName": "DEF company",
                            "superChainCode": "DA012",
                            "superChainName": "ABC CORP",
                            "branchCode": "9999",
                            "branchName": "ABC 123",
                            "divisionCode": "DIV",
                            "divisionName": "My Division Name",
                            "chainCode": "0X1234",
                            "chainName": "My Chain Name",
                            "storeNumber": "000000001",
                            "storeName": "My Store Name",
                            "merchantId": "12345678909876",
                            "merchantName": "Merchant Name",
                        },
                        "business": {
                            "location": {
                                "storeNumber": "000000001",
                                "storeName": "Updated Store",
                                "status": "ACTIVE",
                                "physicalAddress": {
                                    "addressLine1": "100 Main St",
                                    "addressLine2": None,
                                    "city": "New York",
                                    "state": "NY",
                                    "country": "US",
                                    "postalCode": "10001",
                                },
                                "primaryContact": {
                                    "firstName": "Jane",
                                    "lastName": "Smith",
                                    "phoneNumber": "9876543210",
                                },
                            },
                            "primaryContact": {
                                "firstName": "Jane",
                                "lastName": "Smith",
                                "phoneNumber": "9876543210",
                            },
                        },
                    }
                ]
            },
        }

    def test_tc70_update_merchant_success(self, api, logger):
        """TC-70: Valid merchant update should return 200 ACK."""
        logger.info("=" * 60)
        logger.info("TC-70: Update Merchant - Happy Path")
        logger.info("=" * 60)

        payload = self._make_merchant_updated_payload()
        resp = api.send_notification(payload)
        assert_ack_ok(resp)
        assert_response_schema(resp)
        logger.info("TC-70 PASSED")

    def test_tc71_update_merchant_missing_notification_id(self, api, logger):
        """TC-71: Missing notificationId should return 400."""
        logger.info("=" * 60)
        logger.info("TC-71: Update Merchant - Missing notificationId")
        logger.info("=" * 60)

        payload = self._make_merchant_updated_payload()
        del payload["notificationId"]
        resp = api.send_notification(payload)
        assert_ack_bad_request(resp)
        assert_response_schema(resp)
        assert_error_contains(resp, expected_code="PARAMETER_VALIDATION_ERROR", expected_target="notificationId")
        logger.info("TC-71 PASSED")
