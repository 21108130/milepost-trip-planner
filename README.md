# MilePost — Truck Trip Planner & ELD Log Generator

A full-stack application for property-carrying truck drivers: enter a trip, get
a compliant route with fuel/rest stops, and get FMCSA-style Daily Log Sheets
drawn automatically for every day of the trip.

**Stack:** Django + Django REST Framework (backend) · React + Vite (frontend) · OpenStreetMap / OSRM (maps & routing, free, no API key)

---

## 1. What it does

Given:
- Current location
- Pickup location
- Dropoff location
- Current cycle hours already used (0–70)

It produces:
- A driving route (current → pickup → dropoff) rendered on an interactive map
- Total distance and estimated drive time
- Turn-by-turn directions
- Fuel stops (every 1,000 miles), rest stops (10-hr off duty), and 30-minute breaks — placed exactly where HOS rules require them
- One FMCSA-style Daily Log Sheet (drawn as an SVG duty-status grid) per day of the trip

### Assumptions (fixed, per the assessment brief)
- Property-carrying driver, 70-hour / 8-day cycle
- No adverse driving conditions
- Fuel at least once every 1,000 miles
- 1 hour each for pickup and dropoff
- Average driving speed: 55 mph (used to convert HOS hour-limits into mile-limits)

---

## 2. Architecture

```
trip-planner/
├── backend/            Django + DRF API
│   └── trips/
│       ├── models.py          Trip, Stop, DailyLog, LogEntry
│       ├── serializers.py     Request/response shapes
│       ├── views.py           Thin views — no business logic
│       ├── services/          All business logic lives here
│       │   ├── geocoding_service.py     Nominatim (OpenStreetMap)
│       │   ├── routing_service.py       OSRM driving directions
│       │   ├── hos_planner_service.py   HOS rules simulation engine
│       │   ├── eld_log_service.py       Splits timeline into daily logs
│       │   ├── stop_extraction_service.py
│       │   └── trip_service.py          Orchestrates + persists everything
│       ├── utils/              Custom exceptions, DRF exception handler
│       └── tests/              22 unit + API tests
└── frontend/            React (Vite) SPA
    └── src/
        ├── api/                 Axios client + trip endpoints
        ├── components/
        │   ├── trip/            Form, stops timeline, route instructions
        │   ├── map/              React-Leaflet route map
        │   ├── eld/              FMCSA-style log grid (SVG) + daily sheet
        │   └── layout/           NavBar, Card, StatCard, Loading/Error states
        └── pages/               Home, Results, ELD Logs
```

Backend follows clean architecture: **views never contain business logic** —
they validate input, call a service, and serialize the result. All routing,
HOS math, and log-splitting logic lives in `trips/services/`.

### The HOS engine (`hos_planner_service.py`)

Simulates the trip as a sequence of duty-status segments, enforcing:
- 11-hour driving limit per shift
- 14-hour on-duty window per shift
- 30-minute break required after 8 cumulative hours of driving
- 10 consecutive hours off duty between shifts
- 70-hour / 8-day cycle limit, with a 34-hour restart if exceeded
- A fuel stop inserted at least every 1,000 miles
- 1 hour on-duty (not driving) for pickup and for dropoff

`eld_log_service.py` then splits that timeline at midnight boundaries into
one `DailyLog` per calendar day, with `LogEntry` rows describing each
duty-status segment (used to draw the grid).

---

## 3. Running locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```
API available at `http://localhost:8000/api/`. Admin at `http://localhost:8000/admin/`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env             # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev
```
App available at `http://localhost:5173`.

### Running tests

```bash
cd backend
source venv/bin/activate
python manage.py test trips
```
22 tests covering models, the HOS planner (break/rest/restart/fuel-stop
rules), ELD day-splitting, and the API endpoints (with geocoding/routing
mocked so tests run offline and deterministically).

---

## 4. API Reference

| Method | Endpoint                | Description                                   |
|--------|--------------------------|------------------------------------------------|
| POST   | `/api/trips/plan/`      | Plan a new trip. Body: `current_location`, `pickup_location`, `dropoff_location`, `current_cycle_used_hours`. Returns the full trip with stops and daily logs. |
| GET    | `/api/trips/`           | List previously planned trips.                 |
| GET    | `/api/trips/<id>/`      | Retrieve a single trip with full details.      |

Errors are returned as `{"error": {"message": "...", "detail": "..."}}` with
an appropriate HTTP status code (400 for validation errors, 422 if a route
can't be planned, 404 if not found).

---

## 5. Deployment

### Backend → Render

1. Push `backend/` to GitHub.
2. In Render, "New +" → "Blueprint", point it at the repo — `render.yaml` is
   already configured (installs requirements, runs migrations, starts
   gunicorn).
3. Set `CORS_ALLOWED_ORIGINS` to your deployed frontend URL once you have it
   (or leave `CORS_ALLOW_ALL_ORIGINS=True` for a quick demo).

### Frontend → Vercel

1. Push `frontend/` to GitHub (or import the monorepo and set the project
   root to `frontend/`).
2. Set the environment variable `VITE_API_BASE_URL` to your deployed backend's
   `/api` URL (e.g. `https://trip-planner-backend.onrender.com/api`).
3. Deploy — `vercel.json` handles SPA routing so refreshing `/trips/1/logs`
   doesn't 404.

---

## 6. Notes on the free map APIs

- **Geocoding**: [Nominatim](https://nominatim.openstreetmap.org/) (OpenStreetMap) — free, no API key, rate-limited to ~1 request/second (handled automatically).
- **Routing**: [OSRM](http://router.project-osrm.org/) public demo server — free, no API key, returns real driving distances, durations, geometry, and turn-by-turn steps.

Both are best-effort public services with no uptime SLA. For a production
deployment with guaranteed throughput, swap in a paid tier or self-hosted
OSRM instance — the `RoutingService`/`GeocodingService` classes are the only
places that would need to change.

---

## 7. Tech decisions worth knowing about

- **SQLite in dev, Postgres-ready**: `DATABASE_URL` env var switches to
  Postgres automatically via `dj-database-url` — no code changes needed.
- **55 mph average speed** is used only to convert HOS hour-limits into
  mile-limits for the simulation; the actual route distance/duration shown
  to the user comes from OSRM's real driving-time estimate.
- **Stops are placed exactly at mile markers** derived from the timeline
  simulation, then their lat/lng is interpolated along the actual route
  geometry so they land approximately on the road, not in a straight line.
