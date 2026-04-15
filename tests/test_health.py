"""TEST SUITE: Health Check — verify service is alive before running boarding tests."""


class TestHealthCheck:
    """Verify service is alive before running boarding tests."""

    def test_health_endpoint(self, api, logger):
        logger.info("=" * 60)
        logger.info("TEST: Health Check")
        logger.info("=" * 60)
        resp = api.health_check()
        assert resp.status_code == 200
        assert "Healthy" in resp.text
