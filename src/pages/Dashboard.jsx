import Map from '../components/Map';
import AlertPane from '../components/AlertPane';
import Chart from '../components/Chart';

function Dashboard() {
  return (
    <div style={{display: "flex", flexDirection: "column", gap: "50px"}}>
        <div style={{display: "flex", justifyContent: "center"}}>
        <h1 style={{borderBottom: "1px solid black"}}>Central Dashboard</h1>
        </div>

      <div style={{ display: "flex", width: "100%", marginLeft: "50px", justifyContent: "center", gap: "50px" }}>
        <Map style={{width: "50%", marginRight: "50px"}} /> 
        <AlertPane style={{marginLeft: "50px", width: "50%"}} />
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