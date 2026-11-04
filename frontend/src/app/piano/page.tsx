'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';

const fileUrl = (path: string) => `${API_URL}/files/${path}`;

type Role = 'scoperta' | 'acquisto';
type SlotState = 'proposto' | 'creato' | 'pubblicato' | 'saltato';

interface Piece {
  run_id: string;
  title: string;
  price_text: string;
  location_label: string;
  cover: string;
  code: string;
}

interface Proposal {
  ruolo: Role;
  ruolo_etichetta: string;
  tema: string;
  skill: { id: string; label: string; uses_model: boolean };
  pezzo: Piece | null;
  motivo: string;
  motivo_pezzo: string;
  brief: string;
  storie: string;
  storie_promemoria: string;
  avvisi: string[];
}

interface Slot {
  stato: SlotState;
  proposta: Proposal | null;
  reel_id: string | null;
  pubblicato_il: string | null;
  motivo_salto: string;
}

interface Week {
  inizio: string;
  etichetta: string;
  tema: string;
  corrente: boolean;
  provvisoria: boolean;
  slot: Record<Role, Slot>;
}

interface PlanView {
  oggi: string;
  settimane: Week[];
  regole: string[];
}

const ROLES: Role[] = ['scoperta', 'acquisto'];
const STATE_LABEL: Record<SlotState, string> = {
  proposto: 'Da fare',
  creato: 'Creato',
  pubblicato: 'Pubblicato',
  saltato: 'Saltato',
};

