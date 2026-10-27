'use client';

import { useCallback, useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://monili-backend.onrender.com';
const fileUrl = (path: string) => `${API_URL}/files/${path}`;

type Metrics = Partial<Record<'views' | 'reach' | 'likes' | 'comments' | 'saves' | 'sends' | 'dms' | 'store_visits' | 'sales_eur', number | null>>;

interface Entry {
  id: string;
  title: string;
  skill: string;
  format: 'reel' | 'story' | 'post';
  published_on: string;
  hour: number | null;
  metrics: Metrics;
  notes: string;
  cover?: string | null;
}

interface GroupRow {
  key: string;
  count: number;
  avg_views: number | null;
  send_rate: number | null;
  avg_dms: number | null;
  reliable: boolean;
}

interface Summary {
  count: number;
  with_numbers: number;
  totals: Record<string, number>;
  by_skill: GroupRow[];
  by_format: GroupRow[];
  by_weekday: GroupRow[];
  by_hour: GroupRow[];
  min_sample: number;
}

interface Pending {
  id: string;
  title: string;
  format: string;
  cover?: string;
  created_at: string;
}

const METRIC_ORDER: (keyof Metrics)[] = ['views', 'reach', 'likes', 'comments', 'saves', 'sends', 'dms', 'store_visits', 'sales_eur'];
const METRIC_HINTS: Partial<Record<keyof Metrics, string>> = {
  sends: 'icona aeroplanino',
  dms: 'messaggi arrivati per questo contenuto',
  store_visits: 'clienti che ne hanno parlato in negozio',
};

async function readError(res: Response) {
  try {
    return (await res.json()).error || `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}

function emptyForm(id = '', title = '', format: Entry['format'] = 'reel'): Entry {
  return {
    id,
    title,
    skill: '',
    format,
    published_on: new Date().toISOString().slice(0, 10),
    hour: 18,
    metrics: {},
    notes: '',
  };
}

function GroupTable({ title, rows, prefix = '' }: { title: string; rows: GroupRow[]; prefix?: string }) {
  if (!rows.length) return null;
  return (
    <div className="rs-copy-block">
      <div className="rs-copy-head"><span>{title}</span></div>
      <table className="rz-table">
        <thead>
          <tr><th /><th>contenuti</th><th>visual. medie</th><th>% invii</th><th>DM medi</th></tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.key} className={row.reliable ? '' : 'rz-weak'}>
              <td>{prefix}{row.key}</td>
              <td>{row.count}</td>
              <td>{row.avg_views ?? '—'}</td>
              <td>{row.send_rate != null ? `${row.send_rate}%` : '—'}</td>
              <td>{row.avg_dms ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function RisultatiPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [pending, setPending] = useState<Pending[]>([]);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [skills, setSkills] = useState<{ id: string; label: string }[]>([]);
  const [form, setForm] = useState<Entry | null>(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/results`, { cache: 'no-store' });
      if (!res.ok) throw new Error(await readError(res));
      const data = await res.json();
      setEntries(data.items || []);
      setSummary(data.summary || null);
      setPending(data.pending || []);
      setLabels(data.metric_labels || {});
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
    try {
      const res = await fetch(`${API_URL}/reel/config`);
      if (res.ok) setSkills(((await res.json()).recipes || []).map((r: { id: string; label: string }) => ({ id: r.id, label: r.label })));
    } catch {
      /* elenco skill facoltativo */
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openForm = (entry: Entry) => {
    setForm(JSON.parse(JSON.stringify(entry)));
    setMessage('');
    setError('');
    setTimeout(() => document.getElementById('rz-form')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  const save = async () => {
    if (!form) return;
    const id = form.id || `manuale-${Date.now()}`;
    const res = await fetch(`${API_URL}/results/${encodeURIComponent(id)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, id }),
    });
    if (!res.ok) {
      setError(await readError(res));
      return;
    }
    setMessage('Salvato ✓ — gli agenti useranno questi numeri dal prossimo contenuto.');
    setForm(null);
    load();
  };

  const remove = async (id: string) => {
    if (!window.confirm('Elimino i numeri di questo contenuto?')) return;
    await fetch(`${API_URL}/results/${encodeURIComponent(id)}`, { method: 'DELETE' });
    load();
  };

  const setMetric = (key: keyof Metrics, value: string) => {
    if (!form) return;
    setForm({ ...form, metrics: { ...form.metrics, [key]: value === '' ? null : Number(value) } });
  };

  const totals = summary?.totals || {};

  return (
    <div className="rs-page">
      <header className="app-header sticky top-0 z-50">
        <div className="rs-header">
          <a href="/reel" className="rs-back">← Reel Studio</a>
          <div className="rs-brand">
            <span className="rs-brand-title">Risultati</span>
            <span className="rs-brand-sub">cosa funziona davvero</span>
          </div>
          <span />
        </div>
      </header>

      <main className="rs-main">
        <section className="card rs-card">
          <div className="label-eyebrow">Come si usa</div>
          <p className="rs-muted">
            2-3 giorni dopo la pubblicazione apri il contenuto su Instagram → <strong>Visualizza insight</strong> e copia
            qui i numeri. Bastano visualizzazioni, invii e DM. Dopo almeno {summary?.min_sample ?? 2} contenuti per
            skill, gli agenti scelgono hook e struttura in base a cosa ha funzionato con le tue clienti.
          </p>
        </section>

        {error && <div className="rs-error">{error}</div>}
        {message && <div className="rs-banner">{message}</div>}

        {summary && summary.with_numbers > 0 && (
          <section className="rz-cards">
            <div className="rz-card"><span>{summary.with_numbers}</span>contenuti misurati</div>
            <div className="rz-card"><span>{Math.round(totals.views || 0)}</span>visualizzazioni</div>
            <div className="rz-card"><span>{Math.round(totals.sends || 0)}</span>invii</div>
            <div className="rz-card"><span>{Math.round(totals.dms || 0)}</span>DM</div>
            <div className="rz-card"><span>{Math.round(totals.store_visits || 0)}</span>visite in negozio</div>
            <div className="rz-card"><span>{Math.round(totals.sales_eur || 0)} €</span>vendite</div>
          </section>
        )}

        {pending.length > 0 && (
          <section className="rs-history">
            <div className="rs-section-title">Da completare</div>
            <p className="rs-muted rs-small">Video creati con l&apos;app che non hanno ancora i numeri.</p>
            <div className="rs-history-grid">
              {pending.map((item) => (
                <button key={item.id} type="button" className="rs-history-item" onClick={() => openForm(emptyForm(item.id, item.title, item.format as Entry['format']))}>
                  {item.cover ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={fileUrl(item.cover)} alt={item.title} />
                  ) : (
                    <div className="rs-history-placeholder">{item.format}</div>
                  )}
                  <span className="rs-history-title">{item.title || item.id}</span>
                  <span className="rs-history-status">+ inserisci numeri</span>
                </button>
              ))}
            </div>
          </section>
        )}

        <button type="button" className="btn-secondary rs-small-btn" onClick={() => openForm(emptyForm())}>
          + Aggiungi un contenuto pubblicato fuori dall&apos;app
        </button>

        {form && (
          <section id="rz-form" className="card rs-card">
            <div className="label-eyebrow">{form.id ? 'Numeri del contenuto' : 'Nuovo contenuto'}</div>
            <div className="rs-grid-2">
              <label className="rs-field">
                <span className="rs-field-label">Titolo</span>
                <input className="rs-input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="es. Orecchini blu serata" />
              </label>
              <label className="rs-field">
                <span className="rs-field-label">Skill usata</span>
                <select className="rs-input" value={form.skill} onChange={(e) => setForm({ ...form, skill: e.target.value })}>
                  <option value="">{form.id && !form.id.startsWith('manuale-') ? '(dal video)' : 'altro / nessuna'}</option>
                  {skills.map((s) => <option key={s.id} value={s.id}>/{s.id}</option>)}
                </select>
              </label>
            </div>
            <div className="rs-grid-3">
              <label className="rs-field">
                <span className="rs-field-label">Formato</span>
                <select className="rs-input" value={form.format} onChange={(e) => setForm({ ...form, format: e.target.value as Entry['format'] })}>
                  <option value="reel">Reel</option>
                  <option value="story">Story</option>
                  <option value="post">Post</option>
                </select>
              </label>
              <label className="rs-field">
                <span className="rs-field-label">Pubblicato il</span>
                <input className="rs-input" type="date" value={form.published_on} onChange={(e) => setForm({ ...form, published_on: e.target.value })} />
              </label>
              <label className="rs-field">
                <span className="rs-field-label">Ora</span>
                <input className="rs-input" type="number" min={0} max={23} value={form.hour ?? ''} onChange={(e) => setForm({ ...form, hour: e.target.value === '' ? null : Number(e.target.value) })} />
              </label>
            </div>
            <div className="rz-metrics">
              {METRIC_ORDER.map((key) => (
                <label key={key} className="rs-field">
                  <span className="rs-field-label">{labels[key] || key}</span>
                  <input
                    className="rs-input"
                    type="number"
                    inputMode="decimal"
                    min={0}
                    value={form.metrics[key] ?? ''}
                    onChange={(e) => setMetric(key, e.target.value)}
                    placeholder={METRIC_HINTS[key] || ''}
                  />
                </label>
              ))}
            </div>
            <label className="rs-field">
              <span className="rs-field-label">Note</span>
              <textarea className="brief-area" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="es. 2 clienti sono venute a chiederli, audio di tendenza X" />
            </label>
            <div className="rs-actions">
              <button type="button" className="btn-mission rs-small-btn" onClick={save}>Salva</button>
              <button type="button" className="btn-secondary rs-small-btn" onClick={() => setForm(null)}>Annulla</button>
            </div>
          </section>
        )}

        {summary && summary.with_numbers > 0 && (
          <section className="rs-history">
            <div className="rs-section-title">Cosa funziona</div>
            <p className="rs-muted rs-small">Le righe in grigio hanno meno di {summary.min_sample} contenuti: sono indicazioni, non ancora regole.</p>
            <GroupTable title="Per skill" rows={summary.by_skill} prefix="/" />
            <GroupTable title="Per formato" rows={summary.by_format} />
            <GroupTable title="Per giorno" rows={summary.by_weekday} />
            <GroupTable title="Per fascia oraria" rows={summary.by_hour} />
          </section>
        )}

        {entries.length > 0 && (
          <section className="rs-history">
            <div className="rs-section-title">Contenuti registrati</div>
            <div className="rz-list">
              {entries.map((entry) => (
                <div key={entry.id} className="rz-row">
                  {entry.cover ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={fileUrl(entry.cover)} alt="" />
                  ) : (
                    <div className="rz-thumb">{entry.format}</div>
                  )}
                  <div className="rz-row-main">
                    <strong>{entry.title || entry.id}</strong>
                    <span className="rs-muted rs-small">
                      {entry.published_on || 'data?'}{entry.hour != null ? ` · ${entry.hour}:00` : ''} · {entry.skill ? `/${entry.skill}` : 'altro'} · {entry.format}
                    </span>
                    <span className="rs-small">
                      {entry.metrics.views ?? '—'} visual. · {entry.metrics.sends ?? '—'} invii · {entry.metrics.dms ?? '—'} DM
                    </span>
                  </div>
                  <div className="rz-row-actions">
                    <button type="button" className="btn-ghost" onClick={() => openForm(entry)}>Modifica</button>
                    <button type="button" className="btn-ghost" onClick={() => remove(entry.id)}>✕</button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
