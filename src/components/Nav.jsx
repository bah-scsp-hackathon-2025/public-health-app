import styles from './Nav.module.css'
import { useNavigate } from 'react-router-dom';

function Nav() {

  const navigate = useNavigate();

  const goToDashboard = () => {
     navigate(`/`);
  };


return (
<nav className={styles.navbar}>
    <div className={styles.logoContainer}>
        <span>Public Health Sentinel</span>
        </div>
    <ul>
    <li className={styles.listItemContainer}>
        <span className={styles.listItem}>Home</span>
    </li>
     <li className={styles.listItemContainer}> 
         <span onClick={() => goToDashboard()} className={styles.listItem}>Dashboard</span>
    </li>
    <li className={styles.listItemContainer}> 
         <span className={styles.listItem}>FAQs</span>
    </li>
     <li className={styles.listItemContainer}> 
         <span className={styles.listItem}>Reporting and Communication Hub</span>
    </li>
    </ul>
</nav>

)

}

export default Nav


