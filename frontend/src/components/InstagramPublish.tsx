'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';

interface Props {
  reelId: string;
  kind: 'reel' | 'story';
  caption: string;
  firstComment?: string;
  hasAiWoman: boolean;
}

interface Status {
  configured: boolean;
  connected: boolean;
  username?: string;
  error?: string;
}

interface PostInfo {
  status?: string;
  url?: string;
  error?: string;
  account?: string;
}

const POLL_MS = 6000;
const LABEL = { reel: 'Reel', story: 'Storia' } as const;

// Pubblica su Instagram tramite Zernio. Parte solo dopo la conferma di chi ha il PC davanti.
export default function InstagramPublish({ reelId, kind, caption, firstComment = '', hasAiWoman }: Props) {
  const [status, setStatus] = useState<Status | null>(null);
  const [record, setRecord] = useState<PostInfo>({});
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const base = `${API_URL}/reel/${encodeURIComponent(reelId)}`;

  const check = useCallback(async () => {
    try {
      const res = await fetch(`${base}/instagram/${kind}/status`, { cache: 'no-store' });
      if (!res.ok) return;
      const data: PostInfo = await res.json();
      setRecord(data);
      const waiting = !['published', 'failed', 'cancelled', 'partial'].includes(data.status ?? '');
      if (waiting) timer.current = setTimeout(check, POLL_MS);
    } catch {
      /* si riprova al prossimo giro o alla riapertura */
    }
  }, [base, kind]);

  useEffect(() => {
    let alive = true;
    fetch(`${API_URL}/instagram/status`, { cache: 'no-store' })
      .then((res) => res.json())
      .then((data: Status) => alive && setStatus(data))
      .catch(() => alive && setStatus({ configured: false, connected: false }));
    fetch(`${base}/instagram`, { cache: 'no-store' })
      .then((res) => (res.ok ? res.json() : {}))
      .then((data: { [key: string]: PostInfo }) => {
        if (!alive || !data[kind]) return;
        setRecord(data[kind]);
        void check();
      })
      .catch(() => undefined);
    return () => {
      alive = false;
      if (timer.current) clearTimeout(timer.current);
    };
  }, [base, kind, check]);

  if (!status || !status.configured) return null;

  const connect = async () => {
    setMessage('');
    try {
      const res = await fetch(`${API_URL}/instagram/connect`, { cache: 'no-store' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Collegamento non disponibile.');
      window.open(data.url, '_blank', 'noopener');
      setMessage('Autorizza l’accesso nella pagina di Instagram che si è aperta, poi ricarica questa pagina.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Collegamento non disponibile.');
    }
  };

  const publish = async () => {
    const what = kind === 'reel' ? `questo Reel con la caption (${caption.length} caratteri)` : 'questa Storia (senza testo)';
    const ok = window.confirm(
      `Pubblicare ora su Instagram${status.username ? ` (@${status.username})` : ''} ${what}?\n\nVa online subito e il pubblico lo vede.`,
    );
    if (!ok) return;
    setBusy(true);
    setMessage('');
    try {
      const res = await fetch(`${base}/instagram`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kind, caption: kind === 'reel' ? caption : '', first_comment: kind === 'reel' ? firstComment : '', ai_generated: hasAiWoman, confirm: true }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Pubblicazione non riuscita.');
      setRecord(data);
      void check();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Pubblicazione non riuscita.');
    } finally {
      setBusy(false);
    }
  };

  if (!status.connected) {
    return (
      <div className="ig-share">
        <button type="button" className="btn-secondary" onClick={connect}>Collega Instagram a Zernio</button>
        <p className="ig-note">Instagram non è ancora collegato: serve una volta sola, dal profilo professionale del negozio.</p>
        {message && <p className="ig-note" role="status">{message}</p>}
      </div>
    );
  }

  const done = record.status === 'published';
  const failed = record.status === 'failed' || record.status === 'partial';
  const sent = Boolean(record.status) && !failed;
  return (
    <div className="ig-share">
      {!sent && (
        <button type="button" className="btn-mission ig-share-btn" onClick={publish} disabled={busy}>
          {busy ? 'Pubblico...' : `Pubblica ${LABEL[kind]} su Instagram`}
        </button>
      )}
      {sent && !done && <p className="ig-note" role="status">In pubblicazione su Instagram... può volerci un minuto.</p>}
      {done && (
        <p className="ig-note" role="status">
          Pubblicato su Instagram.{' '}
          {record.url && <a href={record.url} target="_blank" rel="noreferrer">Aprilo</a>}
        </p>
      )}
      {failed && <p className="ig-note" role="alert">Instagram non ha completato la pubblicazione{record.error ? `: ${record.error}` : '.'}</p>}
      {message && <p className="ig-note" role="alert">{message}</p>}
    </div>
  );
}
