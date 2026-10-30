'use client';

import { useEffect, useId, useMemo, useState } from 'react';

interface Props {
  files: File[];
  onFiles: (files: File[]) => void;
  accept: string;
  max: number;
  kind: 'photo' | 'video';
  title: string;
  hint: string;
  // Testo al posto del riquadro vuoto quando non serve caricare niente (es. si usa la foto della scheda).
  note?: string;
}

// Lo stesso riquadro della pagina Nuovo pezzo, per più file (foto o clip).
export default function FileDropzone({ files, onFiles, accept, max, kind, title, hint, note }: Props) {
  const inputId = useId();
  const [dragging, setDragging] = useState(false);
  const previews = useMemo(() => (kind === 'photo' ? files.map((file) => URL.createObjectURL(file)) : []), [files, kind]);

  useEffect(() => () => previews.forEach((url) => URL.revokeObjectURL(url)), [previews]);

  const take = (list: FileList | File[]) => {
    const next = Array.from(list).slice(0, max);
    if (next.length) onFiles(next);
  };

  return (
    <div>
      <label
        htmlFor={inputId}
        className={`bot-upload-card dropzone-small${dragging ? ' drag-over' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          take(e.dataTransfer.files);
        }}
      >
        <input
          id={inputId}
          type="file"
          accept={accept}
          multiple={max > 1}
          style={{ position: 'absolute', opacity: 0, width: 1, height: 1 }}
          onChange={(e) => {
            if (e.target.files) take(e.target.files);
            e.target.value = '';
          }}
        />
        <div className="bot-upload-title">{files.length ? `${title}: ${files.length} su ${max}` : title}</div>
        <div className="bot-upload-sub">{note && !files.length ? note : hint}</div>
        <div className="bot-upload-button">{files.length ? 'Cambia' : kind === 'photo' ? 'Scegli le foto' : 'Scegli le clip'}</div>
      </label>
      {files.length > 0 && (
        <div className="file-previews">
          {kind === 'photo'
            ? previews.map((url, index) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img key={url} src={url} alt={`Foto ${index + 1}`} />
              ))
            : files.map((file) => (
                <span key={file.name + file.size} className="file-chip">{file.name}</span>
              ))}
          <button type="button" className="btn-secondary" onClick={() => onFiles([])}>Togli</button>
        </div>
      )}
    </div>
  );
}
