
import logging

import requests

from trips.utils.exceptions import RoutingError

logger = logging.getLogger(__name__)

OSRM_BASE_URL = "https://router.project-osrm.org/route/v1/driving"


class RoutingService:
    """Calculates driving routes between two or more coordinates."""

    @classmethod
    def get_route(cls, waypoints: list) -> dict:
        """
        Get a driving route through an ordered list of waypoints.

        Args:
            waypoints: list of dicts with "lat" and "lng" keys, in visit order.
                       Must contain at least 2 points.

        Returns:
            dict with keys:
                distance_miles (float)
                duration_hours (float)
                geometry (GeoJSON LineString coordinates as [lng, lat] pairs)
                instructions (list of turn-by-turn steps)

        Raises:
            RoutingError: if the route cannot be calculated.
        """
        if len(waypoints) < 2:
            raise RoutingError("At least two waypoints are required to calculate a route.")

        coords_str = ";".join(f"{wp['lng']},{wp['lat']}" for wp in waypoints)
        url = f"{OSRM_BASE_URL}/{coords_str}"

        try:
            response = requests.get(
                url,
                params={
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "true",
                    "annotations": "false",
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Routing request failed: %s", exc)
            raise RoutingError("Could not reach routing service.") from exc

        if data.get("code") != "Ok" or not data.get("routes"):
            raise RoutingError(f"No route could be found between the given locations. ({data.get('message', data.get('code'))})")

        route = data["routes"][0]
        distance_meters = route["distance"]
        duration_seconds = route["duration"]

        distance_miles = distance_meters / 1609.344
        duration_hours = duration_seconds / 3600.0

        instructions = cls._extract_instructions(route)

        return {
            "distance_miles": round(distance_miles, 2),
            "duration_hours": round(duration_hours, 2),
            "geometry": route["geometry"],  
            "instructions": instructions,
        }

    @staticmethod
    def _extract_instructions(route: dict) -> list:
        """Flatten OSRM leg/step data into a simple turn-by-turn instruction list."""
        instructions = []
        cumulative_miles = 0.0

        for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                maneuver = step.get("maneuver", {})
                step_distance_miles = step.get("distance", 0) / 1609.344
                cumulative_miles += step_distance_miles

                name = step.get("name") or "unnamed road"
                m_type = maneuver.get("type", "continue")
                modifier = maneuver.get("modifier", "")

                text = RoutingService._describe_maneuver(m_type, modifier, name)

                instructions.append(
                    {
                        "instruction": text,
                        "distance_miles": round(step_distance_miles, 2),
                        "cumulative_distance_miles": round(cumulative_miles, 2),
                        "duration_minutes": round(step.get("duration", 0) / 60, 1),
                    }
                )
        return instructions

    @staticmethod
    def _describe_maneuver(m_type: str, modifier: str, road_name: str) -> str:
        verbs = {
            "depart": "Head out",
            "arrive": "Arrive at destination",
            "turn": f"Turn {modifier}",
            "merge": f"Merge {modifier}".strip(),
            "on ramp": "Take the ramp",
            "off ramp": "Take the exit",
            "fork": f"Keep {modifier} at the fork",
            "roundabout": "Enter the roundabout",
            "rotary": "Enter the rotary",
            "continue": f"Continue {modifier}".strip(),
            "new name": "Continue",
            "end of road": f"Turn {modifier} at the end of the road",
        }
        verb = verbs.get(m_type, m_type.replace("_", " ").capitalize())
        if road_name and road_name != "unnamed road":
            return f"{verb} onto {road_name}"
        return verb
