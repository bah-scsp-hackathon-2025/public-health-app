import { ArrowBigLeftDash } from "lucide-react";
import { useNavigate, useParams } from 'react-router-dom';
import { useState, useEffect } from "react";
import RegularNav from "../../components/RegularNav";
import styles from './Alert.module.css';
import { fetchAlert, fetchApprovedPoliciesByAlert } from "../../common/api";
import PolicyCard from "../../components/PolicyCard";

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
      
   
<div style={{backgroundColor: "#191970", padding: "40px", border: "1px solid black"}}>
      <div style={{ marginBottom: "20px" }}>
        <div style={{ 
          border: "1px solid black", 
          borderRadius: "10px", 
          padding: "10px", 
          minHeight: "80px" ,
           background: "white"
        }}>
          {alert.description}
        </div>
      </div>

      <div style={{ display: "flex", gap: "10px"}}>
        <div style={{ 
          border: "1px solid black", 
          borderRadius: "10px", 
          padding: "10px", 
          flex: "1", 
          minHeight: "80px",
          background: "white"
        }}>
          {alert.risk_score}
        </div>
        <div style={{ 
          border: "1px solid black", 
          borderRadius: "10px", 
          padding: "10px", 
          flex: "2", 
          minHeight: "80px" ,
           background: "white"
        }}>
          {alert.risk_reason}
        </div>
      </div>
      </div>
    
    </div>
    </div>

    <div style={{display: "flex", justifyContent: "center", marginTop: "20px"}}>
    <div style={{fontSize: "30px", fontWeight: "bold", borderBottom: "1px solid black"}}>Policy Document</div>
      <div>
        {policies.map((item) => (
          <PolicyCard policy={item}></PolicyCard>
        ))}
      </div>
    </div>

    </div>
  );
}

export default Alert;
