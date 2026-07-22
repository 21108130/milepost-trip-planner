import './ErrorState.css';

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state" role="alert">
      <div className="error-state__icon" aria-hidden="true">!</div>
      <div>
        <p className="error-state__title">Trip could not be planned</p>
        <p className="error-state__message">{message}</p>
        {onRetry && (
          <button className="error-state__retry" onClick={onRetry} type="button">
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
