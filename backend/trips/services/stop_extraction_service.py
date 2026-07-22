


class StopExtractionService:

    STATUS_TO_STOP_TYPE = {
        "Pickup": "pickup",
        "Dropoff": "dropoff",
        "Fuel Stop": "fuel",
        "30-Minute Break": "break",
    }

    @classmethod
    def extract_stops(cls, segments: list, route_coordinates: list, total_distance_miles: float) -> list:
        """
        Args:
            segments: HOS planner segments.
            route_coordinates: list of [lng, lat] pairs describing the full route geometry.
            total_distance_miles: total driving distance of the route.

        Returns:
            list of stop dicts ready for Stop model creation.
        """
        stops = []
        sequence = 0

        for seg in segments:
            remark = seg["remark"]

            if remark in cls.STATUS_TO_STOP_TYPE:
                stop_type = cls.STATUS_TO_STOP_TYPE[remark]
            elif remark == "10-Hour Rest Break":
                stop_type = "rest"
            elif remark.startswith("34-Hour Restart"):
                stop_type = "rest"
            else:
                continue

            mile_marker = seg["start_mile"]
            lat, lng = cls._interpolate_coordinates(route_coordinates, mile_marker, total_distance_miles)

            sequence += 1
            stops.append(
                {
                    "stop_type": stop_type,
                    "sequence": sequence,
                    "location_name": seg["location"] or remark,
                    "latitude": lat,
                    "longitude": lng,
                    "distance_from_start_miles": round(mile_marker, 2),
                    "arrival_time": seg["start"],
                    "departure_time": seg["end"],
                    "duration_minutes": round((seg["end"] - seg["start"]).total_seconds() / 60, 1),
                }
            )

        return stops

    @staticmethod
    def _interpolate_coordinates(route_coordinates: list, mile_marker: float, total_distance_miles: float):
        """Approximates lat/lng for a given mile marker by proportionally walking the route geometry."""
        if not route_coordinates or total_distance_miles <= 0:
            return None, None

        fraction = max(0.0, min(1.0, mile_marker / total_distance_miles))
        index = int(fraction * (len(route_coordinates) - 1))
        index = max(0, min(len(route_coordinates) - 1, index))

        lng, lat = route_coordinates[index]
        return lat, lng
