
import logging
import time

import requests

from trips.utils.exceptions import GeocodingError

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "TruckTripPlanner/1.0 (assessment-project)"

_last_request_time = 0.0
_MIN_INTERVAL_SECONDS = 1.0


class GeocodingService:
    """Resolves human-readable location strings to coordinates."""

    @staticmethod
    def _throttle():
        global _last_request_time
        elapsed = time.time() - _last_request_time
        if elapsed < _MIN_INTERVAL_SECONDS:
            time.sleep(_MIN_INTERVAL_SECONDS - elapsed)
        _last_request_time = time.time()

    @classmethod
    def geocode(cls, location: str) -> dict:
        """
        Resolve a location string into coordinates.

        Returns:
            dict: {"lat": float, "lng": float, "display_name": str}

        Raises:
            GeocodingError: if the location cannot be resolved.
        """
        if not location or not location.strip():
            raise GeocodingError("Location string is empty.")

        cls._throttle()

        try:
            response = requests.get(
                NOMINATIM_URL,
                params={
                    "q": location,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 0,
                },
                headers={"User-Agent": USER_AGENT},
                timeout=10,
            )
            response.raise_for_status()
            results = response.json()
        except requests.RequestException as exc:
            logger.error("Geocoding request failed for '%s': %s", location, exc)
            raise GeocodingError(f"Could not reach geocoding service for '{location}'.") from exc

        if not results:
            raise GeocodingError(f"No coordinates found for location: '{location}'.")

        result = results[0]
        return {
            "lat": float(result["lat"]),
            "lng": float(result["lon"]),
            "display_name": result.get("display_name", location),
        }
