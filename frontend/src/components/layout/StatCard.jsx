import './StatCard.css';

export default function StatCard({ label, value, unit, accent = 'amber' }) {
  return (
    <div className={`stat-card stat-card--${accent}`}>
      <span className="stat-card__label">{label}</span>
      <span className="stat-card__value">
        {value}
        {unit && <span className="stat-card__unit">{unit}</span>}
      </span>
    </div>
  );
}
