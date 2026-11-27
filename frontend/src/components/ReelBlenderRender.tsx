'use client';

import { useEffect, useState, type FormEvent } from 'react';

interface RenderState {
  id?: string;
  status: 'idle' | 'queued' | 'rendering' | 'packing' | 'ready' | 'error';
  frame?: number;
  frames?: number;
  shots?: number;
  error?: string;
  review_available?: boolean;
}

const inProgress = (value?: RenderState) => value?.status === 'queued' || value?.status === 'rendering' || value?.status === 'packing';

interface Props {
  base: string;
  disabled: boolean;
  shotNames: string[];
  pilotShot?: number;
  onReview: (draft: unknown, previewId: string) => void;
}

export default function ReelBlenderRender({ base, disabled, shotNames, pilotShot, onReview }: Props) {
  const [render, setRender] = useState<RenderState>();
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');
  const [openingReview, setOpeningReview] = useState(false);
  const [chosenShot, setChosenShot] = useState(pilotShot === undefined ? '' : String(pilotShot));
  const loading = render === undefined;
  const running = inProgress(render);

  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    async function refresh() {
      try {
        const response = await fetch(base, { cache: 'no-store', signal: controller.signal });
        if (!response.ok) throw new Error();
        const data: RenderState = await response.json();
        if (controller.signal.aborted) return;
        setRender(data);
        setError('');
        if (inProgress(data)) timer = setTimeout(refresh, 2000);
      } catch {
        if (!controller.signal.aborted) {
          setError('Non riesco a leggere lo stato del render. Riprovo…');
          timer = setTimeout(refresh, 4000);
        }
      }
    }
    if (loading || running) void refresh();
    return () => {
      controller.abort();
      if (timer) clearTimeout(timer);
    };
  }, [base, loading, running]);

  async function start() {
    if (starting || running || openingReview || disabled) return;
    setStarting(true);
    setError('');
    try {
      const response = await fetch(base, { method: 'POST' });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Non riesco ad avviare il render.');
      setRender(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco ad avviare il render.');
    } finally {
      setStarting(false);
    }
  }

  const fileBase = render?.id ? `${base}/${encodeURIComponent(render.id)}` : '';

  async function reviewShot(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (disabled || starting || openingReview || !fileBase || chosenShot === '') return;
    setOpeningReview(true);
    setError('');
    try {
      const response = await fetch(`${fileBase}/review`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shot_index: Number(chosenShot) }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Non riesco ad aprire la ripresa.');
      onReview(data.draft, data.preview_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco ad aprire la ripresa.');
    } finally {
      setOpeningReview(false);
    }
  }

  return (
    <section className="rs-card" aria-labelledby="blender-render-heading">
      <h4 className="rs-h1" id="blender-render-heading">Render e kit Seedance</h4>
      <p className="rs-muted">Salva eventuali modifiche in Blender, poi avvia il render della scena. Puoi continuare a preparare le foto mentre lavora.</p>
      <button className="btn-mission" type="button" disabled={disabled || starting || running || openingReview || !render}
        onClick={() => void start()}>
        {render?.status === 'ready' ? 'Rifai il render' : 'Renderizza e prepara il kit'}
      </button>
      {starting && <p role="status">Avvio del render…</p>}
      {running && (
        <p role="status" className="rs-muted">
          {render?.status === 'packing' ? 'Preparazione del video con musica e delle clip per Seedance…' :
            render?.status === 'queued' ? 'Render in avvio…' :
              render?.frame ? `Blender sta renderizzando · fotogramma ${render.frame} di ${render.frames}` : 'Blender sta renderizzando…'}
        </p>
      )}
      {error && <p role="alert" className="rs-error">{error}</p>}
      {render?.status === 'error' && <p role="alert" className="rs-error">{render.error}</p>}
      {render?.status === 'ready' && fileBase && (
        <div className="rs-card">
          <div className="rs-video-wrap" style={{ maxWidth: 280 }}>
            <video key={fileBase} src={fileBase + '/video'} aria-label="Render Blender con musica"
              crossOrigin="use-credentials" controls playsInline preload="metadata" />
          </div>
          <div className="rs-actions">
            <a className="btn-secondary" href={fileBase + '/video?download=true'}>Scarica render con musica</a>
            <a className="btn-secondary" href={fileBase + '/kit'}>Scarica kit Seedance completo</a>
          </div>
          {render.review_available && shotNames.length > 0 && (
            <form onSubmit={(event) => void reviewShot(event)}>
              <label className="rs-field">
                <span className="rs-field-label">Ripresa da provare in Seedance</span>
                <select className="rs-input" value={chosenShot} required disabled={disabled || starting || openingReview}
                  onChange={(event) => setChosenShot(event.target.value)}>
                  <option value="">Scegli l’inquadratura</option>
                  {shotNames.map((name, index) => (
                    <option key={index} value={index}>{index + 1} · {name}{index === pilotShot ? ' (consigliata)' : ''}</option>
                  ))}
                </select>
              </label>
              <button className="btn-mission" type="submit" disabled={disabled || starting || openingReview || chosenShot === ''}>
                {openingReview ? 'Apertura della ripresa…' : 'Rivedi la ripresa'}
              </button>
            </form>
          )}
          <p className="rs-muted">Nel kit completo trovi {render.shots} clip mute, fotogrammi guida, prompt, foto e tempi di montaggio.</p>
          {!render.review_available && <p className="rs-muted">Per rivedere una ripresa direttamente nello Studio, aggiorna la regia e rifai il render.</p>}
        </div>
      )}
    </section>
  );
}
