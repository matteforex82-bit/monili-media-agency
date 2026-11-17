'use client';

import { useEffect, useRef, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';
import { shrinkPhoto, type Draft } from '@/lib/drafts';

interface Props {
  // Called after each save so the list below can show the new piece.
  onSaved: (draft: Draft) => void;
}

interface Shot {
  file: File;
  url: string;
}

// In the shop: take the photos of the piece, write two lines (price, stone, size) and save. No AI, no wait:
// the Scheda pezzo is made later from the "Da lavorare" list.
export default function QuickCapture({ onSaved }: Props) {
  const [shots, setShots] = useState<Shot[]>([]);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [justSaved, setJustSaved] = useState('');
  const shotsRef = useRef<Shot[]>([]);
  shotsRef.current = shots;

  useEffect(
    () => () => {
      shotsRef.current.forEach((shot) => URL.revokeObjectURL(shot.url));
    },
    [],
  );

  function addFiles(list: FileList | null) {
    if (!list || list.length === 0) return;
    const added = Array.from(list)
      .filter((file) => file.type.startsWith('image/') || /\.(heic|heif)$/i.test(file.name))
      .map((file) => ({ file, url: URL.createObjectURL(file) }));
    setShots((current) => [...current, ...added].slice(0, 8));
    setJustSaved('');
  }

  function removeShot(index: number) {
    setShots((current) => {
      URL.revokeObjectURL(current[index].url);
      return current.filter((_, i) => i !== index);
    });
  }

  async function save() {
    if (shots.length === 0 || saving) return;
    setSaving(true);
    setError('');
    try {
      const form = new FormData();
      for (const shot of shots) {
        const small = await shrinkPhoto(shot.file);
        form.append('foto', small, small.name);
      }
      form.append('nota', note);
      const res = await fetch(`${API_URL}/bozze`, { method: 'POST', body: form });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
      shots.forEach((shot) => URL.revokeObjectURL(shot.url));
      setShots([]);
      setNote('');
      setJustSaved(`Salvato (${data.photos.length} foto${data.note ? ' e nota' : ''}). Puoi fare il prossimo pezzo.`);
      onSaved(data as Draft);
    } catch (err) {
      setError(`Non sono riuscito a salvare: ${err instanceof Error ? err.message : err}. Le foto sono ancora qui, riprova.`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="quick" aria-label="Salva un pezzo per dopo">
      {justSaved && (
        <div className="notice quick-ok" role="status">
          {justSaved}
        </div>
      )}
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}

      {shots.length > 0 && (
      <div className="quick-shots">
        {shots.map((shot, index) => (
          <div className="quick-shot" key={shot.url}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={shot.url} alt={`Foto ${index + 1} del pezzo`} />
            {index === 0 && <span className="quick-tag">principale</span>}
            <button type="button" className="quick-x" onClick={() => removeShot(index)} aria-label={`Togli la foto ${index + 1}`}>
              ×
            </button>
          </div>
        ))}
      </div>
      )}

      {shots.length < 8 && (
        <div className="quick-buttons">
          <label className="btn-mission quick-camera">
            {shots.length === 0 ? 'Scatta la foto' : 'Un’altra foto'}
            <input type="file" accept="image/*" capture="environment" onChange={(e) => { addFiles(e.target.files); e.target.value = ''; }} />
          </label>
          <label className="btn-secondary quick-roll">
            Dal rullino
            <input type="file" accept="image/*,.heic,.heif" multiple onChange={(e) => { addFiles(e.target.files); e.target.value = ''; }} />
          </label>
        </div>
      )}
      <div>
        <label className="field-label" htmlFor="quick-note">
          Due righe sul pezzo <small>prezzo, pietra, misura, colore</small>
        </label>
        <textarea
          id="quick-note"
          className="brief-area"
          rows={3}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Es. anello pietra ametista 159 euro, misura 13"
        />
      </div>

      <div className="cta-bar">
        <button type="button" className="btn-mission" onClick={save} disabled={shots.length === 0 || saving}>
          {saving ? 'Salvo...' : 'Salva per dopo'}
        </button>
        {shots.length === 0 && <p className="page-lead" style={{ margin: 0, textAlign: 'center' }}>Fai almeno una foto per salvare.</p>}
      </div>
    </section>
  );
}
