import './StopsTimeline.css';

const STOP_META = {
  pickup: { label: 'Pickup', color: 'var(--green)' },
  dropoff: { label: 'Dropoff', color: 'var(--red)' },
  fuel: { label: 'Fuel Stop', color: 'var(--orange)' },
  rest: { label: 'Rest / Sleeper Berth', color: 'var(--text-secondary)' },
  break: { label: '30-Minute Break', color: 'var(--text-muted)' },
};

export default function StopsTimeline({ stops }) {
  if (!stops?.length) {
    return <p className="stops-timeline__empty">No stops required for this trip.</p>;
  }

  return (
    <ol className="stops-timeline">
      {stops.map((stop) => {
        const meta = STOP_META[stop.stop_type] || { label: stop.stop_type, color: 'var(--text-muted)' };
        return (
          <li key={stop.id} className="stops-timeline__item">
            <span className="stops-timeline__dot" style={{ background: meta.color }} />
            <div className="stops-timeline__content">
              <div className="stops-timeline__row">
                <span className="stops-timeline__type">{meta.label}</span>
                <span className="stops-timeline__mile">Mile {Math.round(stop.distance_from_start_miles)}</span>
              </div>
              <p className="stops-timeline__location">{stop.location_name}</p>
              <p className="stops-timeline__time">
                {formatTime(stop.arrival_time)} &ndash; {formatTime(stop.departure_time)}
                <span className="stops-timeline__duration"> ({formatDuration(stop.duration_minutes)})</span>
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function formatDuration(minutes) {
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const hours = Math.floor(minutes / 60);
  const rem = Math.round(minutes % 60);
  return rem ? `${hours}h ${rem}m` : `${hours}h`;
}
