import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Card from '../components/layout/Card';
import StatCard from '../components/layout/StatCard';
import LoadingState from '../components/layout/LoadingState';
import ErrorState from '../components/layout/ErrorState';
import RouteMap from '../components/map/RouteMap';
import StopsTimeline from '../components/trip/StopsTimeline';
import RouteInstructions from '../components/trip/RouteInstructions';
import { getTrip } from '../api/trips';
import { extractErrorMessage } from '../api/client';
import './ResultsPage.css';

export default function ResultsPage() {
  const { tripId } = useParams();
  const [trip, setTrip] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getTrip(tripId)
      .then((data) => {
        if (!cancelled) setTrip(data);
      })
      .catch((err) => {
        if (!cancelled) setError(extractErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [tripId]);

  if (loading) return <LoadingState label="Loading trip results…" />;
  if (error) return <div className="results-page__message"><ErrorState message={error} /></div>;
  if (!trip) return null;

  return (
    <div className="results-page">
      <div className="results-page__header">
        <div>
          <span className="results-page__eyebrow">Trip #{trip.id}</span>
          <h1 className="results-page__title">
            {trip.pickup_location} <span className="results-page__arrow">&rarr;</span> {trip.dropoff_location}
          </h1>
          <p className="results-page__subtitle">Starting from {trip.current_location}</p>
        </div>
        <Link className="results-page__logs-link" to={`/trips/${trip.id}/logs`}>
          View ELD Log Sheets &rarr;
        </Link>
      </div>

      <div className="results-page__stats">
        <StatCard label="Total Distance" value={Math.round(trip.total_distance_miles)} unit="mi" />
        <StatCard label="Drive Time" value={trip.total_duration_hours.toFixed(1)} unit="hrs" accent="green" />
        <StatCard label="Fuel Stops" value={trip.stops.filter((s) => s.stop_type === 'fuel').length} />
        <StatCard
          label="Rest Periods"
          value={trip.stops.filter((s) => s.stop_type === 'rest').length}
          accent="red"
        />
        <StatCard label="Log Sheet Days" value={trip.daily_logs.length} />
      </div>

      <Card eyebrow="Route" title="Map & Stops" className="results-page__map-card">
        <RouteMap routeGeometry={trip.route_geometry} stops={trip.stops} />
      </Card>

      <div className="results-page__grid">
        <Card eyebrow="Stops" title="Fuel, Rest & Break Timeline">
          <StopsTimeline stops={trip.stops} />
        </Card>
        <Card eyebrow="Directions" title="Turn-by-Turn Instructions">
          <RouteInstructions instructions={trip.route_instructions} />
        </Card>
      </div>
    </div>
  );
}
