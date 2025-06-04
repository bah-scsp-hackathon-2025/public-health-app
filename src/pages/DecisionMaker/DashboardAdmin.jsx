import { useEffect, useState } from "react";
import { fetchSummaries } from "../../common/api";
import AdminNav from "../../components/AdminNav";
import AlertPane from "../../components/AlertPane";
import Chart from "../../components/Chart";
import Map from "../../components/Map";

function YouTubeEmbed() {
  return (
    <div style={{ position: "relative", paddingBottom: "56.25%", height: 0 }}>
      <iframe
        src="https://www.youtube.com/embed/YdbQ1d0OBt0"
        title="YouTube video"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
        }}
      />
    </div>
  );
}

function AdminDashboard() {
  const [summary, setSummary] = useState([]);
  useEffect(() => {
    const getSummary = async () => {
      const result = await fetchSummaries();
      if (result) {
        setSummary(result[0]);
      } else {
        setSummary({"description": ""});
      }
    };
    getSummary();
  }, []);


  return (
    <div style={{ display: "flex", flexDirection: "column", marginTop: "0%" }}>
      <AdminNav></AdminNav>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          marginBottom: "40px",
          boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)",
        }}
      >
        <h1 style={{ marginBottom: "0px" }}>Central Dashboard</h1>
      </div>

      <div style={{ width: "100%", display: "flex", justifyContent: "center" }}>
        <div style={{ display: "flex", width: "80%", gap: "50px" }}>
          <Map style={{ width: "50%" }} />
          <AlertPane style={{ width: "50%" }} />
        </div>
      </div>

      <div
        style={{
          width: "100%",
          display: "flex",
          justifyContent: "center",
          marginTop: "50px",
        }}
      >
        <div
          style={{
            background: "#f0f0f0",
            width: "80%",
            border: "1px solid black",
            padding: "20px",
            boxSizing: "border-box",
            height: "80%",
          }}
        >
          {summary.description}...
        </div>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "row",
          gap: "50px",
          marginLeft: "50px",
          marginTop: "100px",
        }}
      >
        <Chart />
        <Chart />
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          gap: "50px",
          marginLeft: "50px",
        }}
      >
        <Chart />
        <Chart />
      </div>
      <YouTubeEmbed></YouTubeEmbed>
</div>
  
  );
}

export default AdminDashboard;
