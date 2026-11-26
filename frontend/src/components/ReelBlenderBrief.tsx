'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { API_URL } from '@/lib/apiUrl';
import FileDropzone from '@/components/FileDropzone';
import ReelBlenderReview, { type BlenderPreview } from '@/components/ReelBlenderReview';

interface Brief {
  product: string;
  brief: string;
  target_seconds: number;
  scheda_run_id: string;
}

interface Concept {
  title: string;
  hook: string;
  sequence: string;
  risk: string;
}

interface Package {
  storyboard: string;
  assets: string;
  audio: string;
  blender: string;
  higgsfield: string;
}

interface ReferencePhoto {
  id: string;
  filename: string;
}

const MAX_PHOTOS = 3;

interface Draft extends Brief {
  id: string;
  version: number;
  updated_at: string;
  photos?: ReferencePhoto[];
  concepts?: Concept[];
  recommended?: number;
  recommendation_reason?: string;
  selected?: number | null;
  package?: Package | null;
  package_revision?: string;
  previews?: BlenderPreview[];
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
  const [newPhotos, setNewPhotos] = useState<File[]>([]);
  const [removedPhotos, setRemovedPhotos] = useState<string[]>([]);
  const active = drafts.find((draft) => draft.id === selected);
  const values = fields ?? { product: product ?? '', brief: initialBrief, target_seconds: 12, scheda_run_id: pieceId };

  const keptPhotos = (active?.photos ?? []).filter((photo) => !removedPhotos.includes(photo.id));
  const isSaved = active && !newPhotos.length && !removedPhotos.length && values.product === active.product && values.brief === active.brief &&
    values.target_seconds === active.target_seconds && values.scheda_run_id === active.scheda_run_id;

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
    setNewPhotos([]);
    setRemovedPhotos([]);
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
      const form = new FormData();
      for (const [key, value] of Object.entries(values)) form.append(key, String(value));
      if (active) {
        form.append('draft_id', active.id);
        form.append('expected_updated_at', active.updated_at);
      }
      for (const photo of keptPhotos) form.append('keep_photo_ids', photo.id);
      for (const photo of newPhotos) form.append('photos', photo);
      const response = await fetch(`${API_URL}/reel-blender/drafts/with-photos`, {
        method: 'POST',
        body: form,
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || 'Non riesco a salvare il brief.');
      }
      const draft: Draft = await response.json();
      setDrafts((items) => [draft, ...items.filter((item) => item.id !== draft.id)]);
      setSelected(draft.id);
      setNewPhotos([]);
      setRemovedPhotos([]);
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

  async function requestPlan(id: string, stage: 'concepts' | 'package', index?: number): Promise<Draft> {
    const response = await fetch(`${API_URL}/reel-blender/drafts/${encodeURIComponent(id)}/${stage}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: index === undefined ? undefined : JSON.stringify({ index }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'La generazione non è riuscita.');
    setDrafts((items) => [data, ...items.filter((item) => item.id !== data.id)]);
    return data;
  }

  async function prepare() {
    if (busy || !isSaved || !active) return;
    setError('');
    setSaved(false);
    setBusy(true);
    try {
      const draft = active.concepts?.length ? active : await requestPlan(active.id, 'concepts');
      const index = draft.recommended;
      if (index === undefined || !draft.concepts?.[index]) throw new Error('Non riesco a trovare la regia consigliata.');
      await requestPlan(draft.id, 'package', index);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'La generazione non è riuscita.');
    } finally {
      setBusy(false);
    }
  }

  async function download(format: 'md' | 'json') {
    if (!active?.package || !isSaved) return;
    setError('');
    try {
      let blob: Blob;
      if (format === 'md') {
        const response = await fetch(`${API_URL}/reel-blender/drafts/${encodeURIComponent(active.id)}/package.md`, { cache: 'no-store' });
        if (!response.ok) throw new Error('Non riesco a scaricare il pacchetto.');
        blob = await response.blob();
      } else {
        blob = new Blob([JSON.stringify(active, null, 2)], { type: 'application/json' });
      }
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `reel-blender-${active.id}.${format}`;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco a scaricare il pacchetto.');
    }
  }

  return (
    <section className="card rs-card" aria-labelledby="reel-blender-title">
      <h2 className="rs-h1" id="reel-blender-title">Reel Blender</h2>
      <p className="rs-muted">Salva il brief. Reel Blender sceglie la regia per il tuo pezzo e prepara la scheda per Claude e Blender.</p>
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
        <fieldset disabled={busy} className="rs-field">
          <legend className="rs-field-label">Foto di riferimento (facoltative)</legend>
          {active && keptPhotos.length > 0 && (
            <div className="file-previews">
              {keptPhotos.map((photo) => (
                <div key={photo.id}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`${API_URL}/reel-blender/drafts/${active.id}/photos/${photo.id}`} alt={photo.filename} />
                  <button type="button" className="btn-secondary rs-small-btn" aria-label={`Togli ${photo.filename}`}
                    onClick={() => { setRemovedPhotos((items) => [...items, photo.id]); setSaved(false); }}>Togli</button>
                </div>
              ))}
            </div>
          )}
          {keptPhotos.length < MAX_PHOTOS && (
            <FileDropzone
              files={newPhotos}
              onFiles={(files) => {
                if (busy) return;
                setNewPhotos(files);
                setSaved(false);
              }}
              accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif"
              max={MAX_PHOTOS - keptPhotos.length}
              kind="photo"
              title="Allega foto"
              hint="Fino a 3 foto JPG, PNG, WebP o HEIC. Ad esempio, frontale, tre quarti e dettaglio."
            />
          )}
          {values.scheda_run_id && !keptPhotos.length && !newPhotos.length && (
            <p className="rs-muted">Se non alleghi foto, lo Studio usa quella della Scheda pezzo, se disponibile.</p>
          )}
        </fieldset>
        {error && <p className="rs-error" role="alert">{error}</p>}
        {saved && <p className="rs-muted" role="status">Brief salvato. Puoi riaprirlo da Bozze Reel Blender.</p>}
        <button className="btn-mission rs-cta" type="submit" disabled={busy}>Salva brief</button>
      </form>
      {busy && <p className="rs-muted" role="status">Operazione in corso…</p>}
      {active && !isSaved && <p className="rs-muted">Salva le modifiche al brief per continuare.</p>}
      {isSaved && !active.package && (
        <button className="btn-mission rs-cta" type="button" disabled={busy} onClick={() => void prepare()}>
          Prepara la regia
        </button>
      )}
      {isSaved && active.package && (
        <div className="rs-card">
          <h3 className="rs-h1">La regia del tuo Reel</h3>
          {active.selected != null && active.concepts?.[active.selected] && (
            <p><strong>{active.concepts[active.selected].title}</strong></p>
          )}
          {active.selected === active.recommended && active.recommendation_reason && (
            <p>{active.recommendation_reason}</p>
          )}
          <p>{active.package.storyboard}</p>
          <div className="rs-actions">
            <button className="btn-mission" type="button" disabled={busy} onClick={() => void download('md')}>Scarica Markdown</button>
            <button className="btn-secondary" type="button" disabled={busy} onClick={() => void download('json')}>Scarica JSON</button>
          </div>
        </div>
      )}
      {isSaved && active.package && (
        <ReelBlenderReview
          key={active.id}
          draftId={active.id}
          revision={active.package_revision}
          previews={active.previews ?? []}
          disabled={busy}
          onUpdate={(value) => {
            const draft = value as Draft;
            setDrafts((items) => [draft, ...items.filter((item) => item.id !== draft.id)]);
          }}
        />
      )}
    </section>
  );
}
