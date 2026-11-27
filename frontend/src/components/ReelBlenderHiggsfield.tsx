'use client';

import { useRef, useState, type FormEvent } from 'react';

export interface HiggsfieldResult {
  id: string;
  filename: string;
  duration_ms: number;
}

interface Props {
  base: string;
  referenceUrl: string;
  shotNames: string[];
  shotIndex?: number;
  results: HiggsfieldResult[];
  disabled: boolean;
  onUpdate: (draft: unknown) => void;
}

export default function ReelBlenderHiggsfield({ base, referenceUrl, shotNames, shotIndex, results, disabled, onUpdate }: Props) {
  const [pickedShot, setPickedShot] = useState('');
  const [pickedResult, setPickedResult] = useState('');
  const [downloaded, setDownloaded] = useState(false);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const reference = useRef<HTMLVideoElement>(null);
  const generated = useRef<HTMLVideoElement>(null);
  const selected = shotIndex === undefined ? pickedShot : String(shotIndex);
  const result = results.find((item) => item.id === pickedResult) ?? results[0];
  const locked = disabled || !!busy;

  async function run(message: string, work: () => Promise<void>) {
    if (locked || selected === '') return;
    setError('');
    setBusy(message);
    try {
      await work();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Operazione non riuscita.');
    } finally {
      setBusy('');
    }
  }

  async function post(path: string, body: BodyInit, headers?: HeadersInit) {
    const response = await fetch(base + path, { method: 'POST', body, headers });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || 'Operazione non riuscita.');
    }
    return response;
  }

  async function download() {
    await run('Preparazione dei file…', async () => {
      const response = await post('/package', JSON.stringify({ shot_index: Number(selected) }), {
        'Content-Type': 'application/json',
      });
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement('a');
      link.href = url;
      link.download = `monili-higgsfield-shot-${String(Number(selected) + 1).padStart(2, '0')}.zip`;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setDownloaded(true);
    });
  }

  function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    data.set('shot_index', selected);
    void run('Caricamento del risultato…', async () => {
      const response = await post('/results', data);
      onUpdate(await response.json());
      setPickedResult('');
      form.reset();
    });
  }

  function compare(position: number) {
    for (const player of [reference.current, generated.current]) {
      if (!player || !Number.isFinite(player.duration)) continue;
      player.pause();
      player.currentTime = position * player.duration;
    }
  }

  const uploadForm = (primary = false) => (
    <form className="rb-stack" onSubmit={upload}>
      <label className="rs-field rb-field">
        <span>Risultato Seedance (MP4)</span>
        <input type="file" name="video" className="rs-input" accept=".mp4,video/mp4" required disabled={locked || selected === ''} />
      </label>
      <div className="rb-actions">
        <button type="submit" className={primary ? 'btn-mission' : 'btn-secondary'} disabled={locked || selected === ''}>
          Carica risultato
        </button>
      </div>
    </form>
  );

  return (
    <div className="rb-stack">
      {shotIndex === undefined && (
        <label className="rs-field rb-field">
          <span>Inquadratura di questa clip</span>
          <select className="rs-input" value={pickedShot} onChange={(event) => setPickedShot(event.target.value)} disabled={locked}>
            <option value="">Abbina l’inquadratura</option>
            {shotNames.map((name, index) => <option key={index} value={index}>{index + 1} · {name}</option>)}
          </select>
        </label>
      )}
      {busy && <p className="rb-muted" role="status">{busy}</p>}
      {error && <p className="rs-error" role="alert">{error}</p>}
      {result ? (
        <div className="rb-stack">
          <h4>Confronto della ripresa</h4>
          {results.length > 1 && (
            <label className="rs-field rb-field">
              <span>Risultato da confrontare</span>
              <select className="rs-input" disabled={locked} value={result.id} onChange={(event) => setPickedResult(event.target.value)}>
                {results.map((item) => <option key={item.id} value={item.id}>{item.filename}</option>)}
              </select>
            </label>
          )}
          <div className="rb-comparison">
            <figure>
              <figcaption>Blender</figcaption>
              <video ref={reference} src={referenceUrl} aria-label="Riferimento Blender"
                crossOrigin="use-credentials" controls playsInline muted preload="metadata" />
            </figure>
            <figure>
              <figcaption>Seedance</figcaption>
              <video key={result.id} ref={generated} src={`${base}/results/${encodeURIComponent(result.id)}`}
                aria-label="Risultato Seedance" crossOrigin="use-credentials" controls playsInline muted preload="metadata" />
            </figure>
          </div>
          <div className="rb-actions">
            <button type="button" className="btn-secondary" onClick={() => compare(0)}>Inizio</button>
            <button type="button" className="btn-secondary" onClick={() => compare(0.5)}>Metà</button>
            <button type="button" className="btn-secondary" onClick={() => compare(0.95)}>Finale</button>
          </div>
          <p className="rb-muted">Confronta colore, dettagli del pezzo, posa e movimento.</p>
          <details className="rb-details">
            <summary>Carica un’altra versione</summary>
            {uploadForm()}
          </details>
        </div>
      ) : downloaded ? (
        <>
          <p className="rb-muted">Quando Seedance ha finito, carica qui la ripresa per confrontarla con Blender.</p>
          {uploadForm(true)}
          <button type="button" className="rb-text-button" disabled={locked || selected === ''} onClick={() => void download()}>Scarica di nuovo il kit</button>
        </>
      ) : (
        <>
          <p className="rb-muted">Il kit contiene la clip muta, il fotogramma guida, le foto e i prompt per la prova in Higgsfield.</p>
          <div className="rb-actions">
            <button type="button" className="btn-mission" disabled={locked || selected === ''} onClick={() => void download()}>
              Scarica il kit Seedance
            </button>
          </div>
          <details className="rb-details">
            <summary>Ho già il risultato</summary>
            {uploadForm()}
          </details>
        </>
      )}
    </div>
  );
}
