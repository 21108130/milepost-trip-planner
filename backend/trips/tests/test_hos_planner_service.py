from django.test import TestCase
from django.utils import timezone

from trips.services.hos_planner_service import HOSPlannerService, DutyStatus


class HOSPlannerServiceTests(TestCase):
    def setUp(self):
        self.start_time = timezone.now().replace(hour=6, minute=0, second=0, microsecond=0)

    def test_short_trip_no_rest_needed(self):
        """A short trip well within 11 driving hours should not require a 10-hr rest."""
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=100, leg2_miles=100,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        statuses = [s["status"] for s in segments]
        self.assertIn(DutyStatus.DRIVING, statuses)
        self.assertIn(DutyStatus.ON_DUTY, statuses)

        rest_segments = [s for s in segments if s["remark"] == "10-Hour Rest Break"]
        self.assertEqual(len(rest_segments), 0)

    def test_long_trip_requires_rest(self):
        """A trip requiring more than 11 hours of driving must include a 10-hr rest break."""
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)

        segments = planner.plan_trip(
            leg1_miles=350, leg2_miles=350,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        rest_segments = [s for s in segments if s["remark"] == "10-Hour Rest Break"]
        self.assertGreaterEqual(len(rest_segments), 1)

    def test_break_required_after_8_hours_driving(self):
        """A 30-minute break must appear after 8 cumulative hours of driving."""
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)
     
        segments = planner.plan_trip(
            leg1_miles=500, leg2_miles=0,
            current_label="A", pickup_label="B", dropoff_label="B",
        )
        breaks = [s for s in segments if s["remark"] == "30-Minute Break"]
        self.assertGreaterEqual(len(breaks), 1)

    def test_fuel_stop_inserted_every_1000_miles(self):
        """A fuel stop must be inserted at least once for trips over 1000 miles."""
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=600, leg2_miles=600,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        fuel_stops = [s for s in segments if s["remark"] == "Fuel Stop"]
        self.assertGreaterEqual(len(fuel_stops), 1)

    def test_cycle_limit_triggers_restart(self):
        """If cycle hours used is already near 70, a 34-hour restart should be triggered."""
        planner = HOSPlannerService(current_cycle_used_hours=68, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=300, leg2_miles=300,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        restarts = [s for s in segments if "34-Hour Restart" in s["remark"]]
        self.assertGreaterEqual(len(restarts), 1)

    def test_pickup_and_dropoff_duration_is_one_hour(self):
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=50, leg2_miles=50,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        pickup_segments = [s for s in segments if s["remark"] == "Pickup"]
        dropoff_segments = [s for s in segments if s["remark"] == "Dropoff"]
        self.assertEqual(len(pickup_segments), 1)
        self.assertEqual(len(dropoff_segments), 1)
        pickup_duration = (pickup_segments[0]["end"] - pickup_segments[0]["start"]).total_seconds() / 3600
        dropoff_duration = (dropoff_segments[0]["end"] - dropoff_segments[0]["start"]).total_seconds() / 3600
        self.assertAlmostEqual(pickup_duration, 1.0)
        self.assertAlmostEqual(dropoff_duration, 1.0)

    def test_segments_are_chronologically_ordered(self):
        planner = HOSPlannerService(current_cycle_used_hours=10, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=800, leg2_miles=800,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        for prev, curr in zip(segments, segments[1:]):
            self.assertLessEqual(prev["end"], curr["start"])
