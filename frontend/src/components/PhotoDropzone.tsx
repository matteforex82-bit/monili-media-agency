'use client';

import { useCallback, useState } from 'react';

interface Props {
  photo: File | null;
  photoPreview: string | null;
  onFile: (file: File, previewUrl: string) => void;
  onClear: () => void;
}

export default function PhotoDropzone({ photo, photoPreview, onFile, onClear }: Props) {
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = useCallback((file: File) => {
    const lowerName = file.name.toLowerCase();
    const isHeic = lowerName.endsWith('.heic') || lowerName.endsWith('.heif');
    if (!file.type.startsWith('image/') && !isHeic) return;
    const url = URL.createObjectURL(file);
    onFile(file, url);
  }, [onFile]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const onInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  /* Stato: foto caricata */
  if (photo && photoPreview) {
    return (
      <div style={{
        position: 'relative',
        borderRadius: 22,
        overflow: 'hidden',
        border: '1px solid var(--bot-border)',
        boxShadow: 'var(--bot-shadow-lg)',
        background: '#fff',
        padding: 10,
      }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={photoPreview}
          alt="Prodotto caricato"
          style={{ width: '100%', height: 260, objectFit: 'cover', display: 'block', borderRadius: 18 }}
        />
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(42,31,20,0.78) 0%, transparent 52%)',
          display: 'flex',
          alignItems: 'flex-end',
          padding: '14px 16px',
        }}>
          <div style={{ flex: 1 }}>
            <div style={{
              fontFamily: 'var(--bot-font-sans)',
              fontWeight: 700,
              fontSize: 13,
              color: 'var(--bot-moss-bg)',
              marginBottom: 3,
              display: 'flex',
              alignItems: 'center',
              gap: 5,
            }}>
              Foto caricata
            </div>
            <div style={{
              fontFamily: 'var(--bot-font-mono)',
              fontSize: 10,
              color: 'rgba(255,255,255,0.5)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: 200,
            }}>
              {photo.name}
            </div>
          </div>
          <button
            onClick={onClear}
            className="btn-secondary"
            style={{ padding: '5px 12px', fontSize: 11 }}
          >
            Cambia
          </button>
        </div>
      </div>
    );
  }

  /* Stato: zona upload */
  return (
    <label className={`bot-upload-card ${isDragging ? 'drag-over' : ''}`} onDragOver={e => { e.preventDefault(); setIsDragging(true); }} onDragLeave={() => setIsDragging(false)} onDrop={onDrop}>
      <input type="file" accept="image/*,.heic,.heif" style={{ display: 'none' }} onChange={onInputChange} />

      <div className="bot-upload-mark">
        {isDragging ? 'OK' : '+'}
      </div>

      <div>
        <div className="bot-upload-title">
          {isDragging ? 'Rilascia qui la foto' : 'Carica la foto del prodotto'}
        </div>
        <div className="bot-upload-sub">
          Anche scattata al volo va bene · JPG · PNG · HEIC
        </div>
        <div className="bot-upload-button">
          Sfoglia dall'iPhone
        </div>
      </div>
    </label>
  );
}

