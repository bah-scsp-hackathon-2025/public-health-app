import { useNavigate, useParams } from 'react-router-dom';
import AdminNav from '../../components/AdminNav';
import ScenarioCard from '../../components/ScenarioCard';


function AdminAlert() {
  const { id } = useParams();
  const scenarios = [
  {
    id: 1,
    title: "Activate Emergency Operations Center",
    description: "Mobilize the emergency operations center to coordinate the public health response.",
    priority: "High",
    responsibleAgency: "Public Health Department",
    expectedOutcome: "Streamlined communication and resource allocation during the event.",
    estimatedDurationDays: 7,
  },
  {
    id: 2,
    title: "Issue Public Health Advisory",
    description: "Inform the public about the health risks and recommended preventive measures.",
    priority: "High",
    responsibleAgency: "CDC",
    expectedOutcome: "Increased public awareness and compliance with health guidelines.",
    estimatedDurationDays: 3,
  },
  {
    id: 3,
    title: "Implement Travel Restrictions",
    description: "Restrict travel to and from affected areas to limit disease spread.",
    priority: "Medium",
    responsibleAgency: "Department of Transportation",
    expectedOutcome: "Reduced transmission across regions.",
    estimatedDurationDays: 14,
  },
];

  const navigate = useNavigate()

  const goToDashboard = () => {
    navigate('/admin/dashboard')
  }

  return (
    <div style={{display: "flex", flexDirection: "column", height: "100vh", marginTop: "20px"}}>
      <AdminNav></AdminNav>
      <div style={{display: "flex", justifyContent: "center", flexDirection: "column", textAlign: "center"}}>
        <div onClick={() => goToDashboard()} style={{display: "flex", justifyContent: "start"}}>
        <div>Back to dashboard</div>
        </div>
    <h1>Alert Response Planner</h1>
    <p style={{color: "#191970"}}>View insights on public health alerts. Then, generate response strategies and draft policy documents.</p>
      </div>
      
   

    <div style={{display: "flex", justifyContent: "center"}}>
     
    <div style={{ width: "80%", padding: "20px", height: '100%'}}>
      
   
<div style={{backgroundColor: "#191970", padding: "40px", border: "1px solid black"}}>
      <div style={{ marginBottom: "20px" }}>
        <div style={{ 
          border: "1px solid black", 
          borderRadius: "10px", 
          padding: "10px", 
          minHeight: "80px" ,
           background: "white"
        }}>
          Details
        </div>
      </div>

      <div style={{ display: "flex", gap: "10px"}}>
        <div style={{ 
          border: "1px solid black", 
          borderRadius: "10px", 
          padding: "10px", 
          flex: "1", 
          minHeight: "80px",
          background: "white"
        }}>
          Risk Score
        </div>
        <div style={{ 
          border: "1px solid black", 
          borderRadius: "10px", 
          padding: "10px", 
          flex: "2", 
          minHeight: "80px" ,
           background: "white"
        }}>
          Score Explanation
        </div>
      </div>
      </div>
      <div style={{marginTop: "20px"}}>
      <span>Ready to start planning?</span>
      <button>Generate Courses of Action</button>
      </div>
    </div>
    </div>
     <div style={{display: "flex", justifyContent:"center"}}>
      
    <div style={{width:"80%"}}>
    <h2 style={{borderBottom: "1px dashed black"}}>Generated Scenarios</h2>
    </div>
    </div>
    <div style={{display: "flex", justifyContent:"center"}}>
       
    <div style={{width:"80%"}}>
    {scenarios.map((scenario) => (
        <ScenarioCard scenario={scenario}></ScenarioCard>
    ))
    }
    </div>
    </div>
    </div>
  );
}

export default AdminAlert;
