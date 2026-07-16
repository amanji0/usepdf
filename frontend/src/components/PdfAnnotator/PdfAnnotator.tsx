import React, { useState, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { fabric } from 'fabric';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// @ts-ignore
import workerSrc from 'pdfjs-dist/build/pdf.worker.min.js?url';
pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;

interface Annotation {
  type: 'text' | 'rect';
  page: number;
  text?: string;
  x_pct: number;
  y_pct: number;
  width_pct?: number;
  height_pct?: number;
  size?: number;
}

interface PdfAnnotatorProps {
  file: File;
  onSave: (annotations: Annotation[]) => void;
}

const PdfAnnotator: React.FC<PdfAnnotatorProps> = ({ file, onSave }) => {
  const [numPages, setNumPages] = useState<number>();
  const [pageNumber, setPageNumber] = useState(1);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<fabric.Canvas | null>(null);
  const pageWrapperRef = useRef<HTMLDivElement>(null);
  
  // Store all annotations across pages
  const [allAnnotations, setAllAnnotations] = useState<Annotation[]>([]);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setFileUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  // Initialize Fabric.js canvas when page loads/changes
  const initFabricCanvas = (width: number, height: number) => {
    if (fabricCanvasRef.current) {
      fabricCanvasRef.current.dispose();
    }
    
    if (canvasRef.current) {
      canvasRef.current.width = width;
      canvasRef.current.height = height;
      
      const canvas = new fabric.Canvas(canvasRef.current, {
        width,
        height,
        selection: true
      });
      fabricCanvasRef.current = canvas;
      
      // Load annotations for current page
      const currentPageAnnotations = allAnnotations.filter(a => a.page === pageNumber);
      
      currentPageAnnotations.forEach(ann => {
        if (ann.type === 'text' && ann.text) {
          const text = new fabric.IText(ann.text, {
            left: ann.x_pct * width,
            top: ann.y_pct * height,
            fontSize: ann.size || 16,
            fontFamily: 'Helvetica',
            fill: 'black',
            transparentCorners: false,
            cornerColor: 'blue',
            cornerSize: 8
          });
          canvas.add(text);
        } else if (ann.type === 'rect') {
          const rect = new fabric.Rect({
            left: ann.x_pct * width,
            top: ann.y_pct * height,
            width: (ann.width_pct || 0.1) * width,
            height: (ann.height_pct || 0.05) * height,
            fill: 'white',
            stroke: '#ccc',
            strokeWidth: 1,
            transparentCorners: false,
            cornerColor: 'blue',
            cornerSize: 8
          });
          canvas.add(rect);
        }
      });
      
      canvas.renderAll();
    }
  };

  const saveCurrentPageAnnotations = () => {
    if (!fabricCanvasRef.current) return;
    
    const canvas = fabricCanvasRef.current;
    const width = canvas.getWidth();
    const height = canvas.getHeight();
    
    const objects = canvas.getObjects();
    const newAnnotations: Annotation[] = objects.map(obj => {
      if (obj.type === 'i-text' || obj.type === 'text') {
        const textObj = obj as fabric.IText;
        return {
          type: 'text',
          page: pageNumber,
          text: textObj.text || '',
          x_pct: (textObj.left || 0) / width,
          y_pct: (textObj.top || 0) / height,
          size: textObj.fontSize
        };
      } else if (obj.type === 'rect') {
        const rectObj = obj as fabric.Rect;
        return {
          type: 'rect',
          page: pageNumber,
          x_pct: (rectObj.left || 0) / width,
          y_pct: (rectObj.top || 0) / height,
          width_pct: ((rectObj.width || 0) * (rectObj.scaleX || 1)) / width,
          height_pct: ((rectObj.height || 0) * (rectObj.scaleY || 1)) / height,
        };
      }
      return null;
    }).filter(Boolean) as Annotation[];
    
    setAllAnnotations(prev => {
      const filtered = prev.filter(a => a.page !== pageNumber);
      return [...filtered, ...newAnnotations];
    });
  };

  const handlePageChange = (newPage: number) => {
    saveCurrentPageAnnotations();
    setPageNumber(newPage);
  };

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  function onPageLoadSuccess(page: any) {
    // When the react-pdf page finishes rendering, we can measure its DOM element
    // and initialize our Fabric canvas on top of it.
    setTimeout(() => {
      if (pageWrapperRef.current) {
        const { clientWidth, clientHeight } = pageWrapperRef.current;
        initFabricCanvas(clientWidth, clientHeight);
      }
    }, 100);
  }

  const addText = () => {
    if (!fabricCanvasRef.current) return;
    const canvas = fabricCanvasRef.current;
    
    const text = new fabric.IText('Type here', {
      left: 50,
      top: 50,
      fontFamily: 'Helvetica',
      fill: 'black',
      fontSize: 20,
      transparentCorners: false,
      cornerColor: 'blue',
      cornerSize: 8
    });
    
    canvas.add(text);
    canvas.setActiveObject(text);
    text.enterEditing();
    text.selectAll();
    canvas.renderAll();
  };

  const addWhiteout = () => {
    if (!fabricCanvasRef.current) return;
    const canvas = fabricCanvasRef.current;
    
    const rect = new fabric.Rect({
      left: 100,
      top: 100,
      fill: 'white',
      width: 150,
      height: 30,
      stroke: '#ccc', // subtle border so user can see it while editing
      strokeWidth: 1,
      transparentCorners: false,
      cornerColor: 'blue',
      cornerSize: 8
    });
    
    canvas.add(rect);
    canvas.setActiveObject(rect);
    canvas.renderAll();
  };

  const deleteSelected = () => {
    if (!fabricCanvasRef.current) return;
    const canvas = fabricCanvasRef.current;
    const activeObjects = canvas.getActiveObjects();
    
    if (activeObjects.length) {
      canvas.discardActiveObject();
      activeObjects.forEach(obj => {
        canvas.remove(obj);
      });
    }
  };

  const handleSaveAll = () => {
    saveCurrentPageAnnotations();
    // After state updates, we want to call onSave with the latest state
    // But setState is async, so we'll construct the final list here.
    
    // We already have saveCurrentPageAnnotations updating allAnnotations, but to be sure we send the most up-to-date:
    if (!fabricCanvasRef.current) return;
    const canvas = fabricCanvasRef.current;
    const width = canvas.getWidth();
    const height = canvas.getHeight();
    
    const objects = canvas.getObjects();
    const currentPageAnnotations: Annotation[] = objects.map(obj => {
      if (obj.type === 'i-text' || obj.type === 'text') {
        const textObj = obj as fabric.IText;
        return {
          type: 'text',
          page: pageNumber,
          text: textObj.text || '',
          x_pct: (textObj.left || 0) / width,
          y_pct: (textObj.top || 0) / height,
          size: textObj.fontSize
        };
      } else if (obj.type === 'rect') {
        const rectObj = obj as fabric.Rect;
        return {
          type: 'rect',
          page: pageNumber,
          x_pct: (rectObj.left || 0) / width,
          y_pct: (rectObj.top || 0) / height,
          width_pct: ((rectObj.width || 0) * (rectObj.scaleX || 1)) / width,
          height_pct: ((rectObj.height || 0) * (rectObj.scaleY || 1)) / height,
        };
      }
      return null;
    }).filter(Boolean) as Annotation[];
    
    const filtered = allAnnotations.filter(a => a.page !== pageNumber);
    const finalAnnotations = [...filtered, ...currentPageAnnotations];
    
    onSave(finalAnnotations);
  };

  // Keyboard shortcut for deleting objects
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Delete' || e.key === 'Backspace') {
        // Prevent deleting if user is typing in a text box
        if (fabricCanvasRef.current) {
          const active = fabricCanvasRef.current.getActiveObject();
          if (active && active.type === 'i-text' && (active as fabric.IText).isEditing) {
            return;
          }
          deleteSelected();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', width: '100%' }}>
      
      {/* Toolbar */}
      <div style={{ 
          display: 'flex', 
          gap: '0.5rem', 
          background: 'var(--bg-surface)', 
          padding: '0.75rem', 
          borderRadius: '8px',
          boxShadow: 'var(--shadow-sm)',
          border: '1px solid var(--border-subtle)',
          width: '100%',
          justifyContent: 'center',
          flexWrap: 'wrap'
      }}>
        <button type="button" onClick={addText} className="btn-secondary" style={{ padding: '0.5rem 1rem' }}>
          <span style={{ fontWeight: 600 }}>T</span> Add Text
        </button>
        <button type="button" onClick={addWhiteout} className="btn-secondary" style={{ padding: '0.5rem 1rem' }}>
          ⬜ Add Whiteout Box
        </button>
        <button type="button" onClick={deleteSelected} className="btn-secondary" style={{ padding: '0.5rem 1rem', color: 'red' }}>
          🗑️ Delete Selected
        </button>
      </div>

      {/* Pagination */}
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '0.5rem' }}>
        <button 
            type="button" 
            onClick={() => handlePageChange(Math.max(1, pageNumber - 1))} 
            disabled={pageNumber <= 1}
            style={{ padding: '4px 12px', border: '1px solid #ccc', borderRadius: '4px' }}
        >
            Prev
        </button>
        <span style={{ fontWeight: 500 }}>Page {pageNumber} of {numPages || '?'}</span>
        <button 
            type="button" 
            onClick={() => handlePageChange(Math.min(numPages || 1, pageNumber + 1))} 
            disabled={pageNumber >= (numPages || 1)}
            style={{ padding: '4px 12px', border: '1px solid #ccc', borderRadius: '4px' }}
        >
            Next
        </button>
      </div>

      {/* Editor Canvas Container */}
      <div style={{ 
          position: 'relative', 
          border: '1px solid var(--border-medium)', 
          borderRadius: '8px', 
          overflow: 'hidden',
          boxShadow: 'var(--shadow-card)',
          background: '#e0e0e0', // dark background outside page
          padding: '2rem'
      }}>
        {fileUrl ? (
          <Document 
            file={fileUrl} 
            onLoadSuccess={onDocumentLoadSuccess} 
            onLoadError={(err) => setLoadError(err.message)}
            loading="Loading PDF..."
            error={<div style={{ color: 'red', padding: '1rem' }}>Failed to load PDF: {loadError}</div>}
          >
            <div ref={pageWrapperRef} style={{ position: 'relative', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
              {/* The underlying PDF page */}
              <Page 
                pageNumber={pageNumber} 
                renderTextLayer={false} 
                renderAnnotationLayer={false}
                onLoadSuccess={onPageLoadSuccess}
              />
              
              {/* The interactive Fabric.js overlay */}
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 10 }}>
                <canvas ref={canvasRef} />
              </div>
            </div>
          </Document>
        ) : (
          <div>Preparing Document...</div>
        )}
      </div>
      
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        Drag and drop items to position them. Double-click text to edit. Select an item and press Delete to remove it.
      </p>

      <button type="button" onClick={handleSaveAll} className="btn-primary" style={{ marginTop: '0.5rem', width: '100%', maxWidth: '300px' }}>
        Save Annotations & Process
      </button>
    </div>
  );
};

export default PdfAnnotator;
