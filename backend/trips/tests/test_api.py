from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework import status


def fake_geocode(location):
    fake_coords = {
        "Chicago, IL": {"lat": 41.8781, "lng": -87.6298, "display_name": "Chicago, IL"},
        "Indianapolis, IN": {"lat": 39.7684, "lng": -86.1581, "display_name": "Indianapolis, IN"},
        "Columbus, OH": {"lat": 39.9612, "lng": -82.9988, "display_name": "Columbus, OH"},
    }
    return fake_coords.get(location, {"lat": 40.0, "lng": -85.0, "display_name": location})


def fake_route(waypoints):
  
    distance = 180.0 * (len(waypoints) - 1)
    return {
        "distance_miles": distance,
        "duration_hours": distance / 55,
        "geometry": {
            "type": "LineString",
            "coordinates": [[wp["lng"], wp["lat"]] for wp in waypoints],
        },
        "instructions": [
            {
                "instruction": "Head out",
                "distance_miles": distance,
                "cumulative_distance_miles": distance,
                "duration_minutes": distance / 55 * 60,
            }
        ],
    }


class TripPlanAPITests(APITestCase):

    @patch("trips.services.trip_service.RoutingService.get_route", side_effect=fake_route)
    @patch("trips.services.trip_service.GeocodingService.geocode", side_effect=fake_geocode)
    def test_plan_trip_success(self, mock_geocode, mock_route):
        payload = {
            "current_location": "Chicago, IL",
            "pickup_location": "Indianapolis, IN",
            "dropoff_location": "Columbus, OH",
            "current_cycle_used_hours": 5,
        }
        response = self.client.post("/api/trips/plan/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("stops", response.data)
        self.assertIn("daily_logs", response.data)
        self.assertGreater(len(response.data["daily_logs"]), 0)
        self.assertGreater(response.data["total_distance_miles"], 0)

    def test_plan_trip_missing_fields_returns_400(self):
        response = self.client.post("/api/trips/plan/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_plan_trip_invalid_cycle_hours_returns_400(self):
        payload = {
            "current_location": "Chicago, IL",
            "pickup_location": "Indianapolis, IN",
            "dropoff_location": "Columbus, OH",
            "current_cycle_used_hours": 200,
        }
        response = self.client.post("/api/trips/plan/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("trips.services.trip_service.RoutingService.get_route", side_effect=fake_route)
    @patch("trips.services.trip_service.GeocodingService.geocode", side_effect=fake_geocode)
    def test_trip_list_and_detail(self, mock_geocode, mock_route):
        payload = {
            "current_location": "Chicago, IL",
            "pickup_location": "Indianapolis, IN",
            "dropoff_location": "Columbus, OH",
            "current_cycle_used_hours": 5,
        }
        create_response = self.client.post("/api/trips/plan/", payload, format="json")
        trip_id = create_response.data["id"]

        list_response = self.client.get("/api/trips/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        detail_response = self.client.get(f"/api/trips/{trip_id}/")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["id"], trip_id)

    def test_trip_detail_not_found(self):
        response = self.client.get("/api/trips/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
