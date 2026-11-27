'use client';

import { useEffect, useRef, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';

interface ShotPrompts {
  shot: number;
  title: string;
  product_reference: number | null;
  photo_en: string;
  video_en: string;
}

function Prompt({ label, text }: { label: string; text: string }) {
  const input = useRef<HTMLTextAreaElement>(null);
  const [notice, setNotice] = useState('');

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setNotice('Copiato');
    } catch {
      input.current?.focus();
      input.current?.select();
      setNotice('Testo selezionato. Premi Ctrl+C oppure usa Copia.');
    }
  }

  return (
    <div>
      <label className="rs-field">
        <span className="rs-field-label">{label}</span>
        <textarea ref={input} className="rs-input" readOnly rows={3} value={text} />
      </label>
      <button type="button" className="btn-secondary rs-small-btn" onClick={() => void copy()}>Copia {label.toLowerCase()}</button>
      {notice && <span className="rs-muted" role="status"> {notice}</span>}
    </div>
  );
}

export default function ReelSeedancePrompts({ draftId, revision }: { draftId: string; revision?: string }) {
  const [items, setItems] = useState<ShotPrompts[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setError(false);
    setItems([]);
    fetch(`${API_URL}/reel-blender/drafts/${encodeURIComponent(draftId)}/seedance-prompts`, {
      cache: 'no-store', signal: controller.signal,
    }).then(async (response) => {
      if (!response.ok) throw new Error();
      const data = await response.json();
      if (!controller.signal.aborted) setItems(data.items);
    }).catch(() => {
      if (!controller.signal.aborted) setError(true);
    });
    return () => controller.abort();
  }, [draftId, revision]);

  return (
    <details className="rs-details">
      <summary>Prompt per foto e Seedance</summary>
      <p className="rs-muted">Per ogni inquadratura, prepara il primo fotogramma e confrontalo con il prodotto reale. Usa poi quell’immagine e la clip Blender nella modalità Seedance con riferimenti.</p>
      {error && <p role="alert" className="rs-error">Non riesco a leggere i prompt. Riapri la bozza e riprova.</p>}
      {items.map((shot) => (
        <details className="rs-card" key={shot.shot}>
          <summary>{shot.shot} · {shot.title}</summary>
          <p className="rs-muted">{shot.product_reference ? `Foto prodotto consigliata: ${shot.product_reference}.` : 'Prepara una foto reale del pezzo come riferimento.'}</p>
          <div className="rs-grid-2">
            <Prompt label="Prompt foto" text={shot.photo_en} />
            <Prompt label="Prompt video" text={shot.video_en} />
          </div>
        </details>
      ))}
    </details>
  );
}
