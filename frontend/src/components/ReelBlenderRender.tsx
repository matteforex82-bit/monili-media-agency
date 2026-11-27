'use client';

import { useEffect, useState } from 'react';
import { Clapperboard, Video } from 'lucide-react';

interface RenderState {
  id?: string;
  status: 'idle' | 'queued' | 'rendering' | 'packing' | 'ready' | 'error';
  frame?: number;
  frames?: number;
  shots?: number;
  error?: string;
  review_available?: boolean;
}

function inProgress(value?: RenderState) {
  return value?.status === 'queued' || value?.status === 'rendering' || value?.status === 'packing';
}

export function useReelBlenderRender(base: string) {
  const [entry, setEntry] = useState<{ base: string; value: RenderState }>();
  const [problem, setProblem] = useState<{ base: string; text: string }>();
  const state = entry?.base === base ? entry.value : undefined;
  const error = problem?.base === base ? problem.text : '';
  const polling = !!base && (!state || inProgress(state));

  useEffect(() => {
    if (!polling) return;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout>;
    async function refresh() {
      try {
        const response = await fetch(base, { cache: 'no-store', signal: controller.signal });
        if (!response.ok) throw new Error();
        const value: RenderState = await response.json();
        if (controller.signal.aborted) return;
        setEntry({ base, value });
        setProblem(undefined);
        if (inProgress(value)) timer = setTimeout(refresh, 2000);
      } catch {
        if (controller.signal.aborted) return;
        setProblem({ base, text: 'Lo Studio non riesce a leggere il render. Riprova tra poco.' });
        timer = setTimeout(refresh, 4000);
      }
    }
    void refresh();
    return () => { controller.abort(); clearTimeout(timer); };
  }, [base, polling]);

  return {
    state, error, running: inProgress(state),
    fileBase: state?.id && state.status === 'ready' ? `${base}/${encodeURIComponent(state.id)}` : '',
    setState: (value: RenderState) => setEntry({ base, value }),
  };
}

export type RenderJob = ReturnType<typeof useReelBlenderRender>;

export default function ReelBlenderRender({ base, job, disabled, onContinue }: {
  base: string; job: RenderJob; disabled: boolean; onContinue: () => void;
}) {
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');
  const { state, fileBase, running } = job;

  async function start() {
    if (starting || running || disabled) return;
    setStarting(true);
    setError('');
    try {
      const response = await fetch(base, { method: 'POST' });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Non riesco ad avviare il render. Riprova.');
      job.setState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco ad avviare il render. Riprova.');
    } finally {
      setStarting(false);
    }
  }

  const progress = state?.status === 'packing' ? 'Sto preparando il video e le clip' :
    state?.frame ? `Fotogramma ${state.frame} di ${state.frames ?? '…'}` :
      'Blender sta preparando il video';

  return (
    <div className="rb-stack">
      {fileBase ? (
        <>
          <div className="rb-media rb-media-master">
            <video key={fileBase} src={fileBase + '/video'} aria-label="Render Blender con musica"
              crossOrigin="use-credentials" controls playsInline preload="metadata" />
            <div>
              <h3>Montaggio Blender</h3>
              <p className="rb-muted">Rivedi il video con la musica, poi passa alla prova di una ripresa.</p>
              <button className="btn-mission" type="button" disabled={disabled || starting} onClick={onContinue}>
                Vai alla prova Seedance
              </button>
            </div>
          </div>
          <details className="rb-details">
            <summary>File del render</summary>
            <div className="rb-actions">
              <a className="btn-secondary" href={fileBase + '/video?download=true'}>Scarica video con musica</a>
              <a className="btn-secondary" href={fileBase + '/kit'}>Scarica kit completo</a>
              <button className="btn-secondary" type="button" disabled={disabled || starting} onClick={() => void start()}>
                {starting ? 'Avvio del render…' : 'Rifai il render'}
              </button>
            </div>
          </details>
        </>
      ) : running || starting ? (
        <div className="rb-progress" role="status">
          <Clapperboard aria-hidden="true" size={20} strokeWidth={1.5} />
          <div><strong>Render in corso</strong><p>{progress}</p></div>
          {state?.frame && state.frames ? <progress value={state.frame} max={state.frames} aria-label="Avanzamento del render" /> : null}
        </div>
      ) : (
        <>
          <p className="rb-muted">Salva le modifiche in Blender, poi renderizza il montaggio e le singole riprese.</p>
          <div className="rb-actions">
            <button className="btn-mission" type="button" disabled={disabled || !state} onClick={() => void start()}>
              {state?.status === 'error' ? 'Riprova il render' : 'Renderizza in Blender'}
            </button>
          </div>
        </>
      )}
      {!state && !job.error && <p className="rb-muted" role="status">Controllo lo stato del render…</p>}
      {(error || job.error || state?.error) && (
        <p role="alert" className="rs-error">{error || job.error || state?.error}</p>
      )}
    </div>
  );
}

export function ReelBlenderPilot({ job, shotNames, pilotShot, disabled, onReview }: {
  job: RenderJob; shotNames: string[]; pilotShot?: number; disabled: boolean;
  onReview: (draft: unknown, previewId: string) => void;
}) {
  const suggested = pilotShot !== undefined && !!shotNames[pilotShot] ? pilotShot : undefined;
  const [choice, setChoice] = useState(suggested === undefined ? '' : String(suggested));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function reviewShot() {
    if (disabled || busy || choice === '' || !job.fileBase) return;
    setBusy(true);
    setError('');
    try {
      const response = await fetch(`${job.fileBase}/review`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shot_index: Number(choice) }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Non riesco ad aprire la ripresa. Riprova.');
      onReview(data.draft, data.preview_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco ad aprire la ripresa. Riprova.');
    } finally {
      setBusy(false);
    }
  }

  if (!job.fileBase || !shotNames.length) return null;
  if (!job.state?.review_available) {
    return <p className="rb-muted">Rifai il render dalla scena aggiornata o carica una ripresa da un file.</p>;
  }

  const shotPicker = (
    <label className="rs-field rb-field">
      <span>Inquadratura da rivedere</span>
      <select className="rs-input" value={choice} disabled={disabled || busy} onChange={(event) => setChoice(event.target.value)}>
        <option value="">Scegli una ripresa</option>
        {shotNames.map((name, index) => (
          <option key={index} value={index}>{index + 1} · {name}{index === suggested ? ' (consigliata)' : ''}</option>
        ))}
      </select>
    </label>
  );

  return (
    <div className="rb-stack">
      {choice !== '' && (
        <div className="rb-shot">
          <Video aria-hidden="true" size={20} strokeWidth={1.5} />
          <div>
            <p>{Number(choice) === suggested ? 'Ripresa consigliata' : 'Ripresa scelta'} · {Number(choice) + 1} di {shotNames.length}</p>
            <h3>{shotNames[Number(choice)]}</h3>
          </div>
        </div>
      )}
      {suggested === undefined && shotPicker}
      <div className="rb-actions">
        <button className="btn-mission" type="button" disabled={disabled || busy || choice === ''} onClick={() => void reviewShot()}>
          {busy ? 'Apro la ripresa…' : 'Rivedi la ripresa'}
        </button>
      </div>
      {suggested !== undefined && (
        <details className="rb-details rb-inline-details">
          <summary>Scegli un’altra ripresa</summary>
          {shotPicker}
        </details>
      )}
      {error && <p role="alert" className="rs-error">{error}</p>}
    </div>
  );
}
