import { useState } from 'react';
import './TripForm.css';

const INITIAL_STATE = {
  currentLocation: '',
  pickupLocation: '',
  dropoffLocation: '',
  currentCycleUsedHours: '',
};

export default function TripForm({ onSubmit, isSubmitting }) {
  const [form, setForm] = useState(INITIAL_STATE);
  const [touched, setTouched] = useState({});

  const errors = validate(form);
  const hasErrors = Object.keys(errors).length > 0;

  function handleChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleBlur(field) {
    setTouched((prev) => ({ ...prev, [field]: true }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    setTouched({
      currentLocation: true,
      pickupLocation: true,
      dropoffLocation: true,
      currentCycleUsedHours: true,
    });
    if (hasErrors) return;

    onSubmit({
      currentLocation: form.currentLocation.trim(),
      pickupLocation: form.pickupLocation.trim(),
      dropoffLocation: form.dropoffLocation.trim(),
      currentCycleUsedHours: Number(form.currentCycleUsedHours),
    });
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit} noValidate>
      <div className="trip-form__grid">
        <Field
          label="Current Location"
          hint="Where the driver is right now"
          value={form.currentLocation}
          onChange={(v) => handleChange('currentLocation', v)}
          onBlur={() => handleBlur('currentLocation')}
          error={touched.currentLocation && errors.currentLocation}
          placeholder="e.g. Chicago, IL"
        />
        <Field
          label="Pickup Location"
          hint="Where the load is picked up"
          value={form.pickupLocation}
          onChange={(v) => handleChange('pickupLocation', v)}
          onBlur={() => handleBlur('pickupLocation')}
          error={touched.pickupLocation && errors.pickupLocation}
          placeholder="e.g. Indianapolis, IN"
        />
        <Field
          label="Dropoff Location"
          hint="Final delivery destination"
          value={form.dropoffLocation}
          onChange={(v) => handleChange('dropoffLocation', v)}
          onBlur={() => handleBlur('dropoffLocation')}
          error={touched.dropoffLocation && errors.dropoffLocation}
          placeholder="e.g. Columbus, OH"
        />
        <Field
          label="Current Cycle Used (Hrs)"
          hint="Hours already used in the 70-hr / 8-day cycle"
          value={form.currentCycleUsedHours}
          onChange={(v) => handleChange('currentCycleUsedHours', v)}
          onBlur={() => handleBlur('currentCycleUsedHours')}
          error={touched.currentCycleUsedHours && errors.currentCycleUsedHours}
          placeholder="e.g. 12"
          type="number"
          min={0}
          max={70}
          step={0.5}
        />
      </div>

      <div className="trip-form__footer">
        <div className="trip-form__assumptions">
          <span className="trip-form__chip">Property-carrying driver</span>
          <span className="trip-form__chip">70&#8202;hrs / 8&#8202;days</span>
          <span className="trip-form__chip">No adverse conditions</span>
          <span className="trip-form__chip">Fuel every 1,000&#8202;mi</span>
          <span className="trip-form__chip">1&#8202;hr pickup &amp; dropoff</span>
        </div>
        <button className="trip-form__submit" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Planning Route…' : 'Plan Trip'}
        </button>
      </div>
    </form>
  );
}

function Field({ label, hint, value, onChange, onBlur, error, placeholder, type = 'text', ...rest }) {
  return (
    <label className="trip-form__field">
      <span className="trip-form__label">{label}</span>
      <input
        className={`trip-form__input ${error ? 'has-error' : ''}`}
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        {...rest}
      />
      {error ? (
        <span className="trip-form__error">{error}</span>
      ) : (
        <span className="trip-form__hint">{hint}</span>
      )}
    </label>
  );
}

function validate(form) {
  const errors = {};
  if (!form.currentLocation.trim()) errors.currentLocation = 'Enter the driver\u2019s current location.';
  if (!form.pickupLocation.trim()) errors.pickupLocation = 'Enter a pickup location.';
  if (!form.dropoffLocation.trim()) errors.dropoffLocation = 'Enter a dropoff location.';

  const cycleValue = form.currentCycleUsedHours;
  if (cycleValue === '' || cycleValue === null) {
    errors.currentCycleUsedHours = 'Enter hours already used in the cycle.';
  } else {
    const num = Number(cycleValue);
    if (Number.isNaN(num) || num < 0 || num > 70) {
      errors.currentCycleUsedHours = 'Must be between 0 and 70 hours.';
    }
  }
  return errors;
}
