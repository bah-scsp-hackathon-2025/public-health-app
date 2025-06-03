import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import AdminAlert from './pages/DecisionMaker/AdminAlert';
import AdminFAQs from './pages/DecisionMaker/AdminFAQs';
import AdminReportingHub from './pages/DecisionMaker/AdminReportingHub';
import AdminDashboard from './pages/DecisionMaker/DashboardAdmin';
import Login from './pages/Login';
import Dashboard from './pages/RegularUser/Dashboard';

function App() {
  return (
    <Router>
      <div style={{ height: '100vh', display: 'flex' }}>
        {/* Sidebar (Nav) with fixed width */}
       
        <div style={{ height: '200px'}}>
        </div>

        {/* Main content area fills remaining space */}
        <div style={{ flex: 1, overflow: 'auto', marginTop: "80px" }}>
          <Routes>
            <Route path="/" element={<Login />} />
             <Route path="/dashboard" element={<Dashboard />} />
            <Route path="admin/dashboard" element={<AdminDashboard />} />
            <Route path="admin/alert/:id" element={<AdminAlert />} />
            <Route path="admin/reporting" element={<AdminReportingHub/>}/>
            <Route path="admin/FAQs" element={<AdminFAQs/>}/>
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;

