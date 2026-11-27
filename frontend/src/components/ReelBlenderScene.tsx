'use client';

import { useState, type FormEvent } from 'react';
import { API_URL } from '@/lib/apiUrl';
import ReelBlenderRender, { type RenderJob } from '@/components/ReelBlenderRender';

export interface SceneFile {
  id: string;
  music: string;
  shot_count: number;
}

interface Props {
  draftId: string;
  scene?: SceneFile | null;
  musicBpm: number;
  job: RenderJob;
  disabled: boolean;
  onUpdate: (data: unknown) => void;
  onContinue: () => void;
}

export default function ReelBlenderScene({ draftId, scene, musicBpm, job, disabled, onUpdate, onContinue }: Props) {
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const base = `${API_URL}/reel-blender/drafts/${encodeURIComponent(draftId)}/scene`;
  const locked = busy || disabled || job.running;

  async function request(url: string, init: RequestInit) {
    const response = await fetch(url, init);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Operazione Blender non riuscita. Riprova.');
    return data;
  }

  async function launch(id: string) {
    await request(`${base}/${encodeURIComponent(id)}/open`, { method: 'POST' });
    setNotice('Blender si apre sul PC di AI Studio.');
  }

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (locked) return;
    const form = new FormData(event.currentTarget);
    const file = form.get('music');
    if (file instanceof File && !file.size) form.delete('music');
    setBusy(true);
    setError('');
    setNotice('Creo la scena con le camere e la musica…');
    try {
      const draft = await request(base, { method: 'POST', body: form });
      onUpdate(draft);
      setNotice('Scena salvata.');
      await launch(draft.scene.id);
    } catch (err) {
      setNotice('');
      setError(err instanceof Error ? err.message : 'Operazione Blender non riuscita. Riprova.');
    } finally {
      setBusy(false);
    }
  }

  async function reopen() {
    if (!scene || locked) return;
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await launch(scene.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Operazione Blender non riuscita. Riprova.');
    } finally {
      setBusy(false);
    }
  }

  const musicField = (
    <label className="rs-field rb-field">
      <span>Brano per il montaggio</span>
      <input className="rs-input" type="file" name="music" accept=".mp3,.wav,.m4a,.ogg,.aac,.flac" disabled={locked} />
    </label>
  );

  return (
    <div className="rb-stack">
      {scene ? (
        <>
          <p className="rb-meta">{scene.shot_count} inquadrature · {scene.music}</p>
          <ReelBlenderRender key={scene.id} base={`${base}/${encodeURIComponent(scene.id)}/render`}
            job={job} disabled={busy || disabled} onContinue={onContinue} />
          <details className="rb-details">
            <summary>File Blender e musica</summary>
            <div className="rb-actions">
              <button className="btn-secondary" type="button" disabled={locked} onClick={() => void reopen()}>Apri in Blender</button>
              <a className="btn-secondary" href={`${base}/${encodeURIComponent(scene.id)}`}>Scarica .blend</a>
            </div>
            <form onSubmit={create} className="rb-stack">
              {musicField}
              <p className="rb-muted">Creare una nuova scena sostituisce quella attiva nel progetto.</p>
              <div className="rb-actions">
                <button className="btn-secondary" type="submit" disabled={locked}>Crea una nuova scena</button>
              </div>
            </form>
          </details>
        </>
      ) : (
        <form onSubmit={create} className="rb-stack">
          <p className="rb-muted">Lo Studio prepara le camere, i tagli e una guida ritmica a {musicBpm} BPM. La scena si apre sul PC.</p>
          <details className="rb-details rb-inline-details">
            <summary>Usa un tuo brano</summary>
            {musicField}
          </details>
          <div className="rb-actions">
            <button className="btn-mission" type="submit" disabled={locked}>{busy ? 'Creo la scena…' : 'Crea e apri Blender'}</button>
          </div>
        </form>
      )}
      {notice && <p className="rb-muted" role="status">{notice}</p>}
      {error && <p className="rs-error" role="alert">{error}</p>}
    </div>
  );
}
