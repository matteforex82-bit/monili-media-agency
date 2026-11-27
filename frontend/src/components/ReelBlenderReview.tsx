'use client';

import { useRef, useState, type FormEvent, type ReactNode } from 'react';
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
  extra?: ReactNode;
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

export default function ReelBlenderReview({ draftId, revision, previews, shotNames, initialSelected = '', extra, disabled, onUpdate }: Props) {
  const [selected, setSelected] = useState(initialSelected);
  const [kind, setKind] = useState<'shot' | 'montage'>('shot');
  const [currentTime, setCurrentTime] = useState(0);
  const [text, setText] = useState('');
  const [showReference, setShowReference] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const player = useRef<HTMLVideoElement>(null);
  const active = previews.find((preview) => preview.id === selected) ??
    previews.find((preview) => preview.package_revision === revision) ?? previews[0];
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

  const external = (
    <details className="rb-details">
      <summary>Carica un video da Blender</summary>
      <form className="rb-stack" onSubmit={upload}>
        <div className="rs-grid-2">
          <label className="rs-field rb-field">
            <span>Tipo di video</span>
            <select className="rs-input" name="kind" value={kind} onChange={(event) => setKind(event.target.value === 'montage' ? 'montage' : 'shot')} disabled={locked}>
              <option value="shot">Singola ripresa</option>
              <option value="montage">Montaggio di prova</option>
            </select>
          </label>
          <label className="rs-field rb-field">
            <span>Video verticale MP4</span>
            <input className="rs-input" name="video" type="file" accept=".mp4,video/mp4" required disabled={locked} />
          </label>
        </div>
        {kind === 'shot' && shotNames.length > 0 && (
          <label className="rs-field rb-field">
            <span>Inquadratura del copione</span>
            <select className="rs-input" name="shot_index" disabled={locked} required defaultValue="">
              <option value="">Scegli la ripresa</option>
              {shotNames.map((name, index) => <option key={index} value={index}>{index + 1} · {name}</option>)}
            </select>
          </label>
        )}
        <div className="rb-actions"><button className="btn-secondary" type="submit" disabled={locked}>Carica video</button></div>
      </form>
    </details>
  );

  const approvedShot = isCurrent && active.status === 'approved' && active.kind === 'shot' && shotNames.length > 0;
  const hasResults = approvedShot && !!active.higgsfield_results?.length;
  const title = active?.shot_index !== undefined ? shotNames[active.shot_index] : active?.kind === 'montage' ? 'Montaggio di prova' : 'Ripresa Blender';

  return (
    <div className="rb-stack">
      {error && <p className="rs-error" role="alert">{error}</p>}
      {busy && <p className="rb-muted" role="status">Salvo la revisione…</p>}
      {active && (
        <>
          <div className="rb-review-head">
            <h3>{title || 'Ripresa Blender'}</h3>
            <span className="rb-meta" role="status">{isCurrent ? labels[active.status] : 'Regia precedente'}</span>
          </div>
          <div className={hasResults && !showReference ? "rb-review-grid rb-review-grid-result" : "rb-review-grid"}>
            <div className="rb-stack">
              {!isCurrent && <p className="rb-muted">Questa ripresa appartiene a una versione precedente della regia.</p>}
              {!approvedShot && isCurrent && (
                <>
                  {active.status === 'approved' ? <p className="rb-muted">Il montaggio di prova è approvato.</p> :
                    <p className="rb-muted">Guarda la composizione e il movimento. Se la ripresa va bene, approvala per preparare i file della prova.</p>}
                  {active.status !== 'approved' && (
                    <div className="rb-actions">
                      <button className="btn-mission" type="button" disabled={locked} onClick={() => review('approved')}>
                        {active.kind === 'shot' ? 'Approva per Seedance' : 'Approva montaggio'}
                      </button>
                    </div>
                  )}
                </>
              )}
              {approvedShot && (
                <ReelBlenderHiggsfield key={active.id}
                  base={`${base}/${encodeURIComponent(active.id)}/higgsfield`}
                  referenceUrl={videoUrl} shotNames={shotNames} shotIndex={active.shot_index}
                  results={active.higgsfield_results ?? []} disabled={locked} onUpdate={onUpdate} />
              )}
              <details className="rb-details">
                <summary>Note e file della ripresa{active.notes.length ? ` · ${active.notes.length} note` : ''}</summary>
                {active.notes.length > 0 && (
                  <ul className="rb-notes">
                    {active.notes.map((note) => (
                      <li key={`${note.time_ms}-${note.text}`}>
                        <button type="button" className="rb-text-button" onClick={() => {
                          setShowReference(true);
                          if (player.current) player.current.currentTime = note.time_ms / 1000;
                        }}>{timecode(note.time_ms)}</button>{' '}{note.text}
                      </li>
                    ))}
                  </ul>
                )}
                {hasResults && !showReference && (
                  <button type="button" className="rb-text-button" onClick={() => setShowReference(true)}>Rivedi il video di riferimento</button>
                )}
                {isCurrent && (
                  <form className="rb-stack" onSubmit={(event) => { event.preventDefault(); review(); }}>
                    <label className="rs-field rb-field">
                      <span>Nota al timecode {timecode(Math.round(currentTime * 1000))}</span>
                      <textarea className="rs-input" value={text} rows={2} maxLength={1000} disabled={locked}
                        onChange={(event) => setText(event.target.value)} placeholder="Es. Ferma la camera sul ricamo" />
                    </label>
                    <div className="rb-actions">
                      <button className="btn-secondary" type="submit" disabled={locked || !text.trim()}>Salva nota</button>
                      <button className="btn-secondary" type="button" disabled={locked || (!text.trim() && !active.notes.length)}
                        onClick={() => review('changes_requested')}>Segna da correggere</button>
                    </div>
                  </form>
                )}
                <a href={videoUrl + '?download=true'} className="rb-text-button">Scarica ripresa MP4</a>
              </details>
            </div>
            <div className="rb-review-film" hidden={hasResults && !showReference}>
              <video key={active.id} ref={player} src={videoUrl} crossOrigin="use-credentials"
                onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)} controls playsInline
                preload="metadata" aria-label="Previsualizzazione Blender" />
            </div>
          </div>
        </>
      )}
      {active || extra ? (
        <details className="rb-details">
          <summary>Altre riprese e versioni</summary>
          {previews.length > 1 && active && (
            <label className="rs-field rb-field">
              <span>Versione da rivedere</span>
              <select className="rs-input" value={active.id} disabled={locked} onChange={(event) => {
                setSelected(event.target.value);
                setCurrentTime(0);
                setShowReference(false);
                setText('');
                setError('');
              }}>
                {previews.map((preview, index) => (
                  <option key={preview.id} value={preview.id}>
                    {previews.length - index} · {preview.filename}
                    {preview.shot_index !== undefined ? ` · Ripresa ${preview.shot_index + 1}` : ''}
                    {preview.package_revision !== revision ? ' (regia precedente)' : ''}
                  </option>
                ))}
              </select>
            </label>
          )}
          {extra}
          {external}
        </details>
      ) : external}
    </div>
  );
}
