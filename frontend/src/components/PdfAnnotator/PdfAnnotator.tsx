import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface Annotation {
  page: number;
  text: string;
  x_pct: number;
  y_pct: number;
  size: number;
}

interface PdfAnnotatorProps {
  file: File;
  onSave: (annotations: Annotation[]) => void;
}

const PdfAnnotator: React.FC<PdfAnnotatorProps> = ({ file, onSave }) => {
  const [numPages, setNumPages] = useState<number>();
  const [pageNumber, setPageNumber] = useState(1);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [currentInput, setCurrentInput] = useState<{x: number, y: number, text: string, x_pct: number, y_pct: number} | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);

  React.useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setFileUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  const handlePageClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // If clicking on input, ignore
    if ((e.target as HTMLElement).tagName === 'INPUT') return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const x_pct = x / rect.width;
    const y_pct = y / rect.height;
    
    setCurrentInput({ x, y, text: '', x_pct, y_pct });
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (currentInput && currentInput.text.trim()) {
        setAnnotations(prev => [...prev, {
          page: pageNumber,
          text: currentInput.text,
          x_pct: currentInput.x_pct,
          y_pct: currentInput.y_pct,
          size: 16
        }]);
      }
      setCurrentInput(null);
    } else if (e.key === 'Escape') {
      setCurrentInput(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', width: '100%' }}>
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
        <button 
            type="button" 
            onClick={() => setPageNumber(p => Math.max(1, p - 1))} 
            disabled={pageNumber <= 1}
            style={{ padding: '4px 12px', border: '1px solid #ccc', borderRadius: '4px' }}
        >
            Prev
        </button>
        <span style={{ fontWeight: 500 }}>Page {pageNumber} of {numPages}</span>
        <button 
            type="button" 
            onClick={() => setPageNumber(p => Math.min(numPages || 1, p + 1))} 
            disabled={pageNumber >= (numPages || 1)}
            style={{ padding: '4px 12px', border: '1px solid #ccc', borderRadius: '4px' }}
        >
            Next
        </button>
      </div>

      <div style={{ 
          position: 'relative', 
          border: '1px solid var(--border-medium)', 
          borderRadius: '8px', 
          overflow: 'hidden',
          boxShadow: 'var(--shadow-card)',
          background: 'white'
      }}>
        {fileUrl && (
          <Document file={fileUrl} onLoadSuccess={onDocumentLoadSuccess} loading="Loading PDF...">
            <div onClick={handlePageClick} style={{ position: 'relative', cursor: 'text' }}>
              <Page pageNumber={pageNumber} renderTextLayer={false} renderAnnotationLayer={false} />
            
            {annotations.filter(a => a.page === pageNumber).map((ann, i) => (
              <div key={i} style={{
                position: 'absolute',
                left: `${ann.x_pct * 100}%`,
                top: `${ann.y_pct * 100}%`,
                color: 'black',
                fontSize: '16px',
                fontWeight: 'bold',
                transform: 'translateY(-100%)',
                pointerEvents: 'none'
              }}>
                {ann.text}
              </div>
            ))}
            
            {currentInput && (
              <input
                autoFocus
                type="text"
                value={currentInput.text}
                onChange={e => setCurrentInput({ ...currentInput, text: e.target.value })}
                onKeyDown={handleInputKeyDown}
                onBlur={() => setCurrentInput(null)}
                placeholder="Type here..."
                style={{
                  position: 'absolute',
                  left: currentInput.x,
                  top: currentInput.y,
                  transform: 'translateY(-100%)',
                  fontSize: '16px',
                  border: '1px solid var(--accent-start)',
                  background: 'white',
                  outline: 'none',
                  zIndex: 10,
                  padding: '2px 4px',
                  borderRadius: '2px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}
              />
            )}
          </div>
        </Document>
        )}
      </div>
      
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        Click anywhere on the document to add text. Press <strong>Enter</strong> to confirm.
      </p>

      <button type="button" onClick={() => onSave(annotations)} className="btn-primary" style={{ marginTop: '1rem' }}>
        Save Annotations & Process
      </button>
    </div>
  );
};

export default PdfAnnotator;