async function readError(res: Response) {
  try {
    return (await res.json()).error || `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}

function createHref(week: string, role: Role, proposal: Proposal) {
  const params = new URLSearchParams({ skill: proposal.skill.id, brief: proposal.brief, piano: `${week}:${role}` });
  if (proposal.pezzo) params.set('pezzo', proposal.pezzo.run_id);
  return `/reel?${params.toString()}`;
}

export default function PianoPage() {
  const [plan, setPlan] = useState<PlanView | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState('');
  const [skipping, setSkipping] = useState('');
  const [skipNote, setSkipNote] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/piano`, { cache: 'no-store' });
      if (!res.ok) throw new Error(await readError(res));
      setPlan(await res.json());
      setError('');
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : `Backend non raggiungibile su ${API_URL}`);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const act = async (week: string, role: Role, action: 'altra-idea' | 'salta' | 'pubblicato', body?: object) => {
    setBusy(`${week}:${role}`);
    setError('');
    try {
      const res = await fetch(`${API_URL}/piano/${week}/${role}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body || {}),
      });
      if (!res.ok) throw new Error(await readError(res));
      setPlan(await res.json());
      setSkipping('');
      setSkipNote('');
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy('');
    }
  };

  return (
    <div className="rs-page pn-page">
      <header className="page-head">
        <h1 className="page-title">Piano</h1>
        <p className="page-lead">
          Due idee a settimana, scelte per te. Accetta, cambia idea o salta: nessun giorno è promesso.
        </p>
      </header>

      <main className="rs-main pn-main">
        {error && <div className="rs-error">{error}</div>}
        {!plan && !error && <p className="rs-muted">Preparo le idee della settimana…</p>}

        {plan?.settimane.map((week) => (
          <section key={week.inizio} className={`pn-week ${week.provvisoria ? 'pn-week-preview' : ''}`}>
            <div className="pn-week-head">
              <h2>
                {week.corrente ? 'Questa settimana' : 'Anteprima'} · {week.etichetta}
              </h2>
              <span className="pn-theme">{week.tema}</span>
              {week.provvisoria && <span className="pn-badge pn-badge-soft">Provvisoria: può cambiare</span>}
            </div>

            <div className="pn-slots">
              {ROLES.map((role) => {
                const slot = week.slot[role];
                const proposal = slot.proposta;
                const key = `${week.inizio}:${role}`;
                if (!proposal) return null;
                const piece = proposal.pezzo;
                const open = slot.stato === 'proposto';
                return (
                  <article key={role} className={`card pn-card pn-state-${slot.stato}`}>
                    <div className="pn-card-top">
                      <span className="pn-role">{proposal.ruolo_etichetta}</span>
                      <span className={`pn-badge pn-badge-${slot.stato}`}>{STATE_LABEL[slot.stato]}</span>
                    </div>

                    <div className="pn-body">
                      {piece ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img className="pn-photo" src={fileUrl(piece.cover)} alt={piece.title} />
                      ) : (
                        <div className="pn-photo pn-photo-empty">Nessun pezzo</div>
                      )}
                      <div className="pn-info">
                        <h3 className="pn-skill">
                          {proposal.skill.label} <span>/{proposal.skill.id}</span>
                        </h3>
                        {piece ? (
                          <p className="pn-piece">
                            <strong>{piece.title}</strong>
                            <br />
                            {piece.price_text} · {piece.location_label} · Rif. {piece.code}
                          </p>
                        ) : (
                          <p className="pn-piece">Nessun pezzo pubblicato con prezzo e foto.</p>
                        )}
                        <p className="pn-why">{proposal.motivo}</p>
                        {proposal.motivo_pezzo && <p className="pn-why">{proposal.motivo_pezzo}</p>}
                      </div>
                    </div>

                    <details className="pn-brief">
                      <summary>Brief già pronto</summary>
                      <p>{proposal.brief}</p>
                    </details>

                    {proposal.avvisi.map((notice) => (
                      <p key={notice} className="pn-notice">
                        {notice}
                      </p>
                    ))}

                    <p className="pn-stories">
                      <strong>Storie:</strong> {proposal.storie_promemoria} {proposal.storie}
                    </p>

                    {slot.stato === 'saltato' && (
                      <p className="rs-muted">Saltato{slot.motivo_salto ? `: ${slot.motivo_salto}` : '.'}</p>
                    )}
                    {slot.stato === 'pubblicato' && slot.pubblicato_il && (
                      <p className="rs-muted">Pubblicato il {slot.pubblicato_il}.</p>
                    )}

                    {!week.provvisoria && (
                      <div className="pn-actions">
                        {open && (
                          <>
                            <Link className="btn-mission pn-btn" href={createHref(week.inizio, role, proposal)}>
                              Crea
                            </Link>
                            <button
                              type="button"
                              className="btn-secondary pn-btn"
                              disabled={busy === key}
                              onClick={() => act(week.inizio, role, 'altra-idea')}
                            >
                              Un&apos;altra idea
                            </button>
                            <button
                              type="button"
                              className="btn-secondary pn-btn"
                              disabled={busy === key}
                              onClick={() => setSkipping(skipping === key ? '' : key)}
                            >
                              Salta
                            </button>
                          </>
                        )}
                        {slot.stato === 'creato' && slot.reel_id && (
                          <Link className="btn-secondary pn-btn" href={`/reel?reel=${encodeURIComponent(slot.reel_id)}`}>
                            Apri il Reel
                          </Link>
                        )}
                        {(slot.stato === 'proposto' || slot.stato === 'creato') && (
                          <button
                            type="button"
                            className="btn-secondary pn-btn"
                            disabled={busy === key}
                            onClick={() => act(week.inizio, role, 'pubblicato')}
                          >
                            Segna pubblicato
                          </button>
                        )}
                      </div>
                    )}

                    {skipping === key && (
                      <div className="pn-skip">
                        <label className="rs-field">
                          <span className="rs-field-label">Perché la salti? (facoltativo)</span>
                          <input
                            className="rs-input"
                            maxLength={200}
                            value={skipNote}
                            onChange={(e) => setSkipNote(e.target.value)}
                            placeholder="es. settimana piena di impegni (niente dati di clienti)"
                          />
                        </label>
                        <button
                          type="button"
                          className="btn-secondary pn-btn"
                          disabled={busy === key}
                          onClick={() => act(week.inizio, role, 'salta', { motivo: skipNote })}
                        >
                          Conferma: salta
                        </button>
                      </div>
                    )}
                  </article>
                );
              })}
            </div>
          </section>
        ))}

        {plan && (
          <section className="card rs-card pn-rules">
            <div className="label-eyebrow">Regole del Piano</div>
            <ul>
              {plan.regole.map((rule) => (
                <li key={rule}>{rule}</li>
              ))}
              <li>Con «Info sull&apos;AI» quando compare una donna creata dall&apos;AI.</li>
            </ul>
          </section>
        )}
      </main>
    </div>
  );
}
