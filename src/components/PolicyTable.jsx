import { useEffect, useState } from "react";
import { fetchApprovedPolicies, fetchDraftPolicies } from "../common/api";
import PolicyCard from "./PolicyCard";
import "./PolicyTable.css";

// Divider.jsx
const Divider = ({ vertical = false, style = {} }) => {
  const baseStyle = vertical
    ? {
        width: "2px",
        backgroundColor: "#ccc",
        margin: "0 20px",
        alignSelf: "stretch",
      }
    : {
        height: "1px",
        backgroundColor: "#ccc",
        margin: "10px 0",
        width: "100%",
      };

  return <div style={{ ...baseStyle, ...style }} />;
};


const PolicyTable = () => {
const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [approvedPolicies, setApprovedPolicies] = useState([]);
  useEffect(() => {
    const getApprovedPolicies = async () => {
      const result = await fetchApprovedPolicies();
      setApprovedPolicies(result);
    };
    getApprovedPolicies();
  }, [refreshTrigger]);

  const [draftPolicies, setDraftPolicies] = useState([]);
  useEffect(() => {
    const getDraftPolicies = async () => {
      const result = await fetchDraftPolicies();
      setDraftPolicies(result);
    };
    getDraftPolicies();
  }, [refreshTrigger]);

  return (
    <div className="two-column-container">
      <div className="column">
        <h2>Draft Policies</h2>
        {draftPolicies.map((item) => (
          <PolicyCard policy={item} onUpdate={() => setRefreshTrigger((prev) => prev + 1)}></PolicyCard>
        ))}
      </div>

      <Divider vertical={true} />

      <div className="column">
        <h2>Approved Policies</h2>
        {approvedPolicies.map((item) => (
          <PolicyCard policy={item}></PolicyCard>
        ))}
      </div>
    </div>
  );
};

export default PolicyTable;
