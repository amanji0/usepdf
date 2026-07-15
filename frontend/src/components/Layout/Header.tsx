import { Link } from 'react-router-dom';
import styles from './Header.module.css';

const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logoGroup}>
          <div className={styles.logoIcon}>
            <img src="/logo.jpg" alt="UsePDF Logo" style={{ width: 32, height: 32, borderRadius: 8 }} />
          </div>
          <span className={styles.logoText}>
            Use<span className={styles.logoAccent}>PDF</span>
          </span>
        </Link>

        <nav className={styles.nav}>
          <span className={styles.badge}>✦ Free & Open Source</span>
        </nav>
      </div>
    </header>
  );
};

export default Header;
