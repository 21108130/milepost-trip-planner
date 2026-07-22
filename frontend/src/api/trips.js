import { apiClient } from './client';

export async function planTrip({ currentLocation, pickupLocation, dropoffLocation, currentCycleUsedHours }) {
  const response = await apiClient.post('/trips/plan/', {
    current_location: currentLocation,
    pickup_location: pickupLocation,
    dropoff_location: dropoffLocation,
    current_cycle_used_hours: currentCycleUsedHours,
  });
  return response.data;
}

export async function getTrip(tripId) {
  const response = await apiClient.get(`/trips/${tripId}/`);
  return response.data;
}

export async function listTrips() {
  const response = await apiClient.get('/trips/');
  return response.data;
}
