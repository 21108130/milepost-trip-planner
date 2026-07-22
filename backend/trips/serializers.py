from rest_framework import serializers

from trips.models import Trip, Stop, DailyLog, LogEntry


class TripCreateSerializer(serializers.Serializer):
    """Validates trip-planning input."""

    current_location = serializers.CharField(max_length=255, allow_blank=False)
    pickup_location = serializers.CharField(max_length=255, allow_blank=False)
    dropoff_location = serializers.CharField(max_length=255, allow_blank=False)
    current_cycle_used_hours = serializers.FloatField(min_value=0, max_value=70)

    def validate_current_location(self, value):
        return value.strip()

    def validate_pickup_location(self, value):
        return value.strip()

    def validate_dropoff_location(self, value):
        return value.strip()


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = [
            "id",
            "duty_status",
            "start_time",
            "end_time",
            "start_hour",
            "end_hour",
            "location",
            "remark",
        ]


class DailyLogSerializer(serializers.ModelSerializer):
    entries = LogEntrySerializer(many=True, read_only=True)

    class Meta:
        model = DailyLog
        fields = [
            "id",
            "day_number",
            "log_date",
            "total_driving_hours",
            "total_on_duty_hours",
            "total_off_duty_hours",
            "total_sleeper_berth_hours",
            "starting_location",
            "ending_location",
            "cycle_hours_used",
            "entries",
        ]


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = [
            "id",
            "stop_type",
            "sequence",
            "location_name",
            "latitude",
            "longitude",
            "distance_from_start_miles",
            "arrival_time",
            "departure_time",
            "duration_minutes",
        ]


class TripDetailSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    daily_logs = DailyLogSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "current_location",
            "current_location_lat",
            "current_location_lng",
            "pickup_location",
            "pickup_location_lat",
            "pickup_location_lng",
            "dropoff_location",
            "dropoff_location_lat",
            "dropoff_location_lng",
            "current_cycle_used_hours",
            "total_distance_miles",
            "total_duration_hours",
            "route_geometry",
            "route_instructions",
            "created_at",
            "stops",
            "daily_logs",
        ]


class TripListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "id",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "current_cycle_used_hours",
            "total_distance_miles",
            "total_duration_hours",
            "created_at",
        ]
