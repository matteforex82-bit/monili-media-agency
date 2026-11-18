'use client';

import { useCallback, useEffect, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';

interface Rule {
  id: string;
  text: string;
  model: string;
  category: string;
  why: string;
  status: 'proposta' | 'approvata' | 'scartata';
}

interface RulesPayload {
  rules: Rule[];
  rated?: number;
  min_rated?: number;
}

interface Props {
  engine: string;
  codexModel: string;
}

const scopeLabel = (rule: Rule) => [rule.model || 'ogni modello', rule.category || 'ogni tipo di pezzo'].join(' · ');

// «Impara»: lo Studio legge i voti di Matteo e propone regole; contano nei prompt solo quelle che approva lui.
export default function LearnPanel({ engine, codexModel }: Props) {
  const [rules, setRules] = useState<Rule[]>([]);
  const [rated, setRated] = useState(0);
  const [minRated, setMinRated] = useState(3);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/fucina/regole`, { cache: 'no-store' });
      const body = (await res.json()) as RulesPayload;
      setRules(body.rules);
      setRated(body.rated ?? 0);
      setMinRated(body.min_rated ?? 3);
    } catch {
      setMessage('Non riesco a leggere le regole. Controlla che lo Studio sul PC sia acceso.');
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function call(path: string, init?: RequestInit) {
    const res = await fetch(`${API_URL}/fucina/regole${path}`, init);
    const body = await res.json().catch(() => null);
    if (!res.ok) throw new Error(body?.error || `HTTP ${res.status}`);
    return body as { rules: Rule[]; new?: Rule[] };
  }

  async function learn() {
    setBusy(true);
    setMessage('');
    try {
      const body = await call('/proponi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine, codex_model: codexModel }),
      });
      setRules(body.rules);
      setMessage(body.new && body.new.length > 0 ? `${body.new.length} regole nuove da guardare.` : 'Dai tuoi voti non esce niente di nuovo.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function decide(rule: Rule, patch: { status?: string; text?: string }) {
    try {
      const body = await call(`/${rule.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(patch) });
      setRules(body.rules);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  async function remove(rule: Rule) {
    try {
      setRules((await call(`/${rule.id}`, { method: 'DELETE' })).rules);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  const proposals = rules.filter((r) => r.status === 'proposta');
  const approved = rules.filter((r) => r.status === 'approvata');

  return (
    <details className="lab-learn" open={proposals.length > 0}>
      <summary>
        Cosa ha imparato lo Studio ({approved.length} {approved.length === 1 ? 'regola' : 'regole'}
        {proposals.length > 0 ? `, ${proposals.length} da guardare` : ''})
      </summary>
      <p className="step-hint">
        Le regole nascono dai tuoi voti e dalle tue note. Entrano nei prompt solo quando le approvi. Hai votato {rated} foto.
      </p>
      {proposals.map((rule) => (
        <div className="lab-rule is-proposal" key={rule.id}>
          <textarea
            className="brief-area"
            rows={2}
            defaultValue={rule.text}
            aria-label="Testo della regola"
            onBlur={(e) => {
              if (e.target.value.trim() && e.target.value.trim() !== rule.text) void decide(rule, { text: e.target.value });
            }}
          />
          <small>
            Vale per: {scopeLabel(rule)}. {rule.why}
          </small>
          <div className="draft-actions">
            <button type="button" className="chip-btn" onClick={() => decide(rule, { status: 'approvata' })}>
              Approva
            </button>
            <button type="button" className="chip-btn" onClick={() => decide(rule, { status: 'scartata' })}>
              Scarta
            </button>
          </div>
        </div>
      ))}
      {approved.map((rule) => (
        <div className="lab-rule" key={rule.id}>
          <p>{rule.text}</p>
          <small>Vale per: {scopeLabel(rule)}</small>
          <button type="button" className="link-btn" onClick={() => remove(rule)}>
            Togli la regola
          </button>
        </div>
      ))}
      {message && <p className="step-hint" role="status">{message}</p>}
      <button type="button" className="btn-secondary" onClick={learn} disabled={busy || rated < minRated}>
        {busy ? 'Leggo i tuoi voti…' : 'Impara dai miei voti'}
      </button>
      {rated < minRated && <p className="step-hint">Servono almeno {minRated} foto votate (ne hai {rated}).</p>}
    </details>
  );
}
