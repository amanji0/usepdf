import { useState, useCallback } from 'react';

export function useFileUpload(multiFile: boolean) {
  const [files, setFiles] = useState<File[]>([]);

  const addFiles = useCallback((newFiles: File[]) => {
    if (multiFile) {
      setFiles(prev => [...prev, ...newFiles]);
    } else {
      // Replace existing file if single file mode
      setFiles([newFiles[0]]);
    }
  }, [multiFile]);

  const removeFile = useCallback((indexToRemove: number) => {
    setFiles(prev => prev.filter((_, i) => i !== indexToRemove));
  }, []);

  const reorderFiles = useCallback((fromIndex: number, toIndex: number) => {
    setFiles(prev => {
      const copy = [...prev];
      const [item] = copy.splice(fromIndex, 1);
      copy.splice(toIndex, 0, item);
      return copy;
    });
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  return { files, addFiles, removeFile, reorderFiles, clearFiles };
}
