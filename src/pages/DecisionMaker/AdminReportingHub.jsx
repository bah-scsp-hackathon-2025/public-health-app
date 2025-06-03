import AdminNav from "../../components/AdminNav"
import PolicyTable from "../../components/PolicyTable"

function AdminReportingHub () {
    return (
        <div>
            <AdminNav></AdminNav>
            <div style={{display: "flex", justifyContent: "center"}}>
            <h1>Policy Hub</h1>
            </div>
            <PolicyTable></PolicyTable>
        </div>
    )
}

export default AdminReportingHub