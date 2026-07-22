import { Routes, Route, useLocation } from 'react-router-dom';
import NavBar from './components/layout/NavBar';
import ErrorBoundary from './components/layout/ErrorBoundary';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import EldLogsPage from './pages/EldLogsPage';
import './App.css';

export default function App() {
  const location = useLocation();
  return (
    <>
      <NavBar />
      <main className="app-main">
        <ErrorBoundary key={location.pathname}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/trips/:tripId/results" element={<ResultsPage />} />
            <Route path="/trips/:tripId/logs" element={<EldLogsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ErrorBoundary>
      </main>
      <footer className="app-footer">
        <span>MilePost &mdash; Truck Trip Planner &amp; ELD Log Generator</span>
        <span>Routing by OpenStreetMap &amp; OSRM</span>
      </footer>
    </>
  );
}

function NotFound() {
  return (
    <div className="app-not-found">
      <h1>404</h1>
      <p>That page doesn&rsquo;t exist. Head back to plan a trip.</p>
    </div>
  );
}
