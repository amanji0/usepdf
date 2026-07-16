export type ToolCategory = 'organize' | 'optimize' | 'convert' | 'edit' | 'security' | 'intelligence';

export interface ToolOption {
  name: string;
  label: string;
  type: 'select' | 'number' | 'text';
  defaultValue: string | number;
  choices?: { value: string | number; label: string }[];
}

export interface Tool {
  id: string;
  name: string;
  description: string;
  category: ToolCategory;
  icon: any; // Allow React elements (Lucide icons)
  acceptedTypes: Record<string, string[]>;
  multiFile: boolean;
  apiEndpoint: string;
  options?: ToolOption[];
}

export interface JobStatus {
  job_id: string;
  status: 'queued' | 'processing' | 'done' | 'error';
  progress: number | null;
  download_url: string | null;
  error: string | null;
  filename: string | null;
}

export interface JobResponse {
  job_id: string;
  status: string;
}
