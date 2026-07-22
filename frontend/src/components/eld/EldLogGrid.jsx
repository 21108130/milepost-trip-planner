import './EldLogGrid.css';

const ROW_ORDER = ['off_duty', 'sleeper_berth', 'driving', 'on_duty'];
const ROW_LABELS = {
  off_duty: '1. Off Duty',
  sleeper_berth: '2. Sleeper Berth',
  driving: '3. Driving',
  on_duty: '4. On Duty (Not Driving)',
};

const GUTTER_WIDTH = 168;
const HOUR_WIDTH = 34;
const ROW_HEIGHT = 42;
const CHART_WIDTH = GUTTER_WIDTH + HOUR_WIDTH * 24;
const CHART_TOP = 34;
const CHART_HEIGHT = ROW_HEIGHT * ROW_ORDER.length;
const CHART_BOTTOM = CHART_TOP + CHART_HEIGHT;
const SVG_HEIGHT = CHART_BOTTOM + 26;

function hourToX(hour) {
  return GUTTER_WIDTH + hour * HOUR_WIDTH;
}

function rowY(status) {
  const index = ROW_ORDER.indexOf(status);
  return CHART_TOP + index * ROW_HEIGHT + ROW_HEIGHT / 2;
}

export default function EldLogGrid({ entries }) {
  const sorted = [...entries].sort((a, b) => a.start_hour - b.start_hour);

  // Build the stepped path: horizontal run at each entry's row, vertical jump between entries.
  let pathParts = [];
  sorted.forEach((entry, index) => {
    const y = rowY(entry.duty_status);
    const x1 = hourToX(entry.start_hour);
    const x2 = hourToX(entry.end_hour);

    if (index === 0) {
      pathParts.push(`M ${x1} ${y}`);
    } else {
      const prevY = rowY(sorted[index - 1].duty_status);
      if (prevY !== y) {
        pathParts.push(`L ${x1} ${prevY} L ${x1} ${y}`);
      }
    }
    pathParts.push(`L ${x2} ${y}`);
  });
  const pathD = pathParts.join(' ');

  return (
    <div className="eld-grid">
      <svg
        viewBox={`0 0 ${CHART_WIDTH} ${SVG_HEIGHT}`}
        className="eld-grid__svg"
        role="img"
        aria-label="Daily driver duty status log grid"
      >
        {/* Row labels + row bands */}
        {ROW_ORDER.map((status, i) => (
          <g key={status}>
            <rect
              x={0}
              y={CHART_TOP + i * ROW_HEIGHT}
              width={CHART_WIDTH}
              height={ROW_HEIGHT}
              className={i % 2 === 0 ? 'eld-grid__band' : 'eld-grid__band eld-grid__band--alt'}
            />
            <text x={12} y={CHART_TOP + i * ROW_HEIGHT + ROW_HEIGHT / 2 + 4} className="eld-grid__row-label">
              {ROW_LABELS[status]}
            </text>
          </g>
        ))}

        {/* Vertical hour gridlines */}
        {Array.from({ length: 25 }).map((_, h) => (
          <line
            key={h}
            x1={hourToX(h)}
            x2={hourToX(h)}
            y1={CHART_TOP}
            y2={CHART_BOTTOM}
            className={h % 6 === 0 ? 'eld-grid__gridline eld-grid__gridline--major' : 'eld-grid__gridline'}
          />
        ))}
        {/* Quarter-hour minor ticks */}
        {Array.from({ length: 24 }).map((_, h) =>
          [0.25, 0.5, 0.75].map((frac) => (
            <line
              key={`${h}-${frac}`}
              x1={hourToX(h + frac)}
              x2={hourToX(h + frac)}
              y1={CHART_TOP}
              y2={CHART_BOTTOM}
              className="eld-grid__gridline eld-grid__gridline--minor"
            />
          ))
        )}

        {/* Horizontal row separators */}
        {ROW_ORDER.map((_, i) => (
          <line
            key={`h-${i}`}
            x1={0}
            x2={CHART_WIDTH}
            y1={CHART_TOP + i * ROW_HEIGHT}
            y2={CHART_TOP + i * ROW_HEIGHT}
            className="eld-grid__gridline eld-grid__gridline--major"
          />
        ))}
        <line
          x1={0}
          x2={CHART_WIDTH}
          y1={CHART_BOTTOM}
          y2={CHART_BOTTOM}
          className="eld-grid__gridline eld-grid__gridline--major"
        />

        {/* Hour axis labels */}
        {Array.from({ length: 25 }).map((_, h) => (
          <text key={`label-${h}`} x={hourToX(h)} y={CHART_TOP - 10} className="eld-grid__hour-label">
            {h % 24 === 0 ? 'Mid' : h % 12 === 0 ? 'Noon' : h % 12}
          </text>
        ))}

        {/* The duty status step line */}
        <path d={pathD} className="eld-grid__path" />

        {/* Filled dots at each transition */}
        {sorted.map((entry, i) => (
          <circle key={i} cx={hourToX(entry.start_hour)} cy={rowY(entry.duty_status)} r={2.6} className="eld-grid__dot" />
        ))}
      </svg>

      <ul className="eld-grid__remarks">
        {sorted.map((entry, i) => (
          <li key={i}>
            <span className="eld-grid__remarks-time">
              {formatHour(entry.start_hour)}&ndash;{formatHour(entry.end_hour)}
            </span>
            <span className="eld-grid__remarks-status">{ROW_LABELS[entry.duty_status]}</span>
            <span className="eld-grid__remarks-detail">
              {entry.remark}
              {entry.location ? ` — ${entry.location}` : ''}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatHour(h) {
  const hours = Math.floor(h) % 24;
  const minutes = Math.round((h - Math.floor(h)) * 60);
  const period = hours < 12 ? 'AM' : 'PM';
  const display = hours % 12 === 0 ? 12 : hours % 12;
  return `${display}:${String(minutes).padStart(2, '0')}${period}`;
}
