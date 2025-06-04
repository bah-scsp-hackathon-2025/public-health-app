import { useEffect, useState } from "react";
import { fetchSummaries, fetchTrends } from "../../common/api";
import AdminNav from "../../components/AdminNav";
import AlertPane from "../../components/AlertPane";
import Chart from "../../components/Chart";
import ChartHeader from "../../components/ChartHeader";
import Map from "../../components/Map";

const STATE_ABBR_TO_NAME = {
  AL: "Alabama",
  AK: "Alaska",
  AZ: "Arizona",
  AR: "Arkansas",
  CA: "California",
  CO: "Colorado",
  CT: "Connecticut",
  DE: "Delaware",
  FL: "Florida",
  GA: "Georgia",
  HI: "Hawaii",
  ID: "Idaho",
  IL: "Illinois",
  IN: "Indiana",
  IA: "Iowa",
  KS: "Kansas",
  KY: "Kentucky",
  LA: "Louisiana",
  ME: "Maine",
  MD: "Maryland",
  MA: "Massachusetts",
  MI: "Michigan",
  MN: "Minnesota",
  MS: "Mississippi",
  MO: "Missouri",
  MT: "Montana",
  NE: "Nebraska",
  NV: "Nevada",
  NH: "New Hampshire",
  NJ: "New Jersey",
  NM: "New Mexico",
  NY: "New York",
  NC: "North Carolina",
  ND: "North Dakota",
  OH: "Ohio",
  OK: "Oklahoma",
  OR: "Oregon",
  PA: "Pennsylvania",
  RI: "Rhode Island",
  SC: "South Carolina",
  SD: "South Dakota",
  TN: "Tennessee",
  TX: "Texas",
  UT: "Utah",
  VT: "Vermont",
  VA: "Virginia",
  WA: "Washington",
  WV: "West Virginia",
  WI: "Wisconsin",
  WY: "Wyoming",
  DC: "District of Columbia",
};

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

  const [trends, setTrends] = useState([]);
  
  useEffect(() => {
    const getTrends = async () => {
      const result = await fetchTrends();
  
      if (!Array.isArray(result)) {
        console.error("Expected array from fetchTrends, got:", result);
        setTrends([]);
        return;
      }
  
      const trend_data = result
        .map((item, i) => {
          if (item?.data) {
            try {
              return JSON.parse(item.data);
            } catch (e) {
              console.error(`Error parsing trend.data at index ${i}:`, item.data);
              return null;
            }
          } else {
            console.warn(`Missing .data in item at index ${i}:`, item);
            return null;
          }
        })
        .filter(Boolean); // Remove nulls
  
      console.log("Parsed trend data:", trend_data);
      setTrends(trend_data);
    };
  
    getTrends();
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
          marginBottom: "50px"
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
           <h2
          style={{
            color: "#191970",
            borderBottom: "1px solid black",
            textAlign: "center",
            width: "100%",
          }}
        >
          Summary
          </h2>
          {summary.description}...
        </div>
      </div>

     <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
  {trends.map((trend, index) => {
    const chartData = trend.result.map(point => ({
      time: point.time_value,
      value: point.value,
    }));

    return (
      <div key={index} style={{ marginBottom: "70px", width: "60%" }}>
        <ChartHeader signalName={trend.tool_args.signal} stateAcronym={trend.tool_args.geo_value} />
        <Chart data={chartData} signalName={trend.tool_args.signal} />
      </div>
    );
  })}
</div>
</div>
  
  );
}

export default AdminDashboard;
