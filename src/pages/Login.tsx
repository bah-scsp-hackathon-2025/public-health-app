import { LogIn, User, UserPen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import LoginBar from '../components/LoginBar';
import styles from './Login.module.css';

function Login () {

   
    const navigate = useNavigate();

    const goToAdminDashboard = () => {
     navigate(`/admin/dashboard`);
  };

  const goToRegularDashboard = () => {
     navigate(`/dashboard`);
  };

    return (
        <div className={styles.headerContainer}>
            <LoginBar></LoginBar>
        <h1>Welcome to public health sentinel</h1>

        <div style={{width: "40%", height: "50%", background: "lightgrey", marginTop: "60px"}}>
               <h2>I am a...</h2>

               <div className={styles.userTypeContainer}>
                <div className={styles.userType}>
                    <UserPen />
                    <span>Decision Maker</span>
                    <LogIn onClick={()=> goToAdminDashboard()} className={styles.icon} height={24} width={36}/>
                </div>
               </div>

               <div className={styles.userTypeContainer}>
                <div className={styles.userType}>
                    <User/>
                    <span>Regular User</span>
                    <LogIn onClick={() => goToRegularDashboard()} className={styles.icon} height={24} width={36}/>
                </div>
               </div>

        </div>
        </div>


    )
}

export default Login