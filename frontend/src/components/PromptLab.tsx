'use client';

import { useCallback, useEffect, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';
import { loadSettings } from '@/lib/settings';

interface CritiqueItem {
  label: string;
  esito: 'ok' | 'dubbio' | 'problema';
  nota: string;
}

interface Critique {
  checklist: Record<string, CritiqueItem>;
  giudizio: string;
  voto_proposto: number;
  correzione: string;
  prompt_corretto: string;
  codex_model: string;
}

interface Attempt {
  id: string;
  shot: string;
  model: string;
  prompt: string;
  created_at: string;
  result: string;
  rating: number;
  note: string;
  critique?: Critique;
}

interface Lab {
  category: string;
  target_model?: string;
  analisi: string;
  styling: string;
  woman: string;
  prompts: Record<string, { text: string; edited: boolean }>;
  scenes?: Record<string, { text: string; edited: boolean }>;
  scenes_idea?: string;
  attempts: Attempt[];
}

interface Payload {
  lab: Lab | null;
  library: { total: number; good: number; bad: number };
}

interface CodexInfo {
  installed: boolean;
  models: { slug: string; name: string }[];
  default: string;
}

const SHOT_LABELS: Record<string, string> = {
  clean: 'Foto catalogo',
  worn: 'Foto indossata',
  worn_2: 'Seconda indossata',
  scena_1: 'Scena 1 · capo intero',
  scena_2: 'Scena 2 · dettaglio',
  scena_3: 'Scena 3 · movimento',
};
const isVideo = (name: string) => /\.(mp4|mov|m4v|webm)$/i.test(name);
const CATEGORY_LABELS: Record<string, string> = { bijoux: 'Bijoux', abbigliamento: 'Abbigliamento', accessori: 'Accessori' };
const MODELS = ['Seedream', 'Nano Banana', 'GPT Image', 'Seedance', 'Altro'];
const CODEX_MODEL_KEY = 'monili_codex_model';
const ESITO_LABEL = { ok: 'ok', dubbio: 'dubbio', problema: 'problema' } as const;

// La fucina dei prompt: lo Studio analizza e scrive il prompt per il modello scelto, poi si ferma.
// Tu crei la foto a mano su Higgsfield, la ricarichi qui accanto alla foto vera, Codex la confronta e tu dai il voto.
export default function PromptLab({ draftId, mainPhoto }: { draftId: string; mainPhoto: string }) {
  const [data, setData] = useState<Payload | null>(null);
  const [category, setCategory] = useState('');
  const [target, setTarget] = useState(MODELS[0]);
  const [busy, setBusy] = useState(false);
  const [judging, setJudging] = useState('');
  const [error, setError] = useState('');
  const [copied, setCopied] = useState('');
  const [codex, setCodex] = useState<CodexInfo | null>(null);
  const [codexModel, setCodexModel] = useState('');
  const [sourceId, setSourceId] = useState('');

  const base = `${API_URL}/bozze/${draftId}`;

  const request = useCallback(
    async (path: string, init?: RequestInit) => {
      const res = await fetch(`${base}${path}`, init);
      const body = await res.json().catch(() => null);
      if (!res.ok) throw new Error(body?.error || `HTTP ${res.status}`);
      return body as Payload;
    },
    [base],
  );

  useEffect(() => {
    request('/prompt', { cache: 'no-store' })
      .then(setData)
      .catch(() => setError('Non riesco a leggere i prompt. Controlla che lo Studio sul PC sia acceso.'));
    fetch(`${API_URL}/fucina/codex`, { cache: 'no-store' })
      .then((res) => res.json())
      .then((info: CodexInfo) => {
        setCodex(info);
        let saved = '';
        try {
          saved = localStorage.getItem(CODEX_MODEL_KEY) ?? '';
        } catch {
          /* storage non disponibile */
        }
        setCodexModel(info.models.some((m) => m.slug === saved) ? saved : '');
      })
      .catch(() => setCodex(null));
  }, [request]);

  const json = (method: string, body: unknown): RequestInit => ({
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  async function run(task: () => Promise<Payload>, fail: string) {
    setError('');
    try {
      setData(await task());
    } catch (err) {
      setError(`${fail}: ${err instanceof Error ? err.message : err}`);
    }
  }

  async function analyze() {
    setBusy(true);
    await run(
      () => request('/prompt', json('POST', { category, model: target, text_model: loadSettings().textModel })),
      'Non sono riuscito a preparare i prompt',
    );
    setBusy(false);
  }

  async function makeScenes() {
    if (!lab) return;
    const source = sourceId || pickable[pickable.length - 1]?.id;
    if (!source) return;
    setBusy(true);
    await run(
      () => request('/scene', json('POST', { attempt_id: source, text_model: loadSettings().textModel })),
      'Non sono riuscito a scrivere le scene',
    );
    setBusy(false);
  }

  async function judge(attempt: Attempt) {
    setJudging(attempt.id);
    await run(
      () => request(`/prove/${attempt.id}/valuta`, json('POST', { model: codexModel })),
      'Codex non ha potuto valutare',
    );
    setJudging('');
  }

  async function copy(key: string, text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(key);
      setTimeout(() => setCopied(''), 2000);
    } catch {
      setError('Non riesco a copiare: tieni premuto sul testo e scegli Copia.');
    }
  }

  const lab = data?.lab;
  const pickable = lab ? lab.attempts.filter((a) => a.result && !a.shot.startsWith('scena') && !/\.(mp4|mov|m4v|webm)$/i.test(a.result)) : [];

  const shotCards = (entries: [string, { text: string; edited: boolean }][]) =>
    entries.map(([shot, prompt]) => {
              const attempts = (lab?.attempts ?? []).filter((a) => a.shot === shot);
              return (
                <section className="lab-shot" key={shot}>
                  <h4>{SHOT_LABELS[shot] ?? shot}</h4>
                  <textarea
                    className="brief-area lab-prompt"
                    rows={9}
                    defaultValue={prompt.text}
                    key={prompt.text}
                    aria-label={`Prompt ${SHOT_LABELS[shot] ?? shot}`}
                    onBlur={(e) => {
                      if (e.target.value.trim() !== prompt.text.trim()) {
                        void run(() => request(`/prompt/${shot}`, json('PUT', { text: e.target.value })), 'Non sono riuscito a salvare il prompt');
                      }
                    }}
                  />
                  <div className="draft-actions">
                    <button type="button" className="btn-secondary" onClick={() => copy(shot, prompt.text)}>
                      {copied === shot ? 'Copiato' : 'Copia il prompt'}
                    </button>
                    <button
                      type="button"
                      className="btn-mission"
                      onClick={() => run(() => request('/prove', json('POST', { shot })), 'Non sono riuscito a segnarla')}
                    >
                      Fatta su Higgsfield
                    </button>
                  </div>
  
                  {attempts.map((attempt) => {
                    const critique = attempt.critique;
                    return (
                      <div className="lab-attempt" key={attempt.id}>
                        <p className="draft-meta">
                          {attempt.model} · {attempt.created_at.slice(11, 16)}
                          {attempt.rating > 0 && ` · il tuo voto ${attempt.rating}/5`}
                        </p>
  
                        <div className="lab-compare">
                          <figure>
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            {realPhoto && <img src={realPhoto} alt="Foto vera" />}
                            <figcaption>Foto vera</figcaption>
                          </figure>
                          <figure>
                            {attempt.result ? (
                              // eslint-disable-next-line @next/next/no-img-element
                              <img src={`${base}/prove/${attempt.id}/risultato?w=640&v=${attempt.result}`} alt="Risultato" />
                            ) : (
                              <label className="btn-secondary lab-upload">
                                Carica il risultato
                                <input
                                  type="file"
                                  accept="image/*,.heic,.heif"
                                  onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    e.target.value = '';
                                    if (!file) return;
                                    const form = new FormData();
                                    form.append('foto', file);
                                    void run(() => request(`/prove/${attempt.id}/risultato`, { method: 'POST', body: form }), 'Non sono riuscito a caricarla');
                                  }}
                                />
                              </label>
                            )}
                            <figcaption>{shot.startsWith('scena') ? 'Video' : 'Creata'} con {attempt.model}</figcaption>
                          </figure>
                        </div>
  
                        {attempt.result && (
                          <div className="draft-actions">
                            {codex?.installed && codex.models.length > 0 && (
                              <select
                                className="lab-select"
                                value={codexModel}
                                aria-label="Modello di Codex"
                                onChange={(e) => {
                                  setCodexModel(e.target.value);
                                  try {
                                    localStorage.setItem(CODEX_MODEL_KEY, e.target.value);
                                  } catch {
                                    /* storage non disponibile */
                                  }
                                }}
                              >
                                <option value="">Codex: {codex.default || 'predefinito'}</option>
                                {codex.models.map((m) => (
                                  <option key={m.slug} value={m.slug}>
                                    {m.name}
                                  </option>
                                ))}
                              </select>
                            )}
                            <button type="button" className="btn-secondary" onClick={() => judge(attempt)} disabled={judging === attempt.id || codex?.installed === false}>
                              {judging === attempt.id ? 'Codex sta guardando...' : critique ? 'Fai rivalutare' : 'Fai valutare a Codex'}
                            </button>
                          </div>
                        )}
  
                        {critique && (
                          <div className="lab-critique">
                            <ul>
                              {Object.entries(critique.checklist).map(([key, item]) => (
                                <li key={key} className={`lab-esito lab-esito-${item.esito}`}>
                                  <strong>{item.label}</strong> <span>{ESITO_LABEL[item.esito]}</span>
                                  {item.nota && <small>{item.nota}</small>}
                                </li>
                              ))}
                            </ul>
                            <p>{critique.giudizio}</p>
                            <p className="draft-hint">
                              Codex ({critique.codex_model || 'predefinito'}) propone {critique.voto_proposto || '?'}/5.
                            </p>
                            {critique.correzione && <p className="draft-hint">Da cambiare: {critique.correzione}</p>}
                            <div className="draft-actions">
                              {critique.voto_proposto > 0 && (
                                <button
                                  type="button"
                                  className="chip-btn"
                                  onClick={() =>
                                    run(() => request(`/prove/${attempt.id}`, json('PUT', { rating: critique.voto_proposto, note: attempt.note })), 'Non sono riuscito a salvare il voto')
                                  }
                                >
                                  Uso il suo voto ({critique.voto_proposto})
                                </button>
                              )}
                              {critique.prompt_corretto && (
                                <>
                                  <button type="button" className="chip-btn" onClick={() => copy(`fix-${attempt.id}`, critique.prompt_corretto)}>
                                    {copied === `fix-${attempt.id}` ? 'Copiato' : 'Copia il prompt corretto'}
                                  </button>
                                  <button
                                    type="button"
                                    className="chip-btn"
                                    onClick={() => run(() => request(`/prompt/${attempt.shot}`, json('PUT', { text: critique.prompt_corretto })), 'Non sono riuscito ad applicarlo')}
                                  >
                                    Usalo come prompt
                                  </button>
                                </>
                              )}
                            </div>
                          </div>
                        )}
  
                        <div className="lab-stars" role="group" aria-label="Il tuo voto">
                          {[1, 2, 3, 4, 5].map((n) => (
                            <button
                              key={n}
                              type="button"
                              className="chip-btn"
                              aria-pressed={attempt.rating === n}
                              onClick={() => run(() => request(`/prove/${attempt.id}`, json('PUT', { rating: n, note: attempt.note })), 'Non sono riuscito a salvare il voto')}
                            >
                              {n}
                            </button>
                          ))}
                        </div>
                        <textarea
                          className="brief-area"
                          rows={2}
                          defaultValue={attempt.note}
                          placeholder="Cosa è venuto bene o male (la pietra è cambiata, troppo scura...)"
                          onBlur={(e) => {
                            if (e.target.value.trim() !== attempt.note) {
                              void run(
                                () => request(`/prove/${attempt.id}`, json('PUT', { rating: attempt.rating, note: e.target.value })),
                                'Non sono riuscito a salvare la nota',
                              );
                            }
                          }}
                        />
                        <button
                          type="button"
                          className="chip-btn"
                          onClick={() => run(() => request(`/prove/${attempt.id}`, { method: 'DELETE' }), 'Non sono riuscito a toglierla')}
                        >
                          Elimina prova
                        </button>
                      </div>
                    );
                  })}
                </section>
              );
            });

  const realPhoto = mainPhoto ? `${API_URL}/bozze/${draftId}/foto/${encodeURIComponent(mainPhoto)}?w=640` : '';

  return (
    <div className="lab">
      <h3 className="lab-title">Fucina dei prompt</h3>
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}

      {!lab && (
        <div className="lab-start">
          <p className="draft-hint">
            Scegli con quale modello creerai la foto: lo Studio guarda la foto «Principale» e la nota, poi scrive il prompt giusto per
            quel modello. Non crea nessuna immagine.
          </p>
          <div className="draft-actions">
            <select className="lab-select" value={target} onChange={(e) => setTarget(e.target.value)} aria-label="Modello con cui crei la foto">
              {MODELS.map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
            <select className="lab-select" value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Tipo di pezzo">
              <option value="">Tipo: lo capisce lui</option>
              {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
            <button type="button" className="btn-mission" onClick={analyze} disabled={busy}>
              {busy ? 'Analizzo...' : 'Analizza e prepara il prompt'}
            </button>
          </div>
        </div>
      )}

      {lab && (
        <>
          <p className="draft-hint">
            {lab.target_model || 'Modello non indicato'} · {CATEGORY_LABELS[lab.category] ?? lab.category} · libreria:{' '}
            {data?.library.good ?? 0} buoni, {data?.library.bad ?? 0} da evitare
          </p>
          <details className="lab-analysis">
            <summary>Analisi del pezzo</summary>
            <pre>{lab.analisi}</pre>
            {lab.styling && <p>{lab.styling}</p>}
            {lab.woman && <p className="draft-hint">Donna: {lab.woman}</p>}
          </details>

          {shotCards(Object.entries(lab.prompts))}

          {lab.category === 'abbigliamento' && (
            <section className="lab-step2">
              <h4>Passo 2 · scene video con Seedance 2.5</h4>
              {pickable.length === 0 ? (
                <p className="draft-hint">
                  Quando hai caricato la foto del capo indossato dalla modella, scegli qui quella da animare: lo Studio scrive le scene.
                </p>
              ) : (
                <>
                  <p className="draft-hint">Parti da questa foto: sarà il primo fotogramma di ogni scena.</p>
                  <div className="lab-pick">
                    {pickable.map((a) => (
                      <button
                        key={a.id}
                        type="button"
                        className="lab-pick-item"
                        aria-pressed={(sourceId || pickable[pickable.length - 1].id) === a.id}
                        onClick={() => setSourceId(a.id)}
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={`${base}/prove/${a.id}/risultato?w=200&v=${a.result}`} alt="Foto indossata" />
                        <span>{a.rating > 0 ? `voto ${a.rating}` : 'senza voto'}</span>
                      </button>
                    ))}
                  </div>
                  <div className="draft-actions">
                    <button type="button" className="btn-mission" onClick={makeScenes} disabled={busy}>
                      {busy ? 'Scrivo le scene...' : lab.scenes ? 'Riscrivi le scene' : 'Prepara le scene video'}
                    </button>
                  </div>
                </>
              )}
              {lab.scenes_idea && <p className="draft-hint">Idea: {lab.scenes_idea}</p>}
              {lab.scenes && shotCards(Object.entries(lab.scenes))}
              {lab.scenes && <p className="draft-hint">Chiedi 1080p su Higgsfield: l&apos;uscita normale è 854x480 e sul sito è morbida.</p>}
            </section>
          )}

          <div className="draft-actions">
            <button type="button" className="btn-secondary" onClick={analyze} disabled={busy}>
              {busy ? 'Analizzo...' : 'Rifai l’analisi'}
            </button>
          </div>
          <p className="draft-hint">Voto 4-5: il prompt diventa un esempio per i prossimi pezzi con lo stesso modello. Voto 1-2 con una nota: un errore da non ripetere.</p>
        </>
      )}
    </div>
  );
}
