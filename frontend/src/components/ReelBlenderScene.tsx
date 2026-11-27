'use client';

import { useState, type FormEvent } from 'react';
import { API_URL } from '@/lib/apiUrl';
import ReelBlenderRender from '@/components/ReelBlenderRender';

export interface SceneFile {
  id: string;
  music: string;
  shot_count: number;
}

interface Props {
  draftId: string;
  scene?: SceneFile | null;
  musicBpm: number;
  disabled: boolean;
  onUpdate: (data: unknown) => void;
}

export default function ReelBlenderScene({ draftId, scene, musicBpm, disabled, onUpdate }: Props) {
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const base = `${API_URL}/reel-blender/drafts/${encodeURIComponent(draftId)}/scene`;

  async function request(url: string, init: RequestInit) {
    const response = await fetch(url, init);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Operazione Blender non riuscita.');
    return data;
  }

  async function launch(id: string) {
    await request(`${base}/${encodeURIComponent(id)}/open`, { method: 'POST' });
    setNotice('Ho avviato Blender sul PC di AI Studio.');
  }

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || disabled) return;
    const form = new FormData(event.currentTarget);
    const file = form.get('music');
    if (file instanceof File && !file.size) form.delete('music');
    setBusy(true);
    setError('');
    setNotice('Creazione della scena in corso…');
    try {
      const draft = await request(base, { method: 'POST', body: form });
      onUpdate(draft);
      setNotice('Scena salvata.');
      await launch(draft.scene.id);
    } catch (err) {
      setNotice('');
      setError(err instanceof Error ? err.message : 'Operazione Blender non riuscita.');
    } finally {
      setBusy(false);
    }
  }

  async function reopen() {
    if (!scene || busy || disabled) return;
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await launch(scene.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Operazione Blender non riuscita.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rs-card" aria-labelledby="reel-blender-scene">
      <h3 className="rs-h1" id="reel-blender-scene">Scena e musica in Blender</h3>
      <p className="rs-muted">Crea il set di prova con una camera per inquadratura, i tagli in timeline e le foto di riferimento.</p>
      <form className="rs-card" onSubmit={create}>
        <label className="rs-field">
          <span className="rs-field-label">Il tuo brano (facoltativo)</span>
          <input className="rs-input" type="file" name="music" accept=".mp3,.wav,.m4a,.ogg,.aac,.flac" disabled={busy || disabled} />
        </label>
        <p className="rs-muted">Senza un brano, Blender inserisce una guida ritmica originale a {musicBpm} BPM, con gli accenti previsti dalla regia. La trovi nella scena «Montaggio e musica».</p>
        <button className="btn-mission" type="submit" disabled={busy || disabled}>Crea e apri in Blender</button>
      </form>
      {notice && <p className="rs-muted" role="status">{notice}</p>}
      {error && <p className="rs-error" role="alert">{error}</p>}
      {scene && (
        <>
          <p>{scene.shot_count} inquadrature · {scene.music}</p>
          <div className="rs-actions">
            <button className="btn-secondary" type="button" disabled={busy || disabled} onClick={() => void reopen()}>Apri in Blender</button>
            <a className="btn-secondary" href={`${base}/${encodeURIComponent(scene.id)}`}>Scarica .blend</a>
          </div>
          <ReelBlenderRender key={scene.id} base={`${base}/${encodeURIComponent(scene.id)}/render`} disabled={busy || disabled} />
        </>
      )}
    </section>
  );
}
