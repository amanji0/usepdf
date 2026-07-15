import styles from './JobProgress.module.css';

interface JobProgressProps {
  status: 'queued' | 'processing' | 'done' | 'error' | null;
  progress: number | null;
  error?: string | null;
  downloadUrl?: string | null;
  onReset: () => void;
}

const JobProgress = ({ status, progress, error, downloadUrl, onReset }: JobProgressProps) => {
  if (!status) return null;

  return (
    <div className={styles.container}>
      {status === 'queued' && (
        <div className={styles.stateContent}>
          <div className={styles.spinnerWrap}>
            <div className={styles.spinner} />
          </div>
          <h3 className={styles.heading}>Queued</h3>
          <p className={styles.sub}>Waiting for processing slot…</p>
          <div className={styles.progressBar}>
            <div className={`${styles.progressFill} ${styles.indeterminate}`} />
          </div>
        </div>
      )}

      {status === 'processing' && (
        <div className={styles.stateContent}>
          <div className={styles.spinnerWrap}>
            <div className={styles.spinner} />
            {progress !== null && (
              <span className={styles.progressNum}>{progress}%</span>
            )}
          </div>
          <h3 className={styles.heading}>Processing</h3>
          <p className={styles.sub}>
            {progress !== null ? `${progress}% complete` : 'Working on your file…'}
          </p>
          <div className={styles.progressBar}>
            {progress !== null ? (
              <div className={styles.progressFill} style={{ width: `${progress}%` }} />
            ) : (
              <div className={`${styles.progressFill} ${styles.indeterminate}`} />
            )}
          </div>
        </div>
      )}

      {status === 'done' && (
        <div className={`${styles.stateContent} ${styles.success}`}>
          <div className={styles.successIcon}>
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="27" stroke="url(#check-grad)" strokeWidth="2" />
              <path d="M18 28l7 7 13-13" stroke="url(#check-grad)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <defs>
                <linearGradient id="check-grad" x1="0" y1="0" x2="56" y2="56" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#34d399" />
                  <stop offset="1" stopColor="#10b981" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h3 className={styles.heading}>Ready!</h3>
          <p className={styles.sub}>Your file has been processed successfully.</p>
          {downloadUrl && (
            <a href={downloadUrl} className="btn-primary" download>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 3v9m0 0l-3.5-3.5M9 12l3.5-3.5M3 15h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Download File
            </a>
          )}
          <button onClick={onReset} className={styles.resetBtn}>Process another file</button>
        </div>
      )}

      {status === 'error' && (
        <div className={`${styles.stateContent} ${styles.errorState}`}>
          <div className={styles.errorIcon}>
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="27" stroke="#ef4444" strokeWidth="2" />
              <path d="M20 20l16 16M36 20L20 36" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" />
            </svg>
          </div>
          <h3 className={styles.heading}>Something went wrong</h3>
          <p className={styles.errorText}>{error || 'An unexpected error occurred'}</p>
          <button onClick={onReset} className="btn-primary">Try Again</button>
        </div>
      )}
    </div>
  );
};

export default JobProgress;
