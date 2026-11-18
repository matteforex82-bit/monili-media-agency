'use client';

import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { API_URL } from '@/lib/apiUrl';
import { loadSettings } from '@/lib/settings';
import type { Progress } from '@/lib/drafts';

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
  woman_token?: string;
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
  progress?: Progress;
  library: { total: number; good: number; bad: number };
}

interface CodexInfo {
  installed: boolean;
  models: { slug: string; name: string }[];
  default: string;
}

export type LabStep = 'prompt' | 'generare' | 'valutare' | 'scene';

const SHOT_LABELS: Record<string, string> = {
  clean: 'Catalogo',
  worn: 'Indossata',
  worn_2: 'Seconda indossata',
  scena_1: 'Scena 1 · capo intero',
  scena_2: 'Scena 2 · dettaglio',
  scena_3: 'Scena 3 · movimento',
};
const CATEGORY_LABELS: Record<string, string> = { bijoux: 'Bijoux', abbigliamento: 'Abbigliamento', accessori: 'Accessori' };
const MODELS = ['Seedream', 'Nano Banana', 'GPT Image', 'Altro'];
const CODEX_MODEL_KEY = 'monili_codex_model';
const PREFS_KEY = 'monili_lab_prefs';
const ESITO_LABEL = { ok: 'ok', dubbio: 'dubbio', problema: 'problema' } as const;
const WORKING_TEXT = ['Guardo la foto…', 'Scrivo il prompt…', 'Controllo le regole del negozio…'];
const isVideo = (name: string) => /\.(mp4|mov|m4v|webm)$/i.test(name);

interface Prefs {
  target: string;
  woman: string;
  engine: string;
  category: string;
}
const DEFAULT_PREFS: Prefs = { target: MODELS[0], woman: 'token', engine: 'codex', category: '' };

function loadPrefs(): Prefs {
  try {
    const raw = JSON.parse(localStorage.getItem(PREFS_KEY) ?? 'null');
    if (raw && typeof raw === 'object') return { ...DEFAULT_PREFS, ...raw };
  } catch {
    /* storage non disponibile */
  }
  return DEFAULT_PREFS;
}

interface Props {
  draftId: string;
  mainPhoto: string;
  step: LabStep;
  onStep: (step: LabStep) => void;
  onProgress: (progress: Progress, category: string) => void;
  onDone: () => void;
}

