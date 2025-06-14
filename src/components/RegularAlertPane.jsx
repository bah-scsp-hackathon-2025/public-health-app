import styles from './Alerts.module.css';


function AlertCard({alert, onClick}) {
    return (
        <div onClick={onClick} className={styles.alertCard}>
            <strong>{alert.name}</strong>
            <div>{alert.description.slice(0, 100)}...</div>
        </div>
    )
}

import { useNavigate } from 'react-router-dom';

function RegularAlertPane ({alerts}) {

  const navigate = useNavigate();

  const goToAlert = (id) => {
     navigate(`/alert/${id}`);
  };

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