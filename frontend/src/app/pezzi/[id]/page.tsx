'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
import MosaicTiles, { stepTiles } from '@/components/MosaicTiles';
import PieceView from '@/components/PieceView';
import { API_URL } from '@/lib/apiUrl';
import type { PieceSummary } from '@/lib/pieces';

export default function PiecePage() {
  const params = useParams<{ id: string }>();
  const runId = decodeURIComponent(String(params?.id || ''));
  const [results, setResults] = useState<Record<string, string> | null>(null);
  const [summary, setSummary] = useState<PieceSummary | null>(null);
  const [error, setError] = useState('');

  const loadSummary = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/pieces/${encodeURIComponent(runId)}`, { cache: 'no-store' });
      if (res.ok) setSummary(await res.json());
    } catch {
      /* le tessere restano come sono: il resto della pagina funziona lo stesso */
    }
  }, [runId]);

  useEffect(() => {
    if (!runId) return;
    let alive = true;
    fetch(`${API_URL}/missions/${encodeURIComponent(runId)}`, { cache: 'no-store' })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(res.status === 404 ? 'not-found' : data?.error || `HTTP ${res.status}`);
        return data;
      })
      .then((data) => alive && setResults(data.results || {}))
      .catch((err) =>
        alive &&
        setError(
          err?.message === 'not-found'
            ? 'Questo pezzo non esiste più.'
            : 'Non riesco ad aprire il pezzo. Controlla che lo Studio sul PC sia acceso e riprova.',
        ),
      );
    void loadSummary();
    return () => {
      alive = false;
    };
  }, [runId, loadSummary]);

  let title = summary?.title || '';
  if (!title && results) {
    try {
      title = JSON.parse(results.publish_pack_json || '{}').product_name || '';
    } catch {
      title = '';
    }
  }
  const cover = summary?.cover || (results ? results.image_site_3 || results.image_site_1 || '' : '');

  return (
    <div className="page">
      <Link href="/pezzi" className="back-link">‹ Pezzi</Link>
      {error && (
        <div className="notice error" role="alert">
          {error} <Link href="/pezzi">Torna ai pezzi</Link>
        </div>
      )}
      {!error && !results && <p className="page-lead">Apro il pezzo...</p>}
      {results && (
        <>
          <header className="piece-head">
            {cover && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={`${API_URL}/files/${cover}`} alt={title || 'Foto del pezzo'} className="piece-cover" />
            )}
            <h1>{title || 'Pezzo senza nome'}</h1>
            {summary && <MosaicTiles items={stepTiles(summary.steps)} palette={summary.palette} large />}
          </header>
          <PieceView results={results} apiUrl={API_URL} runId={runId} summary={summary} onChanged={loadSummary} />
        </>
      )}
    </div>
  );
}
