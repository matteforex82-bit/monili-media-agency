'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { API_URL } from '@/lib/apiUrl';

interface Brief {
  product: string;
  brief: string;
  target_seconds: number;
  scheda_run_id: string;
}

interface Draft extends Brief {
  id: string;
  version: number;
}

interface Props {
  product?: string;
  pieceId: string;
  initialBrief: string;
}

export default function ReelBlenderBrief({ product, pieceId, initialBrief }: Props) {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [selected, setSelected] = useState('');
  const [fields, setFields] = useState<Brief | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  const values = fields ?? { product: product ?? '', brief: initialBrief, target_seconds: 12, scheda_run_id: pieceId };

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_URL}/reel-blender/drafts`, { cache: 'no-store', signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error();
        const data: { items: Draft[] } = await res.json();
        if (!controller.signal.aborted) {
          setDrafts((items) => [...items, ...data.items.filter((draft) => !items.some((item) => item.id === draft.id))]);
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) setError('Non riesco a caricare le bozze Reel Blender.');
      });
    return () => controller.abort();
  }, []);

  function edit(patch: Partial<Brief>) {
    setFields({ ...values, ...patch });
    setSaved(false);
  }

  function selectDraft(id: string) {
    const draft = drafts.find((entry) => entry.id === id);
    setSelected(id);
    setFields(draft ? {
      product: draft.product,
      brief: draft.brief,
      target_seconds: draft.target_seconds,
      scheda_run_id: draft.scheda_run_id,
    } : null);
    setSaved(false);
    setError('');
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSaved(false);
    if (!values.product.trim()) {
      setError('Scrivi il nome del prodotto.');
      return;
    }
    setBusy(true);
    try {
      const url = `${API_URL}/reel-blender/drafts${selected ? '/' + encodeURIComponent(selected) : ''}`;
      const response = await fetch(url, {
        method: selected ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || 'Non riesco a salvare il brief.');
      }
      const draft: Draft = await response.json();
      setDrafts((items) => [draft, ...items.filter((item) => item.id !== draft.id)]);
      setSelected(draft.id);
      setFields({
        product: draft.product,
        brief: draft.brief,
        target_seconds: draft.target_seconds,
        scheda_run_id: draft.scheda_run_id,
      });
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco a salvare il brief.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card rs-card" aria-labelledby="reel-blender-title">
      <h2 className="rs-h1" id="reel-blender-title">Reel Blender</h2>
      <p className="rs-muted">Salva il brief per progettare la scena e le riprese in Blender. Puoi iniziare anche senza foto.</p>
      {drafts.length > 0 && (
        <label className="rs-field">
          <span className="rs-field-label">Bozze Reel Blender</span>
          <select className="rs-input" value={selected} disabled={busy} onChange={(event) => selectDraft(event.target.value)}>
            <option value="">Nuovo brief</option>
            {drafts.map((draft) => <option key={draft.id} value={draft.id}>{draft.product}</option>)}
          </select>
        </label>
      )}
      {values.scheda_run_id && (
        <p className="rs-muted">Collegato a una Scheda pezzo.{' '}
          <button className="btn-secondary rs-small-btn" type="button" disabled={busy} onClick={() => edit({ scheda_run_id: '' })}>Scollega</button>
        </p>
      )}
      <form className="rs-card" onSubmit={save}>
        <div className="rs-grid-2">
          <label className="rs-field">
            <span className="rs-field-label">Prodotto</span>
            <input className="rs-input" value={values.product} onChange={(event) => edit({ product: event.target.value })} maxLength={120} required disabled={busy} placeholder="Es. Giacca ricamata" />
          </label>
          <label className="rs-field">
            <span className="rs-field-label">Durata del Reel (secondi)</span>
            <input className="rs-input" type="number" min={10} max={20} value={Number.isFinite(values.target_seconds) ? values.target_seconds : ''} onChange={(event) => edit({ target_seconds: event.target.valueAsNumber })} required disabled={busy} />
          </label>
        </div>
        <label className="rs-field">
          <span className="rs-field-label">Brief</span>
          <textarea className="rs-input" value={values.brief} onChange={(event) => edit({ brief: event.target.value })} maxLength={1500} rows={4} disabled={busy} placeholder="Cosa vuoi mostrare? Es. Il ricamo e la vestibilità, con la modella già in posa." />
        </label>
        {error && <p className="rs-error" role="alert">{error}</p>}
        {saved && <p className="rs-muted" role="status">Brief salvato. Puoi riaprirlo da Bozze Reel Blender.</p>}
        <button className="btn-mission rs-cta" type="submit" disabled={busy}>{busy ? 'Salvataggio…' : 'Salva brief'}</button>
      </form>
    </section>
  );
}
