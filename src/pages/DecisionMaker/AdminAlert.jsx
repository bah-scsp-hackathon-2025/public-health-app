import { ArrowBigLeftDash } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  fetchAlert,
  fetchStrategiesByAlert,
  generateStrategiesByAlert,
} from "../../common/api";
import AdminNav from "../../components/AdminNav";
import StrategyCard from "../../components/StrategyCard";
import styles from "./AdminAlert.module.css";

function AdminAlert() {
  const { id } = useParams();

  const navigate = useNavigate();

  const goToDashboard = () => {
    navigate("/admin/dashboard");
  };

  const [strategies, setStrategies] = useState([]);
  useEffect(() => {
    const getStrategies = async () => {
      const result = await fetchStrategiesByAlert(id);
      setStrategies(result);
    };
    getStrategies();
  }, []);

  const [alert, setAlert] = useState([]);
  useEffect(() => {
    const getAlert = async () => {
      const result = await fetchAlert(id);
      setAlert(result);
    };
    getAlert();
  }, []);

  async function generateStrategies() {
    const result = await generateStrategiesByAlert(id);
    setStrategies(result);
  }

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

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          flexDirection: "column",
          textAlign: "center",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr auto 1fr",
            alignItems: "center",
            width: "100%",
            boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)",
          }}
        >
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

          <h1 style={{ margin: 0, textAlign: "center" }}>
            Alert Response Planner
          </h1>
          <div></div>
          {/* empty spacer to balance the p */}
        </div>

        <p style={{ color: "#191970" }}>
          View insights on public health alerts. Then, generate response
          strategies and draft policy documents.
        </p>
      </div>

      <div style={{ display: "flex", justifyContent: "center" }}>
        <div style={{ width: "80%", padding: "20px", height: "100%" }}>
          <div
            style={{
              backgroundColor: "#191970",
              padding: "40px",
              border: "1px solid black",
            }}
          >
            <div style={{ marginBottom: "20px" }}>
              <div
                style={{
                  border: "1px solid black",
                  borderRadius: "10px",
                  padding: "10px",
                  minHeight: "80px",
                  background: "white",
                }}
              >
                {alert.description}
              </div>
            </div>

            <div style={{ display: "flex", gap: "10px" }}>
              <div
                style={{
                  border: "1px solid black",
                  borderRadius: "10px",
                  padding: "10px",
                  flex: "1",
                  minHeight: "80px",
                  background: "white",
                }}
              >
                {alert.risk_score}
              </div>
              <div
                style={{
                  border: "1px solid black",
                  borderRadius: "10px",
                  padding: "10px",
                  flex: "2",
                  minHeight: "80px",
                  background: "white",
                }}
              >
                {alert.risk_reason}
              </div>
            </div>
          </div>
          <div style={{ marginTop: "20px" }}>
            <span>Ready to start planning?</span>
            <button onClick={generateStrategies}>
              Generate Courses of Action
            </button>
          </div>
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div style={{ width: "80%" }}>
          <h2 style={{ borderBottom: "1px dashed black" }}>
            Generated Strategies
          </h2>
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div style={{ width: "80%" }}>
          {strategies.map((strategy) => (
            <StrategyCard strategy={strategy}></StrategyCard>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AdminAlert;
