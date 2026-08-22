# app/services/geo_service.py
import logging
from typing import Optional, Dict, Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeoResult:
    def __init__(
        self,
        country: Optional[str] = None,
        city: Optional[str] = None,
        region: Optional[str] = None,
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        self.country = country
        self.city = city
        self.region = region
        self.latitude = latitude
        self.longitude = longitude
        self.provider = provider

    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "city": self.city,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "geo_provider": self.provider,
        }


class GeoService:
    """IP → geolocation enrichment with a two-provider fallback chain.

    Provider A: ip-api.com
    Provider B: ipapi.co
    Both down: return empty GeoResult — the submission still succeeds.
    """

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    async def enrich(self, ip_address: str) -> GeoResult:
        # Skip private/localhost IPs
        if ip_address in ("127.0.0.1", "::1", "localhost", "testclient"):
            return GeoResult()

        # Try provider A
        result = await self._try_provider_a(ip_address)
        if result:
            return result

        # Try provider B
        result = await self._try_provider_b(ip_address)
        if result:
            return result

        # All providers down — degrade gracefully
        logger.warning(f"All geo providers failed for IP {ip_address}")
        return GeoResult()

    async def _try_provider_a(self, ip: str) -> Optional[GeoResult]:
        """ip-api.com — free, no key, 45 req/min."""
        try:
            url = f"{settings.GEO_PROVIDER_A_URL}{ip}"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "success":
                    return None

                return GeoResult(
                    country=data.get("country"),
                    city=data.get("city"),
                    region=data.get("regionName"),
                    latitude=str(data.get("lat", "")),
                    longitude=str(data.get("lon", "")),
                    provider="ip-api.com",
                )
        except Exception as e:
            logger.warning(f"Geo provider A (ip-api.com) failed: {e}")
            return None

    async def _try_provider_b(self, ip: str) -> Optional[GeoResult]:
        """ipapi.co — free tier ~1,000 lookups/day."""
        try:
            url = f"{settings.GEO_PROVIDER_B_URL}{ip}/json/"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                if data.get("error"):
                    return None

                return GeoResult(
                    country=data.get("country_name"),
                    city=data.get("city"),
                    region=data.get("region"),
                    latitude=str(data.get("latitude", "")),
                    longitude=str(data.get("longitude", "")),
                    provider="ipapi.co",
                )
        except Exception as e:
            logger.warning(f"Geo provider B (ipapi.co) failed: {e}")
            return None


# Singleton for dependency injection — can be replaced in tests
geo_service = GeoService()