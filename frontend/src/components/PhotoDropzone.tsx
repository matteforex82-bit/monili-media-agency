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
    if (!file.type.startsWith('image/')) return;
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

  /* ── STATO: foto caricata ── */
  if (photo && photoPreview) {
    return (
      <div style={{
        position: 'relative',
        borderRadius: 14,
        overflow: 'hidden',
        border: '1.5px solid rgba(126,158,114,0.45)',
        boxShadow: '0 0 0 3px var(--sage-pale), var(--shadow-sm)',
      }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={photoPreview}
          alt="Prodotto caricato"
          style={{ width: '100%', height: 240, objectFit: 'cover', display: 'block' }}
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
              fontFamily: 'DM Sans',
              fontWeight: 700,
              fontSize: 12,
              color: 'var(--sage-light)',
              marginBottom: 3,
              display: 'flex',
              alignItems: 'center',
              gap: 5,
            }}>
              ✓ Foto caricata
            </div>
            <div style={{
              fontFamily: 'DM Mono',
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

  /* ── STATO: zona upload ── */
  return (
    <label
      className={`upload-zone ${isDragging ? 'drag-over' : ''}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 240,
        cursor: 'pointer',
        gap: 16,
        textAlign: 'center',
        padding: '28px 24px',
      }}
      onDragOver={e => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
    >
      <input type="file" accept="image/*" style={{ display: 'none' }} onChange={onInputChange} />

      {/* Camera icon */}
      <div style={{
        width: 68,
        height: 68,
        borderRadius: '50%',
        background: isDragging ? 'var(--terracotta-pale)' : 'var(--cream-3)',
        border: `2px solid ${isDragging ? 'var(--terracotta)' : 'var(--cream-border)'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 28,
        transition: 'all 0.3s cubic-bezier(0.16,1,0.3,1)',
        boxShadow: isDragging ? '0 0 0 6px var(--terracotta-pale)' : 'none',
      }}>
        {isDragging ? '⬇️' : '📷'}
      </div>

      <div>
        <div style={{
          fontFamily: 'DM Sans',
          fontWeight: 600,
          fontSize: 15,
          color: isDragging ? 'var(--terracotta-dark)' : 'var(--espresso-mid)',
          marginBottom: 6,
          transition: 'color 0.3s',
        }}>
          {isDragging ? 'Rilascia qui la foto' : 'Trascina la foto del prodotto'}
        </div>
        <div style={{ fontSize: 13, color: 'var(--espresso-dim)' }}>
          oppure{' '}
          <span style={{ color: 'var(--terracotta)', fontWeight: 600 }}>
            clicca per scegliere
          </span>
        </div>
        <div style={{ fontSize: 11, color: 'var(--cream-border)', marginTop: 8, letterSpacing: '0.08em' }}>
          JPG · PNG · WEBP
        </div>
      </div>
    </label>
  );
}
