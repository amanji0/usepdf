import { JobResponse, JobStatus } from '../types';

// In development with Vite proxy, use empty base url so requests go to the proxy
// In production, the Nginx config proxies /api to the backend
const BASE_URL = ''; 

export const uploadAndProcess = async (
  endpoint: string, 
  files: File[], 
  options: Record<string, any> = {},
  isMultiFile: boolean = false
): Promise<JobResponse> => {
  const formData = new FormData();
  
  if (!isMultiFile) {
    formData.append('file', files[0]);
  } else {
    files.forEach(file => {
      formData.append('files', file);
    });
  }
  
  Object.entries(options).forEach(([key, value]) => {
    formData.append(key, String(value));
  });
  
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    let errorMessage = `Request failed with status ${response.status}`;
    if (errorData.detail) {
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else {
        errorMessage = JSON.stringify(errorData.detail);
      }
    }
    throw new Error(errorMessage);
  }
  
  return response.json();
};

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await fetch(`${BASE_URL}/api/jobs/${jobId}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch job status');
  }
  
  return response.json();
};

export const getDownloadUrl = (jobId: string): string => {
  return `${BASE_URL}/api/download/${jobId}`;
};
