import { ArrowBigLeftDash } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from 'react-router-dom';
import { fetchAlert, fetchApprovedPoliciesByAlert } from "../../common/api";
import PolicyDocument from "../../components/PolicyDocument";
import RegularNav from "../../components/RegularNav";
import styles from './Alert.module.css';

function Alert() {
  const { id } = useParams();

  const navigate = useNavigate()

  const goToDashboard = () => {
    navigate('/dashboard')
  }

    const [policies, setPolicies] = useState([]);
    useEffect(() => {
      const getPolicies = async () => {
        const result = await fetchApprovedPoliciesByAlert(id);
        setPolicies(result);
      };
      getPolicies();
    }, []);
  
    const [alert, setAlert] = useState([]);
    useEffect(() => {
      const getAlert = async () => {
        const result = await fetchAlert(id);
        setAlert(result);
      };
      getAlert();
    }, []);

    console.log(policies)

  return (
    <div style={{display: "flex", flexDirection: "column", height: "100vh", marginTop: "20px"}}>
      <RegularNav></RegularNav>

    <div style={{display: "flex", justifyContent: "center", flexDirection: "column", textAlign: "center"}}>

    <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center", width: "100%", boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)" }}>
       
      <div className={styles.button}>
                  <div
                  className={styles.logout}
                  onClick={() => goToDashboard()}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px", // space between icon and text
                    cursor: "pointer",
                    color: "#191970",
                  }}
            >
              <ArrowBigLeftDash />
              Go back to dashboard
            </div>
           </div>
    <h1 style={{ margin: 0, textAlign: "center"}}>Alert Response and Policy Updates</h1>
    <div></div>{/* empty spacer to balance the p */}
    </div>

    <p style={{color: "#191970"}}>View response decisions and policy updates to public health situations.</p>
      </div>
      

    <div style={{display: "flex", justifyContent: "center"}}>
     
    <div style={{ width: "80%", padding: "20px", height: '100%'}}>
        <div style={{display: "flex", justifyContent: "center"}}>
       <label style={{ color: "black", marginBottom: "5px", fontSize: "25px", display: "block" }}>{alert.name}</label>
       </div>
       
<div style={{ backgroundColor: "#191970", padding: "40px", border: "1px solid black", borderRadius: "20px" }}>

  <div style={{ marginBottom: "20px" }}>
    <label style={{ color: "white", marginBottom: "5px", display: "block" }}>Alert Description</label>
    <div style={{ 
      border: "1px solid black", 
      borderRadius: "10px", 
      padding: "10px", 
      minHeight: "80px",
      background: "white" 
    }}>
      {alert.description}
    </div>
  </div>

  <div style={{ display: "flex", gap: "10px" }}>
    <div style={{ flex: "1" }}>
      <label style={{ color: "white", marginBottom: "5px", display: "block" }}>Risk Score</label>
      <div style={{ 
        border: "1px solid black", 
        borderRadius: "10px", 
        padding: "10px", 
        minHeight: "80px",
        background: "white" 
      }}>
        {alert.risk_score}
      </div>
    </div>

    <div style={{ flex: "2" }}>
      <label style={{ color: "white", marginBottom: "5px", display: "block" }}>Risk Score Reasoning</label>
      <div style={{ 
        border: "1px solid black", 
        borderRadius: "10px", 
        padding: "10px", 
        minHeight: "80px",
        background: "white" 
      }}>
        {alert.risk_reason}
      </div>
    </div>
  </div>
</div>

    
    </div>
    </div>

    <div style={{display: "flex", justifyContent: "center", marginTop: "20px"}}>
    <div style={{fontSize: "30px", fontWeight: "bold", borderBottom: "1px solid black"}}>Policy Document</div>
       
    </div>
    <div style={{width: "100%", display: "flex", justifyContent: "center", marginTop: "20px"}}>
        {policies.length == 0 && <div>No policies have been approved for this alert yet. Please stay posted for updates.</div>}
        {policies.map((item) => (
                <PolicyDocument policy={item}></PolicyDocument>
                ))}
    </div>
    </div>
  );
}

export default Alert;