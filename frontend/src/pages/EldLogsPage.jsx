import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Card from '../components/layout/Card';
import LoadingState from '../components/layout/LoadingState';
import ErrorState from '../components/layout/ErrorState';
import DailyLogSheet from '../components/eld/DailyLogSheet';
import { getTrip } from '../api/trips';
import { extractErrorMessage } from '../api/client';
import './EldLogsPage.css';

export default function EldLogsPage() {
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

  if (loading) return <LoadingState label="Drawing ELD log sheets…" />;
  if (error) return <div className="eld-logs-page__message"><ErrorState message={error} /></div>;
  if (!trip) return null;

  return (
    <div className="eld-logs-page">
      <div className="eld-logs-page__header">
        <div>
          <span className="eld-logs-page__eyebrow">Trip #{trip.id}</span>
          <h1 className="eld-logs-page__title">ELD Daily Log Sheets</h1>
          <p className="eld-logs-page__subtitle">
            {trip.daily_logs.length} day{trip.daily_logs.length !== 1 ? 's' : ''} &middot;{' '}
            {trip.current_location} to {trip.dropoff_location}
          </p>
        </div>
        <Link className="eld-logs-page__back-link" to={`/trips/${trip.id}/results`}>
          &larr; Back to Route
        </Link>
      </div>

      <div className="eld-logs-page__sheets">
        {trip.daily_logs.map((dailyLog) => (
          <Card key={dailyLog.id} className="eld-logs-page__sheet-card">
            <DailyLogSheet dailyLog={dailyLog} />
          </Card>
        ))}
      </div>
    </div>
  );
}
