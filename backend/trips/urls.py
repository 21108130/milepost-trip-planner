from django.urls import path

from trips.views import TripPlanView, TripListView, TripDetailView

urlpatterns = [
    path("trips/plan/", TripPlanView.as_view(), name="trip-plan"),
    path("trips/", TripListView.as_view(), name="trip-list"),
    path("trips/<int:pk>/", TripDetailView.as_view(), name="trip-detail"),
]
