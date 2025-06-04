import { MapPin } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { fetchAlertByLocation, fetchAlerts, fetchSummaries, fetchTrends } from "../../common/api";
import Chart from "../../components/Chart";
import ChartHeader from "../../components/ChartHeader";
import Map from '../../components/Map';
import RegularAlertPane from "../../components/RegularAlertPane";
import RegularNav from "../../components/RegularNav";


const US_STATE_AND_TERRITORY_NAMES = [
  "Alabama",
  "Alaska",
  "Arizona",
  "Arkansas",
  "California",
  "Colorado",
  "Connecticut",
  "Delaware",
  "Florida",
  "Georgia",
  "Hawaii",
  "Idaho",
  "Illinois",
  "Indiana",
  "Iowa",
  "Kansas",
  "Kentucky",
  "Louisiana",
  "Maine",
  "Maryland",
  "Massachusetts",
  "Michigan",
  "Minnesota",
  "Mississippi",
  "Missouri",
  "Montana",
  "Nebraska",
  "Nevada",
  "New Hampshire",
  "New Jersey",
  "New Mexico",
  "New York",
  "North Carolina",
  "North Dakota",
  "Ohio",
  "Oklahoma",
  "Oregon",
  "Pennsylvania",
  "Rhode Island",
  "South Carolina",
  "South Dakota",
  "Tennessee",
  "Texas",
  "Utah",
  "Vermont",
  "Virginia",
  "Washington",
  "West Virginia",
  "Wisconsin",
  "Wyoming",
  "District of Columbia",
  "American Samoa",
  "Guam",
  "Northern Mariana Islands",
  "Puerto Rico",
  "U.S. Virgin Islands"
];

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


function Dashboard() {
  const location = useLocation();
  const [showVideoModal, setShowVideoModal] = useState(false);

  useEffect(() => {
    if (location.state?.showVideo) {
      setShowVideoModal(true);
    }
  }, [location.state]);
    const [selectedState, setSelectedState] = useState("");

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



      const [alerts, setAlerts] = useState([]);
      async function getAlerts(state) {
        if (state) {
          const result = await fetchAlertByLocation(state);
          if (result.length > 4) {
            setAlerts(result.slice(0, 4));
          } else {
            setAlerts(result);
          }
        } else {
          const result = await fetchAlerts();
          if (result.length > 4) {
            setAlerts(result.slice(0, 4));
          } else {
            setAlerts(result);
          }
        }
      }
      useEffect(() => {getAlerts("")}, []);

      const onChange = (e) => {
        setSelectedState(e.target.value);
        getAlerts(e.target.value);
      }

  return (
    <div style={{display: "flex", flexDirection: "column", marginTop: "0%"}}>
      <RegularNav></RegularNav>

<div style={{display: "flex", justifyContent: "center", marginBottom: "40px", boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)"}}>
      <h1 style={{marginBottom: "0px"}}>Central Dashboard</h1>
      
      </div>

{showVideoModal && (
  <div
    style={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100vw",
      height: "100vh",
      backgroundColor: "rgba(0, 0, 0, 0.7)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 9999
    }}
  >
    <div
      style={{
        position: "relative",
        width: "95%",
        maxWidth: "1400px",  // large modal
        background: "#000",
        borderRadius: "12px",
        overflow: "hidden",
        aspectRatio: "16/9"   // maintains correct video dimensions
      }}
    >
      {/* Close Button */}
      <button
        onClick={() => setShowVideoModal(false)}
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          zIndex: 10000,
          background: "#fff",
          border: "1px solid #ccc",
          borderRadius: "50%",
          width: "30px",
          height: "30px",
          fontSize: "20px",
          cursor: "pointer",
          lineHeight: "24px",
          textAlign: "center",
          padding: 0
        }}
      >
        &times;
      </button>

      {/* YouTube Video */}
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
          height: "100%"
        }}
      />
    </div>
  </div>
)}



      <div style={{ display: "flex", justifyContent: "center", marginBottom: "40px", alignItems: "center" }}>
  <MapPin />
  <div style={{ marginRight: "20px", fontWeight: "bold", fontSize: "20px", padding: "5px" }}>
    Select Your Location
  </div>
  <select
    value={selectedState}
    onChange={onChange}
    style={{
      fontSize: "15px",
      padding: "5px",
      height: "30px",
      minWidth: "250px",
      borderRadius: "5px",
    }}
  >
    {/* Optionally add a default empty option */}
    <option value="">All States</option>
    {US_STATE_AND_TERRITORY_NAMES.map((name) => (
      <option key={name} style={{ fontSize: "20px", height: "50px" }} value={name}>
        {name}
      </option>
    ))}
  </select>

  {/* Clear button */}
  <button
    onClick={() => {
      setSelectedState("");
      getAlerts("");  // reset alerts to default/all
    }}
    style={{
      marginLeft: "15px",
      padding: "5px 15px",
      fontSize: "16px",
      cursor: "pointer",
      borderRadius: "5px",
      border: "1px solid #ccc",
      backgroundColor: "#f5f5f5",
    }}
  >
    Clear State Filter
  </button>
</div>


    

    <div style={{ width: "100%", display: "flex", justifyContent: "center" }}>
        <div style={{ display: "flex", width: "80%", gap: "50px" }}>
        <Map style={{ width: "50%" }} />
        <RegularAlertPane alerts={alerts} style={{ width: "50%" }} />
        </div>
    </div>

        <div style={{ width: "100%", display: "flex", justifyContent: "center", marginTop: "50px",  marginBottom: "50px"}}>
        <div style={{ background: "#f0f0f0", width: "80%", border: "1px solid black",  padding: "20px",
        boxSizing: "border-box", height: "80%"}}>
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

    {showVideoModal && (
             <YouTubeEmbed></YouTubeEmbed>
)}
    
</div>
    
  );
}

export default Dashboard;