// La fucina dei prompt, un passo alla volta: il prompt, la foto fatta a mano su Higgsfield, il confronto con la foto vera.
// Ogni passo mostra solo il suo contenuto e ha una sola azione principale, nella barra in basso.
export default function PromptLab({ draftId, mainPhoto, step, onStep, onProgress, onDone }: Props) {
  const [data, setData] = useState<Payload | null>(null);
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS);
  const [editingPrefs, setEditingPrefs] = useState(false);
  const [busy, setBusy] = useState(false);
  const [workingIndex, setWorkingIndex] = useState(0);
  const [judging, setJudging] = useState('');
  const [error, setError] = useState('');
  const [copied, setCopied] = useState('');
  const [shot, setShot] = useState('');
  const [codex, setCodex] = useState<CodexInfo | null>(null);
  const [codexModel, setCodexModel] = useState('');
  const [sourceId, setSourceId] = useState('');
  const progressRef = useRef(onProgress);
  progressRef.current = onProgress;

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

  const apply = useCallback((payload: Payload) => {
    setData(payload);
    if (payload.progress) progressRef.current(payload.progress, payload.lab?.category ?? '');
  }, []);

  useEffect(() => {
    setPrefs(loadPrefs());
    request('/prompt', { cache: 'no-store' })
      .then(apply)
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
  }, [request, apply]);

  // Mentre Codex lavora, dice cosa sta facendo (non solo "Analizzo...").
  useEffect(() => {
    if (!busy) return;
    setWorkingIndex(0);
    const timer = setInterval(() => setWorkingIndex((i) => Math.min(i + 1, WORKING_TEXT.length - 1)), 12000);
    return () => clearInterval(timer);
  }, [busy]);

  const json = (method: string, body: unknown): RequestInit => ({
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  async function run(task: () => Promise<Payload>, fail: string): Promise<Payload | null> {
    setError('');
    try {
      const payload = await task();
      apply(payload);
      return payload;
    } catch (err) {
      setError(`${fail}: ${err instanceof Error ? err.message : err}`);
      return null;
    }
  }

  const changePrefs = (patch: Partial<Prefs>) => {
    const next = { ...prefs, ...patch };
    setPrefs(next);
    try {
      localStorage.setItem(PREFS_KEY, JSON.stringify(next));
    } catch {
      /* storage non disponibile */
    }
  };

  async function analyze() {
    setBusy(true);
    const payload = await run(
      () =>
        request(
          '/prompt',
          json('POST', {
            category: prefs.category,
            model: prefs.target,
            woman: prefs.woman,
            engine: prefs.engine,
            codex_model: codexModel,
            text_model: loadSettings().textModel,
          }),
        ),
      'Non sono riuscito a preparare i prompt',
    );
    setBusy(false);
    if (payload?.lab) {
      setShot('');
      setEditingPrefs(false);
    }
  }

  async function markDone(key: string) {
    const payload = await run(() => request('/prove', json('POST', { shot: key })), 'Non sono riuscito a segnarla');
    if (payload) onStep('generare');
  }

  async function upload(attempt: Attempt, file: File) {
    const form = new FormData();
    form.append('foto', file);
    const payload = await run(() => request(`/prove/${attempt.id}/risultato`, { method: 'POST', body: form }), 'Non sono riuscito a caricarla');
    if (payload?.lab && !payload.lab.attempts.some((a) => !a.result)) onStep('valutare');
  }

  async function judge(attempt: Attempt) {
    setJudging(attempt.id);
    await run(() => request(`/prove/${attempt.id}/valuta`, json('POST', { model: codexModel })), 'Codex non ha potuto valutare');
    setJudging('');
  }

  async function makeScenes() {
    const current = data?.lab;
    if (!current) return;
    const pickable = pickablePhotos(current);
    const source = sourceId || pickable[pickable.length - 1]?.id;
    if (!source) return;
    setBusy(true);
    await run(
      () => request('/scene', json('POST', { attempt_id: source, engine: prefs.engine, codex_model: codexModel, text_model: loadSettings().textModel })),
      'Non sono riuscito a scrivere le scene',
    );
    setBusy(false);
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

  const lab = data?.lab ?? null;
  const realPhoto = mainPhoto ? `${API_URL}/bozze/${draftId}/foto/${encodeURIComponent(mainPhoto)}?w=900` : '';
  const codexName = codexModel || codex?.default || 'Codex';

  const errorBox = error ? (
    <div className="notice error" role="alert">
      {error}
    </div>
  ) : null;

  // ---------- impostazioni in una riga (ricordate tra i pezzi) ----------
  const settings = (
    <div className="lab-set">
      <div className="lab-set-line">
        <span>
          {prefs.target} · {prefs.woman === 'token' ? <strong className="lab-token">@MODELLA</strong> : 'donna descritta dall’AI'} ·{' '}
          {prefs.engine === 'codex' ? `Codex ${codexName}` : 'OpenRouter'}
        </span>
        <button type="button" className="link-btn" aria-expanded={editingPrefs} onClick={() => setEditingPrefs((v) => !v)}>
          {editingPrefs ? 'Chiudi' : 'Cambia'}
        </button>
      </div>
      {editingPrefs && (
        <div className="lab-set-edit">
          <label>
            Modello con cui crei la foto
            <select className="lab-select" value={prefs.target} onChange={(e) => changePrefs({ target: e.target.value })}>
              {MODELS.map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
          </label>
          <label>
            Tipo di pezzo
            <select className="lab-select" value={prefs.category} onChange={(e) => changePrefs({ category: e.target.value })}>
              <option value="">Lo capisce lo Studio</option>
              {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Donna nel prompt
            <select className="lab-select" value={prefs.woman} onChange={(e) => changePrefs({ woman: e.target.value })}>
              <option value="token">@MODELLA (scelgo io)</option>
              <option value="invented">Descritta dall&apos;AI</option>
            </select>
          </label>
          <label>
            Chi scrive i prompt
            <select className="lab-select" value={prefs.engine} onChange={(e) => changePrefs({ engine: e.target.value })}>
              <option value="codex">Codex (abbonamento)</option>
              <option value="openrouter">OpenRouter (a pagamento)</option>
            </select>
          </label>
          {prefs.engine === 'codex' && codex?.installed && codex.models.length > 0 && (
            <label>
              Modello di Codex
              <select
                className="lab-select"
                value={codexModel}
                onChange={(e) => {
                  setCodexModel(e.target.value);
                  try {
                    localStorage.setItem(CODEX_MODEL_KEY, e.target.value);
                  } catch {
                    /* storage non disponibile */
                  }
                }}
              >
                <option value="">Predefinito: {codex.default}</option>
                {codex.models.map((m) => (
                  <option key={m.slug} value={m.slug}>
                    {m.name}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
      )}
    </div>
  );

  const bar = (primary: ReactNode, secondary?: ReactNode) => (
    <div className="action-bar">
      {primary}
      {secondary}
    </div>
  );

  // ---------- passo: prompt ----------
  if (step === 'prompt') {
    if (!lab) {
      return (
        <>
          <div className="step-body">
            {errorBox}
            <p className="step-hint">
              Lo Studio guarda le foto del pezzo (fino a 4: la principale per prima) e la nota, e scrive il prompt giusto per il modello. Non crea nessuna immagine.
            </p>
            {settings}
            {busy && (
              <p className="step-working" role="status">
                {WORKING_TEXT[workingIndex]} <small>(circa un minuto)</small>
              </p>
            )}
          </div>
          {bar(
            <button type="button" className="btn-mission" onClick={analyze} disabled={busy}>
              {busy ? WORKING_TEXT[workingIndex] : 'Analizza e prepara il prompt'}
            </button>,
          )}
        </>
      );
    }
    const keys = Object.keys(lab.prompts);
    const current = keys.includes(shot) ? shot : keys.includes('worn') ? 'worn' : keys[0];
    const prompt = lab.prompts[current];
    return (
      <>
        <div className="step-body">
          {errorBox}
          {settings}
          {keys.length > 1 && (
            <div className="seg-tabs" role="tablist" aria-label="Foto">
              {keys.map((k) => (
                <button key={k} type="button" role="tab" aria-selected={k === current} onClick={() => setShot(k)}>
                  {SHOT_LABELS[k] ?? k}
                </button>
              ))}
            </div>
          )}
          <div className="prompt-head">
            <span>Prompt · {SHOT_LABELS[current] ?? current}</span>
            <button type="button" className="chip-btn prompt-copy" onClick={() => copy(current, prompt.text)}>
              {copied === current ? 'Copiato ✓' : 'Copia il prompt'}
            </button>
          </div>
          <textarea
            className="brief-area lab-prompt"
            rows={10}
            defaultValue={prompt.text}
            key={`${current}-${prompt.text}`}
            aria-label={`Prompt ${SHOT_LABELS[current] ?? current}`}
            onBlur={(e) => {
              if (e.target.value.trim() !== prompt.text.trim()) {
                void run(() => request(`/prompt/${current}`, json('PUT', { text: e.target.value })), 'Non sono riuscito a salvare il prompt');
              }
            }}
          />
          {lab.woman_token && <p className="step-hint">Prima di generare scrivi al posto di {lab.woman_token} Aurora o l&apos;altra modella.</p>}
          <details className="lab-analysis">
            <summary>Analisi del pezzo</summary>
            <pre>{lab.analisi}</pre>
            {lab.styling && <p>{lab.styling}</p>}
          </details>
          <button type="button" className="link-btn" onClick={analyze} disabled={busy}>
            {busy ? WORKING_TEXT[workingIndex] : 'Rifai l’analisi'}
          </button>
          <p className="step-hint">
            Libreria: {data?.library.good ?? 0} prompt buoni, {data?.library.bad ?? 0} da evitare. Voto 4-5 e 1-2 insegnano allo Studio.
          </p>
        </div>
        {bar(
          <button type="button" className="btn-mission" onClick={() => copy(current, prompt.text)}>
            {copied === current ? 'Copiato ✓' : 'Copia il prompt'}
          </button>,
          <button type="button" className="btn-secondary" onClick={() => markDone(current)}>
            Fatta su Higgsfield
          </button>,
        )}
      </>
    );
  }

  // ---------- passo: generare (caricare il risultato) ----------
  if (step === 'generare') {
    const pending = (lab?.attempts ?? []).filter((a) => !a.result);
    const last = pending[pending.length - 1];
    return (
      <>
        <div className="step-body">
          {errorBox}
          {pending.length === 0 ? (
            <p className="step-hint">
              {lab && lab.attempts.length > 0
                ? 'Hai già caricato tutti i risultati. Vai a valutarli.'
                : 'Crea la foto su Higgsfield con il prompt, poi torna qui a caricarla. Nel passo Prompt, premi «Fatta su Higgsfield».'}
            </p>
          ) : (
            pending.map((a) => (
              <div className="lab-attempt" key={a.id}>
                <p className="lab-attempt-title">
                  {SHOT_LABELS[a.shot] ?? a.shot} <small>· {a.model} · {a.created_at.slice(11, 16)}</small>
                </p>
                <p className="step-hint">{a.shot.startsWith('scena') ? 'Carica il video scaricato da Higgsfield.' : 'Carica la foto scaricata da Higgsfield, in originale.'}</p>
                <button type="button" className="link-btn" onClick={() => run(() => request(`/prove/${a.id}`, { method: 'DELETE' }), 'Non sono riuscito a toglierla')}>
                  Non l’ho fatta, togli
                </button>
              </div>
            ))
          )}
        </div>
        {last ? (
          <div className="action-bar">
            <label className="btn-mission lab-upload-main">
              Carica il risultato
              <input
                type="file"
                accept={last.shot.startsWith('scena') ? 'video/*,.mp4,.mov' : 'image/*,.heic,.heif'}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  e.target.value = '';
                  if (file) void upload(last, file);
                }}
              />
            </label>
          </div>
        ) : (
          bar(
            <button type="button" className="btn-mission" onClick={() => onStep(lab && lab.attempts.length > 0 ? 'valutare' : 'prompt')}>
              {lab && lab.attempts.length > 0 ? 'Vai a valutare' : 'Torna al prompt'}
            </button>,
          )
        )}
      </>
    );
  }

  // ---------- passo: scene video (abbigliamento) ----------
  if (step === 'scene') {
    const pickable = lab ? pickablePhotos(lab) : [];
    const chosen = sourceId || pickable[pickable.length - 1]?.id;
    const scenes = lab?.scenes ?? {};
    return (
      <>
        <div className="step-body">
          {errorBox}
          {pickable.length === 0 ? (
            <p className="step-hint">Quando hai caricato la foto del capo indossato, scegli qui quella da animare: lo Studio scrive le scene per Seedance 2.5.</p>
          ) : (
            <>
              <p className="step-hint">Parti da questa foto: sarà il primo fotogramma di ogni scena.</p>
              <div className="lab-pick">
                {pickable.map((a) => (
                  <button key={a.id} type="button" className="lab-pick-item" aria-pressed={chosen === a.id} onClick={() => setSourceId(a.id)}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={`${base}/prove/${a.id}/risultato?w=200&v=${a.result}`} alt="Foto indossata" />
                    <span>{a.rating > 0 ? `voto ${a.rating}` : 'senza voto'}</span>
                  </button>
                ))}
              </div>
            </>
          )}
          {lab?.scenes_idea && <p className="step-hint">Idea: {lab.scenes_idea}</p>}
          {Object.entries(scenes).map(([key, sc]) => (
            <section className="lab-shot" key={key}>
              <h4>{SHOT_LABELS[key] ?? key}</h4>
              <textarea
                className="brief-area lab-prompt"
                rows={7}
                defaultValue={sc.text}
                key={sc.text}
                aria-label={`Prompt ${SHOT_LABELS[key] ?? key}`}
                onBlur={(e) => {
                  if (e.target.value.trim() !== sc.text.trim()) {
                    void run(() => request(`/prompt/${key}`, json('PUT', { text: e.target.value })), 'Non sono riuscito a salvare il prompt');
                  }
                }}
              />
              <div className="draft-actions">
                <button type="button" className="btn-secondary" onClick={() => copy(key, sc.text)}>
                  {copied === key ? 'Copiato ✓' : 'Copia'}
                </button>
                <button type="button" className="btn-secondary" onClick={() => markDone(key)}>
                  Fatta su Higgsfield
                </button>
              </div>
            </section>
          ))}
          {Object.keys(scenes).length > 0 && (
            <p className="step-hint">Chiedi 1080p su Higgsfield: l&apos;uscita normale è 854x480 e sul sito è morbida.</p>
          )}
        </div>
        {bar(
          <button type="button" className="btn-mission" onClick={makeScenes} disabled={busy || pickable.length === 0}>
            {busy ? WORKING_TEXT[workingIndex] : Object.keys(scenes).length > 0 ? 'Riscrivi le scene' : 'Prepara le scene video'}
          </button>,
        )}
      </>
    );
  }

  // ---------- passo: valutare ----------
  const rated = (lab?.attempts ?? []).filter((a) => a.result);
  const abbigliamento = lab?.category === 'abbigliamento';
  const hasPhotoRated = lab ? pickablePhotos(lab).some((a) => a.rating > 0) : false;
  return (
    <>
      <div className="step-body">
        {errorBox}
        {rated.length === 0 && <p className="step-hint">Nessun risultato da valutare. Carica prima la foto fatta su Higgsfield.</p>}
        {rated.map((attempt) => {
          const critique = attempt.critique;
          return (
            <div className="lab-attempt" key={attempt.id}>
              <p className="lab-attempt-title">
                {SHOT_LABELS[attempt.shot] ?? attempt.shot} <small>· {attempt.model} · {attempt.created_at.slice(11, 16)}</small>
              </p>
              <div className="lab-compare">
                <figure>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  {realPhoto && <img src={realPhoto} alt="Foto vera" />}
                  <figcaption>Foto vera</figcaption>
                </figure>
                <figure>
                  {isVideo(attempt.result) ? (
                    <video src={`${base}/prove/${attempt.id}/risultato`} controls muted playsInline loop />
                  ) : (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={`${base}/prove/${attempt.id}/risultato?w=900&v=${attempt.result}`} alt="Risultato" />
                  )}
                  <figcaption>{isVideo(attempt.result) ? 'Video' : 'Creata'} con {attempt.model}</figcaption>
                </figure>
              </div>

              <div className="lab-judge">
                <button type="button" className="btn-secondary" onClick={() => judge(attempt)} disabled={judging === attempt.id || codex?.installed === false}>
                  {judging === attempt.id ? 'Codex sta guardando…' : critique ? 'Fai rivalutare a Codex' : 'Fai valutare a Codex'}
                </button>
              </div>

              {critique && (
                <div className="lab-critique">
                  <header>
                    <strong>Codex propone {critique.voto_proposto || '?'}/5</strong>
                    <small>{critique.codex_model}</small>
                  </header>
                  <ul className="lab-checks">
                    {Object.entries(critique.checklist).map(([key, item]) => (
                      <li key={key} className={`lab-esito lab-esito-${item.esito}`} title={item.nota}>
                        <span>{item.label}</span> <b>{ESITO_LABEL[item.esito]}</b>
                      </li>
                    ))}
                  </ul>
                  <p>{critique.giudizio}</p>
                  {critique.correzione && <p className="step-hint">Da cambiare: {critique.correzione}</p>}
                  <div className="draft-actions">
                    {critique.voto_proposto > 0 && (
                      <button
                        type="button"
                        className="chip-btn"
                        onClick={() => run(() => request(`/prove/${attempt.id}`, json('PUT', { rating: critique.voto_proposto, note: attempt.note })), 'Non sono riuscito a salvare il voto')}
                      >
                        Uso il suo voto ({critique.voto_proposto})
                      </button>
                    )}
                    {critique.prompt_corretto && (
                      <>
                        <button type="button" className="chip-btn" onClick={() => copy(`fix-${attempt.id}`, critique.prompt_corretto)}>
                          {copied === `fix-${attempt.id}` ? 'Copiato ✓' : 'Copia il prompt corretto'}
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

              <p className="lab-vote-label">Il tuo voto</p>
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
                className="link-btn"
                onClick={() => run(() => request(`/prove/${attempt.id}`, { method: 'DELETE' }), 'Non sono riuscito a toglierla')}
              >
                Elimina questa prova
              </button>
            </div>
          );
        })}
      </div>
      {abbigliamento && hasPhotoRated
        ? bar(
            <button type="button" className="btn-mission" onClick={() => onStep('scene')}>
              Continua con le scene video
            </button>,
            <button type="button" className="btn-secondary" onClick={onDone}>
              Torna all&apos;elenco
            </button>,
          )
        : bar(
            <button type="button" className="btn-mission" onClick={onDone}>
              Fatto, torna all&apos;elenco
            </button>,
          )}
    </>
  );
}

function pickablePhotos(lab: Lab): Attempt[] {
  return lab.attempts.filter((a) => a.result && !a.shot.startsWith('scena') && !isVideo(a.result));
}
