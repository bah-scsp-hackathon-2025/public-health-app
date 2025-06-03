import { MapPin } from "lucide-react";
import { useState, useEffect } from "react";
import Chart from '../../components/Chart';
import Map from '../../components/Map';
import RegularAlertPane from "../../components/RegularAlertPane";
import RegularNav from "../../components/RegularNav";
import { fetchSummary } from "../../common/api";

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


function Dashboard() {
    const [selectedState, setSelectedState] = useState("");

    const [summary, setSummary] = useState([]);
      useEffect(() => {
        const getSummary = async () => {
          const result = await fetchSummary();
          setSummary(result);
        };
        getSummary();
      }, []);

  return (
    <div style={{display: "flex", flexDirection: "column", marginTop: "0%"}}>
      <RegularNav></RegularNav>

<div style={{display: "flex", justifyContent: "center", marginBottom: "40px", boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)"}}>
      <h1 style={{marginBottom: "0px"}}>Central Dashboard</h1>
      
      </div>

      <div style={{display: "flex", justifyContent: "center", marginBottom: "40px"}}>
        <MapPin/>
          <div style={{marginRight: "20px", fontWeight: "bold", fontSize: "20px", padding: "5px"}}>Select Your Location</div>
          <select value={selectedState} onChange={(e) => setSelectedState(e.target.value)}
            style={{
            fontSize: "15px",       // larger text
            padding: "5px",        // larger click area
            height: "30px",         // increase height
            minWidth: "250px",      // optional: wider dropdown
            borderRadius: "5px"     // optional: rounded corners
        }}>
            {US_STATE_AND_TERRITORY_NAMES.map((name) =>
                <option style={{fontSize: "20px", height:"50px"}}>{name}</option>
            )}
          </select>
      </div>

    

    <div style={{ width: "100%", display: "flex", justifyContent: "center" }}>
        <div style={{ display: "flex", width: "80%", gap: "50px" }}>
        <Map style={{ width: "50%" }} />
        <RegularAlertPane style={{ width: "50%" }} />
        </div>
    </div>

        <div style={{ width: "100%", display: "flex", justifyContent: "center", marginTop: "50px"}}>
        <div style={{ background: "lightgrey", width: "80%", border: "1px solid black",  padding: "20px",
        boxSizing: "border-box", height: "80%"}}>
            {summary.description}
        </div>
        </div>

    <div style={{display: "flex", flexDirection: "row", gap: "50px", marginLeft: "50px", marginTop: "100px"}}>
    <Chart/>
    <Chart/>
    </div>
    <div style={{display: "flex", flexDirection: "row", gap: "50px", marginLeft: "50px"}}>
    <Chart/>
    <Chart/>
    </div>
</div>
    
  );
}

export default Dashboard;