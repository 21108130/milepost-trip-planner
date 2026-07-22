import { useState } from 'react';
import './RouteInstructions.css';

const COLLAPSED_COUNT = 8;

export default function RouteInstructions({ instructions }) {
  const [expanded, setExpanded] = useState(false);

  if (!instructions?.length) {
    return <p className="route-instructions__empty">No turn-by-turn instructions available.</p>;
  }

  const visible = expanded ? instructions : instructions.slice(0, COLLAPSED_COUNT);

  return (
    <div>
      <ol className="route-instructions">
        {visible.map((step, i) => (
          <li key={i} className="route-instructions__item">
            <span className="route-instructions__index">{i + 1}</span>
            <div>
              <p className="route-instructions__text">{step.instruction}</p>
              <p className="route-instructions__meta">
                {step.distance_miles.toFixed(1)} mi &middot; mile {Math.round(step.cumulative_distance_miles)}
              </p>
            </div>
          </li>
        ))}
      </ol>
      {instructions.length > COLLAPSED_COUNT && (
        <button className="route-instructions__toggle" onClick={() => setExpanded((e) => !e)} type="button">
          {expanded ? 'Show fewer steps' : `Show all ${instructions.length} steps`}
        </button>
      )}
    </div>
  );
}
