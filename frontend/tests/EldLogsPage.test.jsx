import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import EldLogsPage from '../src/pages/EldLogsPage';
import * as tripsApi from '../src/api/trips';

const SAMPLE_TRIP = {
  id: 1,
  current_location: 'Chicago, IL',
  pickup_location: 'Indianapolis, IN',
  dropoff_location: 'Columbus, OH',
  current_cycle_used_hours: 15,
  total_distance_miles: 360,
  total_duration_hours: 6.5,
  route_geometry: { type: 'LineString', coordinates: [[-87.6, 41.8], [-83, 40]] },
  route_instructions: [],
  stops: [],
  daily_logs: [
    {
      id: 10,
      day_number: 1,
      log_date: '2026-07-22',
      total_driving_hours: 6.5,
      total_on_duty_hours: 2.0,
      total_off_duty_hours: 0.0,
      total_sleeper_berth_hours: 0.0,
      starting_location: 'Chicago, IL',
      ending_location: 'Columbus, OH',
      cycle_hours_used: 23.5,
      entries: [
        { id: 1, duty_status: 'on_duty', start_time: '2026-07-22T06:00:00Z', end_time: '2026-07-22T07:00:00Z', start_hour: 6, end_hour: 7, location: 'Indianapolis, IN', remark: 'Pickup' },
        { id: 2, duty_status: 'driving', start_time: '2026-07-22T07:00:00Z', end_time: '2026-07-22T13:33:00Z', start_hour: 7, end_hour: 13.55, location: 'Columbus, OH', remark: 'Driving' },
        { id: 3, duty_status: 'on_duty', start_time: '2026-07-22T13:33:00Z', end_time: '2026-07-22T14:33:00Z', start_hour: 13.55, end_hour: 14.55, location: 'Columbus, OH', remark: 'Dropoff' },
      ],
    },
  ],
};

describe('EldLogsPage', () => {
  it('renders daily log sheets without crashing given a realistic trip payload', async () => {
    vi.spyOn(tripsApi, 'getTrip').mockResolvedValue(SAMPLE_TRIP);

    render(
      <MemoryRouter initialEntries={['/trips/1/logs']}>
        <Routes>
          <Route path="/trips/:tripId/logs" element={<EldLogsPage />} />
        </Routes>
      </MemoryRouter>
    );

    const heading = await screen.findByText('ELD Daily Log Sheets');
    expect(heading).toBeTruthy();

    const dayLabel = await screen.findByText('Day 1');
    expect(dayLabel).toBeTruthy();
  });
});
