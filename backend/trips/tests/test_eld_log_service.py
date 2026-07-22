from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from trips.services.hos_planner_service import HOSPlannerService
from trips.services.eld_log_service import ELDLogService


class ELDLogServiceTests(TestCase):
    def setUp(self):
        self.start_time = timezone.now().replace(hour=6, minute=0, second=0, microsecond=0)

    def test_single_day_trip_produces_one_daily_log(self):
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=100, leg2_miles=100,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        daily_logs = ELDLogService.build_daily_logs(segments)
        self.assertEqual(len(daily_logs), 1)
        self.assertEqual(daily_logs[0]["day_number"], 1)

    def test_long_trip_produces_multiple_daily_logs(self):
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)

        segments = planner.plan_trip(
            leg1_miles=1250, leg2_miles=1250,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        daily_logs = ELDLogService.build_daily_logs(segments)
        self.assertGreater(len(daily_logs), 1)

        day_numbers = [d["day_number"] for d in daily_logs]
        self.assertEqual(day_numbers, list(range(1, len(daily_logs) + 1)))

    def test_entries_hour_offsets_within_valid_range(self):
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=900, leg2_miles=900,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        daily_logs = ELDLogService.build_daily_logs(segments)
        for day in daily_logs:
            for entry in day["entries"]:
                self.assertGreaterEqual(entry["start_hour"], 0.0)
                self.assertLessEqual(entry["end_hour"], 24.0)
                self.assertLessEqual(entry["start_hour"], entry["end_hour"])

    def test_daily_totals_sum_to_24_hours_for_full_days(self):
        planner = HOSPlannerService(current_cycle_used_hours=0, start_time=self.start_time)
        segments = planner.plan_trip(
            leg1_miles=1200, leg2_miles=1200,
            current_label="A", pickup_label="B", dropoff_label="C",
        )
        daily_logs = ELDLogService.build_daily_logs(segments)
     
        for day in daily_logs[1:-1]:
            total = sum(day["totals"].values())
            self.assertAlmostEqual(total, 24.0, delta=0.1)

    def test_midnight_crossing_segment_is_split(self):
        planner = HOSPlannerService(
            current_cycle_used_hours=0,
            start_time=self.start_time.replace(hour=22),
        )
        segments = planner.plan_trip(
            leg1_miles=200, leg2_miles=0,
            current_label="A", pickup_label="B", dropoff_label="B",
        )
        daily_logs = ELDLogService.build_daily_logs(segments)
        self.assertGreaterEqual(len(daily_logs), 2)
