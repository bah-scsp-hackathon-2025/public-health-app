import Nav from './components/Nav';
import Dashboard from './pages/Dashboard';
import Alert from './pages/Alert';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div style={{ height: '100vh', display: 'flex' }}>
        {/* Sidebar (Nav) with fixed width */}
        <div style={{ width: '200px', backgroundColor: '#ddd' }}>
          <Nav />
        </div>

        {/* Main content area fills remaining space */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alert/:id" element={<Alert />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;

