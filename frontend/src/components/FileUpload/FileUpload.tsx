import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import styles from './FileUpload.module.css';

interface FileUploadProps {
  acceptedTypes: Record<string, string[]>;
  multiFile: boolean;
  files: File[];
  onAddFiles: (files: File[]) => void;
  onRemoveFile: (index: number) => void;
}

const FileUpload = ({ acceptedTypes, multiFile, files, onAddFiles, onRemoveFile }: FileUploadProps) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    onAddFiles(acceptedFiles);
  }, [onAddFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    multiple: multiFile
  });

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className={styles.wrapper}>
      {(!files.length || multiFile) && (
        <div
          {...getRootProps()}
          className={`${styles.dropzone} ${isDragActive ? styles.active : ''}`}
        >
          <input {...getInputProps()} />
          <div className={styles.dropContent}>
            <div className={styles.uploadIcon}>
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="23" stroke="url(#upload-grad)" strokeWidth="1.5" strokeDasharray="4 3" />
                <path d="M24 32V16m0 0l-6 6m6-6l6 6" stroke="url(#upload-grad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <defs>
                  <linearGradient id="upload-grad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#8b5cf6" />
                    <stop offset="1" stopColor="#3b82f6" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <p className={styles.text}>
              {isDragActive ? 'Drop your files here' : 'Drag & drop files here'}
            </p>
            <p className={styles.subtext}>or <span className={styles.browse}>browse</span> to select</p>
          </div>
        </div>
      )}

      {files.length > 0 && (
        <div className={styles.fileList}>
          {files.map((file, idx) => (
            <div key={`${file.name}-${idx}`} className={styles.fileItem} style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className={styles.fileIcon}>
                {file.type === 'application/pdf' ? (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect x="4" y="2" width="16" height="20" rx="2" stroke="#8b5cf6" strokeWidth="1.5" />
                    <path d="M8 7h8M8 11h8M8 15h4" stroke="#8b5cf6" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                ) : file.type.startsWith('image/') ? (
                  <img src={URL.createObjectURL(file)} alt="preview" className={styles.imgPreview} />
                ) : (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect x="4" y="2" width="16" height="20" rx="2" stroke="#6366f1" strokeWidth="1.5" />
                  </svg>
                )}
              </div>
              <div className={styles.fileInfo}>
                <span className={styles.fileName} title={file.name}>{file.name}</span>
                <span className={styles.fileSize}>{formatSize(file.size)}</span>
              </div>
              <button
                className={styles.removeBtn}
                onClick={(e) => { e.stopPropagation(); onRemoveFile(idx); }}
                aria-label="Remove file"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
