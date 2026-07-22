
from django.db import transaction

from trips.models import Trip, Stop, DailyLog, LogEntry
from trips.services.geocoding_service import GeocodingService
from trips.services.routing_service import RoutingService
from trips.services.hos_planner_service import HOSPlannerService
from trips.services.eld_log_service import ELDLogService
from trips.services.stop_extraction_service import StopExtractionService


class TripService:
    """Coordinates all domain services to plan and persist a complete trip."""

    @classmethod
    def plan_and_create_trip(cls, current_location, pickup_location, dropoff_location, current_cycle_used_hours):
        current_geo = GeocodingService.geocode(current_location)
        pickup_geo = GeocodingService.geocode(pickup_location)
        dropoff_geo = GeocodingService.geocode(dropoff_location)

        waypoints = [current_geo, pickup_geo, dropoff_geo]
        route = RoutingService.get_route(waypoints)

        leg1_route = RoutingService.get_route([current_geo, pickup_geo])
        leg2_route = RoutingService.get_route([pickup_geo, dropoff_geo])

        planner = HOSPlannerService(current_cycle_used_hours=current_cycle_used_hours)
        segments = planner.plan_trip(
            leg1_miles=leg1_route["distance_miles"],
            leg2_miles=leg2_route["distance_miles"],
            current_label=current_location,
            pickup_label=pickup_location,
            dropoff_label=dropoff_location,
        )

        daily_logs_data = ELDLogService.build_daily_logs(segments)

        route_coordinates = route["geometry"]["coordinates"]
        stops_data = StopExtractionService.extract_stops(
            segments, route_coordinates, route["distance_miles"]
        )

        with transaction.atomic():
            trip = Trip.objects.create(
                current_location=current_location,
                current_location_lat=current_geo["lat"],
                current_location_lng=current_geo["lng"],
                pickup_location=pickup_location,
                pickup_location_lat=pickup_geo["lat"],
                pickup_location_lng=pickup_geo["lng"],
                dropoff_location=dropoff_location,
                dropoff_location_lat=dropoff_geo["lat"],
                dropoff_location_lng=dropoff_geo["lng"],
                current_cycle_used_hours=current_cycle_used_hours,
                total_distance_miles=route["distance_miles"],
                total_duration_hours=route["duration_hours"],
                route_geometry=route["geometry"],
                route_instructions=route["instructions"],
            )

            cls._create_stops(trip, stops_data)
            cls._create_daily_logs(trip, daily_logs_data, current_cycle_used_hours)

        return trip

    @staticmethod
    def _create_stops(trip, stops_data):
        Stop.objects.bulk_create(
            [
                Stop(
                    trip=trip,
                    stop_type=s["stop_type"],
                    sequence=s["sequence"],
                    location_name=s["location_name"],
                    latitude=s["latitude"],
                    longitude=s["longitude"],
                    distance_from_start_miles=s["distance_from_start_miles"],
                    arrival_time=s["arrival_time"],
                    departure_time=s["departure_time"],
                    duration_minutes=s["duration_minutes"],
                )
                for s in stops_data
            ]
        )

    @staticmethod
    def _create_daily_logs(trip, daily_logs_data, initial_cycle_used):
        cumulative_cycle = initial_cycle_used
        for day_data in daily_logs_data:
            on_duty_and_driving = day_data["totals"]["driving"] + day_data["totals"]["on_duty"]
            cumulative_cycle += on_duty_and_driving

            daily_log = DailyLog.objects.create(
                trip=trip,
                day_number=day_data["day_number"],
                log_date=day_data["log_date"],
                total_driving_hours=day_data["totals"]["driving"],
                total_on_duty_hours=day_data["totals"]["on_duty"],
                total_off_duty_hours=day_data["totals"]["off_duty"],
                total_sleeper_berth_hours=day_data["totals"]["sleeper_berth"],
                starting_location=day_data["starting_location"],
                ending_location=day_data["ending_location"],
                cycle_hours_used=round(min(cumulative_cycle, 70), 2),
            )

            LogEntry.objects.bulk_create(
                [
                    LogEntry(
                        daily_log=daily_log,
                        duty_status=entry["status"],
                        start_time=entry["start"],
                        end_time=entry["end"],
                        start_hour=entry["start_hour"],
                        end_hour=entry["end_hour"],
                        location=entry["location"],
                        remark=entry["remark"],
                    )
                    for entry in day_data["entries"]
                ]
            )
