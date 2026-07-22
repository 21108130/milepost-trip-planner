from django.contrib import admin

from trips.models import Trip, Stop, DailyLog, LogEntry


class StopInline(admin.TabularInline):
    model = Stop
    extra = 0
    ordering = ["sequence"]


class DailyLogInline(admin.TabularInline):
    model = DailyLog
    extra = 0
    ordering = ["day_number"]
    show_change_link = True


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ["id", "current_location", "pickup_location", "dropoff_location", "total_distance_miles", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["current_location", "pickup_location", "dropoff_location"]
    inlines = [StopInline, DailyLogInline]


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ["id", "trip", "stop_type", "sequence", "distance_from_start_miles", "arrival_time"]
    list_filter = ["stop_type"]


class LogEntryInline(admin.TabularInline):
    model = LogEntry
    extra = 0
    ordering = ["start_hour"]


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ["id", "trip", "day_number", "log_date", "total_driving_hours", "cycle_hours_used"]
    inlines = [LogEntryInline]


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ["id", "daily_log", "duty_status", "start_hour", "end_hour", "location"]
    list_filter = ["duty_status"]
