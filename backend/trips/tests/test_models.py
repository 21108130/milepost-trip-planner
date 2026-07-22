from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from trips.models import Trip, Stop, DailyLog, LogEntry


class TripModelTests(TestCase):
    def test_create_trip(self):
        trip = Trip.objects.create(
            current_location="Chicago, IL",
            pickup_location="Indianapolis, IN",
            dropoff_location="Columbus, OH",
            current_cycle_used_hours=10,
        )
        self.assertEqual(str(trip), f"Trip #{trip.pk}: Indianapolis, IN -> Columbus, OH")

    def test_cycle_hours_validation(self):
        trip = Trip(
            current_location="A",
            pickup_location="B",
            dropoff_location="C",
            current_cycle_used_hours=100,
        )
        with self.assertRaises(ValidationError):
            trip.full_clean()


class StopModelTests(TestCase):
    def test_create_stop(self):
        trip = Trip.objects.create(
            current_location="A", pickup_location="B", dropoff_location="C",
            current_cycle_used_hours=0,
        )
        stop = Stop.objects.create(
            trip=trip, stop_type=Stop.StopType.FUEL, sequence=1,
            distance_from_start_miles=1000,
        )
        self.assertEqual(stop.trip, trip)
        self.assertIn("Fuel", str(stop))


class DailyLogModelTests(TestCase):
    def test_unique_day_number_per_trip(self):
        trip = Trip.objects.create(
            current_location="A", pickup_location="B", dropoff_location="C",
            current_cycle_used_hours=0,
        )
        DailyLog.objects.create(trip=trip, day_number=1, log_date=timezone.now().date())
        with self.assertRaises(Exception):
            DailyLog.objects.create(trip=trip, day_number=1, log_date=timezone.now().date())


class LogEntryModelTests(TestCase):
    def test_create_log_entry(self):
        trip = Trip.objects.create(
            current_location="A", pickup_location="B", dropoff_location="C",
            current_cycle_used_hours=0,
        )
        daily_log = DailyLog.objects.create(trip=trip, day_number=1, log_date=timezone.now().date())
        now = timezone.now()
        entry = LogEntry.objects.create(
            daily_log=daily_log,
            duty_status=LogEntry.DutyStatus.DRIVING,
            start_time=now,
            end_time=now,
            start_hour=6.0,
            end_hour=10.0,
        )
        self.assertEqual(entry.daily_log, daily_log)
