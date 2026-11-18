'use client';

import { useCallback, useEffect, useImperativeHandle, useState, forwardRef } from 'react';
import PieceWorkspace from '@/components/PieceWorkspace';
import { API_URL } from '@/lib/apiUrl';
import { formatDraftTime, type Draft } from '@/lib/drafts';

export interface DraftListHandle {
  refresh: () => void;
}

interface Props {
  // Called with the job id when "Crea la scheda" starts the work (the page then follows it).
  onStarted: (jobId: string) => void;
  // The page hides the photo capture while a piece is open.
  onOpenChange?: (open: boolean) => void;
}

const photoUrl = (draft: Draft, name: string, width = 360) => `${API_URL}/bozze/${draft.id}/foto/${encodeURIComponent(name)}?w=${width}`;

type Filter = 'tutti' | 'prompt' | 'crea' | 'valuta';
const FILTERS: { key: Filter; label: string }[] = [
  { key: 'tutti', label: 'Tutti' },
  { key: 'prompt', label: 'Prompt da fare' },
  { key: 'crea', label: 'Foto da creare' },
  { key: 'valuta', label: 'Da valutare' },
];

// «prossimo passo» di un pezzo: il testo della pillola e il suo colore (grigio = da iniziare, ocra = in attesa, verde = pronto)
function nextStep(draft: Draft): { label: string; tone: 'todo' | 'wait' | 'ready'; filter: Filter } {
  if (draft.status === 'scheda_pronta') return { label: 'Scheda pronta', tone: 'ready', filter: 'tutti' };
  if (draft.status === 'in_corso') return { label: 'Scheda in preparazione', tone: 'wait', filter: 'tutti' };
  switch (draft.progress?.stage) {
    case 'crea':
      return { label: 'Foto da creare su Higgsfield', tone: 'wait', filter: 'crea' };
    case 'carica':
      return { label: 'Carica il risultato', tone: 'wait', filter: 'crea' };
    case 'valuta':
      return { label: 'Da valutare', tone: 'ready', filter: 'valuta' };
    case 'fatto':
      return { label: 'Valutata', tone: 'ready', filter: 'tutti' };
    default:
      return { label: 'Prompt da fare', tone: 'todo', filter: 'prompt' };
  }
}

// I pezzi salvati in negozio: un elenco che dice cosa manca a ciascuno, e il pezzo aperto come spazio di lavoro.
const DraftList = forwardRef<DraftListHandle, Props>(function DraftList({ onStarted, onOpenChange }, ref) {
  const [drafts, setDrafts] = useState<Draft[] | null>(null);
  const [error, setError] = useState('');
  const [openId, setOpenId] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>('tutti');

  const refresh = useCallback(() => {
    fetch(`${API_URL}/bozze`, { cache: 'no-store' })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setDrafts(Array.isArray(data?.items) ? data.items : []);
        setError('');
      })
      .catch(() => setError('Non riesco a leggere i pezzi salvati. Controlla che lo Studio sul PC sia acceso.'));
  }, []);

  useImperativeHandle(ref, () => ({ refresh }), [refresh]);
  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    onOpenChange?.(openId !== null);
  }, [openId, onOpenChange]);

  // While a Scheda is being made, look again now and then.
  useEffect(() => {
    if (!drafts?.some((draft) => draft.status === 'in_corso')) return;
    const timer = setInterval(refresh, 5000);
    return () => clearInterval(timer);
  }, [drafts, refresh]);

  const replace = (next: Draft) => setDrafts((list) => (list ? list.map((d) => (d.id === next.id ? next : d)) : list));

  if (drafts === null && !error) return <p className="page-lead">Carico i pezzi salvati...</p>;

  const open = openId ? drafts?.find((d) => d.id === openId) : undefined;
  if (open) {
    return (
      <PieceWorkspace
        key={open.id}
        draft={open}
        onBack={() => {
          setOpenId(null);
          refresh();
        }}
        onUpdate={replace}
        onRemoved={(id) => {
          setDrafts((list) => (list ? list.filter((d) => d.id !== id) : list));
          setOpenId(null);
        }}
        onStarted={onStarted}
      />
    );
  }

  const all = drafts ?? [];
  const todo = all.filter((d) => d.status !== 'scheda_pronta');
  const ready = all.filter((d) => d.status === 'scheda_pronta');
  const count = (f: Filter) => (f === 'tutti' ? todo.length : todo.filter((d) => nextStep(d).filter === f).length);
  const shown = (filter === 'tutti' ? todo : todo.filter((d) => nextStep(d).filter === filter)).concat(filter === 'tutti' ? ready : []);

  return (
    <section className="drafts" aria-label="Pezzi salvati da lavorare">
      <h2 className="drafts-title">
        Da lavorare <span>{todo.length}</span>
      </h2>
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}
      {drafts && todo.length === 0 && <p className="page-lead">Niente in attesa. I pezzi che salvi dal negozio compaiono qui.</p>}

      {todo.length > 0 && (
        <div className="filter-chips" role="group" aria-label="Filtra per passo">
          {FILTERS.map((f) => (
            <button key={f.key} type="button" aria-pressed={filter === f.key} onClick={() => setFilter(f.key)}>
              {f.label} <b>{count(f.key)}</b>
            </button>
          ))}
        </div>
      )}
      {todo.length > 0 && shown.length === 0 && <p className="page-lead">Nessun pezzo in questo passo.</p>}

      <ul className="draft-list">
        {shown.map((draft) => {
          const cover = draft.main || draft.photos[0];
          const facts = draft.facts || {};
          const step = nextStep(draft);
          return (
            <li key={draft.id} className={`draft ${draft.status === 'scheda_pronta' ? 'draft-done' : ''}`}>
              <button type="button" className="draft-head" onClick={() => setOpenId(draft.id)}>
                {cover ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={photoUrl(draft, cover)} alt="" loading="lazy" />
                ) : (
                  <span className="piece-thumb-empty" />
                )}
                <span className="draft-text">
                  <span className="draft-note">{draft.note || 'Nessuna nota'}</span>
                  <span className="draft-chips">
                    {facts.pietre?.map((stone) => (
                      <span className="chip" key={stone}>
                        {stone}
                      </span>
                    ))}
                    {facts.prezzo !== undefined && <span className="chip chip-price">{facts.prezzo} €</span>}
                    {facts.misura && <span className="chip">mis. {facts.misura}</span>}
                  </span>
                  <span className="draft-meta">
                    <span className={`step-pill step-${step.tone}`}>{step.label}</span> {formatDraftTime(draft.created_at)} · {draft.photos.length} foto
                  </span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
});

export default DraftList;
