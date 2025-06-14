import { LogOut } from "lucide-react";
import { useNavigate } from 'react-router-dom';
import styles from './Nav.module.css';

function AdminNav() {
   const navigate = useNavigate()

   const selected = ""

  const goToLogin = () => {
     navigate(`/`);
  };

  const goToDashboard = () => {
     navigate(`/admin/dashboard`);
  };

  const goToReportingHub = () => {
     navigate(`/admin/reporting`);
  };


return (
<nav className={styles.navbar}>
    <div className={styles.logoContainer}>
        <span>Public Health Sentinel</span>
        </div>
    <ul>
     <li onClick={() => goToDashboard()} className={selected === "dashboard"
      ? `${styles.listItemContainer} ${styles.selected}`
      : styles.listItemContainer}> 
         <span className={styles.listItem}>Central Dashboard </span>
    </li>
     <li onClick={() => goToReportingHub()} className={selected === "reporting"
      ? `${styles.listItemContainer} ${styles.selected}`
      : styles.listItemContainer}> 
         <span  className={styles.listItem}>Reporting and Communication Hub</span>
    </li>
  
    </ul>

<div style={{width: "15%"}}>
   <div className={styles.logoutContainer}>
   
    <div
      className={styles.logout}
      onClick={() => goToLogin()}
      style={{
         display: "flex",
         alignItems: "center",
         gap: "8px", // space between icon and text
         cursor: "pointer",
      }}
      >
  <LogOut />
  Logout
</div>
    </div>
    </div>
</nav>

)

}

export default AdminNav


