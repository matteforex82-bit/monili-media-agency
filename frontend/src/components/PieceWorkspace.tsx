'use client';

import Link from 'next/link';
import { useState } from 'react';
import PromptLab, { type LabStep } from '@/components/PromptLab';
import { API_URL } from '@/lib/apiUrl';
import { formatDraftTime, type Draft, type Progress } from '@/lib/drafts';
import { loadSettings } from '@/lib/settings';

type Step = 'foto' | LabStep;

interface Props {
  draft: Draft;
  onBack: () => void;
  onUpdate: (draft: Draft) => void;
  onRemoved: (id: string) => void;
  onStarted: (jobId: string) => void;
}

const photoUrl = (draft: Draft, name: string, width = 480) => `${API_URL}/bozze/${draft.id}/foto/${encodeURIComponent(name)}?w=${width}`;

function firstStep(progress?: Progress): Step {
  switch (progress?.stage) {
    case 'carica':
      return 'generare';
    case 'valuta':
    case 'fatto':
      return 'valutare';
    default:
      return 'prompt';
  }
}

// Un pezzo è un piccolo spazio di lavoro a passi: Foto, Prompt, Generare, Valutare (e Scene per l'abbigliamento).
export default function PieceWorkspace({ draft, onBack, onUpdate, onRemoved, onStarted }: Props) {
  const [step, setStep] = useState<Step>(() => firstStep(draft.progress));
  const [progress, setProgress] = useState<Progress | undefined>(draft.progress);
  const [category, setCategory] = useState('');
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const facts = draft.facts || {};
  const done = draft.status === 'scheda_pronta';
  const running = draft.status === 'in_corso';
  const cover = draft.main || draft.photos[0];

  async function call(path: string, init: RequestInit) {
    const res = await fetch(`${API_URL}/bozze/${draft.id}${path}`, init);
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
    return data;
  }

  const keep = (next: Draft) => onUpdate({ ...next, progress: next.progress ?? progress });

  async function saveChoices(patch: Partial<Pick<Draft, 'note' | 'main' | 'detail'>>) {
    try {
      keep(await call('', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(patch) }));
    } catch (err) {
      setError(`Non sono riuscito a salvare la modifica: ${err instanceof Error ? err.message : err}`);
    }
  }

  async function removePhoto(name: string) {
    try {
      keep(await call(`/foto/${encodeURIComponent(name)}`, { method: 'DELETE' }));
    } catch (err) {
      setError(`Non sono riuscito a togliere la foto: ${err instanceof Error ? err.message : err}`);
    }
  }

  async function addPhotos(files: FileList | null) {
    if (!files || files.length === 0) return;
    const form = new FormData();
    Array.from(files).forEach((file) => form.append('foto', file));
    try {
      keep(await call('/foto', { method: 'POST', body: form }));
    } catch (err) {
      setError(`Non sono riuscito ad aggiungere la foto: ${err instanceof Error ? err.message : err}`);
    }
  }

  async function createScheda() {
    setBusy(true);
    setError('');
    try {
      const settings = loadSettings();
      const data = await call('/crea', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text_model: settings.textModel, image_model: settings.imageModel }),
      });
      onStarted(data.job_id);
    } catch (err) {
      setError(`Non riesco a creare la scheda: ${err instanceof Error ? err.message : err}`);
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    setBusy(true);
    try {
      await call('', { method: 'DELETE' });
      onRemoved(draft.id);
    } catch (err) {
      setError(`Non sono riuscito a eliminare: ${err instanceof Error ? err.message : err}`);
      setBusy(false);
    }
  }

  const steps: { key: Step; label: string; done: boolean }[] = [
    { key: 'foto', label: 'Foto', done: true },
    { key: 'prompt', label: 'Prompt', done: !!progress?.done.prompt },
    { key: 'generare', label: 'Generare', done: !!progress?.done.generare },
    { key: 'valutare', label: 'Valutare', done: !!progress?.done.valutare },
  ];
  if (category === 'abbigliamento') steps.push({ key: 'scene', label: 'Scene', done: false });

  return (
    <section className="workspace" aria-label="Pezzo in lavorazione">
      <header className="ws-top">
        <button type="button" className="ws-back" onClick={onBack} aria-label="Torna all’elenco dei pezzi">
          ‹
        </button>
        <div className="ws-title">
          <h2>{draft.note || 'Pezzo senza nota'}</h2>
          <p>
            {facts.prezzo !== undefined && `${facts.prezzo} € · `}
            {facts.misura && `mis. ${facts.misura} · `}
            {formatDraftTime(draft.created_at)}
            {running && ' · scheda in preparazione'}
            {done && ' · scheda pronta'}
          </p>
        </div>
        <details className="ws-more">
          <summary aria-label="Altre azioni">⋯</summary>
          <div className="ws-more-menu">
            <a href={`${API_URL}/bozze/${draft.id}/scarica`} download>
              Scarica le foto originali
            </a>
            {done && draft.run_id ? (
              <Link href={`/pezzi/${encodeURIComponent(draft.run_id)}`}>Apri la scheda</Link>
            ) : (
              <button type="button" onClick={createScheda} disabled={busy || running}>
                {running ? 'Scheda in preparazione…' : 'Crea la scheda (flusso automatico)'}
              </button>
            )}
            <button type="button" className="danger" onClick={() => setConfirming(true)}>
              Elimina il pezzo
            </button>
          </div>
        </details>
      </header>

      {confirming && (
        <div className="piece-confirm" role="group" aria-label="Conferma eliminazione">
          <p>Tolgo questo pezzo salvato? Finisce nel cestino sul PC.</p>
          <div>
            <button type="button" className="btn-mission" disabled={busy} onClick={remove}>
              Sì, elimina
            </button>
            <button type="button" className="btn-secondary" onClick={() => setConfirming(false)}>
              Annulla
            </button>
          </div>
        </div>
      )}
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}
      {draft.error && !running && !done && <p className="draft-error">{draft.error}</p>}

      <nav className="stepper" aria-label="Passi">
        {steps.map((s) => (
          <button key={s.key} type="button" className={`stepper-item ${s.done ? 'is-done' : ''}`} aria-current={step === s.key ? 'step' : undefined} onClick={() => setStep(s.key)}>
            <i aria-hidden="true" />
            <span>{s.done && step !== s.key ? `${s.label} ✓` : s.label}</span>
          </button>
        ))}
      </nav>

      {step !== 'foto' && cover && (
        <button type="button" className="ws-photos" onClick={() => setStep('foto')} aria-label="Vedi e cambia le foto del pezzo">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <figure>
            <img src={photoUrl(draft, cover, 240)} alt="Foto principale" />
            <figcaption>Principale</figcaption>
          </figure>
          {draft.detail && draft.detail !== cover && (
            <figure>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={photoUrl(draft, draft.detail, 240)} alt="Foto dettaglio" />
              <figcaption>Dettaglio</figcaption>
            </figure>
          )}
          <span className="ws-photos-note">
            Il prompt parte da {draft.detail && draft.detail !== cover ? 'queste foto' : 'questa foto'}.<br />
            <b>Cambia</b>
          </span>
        </button>
      )}

      {step === 'foto' ? (
        <>
          <div className="step-body">
            <div className="draft-photos">
              {draft.photos.map((name) => (
                <div className="draft-photo" key={name}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={photoUrl(draft, name)} alt="" loading="lazy" />
                  <div className="draft-photo-actions">
                    <button type="button" className="chip-btn" aria-pressed={draft.main === name} onClick={() => saveChoices({ main: name })}>
                      Principale
                    </button>
                    <button
                      type="button"
                      className="chip-btn"
                      aria-pressed={draft.detail === name}
                      disabled={draft.main === name}
                      onClick={() => saveChoices({ detail: draft.detail === name ? '' : name })}
                    >
                      Dettaglio
                    </button>
                    <a className="chip-btn" href={`${API_URL}/bozze/${draft.id}/foto/${encodeURIComponent(name)}?scarica=1`} download>
                      Scarica
                    </a>
                    {draft.photos.length > 1 && (
                      <button type="button" className="chip-btn" onClick={() => removePhoto(name)} aria-label="Togli questa foto">
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
                  <input
                    type="file"
                    accept="image/*,.heic,.heif"
                    multiple
                    onChange={(e) => {
                      void addPhotos(e.target.files);
                      e.target.value = '';
                    }}
                  />
                </label>
              )}
            </div>
            <label className="field-label" htmlFor={`note-${draft.id}`}>
              Nota
            </label>
            <textarea
              id={`note-${draft.id}`}
              className="brief-area"
              rows={3}
              defaultValue={draft.note}
              onBlur={(e) => {
                if (e.target.value.trim() !== draft.note) void saveChoices({ note: e.target.value });
              }}
              placeholder="Prezzo, pietra, misura, colore"
            />
            <p className="step-hint">Lo Studio usa la foto «Principale» e, se c&apos;è, quella «Dettaglio»; la nota guida il prompt.</p>
          </div>
          <div className="action-bar">
            <button type="button" className="btn-mission" onClick={() => setStep('prompt')}>
              Continua con il prompt
            </button>
          </div>
        </>
      ) : (
        <PromptLab
          draftId={draft.id}
          mainPhoto={cover || ''}
          step={step}
          onStep={(next) => setStep(next)}
          onProgress={(p, cat) => {
            setProgress(p);
            if (cat) setCategory(cat);
            onUpdate({ ...draft, progress: p });
          }}
          onDone={onBack}
        />
      )}
    </section>
  );
}
