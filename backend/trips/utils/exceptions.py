class TripPlanningError(Exception):
    """Base exception for trip-planning related errors."""


class GeocodingError(TripPlanningError):
    """Raised when a location string cannot be geocoded."""


class RoutingError(TripPlanningError):
    """Raised when a route cannot be calculated between two points."""


class HOSValidationError(TripPlanningError):
    """Raised when Hours-of-Service constraints cannot be satisfied."""
