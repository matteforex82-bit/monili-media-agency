'use client';

import Link from 'next/link';
import { Trash2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import MosaicTiles, { stepTiles } from '@/components/MosaicTiles';
import { API_URL } from '@/lib/apiUrl';
import { formatPieceDate, nextStep, type PieceSummary } from '@/lib/pieces';

export default function PiecesPage() {
  const [pieces, setPieces] = useState<PieceSummary[] | null>(null);
  const [error, setError] = useState('');
  // The piece waiting for "Sì, elimina", and the one being deleted right now.
  const [confirming, setConfirming] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

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

  // The backend moves the piece to the Studio trash (MoniliStorage\cestino), it does not erase it.
  async function deletePiece(runId: string) {
    setDeleting(runId);
    setError('');
    try {
      const res = await fetch(`${API_URL}/pieces/${encodeURIComponent(runId)}`, { method: 'DELETE' });
      if (!res.ok && res.status !== 404) {
        // se il sito non risponde il pezzo NON è stato eliminato: il motivo arriva dallo Studio
        const body = await res.json().catch(() => null);
        throw new Error(typeof body?.error === 'string' ? body.error : `HTTP ${res.status}`);
      }
      setPieces((list) => (list ? list.filter((piece) => piece.run_id !== runId) : list));
      setConfirming(null);
    } catch (err) {
      const detail = err instanceof Error && !err.message.startsWith('HTTP') && err.message !== 'Failed to fetch' ? ` ${err.message}` : '';
      setError(`Non sono riuscito a eliminare il pezzo.${detail || ' Controlla che lo Studio sul PC sia acceso e riprova.'}`);
    } finally {
      setDeleting(null);
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">Pezzi</h1>
      <p className="page-lead">Il tuo archivio. Ogni pezzo ricorda a che punto è e ti porta al passo che manca: sito, video, pubblicazione.</p>

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
          {pieces.map((piece) => {
            const name = piece.title || 'Pezzo senza nome';
            const next = nextStep(piece.steps);
            return (
              <li key={piece.run_id} className="piece-row">
                <Link href={`/pezzi/${encodeURIComponent(piece.run_id)}?tab=${next.tab}`} className="piece-card">
                  {piece.cover ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={`${API_URL}/files/${piece.cover}`} alt="" loading="lazy" />
                  ) : (
                    <span className="piece-thumb-empty" />
                  )}
                  <div>
                    <h2>{name}</h2>
                    <time dateTime={piece.created_at}>{formatPieceDate(piece.created_at)}</time>
                    <p className="piece-next" data-done={next.done}>{next.label}</p>
                    <MosaicTiles items={stepTiles(piece.steps)} palette={piece.palette} />
                  </div>
                </Link>
                <button
                  type="button"
                  className="piece-delete"
                  aria-label={`Elimina ${name}`}
                  aria-expanded={confirming === piece.run_id}
                  onClick={() => setConfirming(confirming === piece.run_id ? null : piece.run_id)}
                >
                  <Trash2 size={18} aria-hidden="true" />
                  <span>Elimina</span>
                </button>
                {confirming === piece.run_id && (
                  <div className="piece-confirm" role="group" aria-label={`Conferma eliminazione di ${name}`}>
                    <p>
                      {piece.steps.sito !== 'none'
                        ? <>Elimino &laquo;{name}&raquo;? Il pezzo è sul sito e <strong>viene tolto anche da lì</strong>: è unico, se lo elimini non c&apos;è più. Nello Studio finisce nel cestino sul PC.</>
                        : <>Elimino &laquo;{name}&raquo; dallo Studio? Finisce nel cestino sul PC.</>}
                    </p>
                    <div>
                      <button
                        type="button"
                        className="btn-mission"
                        disabled={deleting === piece.run_id}
                        onClick={() => deletePiece(piece.run_id)}
                      >
                        {deleting === piece.run_id ? 'Elimino...' : 'Sì, elimina'}
                      </button>
                      <button type="button" className="btn-secondary" onClick={() => setConfirming(null)}>
                        Annulla
                      </button>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
