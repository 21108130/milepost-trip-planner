from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Trip(models.Model):
    """Represents a single planned truck trip."""

    current_location = models.CharField(max_length=255)
    current_location_lat = models.FloatField(null=True, blank=True)
    current_location_lng = models.FloatField(null=True, blank=True)

    pickup_location = models.CharField(max_length=255)
    pickup_location_lat = models.FloatField(null=True, blank=True)
    pickup_location_lng = models.FloatField(null=True, blank=True)

    dropoff_location = models.CharField(max_length=255)
    dropoff_location_lat = models.FloatField(null=True, blank=True)
    dropoff_location_lng = models.FloatField(null=True, blank=True)

    current_cycle_used_hours = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(70)],
        help_text="Hours already used in the driver's 70-hour/8-day cycle.",
    )

    total_distance_miles = models.FloatField(null=True, blank=True)
    total_duration_hours = models.FloatField(null=True, blank=True)

    route_geometry = models.JSONField(null=True, blank=True, help_text="GeoJSON route geometry.")
    route_instructions = models.JSONField(null=True, blank=True, help_text="Turn-by-turn instructions.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Trip #{self.pk}: {self.pickup_location} -> {self.dropoff_location}"


class Stop(models.Model):
    """Represents a stop along the route (fuel, rest, pickup, dropoff, break)."""

    class StopType(models.TextChoices):
        PICKUP = "pickup", "Pickup"
        DROPOFF = "dropoff", "Dropoff"
        FUEL = "fuel", "Fuel"
        REST = "rest", "Rest (10-hr off duty)"
        BREAK = "break", "30-Minute Break"

    trip = models.ForeignKey(Trip, related_name="stops", on_delete=models.CASCADE)
    stop_type = models.CharField(max_length=20, choices=StopType.choices)
    sequence = models.PositiveIntegerField(help_text="Order of the stop along the route.")

    location_name = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    distance_from_start_miles = models.FloatField(default=0)
    arrival_time = models.DateTimeField(null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.FloatField(default=0)

    class Meta:
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.get_stop_type_display()} @ {self.distance_from_start_miles:.0f}mi (Trip #{self.trip_id})"


class DailyLog(models.Model):
    """Represents a single day's ELD log sheet."""

    trip = models.ForeignKey(Trip, related_name="daily_logs", on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()
    log_date = models.DateField()

    total_driving_hours = models.FloatField(default=0)
    total_on_duty_hours = models.FloatField(default=0)
    total_off_duty_hours = models.FloatField(default=0)
    total_sleeper_berth_hours = models.FloatField(default=0)

    starting_location = models.CharField(max_length=255, blank=True)
    ending_location = models.CharField(max_length=255, blank=True)

    cycle_hours_used = models.FloatField(default=0, help_text="Cumulative cycle hours used through this day.")

    class Meta:
        ordering = ["day_number"]
        unique_together = ("trip", "day_number")

    def __str__(self):
        return f"Daily Log Day {self.day_number} (Trip #{self.trip_id})"


class LogEntry(models.Model):
    """Represents a single duty-status segment within a daily log (drawn on the grid)."""

    class DutyStatus(models.TextChoices):
        OFF_DUTY = "off_duty", "Off Duty"
        SLEEPER_BERTH = "sleeper_berth", "Sleeper Berth"
        DRIVING = "driving", "Driving"
        ON_DUTY_NOT_DRIVING = "on_duty", "On Duty (Not Driving)"

    daily_log = models.ForeignKey(DailyLog, related_name="entries", on_delete=models.CASCADE)
    duty_status = models.CharField(max_length=20, choices=DutyStatus.choices)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    
    start_hour = models.FloatField()
    end_hour = models.FloatField()

    location = models.CharField(max_length=255, blank=True)
    remark = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["start_hour"]

    def __str__(self):
        return f"{self.get_duty_status_display()} {self.start_hour}-{self.end_hour} (Log #{self.daily_log_id})"
