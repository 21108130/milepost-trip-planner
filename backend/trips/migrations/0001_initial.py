

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.PositiveIntegerField()),
                ('log_date', models.DateField()),
                ('total_driving_hours', models.FloatField(default=0)),
                ('total_on_duty_hours', models.FloatField(default=0)),
                ('total_off_duty_hours', models.FloatField(default=0)),
                ('total_sleeper_berth_hours', models.FloatField(default=0)),
                ('starting_location', models.CharField(blank=True, max_length=255)),
                ('ending_location', models.CharField(blank=True, max_length=255)),
                ('cycle_hours_used', models.FloatField(default=0, help_text='Cumulative cycle hours used through this day.')),
            ],
            options={
                'ordering': ['day_number'],
            },
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_location', models.CharField(max_length=255)),
                ('current_location_lat', models.FloatField(blank=True, null=True)),
                ('current_location_lng', models.FloatField(blank=True, null=True)),
                ('pickup_location', models.CharField(max_length=255)),
                ('pickup_location_lat', models.FloatField(blank=True, null=True)),
                ('pickup_location_lng', models.FloatField(blank=True, null=True)),
                ('dropoff_location', models.CharField(max_length=255)),
                ('dropoff_location_lat', models.FloatField(blank=True, null=True)),
                ('dropoff_location_lng', models.FloatField(blank=True, null=True)),
                ('current_cycle_used_hours', models.FloatField(help_text="Hours already used in the driver's 70-hour/8-day cycle.", validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(70)])),
                ('total_distance_miles', models.FloatField(blank=True, null=True)),
                ('total_duration_hours', models.FloatField(blank=True, null=True)),
                ('route_geometry', models.JSONField(blank=True, help_text='GeoJSON route geometry.', null=True)),
                ('route_instructions', models.JSONField(blank=True, help_text='Turn-by-turn instructions.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duty_status', models.CharField(choices=[('off_duty', 'Off Duty'), ('sleeper_berth', 'Sleeper Berth'), ('driving', 'Driving'), ('on_duty', 'On Duty (Not Driving)')], max_length=20)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('start_hour', models.FloatField()),
                ('end_hour', models.FloatField()),
                ('location', models.CharField(blank=True, max_length=255)),
                ('remark', models.CharField(blank=True, max_length=255)),
                ('daily_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='trips.dailylog')),
            ],
            options={
                'ordering': ['start_hour'],
            },
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_type', models.CharField(choices=[('pickup', 'Pickup'), ('dropoff', 'Dropoff'), ('fuel', 'Fuel'), ('rest', 'Rest (10-hr off duty)'), ('break', '30-Minute Break')], max_length=20)),
                ('sequence', models.PositiveIntegerField(help_text='Order of the stop along the route.')),
                ('location_name', models.CharField(blank=True, max_length=255)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('distance_from_start_miles', models.FloatField(default=0)),
                ('arrival_time', models.DateTimeField(blank=True, null=True)),
                ('departure_time', models.DateTimeField(blank=True, null=True)),
                ('duration_minutes', models.FloatField(default=0)),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stops', to='trips.trip')),
            ],
            options={
                'ordering': ['sequence'],
            },
        ),
        migrations.AddField(
            model_name='dailylog',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_logs', to='trips.trip'),
        ),
        migrations.AlterUniqueTogether(
            name='dailylog',
            unique_together={('trip', 'day_number')},
        ),
    ]
