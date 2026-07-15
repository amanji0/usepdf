import { useState, FormEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import { TOOLS } from '../../data/tools';
import { uploadAndProcess } from '../../api/client';
import { useJobPoller } from '../../hooks/useJobPoller';
import { useFileUpload } from '../../hooks/useFileUpload';
import FileUpload from '../../components/FileUpload/FileUpload';
import PdfAnnotator from '../../components/PdfAnnotator/PdfAnnotator';
import JobProgress from '../../components/JobProgress/JobProgress';
import styles from './ToolPage.module.css';

const ToolPage = () => {
  const { toolId } = useParams<{ toolId: string }>();
  const tool = TOOLS.find(t => t.id === toolId);

  const [jobId, setJobId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [options, setOptions] = useState<Record<string, string | number>>(() => {
    const defaultOpts: Record<string, string | number> = {};
    tool?.options?.forEach(opt => {
      defaultOpts[opt.name] = opt.defaultValue;
    });
    return defaultOpts;
  });

  const { files, addFiles, removeFile, clearFiles } = useFileUpload(tool?.multiFile || false);
  const { status, progress, error, downloadUrl } = useJobPoller(jobId);

  if (!tool) {
    return (
      <div className={styles.notFound}>
        <h2>Tool not found</h2>
        <Link to="/" className="btn-primary">← Back to tools</Link>
      </div>
    );
  }

  const handleOptionChange = (name: string, value: string | number) => {
    setOptions(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (files.length === 0 || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const response = await uploadAndProcess(tool.apiEndpoint, files, options, tool.multiFile);
      setJobId(response.job_id);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveAnnotations = async (annotations: any[]) => {
    if (files.length === 0 || isSubmitting) return;

    setIsSubmitting(true);
    try {
      // @ts-ignore apiEndpoint exists
      const response = await uploadAndProcess(tool.apiEndpoint || '/api/tools/edit', files, { annotations: JSON.stringify(annotations) }, false);
      setJobId(response.job_id);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setJobId(null);
    clearFiles();
  };

  const isUploading = jobId === null;

  return (
    <div className={styles.page}>
      <Link to="/" className={styles.backLink}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 12L6 8l4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        All tools
      </Link>

      <header className={styles.header}>
        <div className={styles.iconBadge} data-category={tool.category}>
          <tool.icon size={48} strokeWidth={1.5} />
        </div>
        <h1 className={styles.title}>{tool.name}</h1>
        <p className={styles.description}>{tool.description}</p>
      </header>

      <div className={styles.content}>
        {isUploading ? (
          <form onSubmit={handleSubmit} className={styles.form}>
            <FileUpload
              acceptedTypes={tool.acceptedTypes}
              multiFile={tool.multiFile}
              files={files}
              onAddFiles={addFiles}
              onRemoveFile={removeFile}
            />

            {files.length > 0 && tool.id === 'edit' ? (
              <div style={{ marginTop: '2rem' }}>
                <PdfAnnotator file={files[0]} onSave={handleSaveAnnotations} />
              </div>
            ) : (
              <>
                {files.length > 0 && tool.options && tool.options.length > 0 && (
                  <div className={styles.optionsPanel}>
                    <h3 className={styles.optionsTitle}>Options</h3>
                    <div className={styles.optionsGrid}>
                      {tool.options.map(opt => (
                        <div key={opt.name} className={styles.formGroup}>
                          <label htmlFor={opt.name}>{opt.label}</label>
                          {opt.type === 'select' ? (
                            <select
                              id={opt.name}
                              value={options[opt.name] || ''}
                              onChange={(e) => handleOptionChange(opt.name, e.target.value)}
                              className={styles.input}
                            >
                              {opt.choices?.map(choice => (
                                <option key={choice.value} value={choice.value}>{choice.label}</option>
                              ))}
                            </select>
                          ) : (
                            <input
                              type={opt.type}
                              id={opt.name}
                              value={options[opt.name] || ''}
                              onChange={(e) => handleOptionChange(opt.name, e.target.value)}
                              className={styles.input}
                              placeholder={opt.label}
                            />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {files.length > 0 && (
                  <button
                    type="submit"
                    className={`btn-primary ${styles.submitBtn}`}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className={styles.btnSpinner} />
                    Uploading…
                  </>
                ) : (
                  <>
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                      <path d="M3 9.5l4.5 4.5L15 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    Process {tool.multiFile && files.length > 1 ? `${files.length} files` : 'file'}
                  </>
                )}
              </button>
            )}
            </>
            )}
          </form>
        ) : (
          <JobProgress
            status={status}
            progress={progress}
            error={error}
            downloadUrl={downloadUrl}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  );
};

export default ToolPage;
