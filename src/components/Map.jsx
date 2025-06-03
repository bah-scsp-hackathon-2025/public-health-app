import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect, useState } from 'react';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';

// Sample data with details
const timeSeriesData = [
  { time: 1, lat: 40.7128, lon: -74.0060, city: 'New York', details: 'High hospitalization rate' },
  { time: 2, lat: 34.0522, lon: -118.2437, city: 'Los Angeles', details: 'Moderate COVID cases' },
  { time: 3, lat: 41.8781, lon: -87.6298, city: 'Chicago', details: 'Vaccination drive ongoing' },
  { time: 4, lat: 29.7604, lon: -95.3698, city: 'Houston', details: 'New variant detected' },
];

export default function USMapWithDots() {
  const [currentMarkers, setCurrentMarkers] = useState([]);

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i >= timeSeriesData.length) {
        clearInterval(interval);
        return;
      }
      setCurrentMarkers((prev) => [...prev, timeSeriesData[i]]);
      i++;
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <MapContainer
      center={[37.8, -96]}
      zoom={4}
      style={{ height: '550px', width: '600px', border: "1px solid black" }}
      scrollWheelZoom={false}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {currentMarkers.map((marker, idx) => (
        marker &&
        <Marker
          key={idx}
          position={[marker.lat, marker.lon]}
          icon={L.icon({
            iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).toString(),
            iconSize: [25, 41],
            iconAnchor: [12, 41],
          })}
        >
          <Popup>
            <strong>{marker.city}</strong><br />
            {marker.details}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
