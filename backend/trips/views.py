import logging

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from trips.models import Trip
from trips.serializers import (
    TripCreateSerializer,
    TripDetailSerializer,
    TripListSerializer,
)
from trips.services.trip_service import TripService
from trips.utils.exceptions import TripPlanningError

logger = logging.getLogger(__name__)


class TripPlanView(APIView):
    """POST /api/trips/plan/ - Plans a new trip and returns full route + ELD log data."""

    def post(self, request):
        serializer = TripCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            trip = TripService.plan_and_create_trip(
                current_location=data["current_location"],
                pickup_location=data["pickup_location"],
                dropoff_location=data["dropoff_location"],
                current_cycle_used_hours=data["current_cycle_used_hours"],
            )
        except TripPlanningError as exc:
            logger.warning("Trip planning failed: %s", exc)
            return Response(
                {"error": {"message": "Trip planning failed.", "detail": str(exc)}},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        result = TripDetailSerializer(trip)
        return Response(result.data, status=status.HTTP_201_CREATED)


class TripListView(ListAPIView):
    """GET /api/trips/ - Lists previously planned trips."""

    queryset = Trip.objects.all()
    serializer_class = TripListSerializer


class TripDetailView(RetrieveAPIView):
    """GET /api/trips/<id>/ - Retrieves a single trip with full details."""

    queryset = Trip.objects.all()
    serializer_class = TripDetailSerializer
