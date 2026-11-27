'use client';

import { useRef, useState, type FormEvent } from 'react';
import { API_URL } from '@/lib/apiUrl';
import ReelBlenderHiggsfield, { type HiggsfieldResult } from '@/components/ReelBlenderHiggsfield';

export type PreviewStatus = 'to_review' | 'changes_requested' | 'approved';

export interface BlenderPreview {
  id: string;
  filename: string;
  kind: 'shot' | 'montage';
  duration_ms: number;
  package_revision: string;
  status: PreviewStatus;
  notes: { time_ms: number; text: string }[];
  shot_index?: number;
  higgsfield_results?: HiggsfieldResult[];
}

interface Props {
  draftId: string;
  revision?: string;
  previews: BlenderPreview[];
  shotNames: string[];
  initialSelected?: string;
  disabled: boolean;
  onUpdate: (draft: unknown) => void;
}

const labels: Record<PreviewStatus, string> = {
  to_review: 'Da rivedere',
  changes_requested: 'Modifiche richieste',
  approved: 'Approvata',
};

function timecode(milliseconds: number) {
  const minutes = Math.floor(milliseconds / 60_000);
  const seconds = Math.floor(milliseconds / 1000) % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(milliseconds % 1000).padStart(3, '0')}`;
}

export default function ReelBlenderReview({ draftId, revision, previews, shotNames, initialSelected = '', disabled, onUpdate }: Props) {
  const [selected, setSelected] = useState(initialSelected);
  const [kind, setKind] = useState<'shot' | 'montage'>('shot');
  const [currentTime, setCurrentTime] = useState(0);
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const player = useRef<HTMLVideoElement>(null);
  const active = previews.find((preview) => preview.id === selected) ?? previews[0];
  const isCurrent = active && active.package_revision === revision;
  const base = `${API_URL}/reel-blender/drafts/${encodeURIComponent(draftId)}/previews`;
  const locked = disabled || busy;
  const videoUrl = active ? `${base}/${encodeURIComponent(active.id)}/video` : '';

  async function request(url: string, init: RequestInit, onSuccess?: (data: unknown) => void) {
    setError('');
    setBusy(true);
    try {
      const res = await fetch(url, init);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || 'Operazione non riuscita.');
      onUpdate(data);
      onSuccess?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Operazione non riuscita.');
    } finally {
      setBusy(false);
    }
  }

  function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    void request(base, { method: 'POST', body: new FormData(form) }, () => {
      setSelected('');
      setCurrentTime(0);
      setText('');
      form.reset();
      setKind('shot');
    });
  }

  function review(status?: PreviewStatus) {
    if (!active || !isCurrent || locked) return;
    const note = text.trim();
    if (!note && !status) return;
    const seconds = player.current?.currentTime ?? currentTime;
    const time_ms = Math.max(0, Math.min(Math.round(seconds * 1000), active.duration_ms));
    const body = { status, note: note ? { time_ms, text: note } : undefined };
    void request(`${base}/${encodeURIComponent(active.id)}/review`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }, () => setText(''));
  }

  return (
    <section className="rs-card" aria-labelledby="blender-preview-heading">
      <h3 className="rs-h1" id="blender-preview-heading">Revisione e prova Seedance</h3>
      <details className="rs-details">
        <summary>Carica una previsualizzazione esterna</summary>
        <form className="rs-card" onSubmit={upload}>
          <div className="rs-grid-2">
            <label className="rs-field">
              <span className="rs-field-label">Cosa carichi</span>
              <select className="rs-input" name="kind" value={kind} onChange={(event) => setKind(event.target.value === 'montage' ? 'montage' : 'shot')} disabled={locked}>
                <option value="shot">Una singola ripresa</option>
                <option value="montage">Il montaggio di prova</option>
              </select>
            </label>
            <label className="rs-field">
              <span className="rs-field-label">Video verticale MP4 H.264</span>
              <input className="rs-input" name="video" type="file" accept=".mp4,video/mp4" required disabled={locked} />
            </label>
          </div>
          {kind === 'shot' && shotNames.length > 0 && (
            <label className="rs-field">
              <span className="rs-field-label">Inquadratura del copione</span>
              <select className="rs-input" name="shot_index" disabled={locked} required defaultValue="">
                <option value="">Scegli la ripresa che hai esportato</option>
                {shotNames.map((name, index) => <option key={index} value={index}>{index + 1} · {name}</option>)}
              </select>
            </label>
          )}
          <button className="btn-secondary" type="submit" disabled={locked}>Carica previsualizzazione</button>
        </form>
      </details>
      {!active && <p className="rs-muted">Dopo il render, apri una ripresa con «Rivedi la ripresa». Una volta approvata puoi scaricare i file per Seedance.</p>}
      {error && <p className="rs-error" role="alert">{error}</p>}
      {busy && <p className="rs-muted" role="status">Operazione in corso…</p>}
      {active && (
        <div className="rs-card">
          <label className="rs-field">
            <span className="rs-field-label">Versione da rivedere</span>
            <select className="rs-input" value={active.id} disabled={locked} onChange={(event) => {
              setSelected(event.target.value);
              setCurrentTime(0);
              setText('');
              setError('');
            }}>
              {previews.map((preview, index) => (
                <option key={preview.id} value={preview.id}>
                  {previews.length - index} · {preview.kind === 'shot' ? 'Ripresa' : 'Montaggio'} · {preview.filename}
                  {preview.shot_index !== undefined ? ` · Shot ${preview.shot_index + 1}` : ''}
                  {preview.package_revision !== revision ? ' (pacchetto precedente)' : ''}
                </option>
              ))}
            </select>
          </label>
          <p role="status" className="rs-muted">{labels[active.status]}</p>
          <div className="rs-video-wrap" style={{ maxWidth: 280 }}>
            <video
              key={active.id}
              ref={player}
              src={videoUrl}
              crossOrigin="use-credentials"
              onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
              controls
              playsInline
              preload="metadata"
              aria-label="Previsualizzazione Blender"
            />
          </div>
          <a href={videoUrl + '?download=true'} className="btn-secondary rs-small-btn">Scarica MP4</a>
          {active.notes.length > 0 && (
            <ul>
              {active.notes.map((note) => (
                <li key={`${note.time_ms}-${note.text}`}>
                  <button type="button" className="btn-secondary rs-small-btn" onClick={() => {
                    if (player.current) player.current.currentTime = note.time_ms / 1000;
                  }}>{timecode(note.time_ms)}</button>{' '}{note.text}
                </li>
              ))}
            </ul>
          )}
          {isCurrent ? (
            <form className="rs-card" onSubmit={(event) => { event.preventDefault(); review(); }}>
              <label className="rs-field">
                <span className="rs-field-label">Nota al timecode {timecode(Math.round(currentTime * 1000))}</span>
                <textarea className="rs-input" value={text} rows={2} maxLength={1000} disabled={locked}
                  onChange={(event) => setText(event.target.value)} placeholder="Es. Ferma la camera quando la pietra prende luce." />
              </label>
              <div className="rs-actions">
                <button className="btn-secondary" type="submit" disabled={locked || !text.trim()}>Salva nota</button>
                <button className="btn-secondary" type="button" disabled={locked || (!text.trim() && !active.notes.length)} onClick={() => review('changes_requested')}>Segna da correggere</button>
                <button className="btn-mission" type="button" disabled={locked || active.status === 'approved'} onClick={() => review('approved')}>
                  {active.kind === 'shot' ? 'Approva per Seedance' : 'Approva montaggio di prova'}
                </button>
              </div>
              {active.status === 'approved' && active.kind === 'shot' && (
                <p className="rs-muted">Ripresa approvata per la prova manuale in Higgsfield.</p>
              )}
            </form>
          ) : <p className="rs-muted">Questa versione appartiene a un pacchetto precedente.</p>}
          {isCurrent && active.status === 'approved' && active.kind === 'shot' && shotNames.length > 0 && (
            <ReelBlenderHiggsfield
              key={active.id}
              base={`${base}/${encodeURIComponent(active.id)}/higgsfield`}
              referenceUrl={videoUrl}
              shotNames={shotNames}
              shotIndex={active.shot_index}
              results={active.higgsfield_results ?? []}
              disabled={locked}
              onUpdate={onUpdate}
            />
          )}
        </div>
      )}
    </section>
  );
}
