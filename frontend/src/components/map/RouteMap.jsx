import { useMemo } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import 'leaflet/dist/leaflet.css';
import './RouteMap.css';

// Fix default marker icon paths (Vite bundling breaks Leaflet's default asset lookup).
const defaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const STOP_COLORS = {
  pickup: '#2fbd6b',
  dropoff: '#ef4444',
  fuel: '#ff6a1a',
  rest: '#8a90a0',
  break: '#5a6072',
};

const STOP_LABELS = {
  pickup: 'Pickup',
  dropoff: 'Dropoff',
  fuel: 'Fuel Stop',
  rest: 'Rest / Sleeper Berth',
  break: '30-Minute Break',
};

function stopIcon(stopType) {
  const color = STOP_COLORS[stopType] || '#34405a';
  return L.divIcon({
    className: 'route-map__stop-icon',
    html: `<span style="background:${color}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
}

function FitBounds({ positions }) {
  const map = useMap();
  useMemo(() => {
    if (positions.length > 0) {
      map.fitBounds(positions, { padding: [40, 40] });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [positions.length]);
  return null;
}

export default function RouteMap({ routeGeometry, stops = [] }) {
  const routePositions = useMemo(() => {
    if (!routeGeometry?.coordinates) return [];
    return routeGeometry.coordinates.map(([lng, lat]) => [lat, lng]);
  }, [routeGeometry]);

  const stopPositions = stops
    .filter((s) => s.latitude != null && s.longitude != null)
    .map((s) => [s.latitude, s.longitude]);

  const allPositions = routePositions.length > 0 ? routePositions : stopPositions;
  const center = allPositions[Math.floor(allPositions.length / 2)] || [39.5, -87.5];

  return (
    <div className="route-map">
      <MapContainer center={center} zoom={6} scrollWheelZoom className="route-map__container">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
        />
        {routePositions.length > 0 && (
          <Polyline positions={routePositions} pathOptions={{ color: '#ff6a1a', weight: 4, opacity: 0.95 }} />
        )}
        {stops.map((stop) =>
          stop.latitude != null && stop.longitude != null ? (
            <Marker
              key={stop.id}
              position={[stop.latitude, stop.longitude]}
              icon={stop.stop_type ? stopIcon(stop.stop_type) : defaultIcon}
            >
              <Popup>
                <strong>{STOP_LABELS[stop.stop_type] || stop.stop_type}</strong>
                <br />
                {stop.location_name}
                <br />
                Mile {Math.round(stop.distance_from_start_miles)}
              </Popup>
            </Marker>
          ) : null
        )}
        <FitBounds positions={allPositions} />
      </MapContainer>

      <div className="route-map__legend">
        {Object.entries(STOP_LABELS).map(([key, label]) => (
          <span key={key} className="route-map__legend-item">
            <span className="route-map__legend-dot" style={{ background: STOP_COLORS[key] }} />
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}
