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

  const goToFAQs = () => {
    console.log("Click")
    navigate(`/admin/FAQs`);
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
         <span className={styles.listItem}>Dashboard (Home) </span>
    </li>
     <li onClick={() => goToReportingHub()} className={selected === "reporting"
      ? `${styles.listItemContainer} ${styles.selected}`
      : styles.listItemContainer}> 
         <span  className={styles.listItem}>Reporting and Communication Hub</span>
    </li>
    <li onClick={() => goToFAQs()} className={selected === "FAQs"
      ? `${styles.listItemContainer} ${styles.selected}`
      : styles.listItemContainer}> 
         <span className={styles.listItem}>FAQs</span>
    </li>
    
    </ul>

    <div className={styles.logoutContainer} onClick={() => goToLogin()}>Logout</div>
</nav>

)

}

export default AdminNav


