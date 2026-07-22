import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TripForm from '../components/trip/TripForm';
import Card from '../components/layout/Card';
import ErrorState from '../components/layout/ErrorState';
import { planTrip } from '../api/trips';
import { extractErrorMessage } from '../api/client';
import './HomePage.css';

export default function HomePage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(formValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      const trip = await planTrip(formValues);
      navigate(`/trips/${trip.id}/results`);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="home-page">
      <section className="home-hero">
        <div className="home-hero__inner">
          <span className="home-hero__eyebrow">Property-Carrying &middot; 70&#8202;hr / 8&#8202;day Cycle</span>
          <h1 className="home-hero__title">
            Plan the route. <br />
            Draw the log. <br />
            <span className="home-hero__accent">Stay compliant.</span>
          </h1>
          <p className="home-hero__subtitle">
            Enter a trip and MilePost calculates the drivable route, places fuel and rest
            stops where HOS rules require them, and fills out FMCSA-style daily log sheets
            automatically — for as many days as the trip takes.
          </p>
        </div>
      </section>

      <div className="home-page__content">
        <Card eyebrow="Step 1 of 3" title="Trip Details">
          <TripForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
        </Card>

        {error && (
          <div className="home-page__error">
            <ErrorState message={error} />
          </div>
        )}

        <div className="home-page__how-it-works">
          <HowItWorksStep
            number="01"
            title="Route calculated"
            description="Free OpenStreetMap routing plots current → pickup → dropoff and totals the miles and drive time."
          />
          <HowItWorksStep
            number="02"
            title="HOS rules applied"
            description="11-hr driving cap, 14-hr window, 30-min breaks, 10-hr rest, and 70/8 cycle limits are simulated mile by mile."
          />
          <HowItWorksStep
            number="03"
            title="Logs drawn for you"
            description="Every day of the trip gets its own filled-out ELD grid — off duty, sleeper berth, driving, on duty."
          />
        </div>
      </div>
    </div>
  );
}

function HowItWorksStep({ number, title, description }) {
  return (
    <div className="how-it-works__step">
      <span className="how-it-works__number">{number}</span>
      <div>
        <h4 className="how-it-works__title">{title}</h4>
        <p className="how-it-works__description">{description}</p>
      </div>
    </div>
  );
}
