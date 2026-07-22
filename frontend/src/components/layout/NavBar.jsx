import { NavLink, useParams } from 'react-router-dom';
import './NavBar.css';

export default function NavBar() {
  const { tripId } = useParams();

  return (
    <header className="navbar">
      <div className="navbar__inner">
        <div className="navbar__brand">
          <span className="navbar__mark">MP</span>
          <span className="navbar__title">MilePost</span>
        </div>

        <nav className="navbar__links">
          <NavLink to="/" end className={({ isActive }) => `navbar__link ${isActive ? 'is-active' : ''}`}>
            Plan a Trip
          </NavLink>
          <NavLink
            to={tripId ? `/trips/${tripId}/results` : '/'}
            className={({ isActive }) => `navbar__link ${isActive ? 'is-active' : ''} ${!tripId ? 'is-disabled' : ''}`}
          >
            Route &amp; Stops
          </NavLink>
          <NavLink
            to={tripId ? `/trips/${tripId}/logs` : '/'}
            className={({ isActive }) => `navbar__link ${isActive ? 'is-active' : ''} ${!tripId ? 'is-disabled' : ''}`}
          >
            ELD Logs
          </NavLink>
        </nav>

        <div className="navbar__meta">
          <span className="navbar__meta-pill">
            <span className="navbar__meta-dot" />
            70&#8202;hr / 8&#8202;day cycle
          </span>
        </div>
      </div>
    </header>
  );
}
