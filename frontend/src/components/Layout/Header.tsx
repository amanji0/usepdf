import { Link } from 'react-router-dom';
import { FileBox } from 'lucide-react';
import styles from './Header.module.css';

const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logoGroup}>
          <div className={styles.logoIcon}>
            <FileBox size={28} color="var(--accent-start)" strokeWidth={2.5} />
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
