import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import EldLogsPage from '../src/pages/EldLogsPage';
import ResultsPage from '../src/pages/ResultsPage';
import HomePage from '../src/pages/HomePage';
import * as tripsApi from '../src/api/trips';

function buildDailyLog(overrides = {}) {
  return {
    id: overrides.id ?? 1,
    day_number: overrides.day_number ?? 1,
    log_date: overrides.log_date ?? '2026-07-22',
    total_driving_hours: 8,
    total_on_duty_hours: 2,
    total_off_duty_hours: 4,
    total_sleeper_berth_hours: 10,
    starting_location: 'Chicago, IL',
    ending_location: 'Indianapolis, IN',
    cycle_hours_used: 20,
    entries: [
      { id: 1, duty_status: 'driving', start_time: '2026-07-22T06:00:00Z', end_time: '2026-07-22T14:00:00Z', start_hour: 6, end_hour: 14, location: 'En Route', remark: 'Driving' },
    ],
    ...overrides,
  };
}

const MULTI_DAY_TRIP = {
  id: 2,
  current_location: 'Los Angeles, CA',
  pickup_location: 'Phoenix, AZ',
  dropoff_location: 'Dallas, TX',
  current_cycle_used_hours: 5,
  total_distance_miles: 1400,
  total_duration_hours: 25,
  route_geometry: { type: 'LineString', coordinates: [[-118, 34], [-96, 32]] },
  route_instructions: [
    { instruction: 'Head east', distance_miles: 1400, cumulative_distance_miles: 1400, duration_minutes: 1500 },
  ],
  stops: [
    { id: 1, stop_type: 'fuel', sequence: 1, location_name: 'Somewhere, TX', latitude: 32, longitude: -100, distance_from_start_miles: 1000, arrival_time: '2026-07-22T12:00:00Z', departure_time: '2026-07-22T12:30:00Z', duration_minutes: 30 },
    { id: 2, stop_type: 'rest', sequence: 2, location_name: 'Rest Area', latitude: 33, longitude: -99, distance_from_start_miles: 1100, arrival_time: '2026-07-22T14:00:00Z', departure_time: '2026-07-23T00:00:00Z', duration_minutes: 600 },
  ],
  daily_logs: [
    buildDailyLog({ id: 1, day_number: 1, log_date: '2026-07-22' }),
    buildDailyLog({ id: 2, day_number: 2, log_date: '2026-07-23' }),
    buildDailyLog({ id: 3, day_number: 3, log_date: '2026-07-24' }),
  ],
};

describe('Multi-day ELD logs (long trip)', () => {
  it('renders one log sheet per day for a multi-day trip', async () => {
    vi.spyOn(tripsApi, 'getTrip').mockResolvedValue(MULTI_DAY_TRIP);

    render(
      <MemoryRouter initialEntries={['/trips/2/logs']}>
        <Routes>
          <Route path="/trips/:tripId/logs" element={<EldLogsPage />} />
        </Routes>
      </MemoryRouter>
    );

    await screen.findByText('Day 1');
    expect(screen.getByText('Day 2')).toBeTruthy();
    expect(screen.getByText('Day 3')).toBeTruthy();
  });
});

describe('ResultsPage', () => {
  it('renders map, stats, stops, and instructions without crashing', async () => {
    vi.spyOn(tripsApi, 'getTrip').mockResolvedValue(MULTI_DAY_TRIP);

    render(
      <MemoryRouter initialEntries={['/trips/2/results']}>
        <Routes>
          <Route path="/trips/:tripId/results" element={<ResultsPage />} />
        </Routes>
      </MemoryRouter>
    );

    await screen.findByText(/Phoenix, AZ/);
    expect(screen.getByText('Fuel, Rest & Break Timeline')).toBeTruthy();
    expect(screen.getByText('Turn-by-Turn Instructions')).toBeTruthy();
  });
});

describe('HomePage', () => {
  it('renders the trip form without crashing', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Trip Details')).toBeTruthy();
    expect(screen.getByPlaceholderText('e.g. Chicago, IL')).toBeTruthy();
  });
});
