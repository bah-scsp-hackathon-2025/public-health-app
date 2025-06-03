import AdminNav from '../../components/AdminNav';
import AlertPane from '../../components/AlertPane';
import Chart from '../../components/Chart';
import Map from '../../components/Map';

function AdminDashboard() {
  return (
    <div style={{display: "flex", flexDirection: "column", marginTop: "0%"}}>
      <AdminNav></AdminNav>

<div style={{display: "flex", justifyContent: "center", marginBottom: "20px"}}>
      <h1>Central Dashboard</h1>
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

export default AdminDashboard;