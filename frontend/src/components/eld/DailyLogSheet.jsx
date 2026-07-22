import EldLogGrid from './EldLogGrid';
import './DailyLogSheet.css';

export default function DailyLogSheet({ dailyLog }) {
  const {
    day_number,
    log_date,
    starting_location,
    ending_location,
    total_off_duty_hours,
    total_sleeper_berth_hours,
    total_driving_hours,
    total_on_duty_hours,
    cycle_hours_used,
    entries,
  } = dailyLog;

  return (
    <div className="log-sheet">
      <div className="log-sheet__header">
        <div>
          <span className="log-sheet__day">Day {day_number}</span>
          <h3 className="log-sheet__date">{formatDate(log_date)}</h3>
        </div>
        <div className="log-sheet__route-line">
          <span>{starting_location}</span>
          <span className="log-sheet__route-arrow">&rarr;</span>
          <span>{ending_location}</span>
        </div>
      </div>

      <div className="log-sheet__totals">
        <Total label="Off Duty" value={total_off_duty_hours} />
        <Total label="Sleeper Berth" value={total_sleeper_berth_hours} />
        <Total label="Driving" value={total_driving_hours} accent="amber" />
        <Total label="On Duty" value={total_on_duty_hours} />
        <Total label="Cycle Used / 70" value={cycle_hours_used} accent="red" suffix=" hrs" />
      </div>

      <EldLogGrid entries={entries || []} />
    </div>
  );
}

function Total({ label, value, accent, suffix = 'h' }) {
  const numericValue = Number(value) || 0;
  return (
    <div className={`log-sheet__total ${accent ? `log-sheet__total--${accent}` : ''}`}>
      <span className="log-sheet__total-value">
        {numericValue.toFixed(1)}
        {suffix === 'h' ? <span className="log-sheet__total-suffix">h</span> : suffix}
      </span>
      <span className="log-sheet__total-label">{label}</span>
    </div>
  );
}

function formatDate(dateStr) {
  const date = new Date(`${dateStr}T00:00:00`);
  return date.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });
}
