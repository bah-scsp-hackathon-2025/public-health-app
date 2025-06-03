import styles from './Alerts.module.css';

function AlertCard({alert, onClick}) {
    return (
        <div onClick={onClick} className={styles.alertCard}>
            <strong>{alert.city}</strong>
            <div>{alert.details}</div>
        </div>
    )
}

import { useNavigate } from 'react-router-dom';

function RegularAlertPane () {

  const navigate = useNavigate();

  const goToAlert = (id) => {
     navigate(`/alert/${id}`);
  };

    // Sample data with details
    const timeSeriesData = [
    { time: 1, lat: 40.7128, lon: -74.0060, city: 'New York', details: 'High hospitalization rate' },
    { time: 2, lat: 34.0522, lon: -118.2437, city: 'Los Angeles', details: 'Moderate COVID cases' },
    { time: 3, lat: 41.8781, lon: -87.6298, city: 'Chicago', details: 'Vaccination drive ongoing' },
    { time: 4, lat: 29.7604, lon: -95.3698, city: 'Houston', details: 'New variant detected' },
    ];

    return (
        <div style={{height: "550px", width: "600px", backgroundColor: '#f0f0f0', border: "1px solid black"}}>
            <div style={{display: "flex", justifyContent: "center"}}>
                <h2 style={{color: "#191970", borderBottom: "1px solid black", textAlign: "center", width: "100%"}}>Alerts</h2>
               
            </div>
            <div style={{display: "flex", alignItems: "center", flexDirection: "column", gap: "20px"}}>
            {timeSeriesData.map((data) => (
                <AlertCard onClick={() => goToAlert(data.time)} key={data.time} alert={data} />
            ))}
            </div>
        </div>
    )
}

export default RegularAlertPane