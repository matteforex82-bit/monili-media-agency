'use client';

import Link from 'next/link';
import { useCallback, useEffect, useImperativeHandle, useState, forwardRef } from 'react';
import { API_URL } from '@/lib/apiUrl';
import { formatDraftTime, type Draft } from '@/lib/drafts';
import { loadSettings } from '@/lib/settings';

export interface DraftListHandle {
  refresh: () => void;
}

interface Props {
  // Called with the job id when "Crea la scheda" starts the work (the page then follows it).
  onStarted: (jobId: string) => void;
}

const photoUrl = (draft: Draft, name: string, width = 480) =>
  `${API_URL}/bozze/${draft.id}/foto/${encodeURIComponent(name)}?w=${width}`;

// The pieces saved in the shop, waiting for their Scheda pezzo.
const DraftList = forwardRef<DraftListHandle, Props>(function DraftList({ onStarted }, ref) {
  const [drafts, setDrafts] = useState<Draft[] | null>(null);
  const [error, setError] = useState('');
  const [open, setOpen] = useState<string | null>(null);
  const [confirming, setConfirming] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const refresh = useCallback(() => {
    fetch(`${API_URL}/bozze`, { cache: 'no-store' })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setDrafts(Array.isArray(data?.items) ? data.items : []);
        setError('');
      })
      .catch(() => setError('Non riesco a leggere i pezzi salvati. Controlla che lo Studio sul PC sia acceso.'));
  }, []);

  useImperativeHandle(ref, () => ({ refresh }), [refresh]);
  useEffect(() => {
    refresh();
  }, [refresh]);

  // While a Scheda is being made, look again now and then.
  useEffect(() => {
    if (!drafts?.some((draft) => draft.status === 'in_corso')) return;
    const timer = setInterval(refresh, 5000);
    return () => clearInterval(timer);
  }, [drafts, refresh]);

  const replace = (next: Draft) => setDrafts((list) => (list ? list.map((d) => (d.id === next.id ? next : d)) : list));

  async function call(draft: Draft, path: string, init: RequestInit) {
    const res = await fetch(`${API_URL}/bozze/${draft.id}${path}`, init);
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
    return data;
  }

  async function saveChoices(draft: Draft, patch: Partial<Pick<Draft, 'note' | 'main' | 'detail'>>) {
    try {
      replace(await call(draft, '', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(patch) }));
    } catch (err) {
      setError(`Non sono riuscito a salvare la modifica: ${err instanceof Error ? err.message : err}`);
    }
  }

  async function create(draft: Draft) {
    setBusy(draft.id);
    setError('');
    try {
      const settings = loadSettings();
      const data = await call(draft, '/crea', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text_model: settings.textModel, image_model: settings.imageModel }),
      });
      onStarted(data.job_id);
    } catch (err) {
      setError(`Non riesco a creare la scheda: ${err instanceof Error ? err.message : err}`);
      refresh();
    } finally {
      setBusy(null);
    }
  }

  async function remove(draft: Draft) {
    setBusy(draft.id);
    try {
      await call(draft, '', { method: 'DELETE' });
      setDrafts((list) => (list ? list.filter((d) => d.id !== draft.id) : list));
      setConfirming(null);
      setOpen(null);
    } catch (err) {
      setError(`Non sono riuscito a eliminare: ${err instanceof Error ? err.message : err}`);
    } finally {
      setBusy(null);
    }
  }

  async function removePhoto(draft: Draft, name: string) {
    try {
      replace(await call(draft, `/foto/${encodeURIComponent(name)}`, { method: 'DELETE' }));
    } catch (err) {
      setError(`Non sono riuscito a togliere la foto: ${err instanceof Error ? err.message : err}`);
    }
  }

  async function addPhotos(draft: Draft, files: FileList | null) {
    if (!files || files.length === 0) return;
    const form = new FormData();
    Array.from(files).forEach((file) => form.append('foto', file));
    try {
      replace(await call(draft, '/foto', { method: 'POST', body: form }));
    } catch (err) {
      setError(`Non sono riuscito ad aggiungere la foto: ${err instanceof Error ? err.message : err}`);
    }
  }

  const todo = drafts?.filter((d) => d.status !== 'scheda_pronta') ?? [];
  const ready = drafts?.filter((d) => d.status === 'scheda_pronta') ?? [];

  if (drafts === null && !error) return <p className="page-lead">Carico i pezzi salvati...</p>;

  return (
    <section className="drafts" aria-label="Pezzi salvati da lavorare">
      <h2 className="drafts-title">
        Da lavorare <span>{todo.length}</span>
      </h2>
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}
      {drafts && todo.length === 0 && <p className="page-lead">Niente in attesa. I pezzi che salvi dal negozio compaiono qui.</p>}

      <ul className="draft-list">
        {[...todo, ...ready].map((draft) => {
          const cover = draft.main || draft.photos[0];
          const isOpen = open === draft.id;
          const running = draft.status === 'in_corso';
          const done = draft.status === 'scheda_pronta';
          const facts = draft.facts || {};
          return (
            <li key={draft.id} className={`draft ${done ? 'draft-done' : ''}`}>
              <button type="button" className="draft-head" aria-expanded={isOpen} onClick={() => setOpen(isOpen ? null : draft.id)}>
                {cover ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={photoUrl(draft, cover, 360)} alt="" loading="lazy" />
                ) : (
                  <span className="piece-thumb-empty" />
                )}
                <span className="draft-text">
                  <span className="draft-chips">
                    {facts.pietre?.map((stone) => (
                      <span className="chip" key={stone}>{stone}</span>
                    ))}
                    {facts.prezzo !== undefined && <span className="chip chip-price">{facts.prezzo} €</span>}
                    {facts.misura && <span className="chip">mis. {facts.misura}</span>}
                  </span>
                  <span className="draft-note">{draft.note || 'Nessuna nota'}</span>
                  <span className="draft-meta">
                    {formatDraftTime(draft.created_at)} · {draft.photos.length} foto
                    {running && ' · scheda in preparazione'}
                    {done && ' · scheda pronta'}
                  </span>
                </span>
              </button>

              {draft.error && !running && !done && <p className="draft-error">{draft.error}</p>}

              {isOpen && (
                <div className="draft-body">
                  <div className="draft-photos">
                    {draft.photos.map((name) => (
                      <div className="draft-photo" key={name}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={photoUrl(draft, name)} alt="" loading="lazy" />
                        <div className="draft-photo-actions">
                          <button type="button" className="chip-btn" aria-pressed={draft.main === name} onClick={() => saveChoices(draft, { main: name })}>
                            Principale
                          </button>
                          <button
                            type="button"
                            className="chip-btn"
                            aria-pressed={draft.detail === name}
                            disabled={draft.main === name}
                            onClick={() => saveChoices(draft, { detail: draft.detail === name ? '' : name })}
                          >
                            Dettaglio
                          </button>
                          {draft.photos.length > 1 && (
                            <button type="button" className="chip-btn" onClick={() => removePhoto(draft, name)} aria-label="Togli questa foto">
                              ×
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                    {draft.photos.length < 8 && (
                      <label className="quick-add draft-add">
                        <span aria-hidden="true">+</span>
                        Foto
                        <input type="file" accept="image/*,.heic,.heif" multiple onChange={(e) => { void addPhotos(draft, e.target.files); e.target.value = ''; }} />
                      </label>
                    )}
                  </div>

                  <label className="field-label" htmlFor={`note-${draft.id}`}>Nota</label>
                  <textarea
                    id={`note-${draft.id}`}
                    className="brief-area"
                    rows={3}
                    defaultValue={draft.note}
                    onBlur={(e) => {
                      if (e.target.value.trim() !== draft.note) void saveChoices(draft, { note: e.target.value });
                    }}
                    placeholder="Prezzo, pietra, misura, colore"
                  />
                  <p className="draft-hint">
                    Alla creazione uso la foto «Principale» e, se c&apos;è, quella «Dettaglio»; la nota guida la scheda.
                  </p>

                  <div className="draft-actions">
                    {done && draft.run_id ? (
                      <Link href={`/pezzi/${encodeURIComponent(draft.run_id)}`} className="btn-mission" style={{ textDecoration: 'none' }}>
                        Apri la scheda
                      </Link>
                    ) : (
                      <button type="button" className="btn-mission" disabled={busy === draft.id || running} onClick={() => create(draft)}>
                        {running ? 'In preparazione...' : busy === draft.id ? 'Avvio...' : 'Crea la scheda'}
                      </button>
                    )}
                    <button type="button" className="btn-secondary" onClick={() => setConfirming(confirming === draft.id ? null : draft.id)}>
                      Elimina
                    </button>
                  </div>

                  {confirming === draft.id && (
                    <div className="piece-confirm" role="group" aria-label="Conferma eliminazione">
                      <p>Tolgo questo pezzo salvato? Finisce nel cestino sul PC.</p>
                      <div>
                        <button type="button" className="btn-mission" disabled={busy === draft.id} onClick={() => remove(draft)}>
                          Sì, elimina
                        </button>
                        <button type="button" className="btn-secondary" onClick={() => setConfirming(null)}>
                          Annulla
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
});

export default DraftList;
