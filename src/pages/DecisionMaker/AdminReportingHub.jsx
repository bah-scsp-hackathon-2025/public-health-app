import AdminNav from "../../components/AdminNav"
import PolicyTable from "../../components/PolicyTable"

function AdminReportingHub () {
    return (
        <div>
            <AdminNav></AdminNav>
            <div style={{display: "flex", justifyContent: "center"}}>
            <h1 style={{boxShadow: "0 4px 6px -4px rgba(0, 0, 0, 0.3)", textAlign: "center", width: "100%"}}>Policy Hub</h1>
            </div>
            <PolicyTable></PolicyTable>
        </div>
    )
}

export default AdminReportingHub