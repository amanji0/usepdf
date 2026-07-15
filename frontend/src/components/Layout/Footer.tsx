import styles from './Footer.module.css';

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.trustRow}>
          <div className={styles.trustItem}>
            <span className={styles.trustIcon}>🔒</span>
            <span>Files auto-delete in 1 hour</span>
          </div>
          <div className={styles.divider} />
          <div className={styles.trustItem}>
            <span className={styles.trustIcon}>🖥️</span>
            <span>100% self-hosted</span>
          </div>
          <div className={styles.divider} />
          <div className={styles.trustItem}>
            <span className={styles.trustIcon}>⚡</span>
            <span>No file size limits</span>
          </div>
        </div>
        <p className={styles.copyright}>
          Built with open-source tools. No data leaves your server.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
