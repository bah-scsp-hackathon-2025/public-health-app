import { useState, useEffect } from "react";
import styles from './Alerts.module.css';
import { fetchAlerts } from "../common/api";


function AlertCard({alert, onClick}) {
    return (
        <div onClick={onClick} className={styles.alertCard}>
            <strong>{alert.name}</strong>
            <div>{alert.description}</div>
        </div>
    )
}

import { useNavigate } from 'react-router-dom';

function RegularAlertPane () {

  const navigate = useNavigate();

  const goToAlert = (id) => {
     navigate(`/alert/${id}`);
  };

    const [alerts, setAlerts] = useState([]);
    useEffect(() => {
      const getAlerts = async () => {
        const result = await fetchAlerts();
        // set alerts to be just the first 4 for now
        setAlerts(result.slice(0, 4));
      };
      getAlerts();
    }, []);

    return (
        <div style={{height: "550px", width: "600px", backgroundColor: '#f0f0f0', border: "1px solid black"}}>
            <div style={{display: "flex", justifyContent: "center"}}>
                <h2 style={{color: "#191970", borderBottom: "1px solid black", textAlign: "center", width: "100%"}}>Alerts</h2>
               
            </div>
            <div style={{display: "flex", alignItems: "center", flexDirection: "column", gap: "20px"}}>
            {alerts.map((data) => (
                <AlertCard onClick={() => goToAlert(data.id)} key={data.id} alert={data} />
            ))}
            </div>
        </div>
    )
}

export default RegularAlertPane