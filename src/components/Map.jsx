import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { fetchAlerts } from "../common/api";

export default function USMapWithDots() {
  const [alerts, setAlerts] = useState([]);
  useEffect(() => {
    const getAlerts = async () => {
      const result = await fetchAlerts();
      setAlerts(result);
    };
    getAlerts();
  }, []);

  return (
    <MapContainer
      center={[37.8, -96]}
      zoom={4}
      style={{ height: "550px", width: "600px", border: "1px solid black" }}
      scrollWheelZoom={false}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {alerts.map(
        (marker) =>
          marker && (
            <Marker
              key={marker.id}
              position={[marker.latitude, marker.longitude]}
              icon={L.icon({
                iconUrl: new URL(
                  "leaflet/dist/images/marker-icon.png",
                  import.meta.url
                ).toString(),
                iconSize: [25, 41],
                iconAnchor: [12, 41],
              })}
            >
              <Popup>
                <strong>{marker.location}</strong>
                <br />
                {marker.description}
              </Popup>
            </Marker>
          )
      )}
    </MapContainer>
  );
}
