# tests/test_geo_fallback.py
"""Test geo enrichment fallback chain with mocked providers."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.geo_service import GeoService, GeoResult


@pytest.mark.asyncio
async def test_provider_a_succeeds():
    """Provider A works → enriched with provider A data."""
    service = GeoService()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "country": "United States",
        "city": "New York",
        "regionName": "New York",
        "lat": 40.7128,
        "lon": -74.0060,
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await service.enrich("8.8.8.8")
        assert result.country == "United States"
        assert result.provider == "ip-api.com"


@pytest.mark.asyncio
async def test_provider_a_fails_provider_b_succeeds():
    """Provider A down → Provider B enriches."""
    service = GeoService()

    call_count = 0

    async def mock_get(url, **kwargs):
        nonlocal call_count
        call_count += 1
        if "ip-api.com" in url:
            raise Exception("Provider A is down")
        else:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "country_name": "Germany",
                "city": "Berlin",
                "region": "Berlin",
                "latitude": 52.52,
                "longitude": 13.405,
            }
            mock_resp.raise_for_status = MagicMock()
            return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await service.enrich("1.2.3.4")
        assert result.country == "Germany"
        assert result.provider == "ipapi.co"


@pytest.mark.asyncio
async def test_both_providers_down():
    """Both providers down → submission still succeeds, no geo data."""
    service = GeoService()

    async def mock_get(url, **kwargs):
        raise Exception("Provider is down")

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await service.enrich("1.2.3.4")
        assert result.country is None
        assert result.city is None
        assert result.provider is None