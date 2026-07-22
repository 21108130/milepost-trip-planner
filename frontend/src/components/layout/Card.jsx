import './Card.css';

export default function Card({ title, eyebrow, action, children, className = '' }) {
  return (
    <section className={`card ${className}`}>
      {(title || eyebrow || action) && (
        <header className="card__header">
          <div>
            {eyebrow && <span className="card__eyebrow">{eyebrow}</span>}
            {title && <h3 className="card__title">{title}</h3>}
          </div>
          {action && <div className="card__action">{action}</div>}
        </header>
      )}
      <div className="card__body">{children}</div>
    </section>
  );
}
