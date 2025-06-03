import AdminNav from '../../components/AdminNav';
import AlertPane from '../../components/AlertPane';
import Chart from '../../components/Chart';
import Map from '../../components/Map';

function AdminDashboard() {
  return (
    <div style={{display: "flex", flexDirection: "column", marginTop: "0%"}}>
      <AdminNav></AdminNav>

<div style={{display: "flex", justifyContent: "center", marginBottom: "40px", boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)",}}>
      <h1 style={{marginBottom: "0px"}}>Central Dashboard</h1>
      </div>

  <div style={{ width: "100%", display: "flex", justifyContent: "center" }}>
    <div style={{ display: "flex", width: "80%", gap: "50px" }}>
      <Map style={{ width: "50%" }} />
      <AlertPane style={{ width: "50%" }} />

    </div>
  </div>

    <div style={{ width: "100%", display: "flex", justifyContent: "center", marginTop: "50px"}}>
      <div style={{ background: "lightgrey", width: "80%", border: "1px solid black",  padding: "20px",
    boxSizing: "border-box", height: "80%"}}>
        Summary
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

export default AdminDashboard;