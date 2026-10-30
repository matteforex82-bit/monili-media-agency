'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import MosaicTiles, { stepTiles } from '@/components/MosaicTiles';
import { API_URL } from '@/lib/apiUrl';
import { formatPieceDate, type PieceSummary } from '@/lib/pieces';

export default function PiecesPage() {
  const [pieces, setPieces] = useState<PieceSummary[] | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let alive = true;
    fetch(`${API_URL}/pieces?limit=60`, { cache: 'no-store' })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => alive && setPieces(Array.isArray(data?.items) ? data.items : []))
      .catch(() => alive && setError('Non riesco a leggere i pezzi. Controlla che lo Studio sul PC sia acceso e riprova.'));
    return () => {
      alive = false;
    };
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">Pezzi</h1>
      <p className="page-lead">Ogni pezzo con i passaggi fatti: scheda, sito, Reel, Instagram.</p>

      {error && <div className="notice error" role="alert">{error}</div>}
      {!error && pieces === null && <p className="page-lead">Carico i pezzi...</p>}
      {pieces && pieces.length === 0 && (
        <div className="empty">
          <h2>Nessun pezzo ancora</h2>
          <p>Fotografa il primo: in pochi minuti hai la scheda per il sito.</p>
          <Link href="/" className="btn-mission" style={{ textDecoration: 'none' }}>Fotografa il primo pezzo</Link>
        </div>
      )}
      {pieces && pieces.length > 0 && (
        <ul className="piece-list">
          {pieces.map((piece) => (
            <li key={piece.run_id}>
              <Link href={`/pezzi/${encodeURIComponent(piece.run_id)}`} className="piece-card">
                {piece.cover ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={`${API_URL}/files/${piece.cover}`} alt="" loading="lazy" />
                ) : (
                  <span className="piece-thumb-empty" />
                )}
                <div>
                  <h2>{piece.title || 'Pezzo senza nome'}</h2>
                  <time dateTime={piece.created_at}>{formatPieceDate(piece.created_at)}</time>
                  <MosaicTiles items={stepTiles(piece.steps)} palette={piece.palette} />
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
