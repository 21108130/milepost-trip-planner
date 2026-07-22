
from datetime import datetime, time, timedelta


class ELDLogService:
    """Splits duty segments across calendar days and builds daily log data."""

    @staticmethod
    def build_daily_logs(segments: list) -> list:
        """
        Args:
            segments: ordered list of dicts from HOSPlannerService, each with
                      status, start (datetime), end (datetime), location, remark.

        Returns:
            list of daily log dicts:
                {
                    "day_number": int,
                    "log_date": date,
                    "starting_location": str,
                    "ending_location": str,
                    "totals": {"off_duty": h, "sleeper_berth": h, "driving": h, "on_duty": h},
                    "entries": [
                        {"status": str, "start_hour": float, "end_hour": float,
                         "location": str, "remark": str, "start": dt, "end": dt}
                    ]
                }
        """
        if not segments:
            return []

        split_segments = ELDLogService._split_at_midnight(segments)

        days = {}
        order = []
        for seg in split_segments:
            day_key = seg["start"].date()
            if day_key not in days:
                days[day_key] = []
                order.append(day_key)
            days[day_key].append(seg)

        daily_logs = []
        last_known_location = None

        for index, day_key in enumerate(order, start=1):
            day_segments = days[day_key]

            entries = []
            totals = {"off_duty": 0.0, "sleeper_berth": 0.0, "driving": 0.0, "on_duty": 0.0}

            day_start_location = None
            day_end_location = None

            for seg in day_segments:
                start_hour = ELDLogService._time_to_hour(seg["start"])
                end_hour = ELDLogService._time_to_hour(seg["end"])
                if end_hour <= start_hour:
                    end_hour = 24.0

                duration = end_hour - start_hour
                totals[seg["status"]] += duration

                location = seg["location"] or last_known_location
                if seg["location"]:
                    last_known_location = seg["location"]
                    day_end_location = seg["location"]
                if day_start_location is None:
                    day_start_location = location

                entries.append(
                    {
                        "status": seg["status"],
                        "start_hour": round(start_hour, 3),
                        "end_hour": round(end_hour, 3),
                        "location": location or "En Route",
                        "remark": seg["remark"],
                        "start": seg["start"],
                        "end": seg["end"],
                    }
                )

            daily_logs.append(
                {
                    "day_number": index,
                    "log_date": day_key,
                    "starting_location": day_start_location or "En Route",
                    "ending_location": day_end_location or day_start_location or "En Route",
                    "totals": {k: round(v, 2) for k, v in totals.items()},
                    "entries": entries,
                }
            )

        return daily_logs

    @staticmethod
    def _time_to_hour(dt: datetime) -> float:
        return dt.hour + dt.minute / 60 + dt.second / 3600

    @staticmethod
    def _split_at_midnight(segments: list) -> list:
        """Splits any segment that crosses midnight into two segments."""
        result = []
        for seg in segments:
            start = seg["start"]
            end = seg["end"]

            cursor = start
            while cursor.date() != end.date():
                midnight = datetime.combine(cursor.date() + timedelta(days=1), time.min, tzinfo=cursor.tzinfo)
                if midnight >= end:
                    break
                result.append({**seg, "start": cursor, "end": midnight})
                cursor = midnight

            result.append({**seg, "start": cursor, "end": end})

        return result
