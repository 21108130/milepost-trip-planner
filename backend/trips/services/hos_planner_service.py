
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from trips.utils.exceptions import HOSValidationError

MAX_ITERATIONS = 5000


class DutyStatus:
    OFF_DUTY = "off_duty"
    SLEEPER_BERTH = "sleeper_berth"
    DRIVING = "driving"
    ON_DUTY = "on_duty"


class HOSPlannerService:
    """Builds an HOS-compliant duty-status timeline for a trip."""

    def __init__(self, current_cycle_used_hours: float, start_time=None):
        self.avg_speed = settings.HOS_AVERAGE_SPEED_MPH
        self.cycle_used = current_cycle_used_hours
        self.current_time = start_time or timezone.now()

        self.driving_since_break = 0.0
        self.driving_this_shift = 0.0
        self.on_duty_shift_start = self.current_time

        self.mile = 0.0
        self.next_fuel_mile = settings.HOS_FUEL_INTERVAL_MILES

        self.segments = []
        self._iterations = 0


    def plan_trip(self, leg1_miles, leg2_miles, current_label, pickup_label, dropoff_label):
        """
        Simulate: drive to pickup -> load (1hr) -> drive to dropoff -> unload (1hr).

        Returns the ordered list of duty-status segments (dicts).
        """
        self._drive_distance(leg1_miles, current_label, pickup_label)
        self._add_fixed_duty(settings.HOS_PICKUP_DURATION_HOURS, pickup_label, "Pickup")
        self._drive_distance(leg2_miles, pickup_label, dropoff_label)
        self._add_fixed_duty(settings.HOS_DROPOFF_DURATION_HOURS, dropoff_label, "Dropoff")
        return self.segments

 
    def _drive_distance(self, distance_miles, from_label, to_label):
        remaining = distance_miles

        while remaining > 1e-6:
            self._tick()

            break_room_hours = settings.HOS_BREAK_AFTER_HOURS - self.driving_since_break
            shift_room_hours = settings.HOS_MAX_DRIVING_HOURS - self.driving_this_shift
            window_elapsed = (self.current_time - self.on_duty_shift_start).total_seconds() / 3600
            window_room_hours = settings.HOS_MAX_ON_DUTY_WINDOW - window_elapsed
            cycle_room_hours = settings.HOS_CYCLE_MAX_HOURS - self.cycle_used

            if break_room_hours <= 1e-6:
                self._add_break()
                continue

            if shift_room_hours <= 1e-6 or window_room_hours <= 1e-6:
                self._add_rest()
                continue

            if cycle_room_hours <= 1e-6:
                self._add_restart()
                continue

            max_drive_hours = min(break_room_hours, shift_room_hours, window_room_hours, cycle_room_hours)
            max_drive_miles = max_drive_hours * self.avg_speed

            miles_to_fuel = self.next_fuel_mile - self.mile
            if miles_to_fuel <= 1e-6:
                self._add_fuel_stop(to_label)
                continue

            drive_miles = min(remaining, max_drive_miles, miles_to_fuel)
            drive_hours = drive_miles / self.avg_speed

            self._add_driving(drive_hours, drive_miles, to_label)
            remaining -= drive_miles

    def _tick(self):
        self._iterations += 1
        if self._iterations > MAX_ITERATIONS:
            raise HOSValidationError("Trip simulation exceeded maximum iterations; check inputs.")

    def _add_driving(self, hours, miles, location_label):
        start = self.current_time
        end = start + timedelta(hours=hours)
        self.segments.append(
            {
                "status": DutyStatus.DRIVING,
                "start": start,
                "end": end,
                "start_mile": self.mile,
                "end_mile": self.mile + miles,
                "location": location_label,
                "remark": "Driving",
            }
        )
        self.current_time = end
        self.mile += miles
        self.driving_since_break += hours
        self.driving_this_shift += hours
        self.cycle_used += hours

    def _add_break(self):
        hours = settings.HOS_BREAK_DURATION_MINUTES / 60
        start = self.current_time
        end = start + timedelta(hours=hours)
        self.segments.append(
            {
                "status": DutyStatus.OFF_DUTY,
                "start": start,
                "end": end,
                "start_mile": self.mile,
                "end_mile": self.mile,
                "location": None,
                "remark": "30-Minute Break",
            }
        )
        self.current_time = end
        self.driving_since_break = 0.0

    def _add_rest(self):
        hours = settings.HOS_MIN_OFF_DUTY_HOURS
        start = self.current_time
        end = start + timedelta(hours=hours)
        self.segments.append(
            {
                "status": DutyStatus.SLEEPER_BERTH,
                "start": start,
                "end": end,
                "start_mile": self.mile,
                "end_mile": self.mile,
                "location": None,
                "remark": "10-Hour Rest Break",
            }
        )
        self.current_time = end
        self.driving_since_break = 0.0
        self.driving_this_shift = 0.0
        self.on_duty_shift_start = self.current_time

    def _add_restart(self):
        hours = 34
        start = self.current_time
        end = start + timedelta(hours=hours)
        self.segments.append(
            {
                "status": DutyStatus.OFF_DUTY,
                "start": start,
                "end": end,
                "start_mile": self.mile,
                "end_mile": self.mile,
                "location": None,
                "remark": "34-Hour Restart (70-Hour Cycle Reached)",
            }
        )
        self.current_time = end
        self.driving_since_break = 0.0
        self.driving_this_shift = 0.0
        self.on_duty_shift_start = self.current_time
        self.cycle_used = 0.0

    def _add_fuel_stop(self, location_label):
        hours = 0.5
        start = self.current_time
        end = start + timedelta(hours=hours)
        self.segments.append(
            {
                "status": DutyStatus.ON_DUTY,
                "start": start,
                "end": end,
                "start_mile": self.mile,
                "end_mile": self.mile,
                "location": location_label,
                "remark": "Fuel Stop",
            }
        )
        self.current_time = end
        self.cycle_used += hours
        self.next_fuel_mile += settings.HOS_FUEL_INTERVAL_MILES

    def _add_fixed_duty(self, hours, location_label, remark):
        window_elapsed = (self.current_time - self.on_duty_shift_start).total_seconds() / 3600
        window_room_hours = settings.HOS_MAX_ON_DUTY_WINDOW - window_elapsed
        cycle_room_hours = settings.HOS_CYCLE_MAX_HOURS - self.cycle_used

        if window_room_hours <= hours:
            self._add_rest()
        if cycle_room_hours <= hours:
            self._add_restart()

        start = self.current_time
        end = start + timedelta(hours=hours)
        self.segments.append(
            {
                "status": DutyStatus.ON_DUTY,
                "start": start,
                "end": end,
                "start_mile": self.mile,
                "end_mile": self.mile,
                "location": location_label,
                "remark": remark,
            }
        )
        self.current_time = end
        self.cycle_used += hours
