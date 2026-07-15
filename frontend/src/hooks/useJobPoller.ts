import { useState, useEffect, useRef } from 'react';
import { JobStatus } from '../types';
import { getJobStatus, getDownloadUrl } from '../api/client';

export function useJobPoller(jobId: string | null) {
  const [status, setStatus] = useState<JobStatus['status'] | null>(null);
  const [progress, setProgress] = useState<number | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    if (!jobId) {
      // Reset state if jobId becomes null
      setStatus(null);
      setProgress(null);
      setDownloadUrl(null);
      setError(null);
      setFilename(null);
      setIsPolling(false);
      return;
    }

    const poll = async () => {
      try {
        const job = await getJobStatus(jobId);
        setStatus(job.status);
        setProgress(job.progress);
        setFilename(job.filename);
        
        if (job.status === 'done') {
          setDownloadUrl(getDownloadUrl(jobId));
          setIsPolling(false);
        } else if (job.status === 'error') {
          setError(job.error || 'An unknown error occurred');
          setIsPolling(false);
        } else {
          // Still processing, continue polling
          timerRef.current = window.setTimeout(poll, 1500);
        }
      } catch (err) {
        console.error("Polling error:", err);
        setError(err instanceof Error ? err.message : 'Network error');
        setStatus('error');
        setIsPolling(false);
      }
    };

    setIsPolling(true);
    poll();

    return () => {
      if (timerRef.current !== null) {
        clearTimeout(timerRef.current);
      }
    };
  }, [jobId]);

  return { status, progress, downloadUrl, error, filename, isPolling };
}
