import { ArrowBigLeftDash, NotebookPen } from "lucide-react";
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from "react-router-dom";
import {
  fetchAlert,
  fetchPoliciesByAlert,
  fetchStrategiesByAlert,
  generateStrategiesByAlert
} from "../../common/api";
import AdminNav from "../../components/AdminNav";
import StrategyCard from '../../components/StrategyCard';
import styles from "./AdminAlert.module.css";

function AdminAlert() {
  const { id } = useParams();

  const [selectedId, setSelectedId] = useState(null);

  const navigate = useNavigate();

  const goToDashboard = () => {
    navigate("/admin/dashboard");
  };

  const [strategies, setStrategies] = useState([]);
  useEffect(() => {
    const getStrategies = async () => {
      try {
        const result = await fetchStrategiesByAlert(id);
        setStrategies(result);
      } catch (error) {
        console.error("Error getting alerts:", error);
      }
    };
    getStrategies();
  }, []);

  const [alert, setAlert] = useState([]);
  useEffect(() => {
    const getAlert = async () => {
      try {
        const result = await fetchAlert(id);
        setAlert(result);
      } catch (error) {
        console.error("Error getting alerts:", error);
      }
    };
    getAlert();
  }, []);

  const [policiesForAlert, setPoliciesForAlert] = useState([]);
useEffect(() => {
  const getPolicies = async () => {
    try {
      console.log(id)
        const result = await fetchPoliciesByAlert(id);
        console.log(result)
        setPoliciesForAlert(result);
    } catch (error) {
      console.error("Error getting policies:", error);
    }
  };
  getPolicies();
}, []);


  async function generateStrategies() {
    const result = await generateStrategiesByAlert(id);
    setStrategies(result);
  }

  console.log(policiesForAlert)

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        marginTop: "20px",
      }}
    >
      <AdminNav></AdminNav>

         <div style={{display: "flex", justifyContent: "center", flexDirection: "column", textAlign: "center"}}>
      
          <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center", width: "100%",boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)"}}>
             
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

          <h1 style={{ margin: 0, textAlign: "center"}}>Alert Response Planner</h1>
          <div></div>{/* empty spacer to balance the p */}
          </div>
      
          <p style={{color: "#191970"}}>View insights on public health alerts. Then, generate response strategies and draft policy documents.</p>
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
        background: "white",
        color: alert.risk_score < 4 ? "green" : alert.risk_score < 7 ? "orange" : "red",
        fontWeight: "bold",
        fontSize: "50px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        textAlign: "center",
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

          {strategies.length == 0 &&
          <div style={{ marginTop: "20px", display: "flex", justifyContent: "center", alignItems: "center" }}>
            <NotebookPen/>
            <span>Ready to start planning?</span>
            <button onClick={generateStrategies}>
              Generate Strategies
            </button>
          </div>
      
         }
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div style={{ width: "80%" }}>
          <h1 style={{ borderBottom: "1px solid black" , textAlign: "center"}}>
            Generated Strategies
          </h1>
          {strategies != 0 ? 
          <p style={{textAlign: "center"}}>View and evaluate the generated strategies. Then, select a strategy to generate a draft policy document</p>
          : 
           <p style={{textAlign: "center"}}>No policies have been generated yet for this alert.</p>
           }
          <div style={{ width: "80%", marginLeft: "75px"}}>
     {policiesForAlert.length == 0 ?
        <div style={{display: "flex", flexDirection: "column", alignItems: "center", width: "100%", marginLeft: "15%"}}>
        {strategies.map((strategy) => (
        <div key={strategy.id} style={{width: "100%"}}>
       <StrategyCard
          key={strategy.id}
          strategy={strategy}
          isSelected={strategy.id === selectedId}
          onClick={() => setSelectedId(strategy.id)}
        
      />
    </div>
        ))
      } </div>
      : <div></div>} 

        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        </div>
      </div>
    </div>
  );
}

export default AdminAlert;