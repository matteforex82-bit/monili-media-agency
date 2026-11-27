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

  return (
    <section className="rs-card" aria-labelledby="reel-blender-higgsfield">
      <h4 className="rs-h1" id="reel-blender-higgsfield">Prova una ripresa in Higgsfield</h4>
      {shotIndex === undefined ? (
        <label className="rs-field">
          <span className="rs-field-label">Inquadratura di questa clip</span>
          <select className="rs-input" value={pickedShot} onChange={(event) => setPickedShot(event.target.value)} disabled={locked}>
            <option value="">Abbina l’inquadratura</option>
            {shotNames.map((name, index) => <option key={index} value={index}>{index + 1} · {name}</option>)}
          </select>
        </label>
      ) : <p className="rs-muted">Inquadratura {shotIndex + 1} · {shotNames[shotIndex]}</p>}
      <p className="rs-muted">Lo ZIP contiene la clip muta, le referenze disponibili, un prompt e i controlli per la prova manuale.</p>
      <button type="button" className="btn-mission" disabled={locked || selected === ''} onClick={() => void download()}>
        Scarica pacchetto Higgsfield
      </button>
      <form className="rs-card" onSubmit={upload}>
        <label className="rs-field">
          <span className="rs-field-label">Risultato Higgsfield (MP4)</span>
          <input type="file" name="video" className="rs-input" accept=".mp4,video/mp4" required disabled={locked || selected === ''} />
        </label>
        <button type="submit" className="btn-secondary" disabled={locked || selected === ''}>Carica risultato</button>
      </form>
      {busy && <p className="rs-muted" role="status">{busy}</p>}
      {error && <p className="rs-error" role="alert">{error}</p>}
      {result && (
        <div>
          <h5 className="rs-h1">Confronto della ripresa</h5>
          {results.length > 1 && (
            <label className="rs-field">
              <span className="rs-field-label">Risultato da confrontare</span>
              <select className="rs-input" disabled={locked} value={result.id} onChange={(event) => setPickedResult(event.target.value)}>
                {results.map((item) => <option key={item.id} value={item.id}>{item.filename}</option>)}
              </select>
            </label>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 12, maxWidth: 560 }}>
            <div className="rs-video-wrap">
              <strong>Blender</strong>
              <video ref={reference} src={referenceUrl} aria-label="Riferimento Blender"
                crossOrigin="use-credentials" controls playsInline muted preload="metadata" />
            </div>
            <div className="rs-video-wrap">
              <strong>Higgsfield</strong>
              <video key={result.id} ref={generated} src={`${base}/results/${encodeURIComponent(result.id)}`}
                aria-label="Risultato Higgsfield" crossOrigin="use-credentials" controls playsInline muted preload="metadata" />
            </div>
          </div>
          <div className="rs-actions">
            <button type="button" className="btn-secondary rs-small-btn" onClick={() => compare(0)}>Inizio</button>
            <button type="button" className="btn-secondary rs-small-btn" onClick={() => compare(0.5)}>Metà</button>
            <button type="button" className="btn-secondary rs-small-btn" onClick={() => compare(0.95)}>Finale</button>
          </div>
          <p className="rs-muted">Controlla ricami o pietre, colore e proporzioni sulle foto reali. Poi confronta camera, posa e punto in cui si completa il gesto.</p>
        </div>
      )}
    </section>
  );
}
