'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

// ── CONFIG ──────────────────────────────────────────────────────────────────
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://monili-backend.onrender.com';
const ACTIVE_REEL_KEY = 'monili_active_reel_id';
const POLL_MS = 3000;

// ── TIPI ────────────────────────────────────────────────────────────────────
type ReelStatus = 'planning' | 'storyboard_ready' | 'rendering' | 'done' | 'error';
type ReelFormat = 'reel' | 'story';

interface Shot {
  id: string;
  purpose: string;
  source: 'ai' | 'clip';
  clip_index: number | null;
  clip_start: number;
  photo_index: number;
  keyframe_mode: 'ai' | 'original_photo';
  use_model: boolean;
  end_on_product: boolean;
  duration: number;
  camera: string;
  angle: string;
  lighting: string;
  action: string;
  transition_out: string;
  on_screen_text: string;
  keyframe_prompt_en: string;
  motion_prompt_en: string;
}

interface Storyboard {
  title: string;
  concept: string;
  hook: string;
  music_mood: string;
  cover_text: string;
  scene_bible: string;
  shots: Shot[];
}

interface Estimate {
  exact: boolean;
  lines: { shot: string; label: string; usd: number; eur: number; credits?: number | null }[];
  total_usd: number;
  total_eur: number;
  budget_eur: number;
  over_budget: boolean;
  preview_mode: boolean;
  note: string;
}

interface ReelLog {
  time: string;
  agent: string;
  msg: string;
  type: 'info' | 'success' | 'warn' | 'data';
}

interface ReelCopy {
  caption?: string;
  caption_short?: string;
  hashtags?: string[];
  cover_text?: string;
  first_comment?: string;
  story_stickers?: string[];
  music_suggestion?: string;
  best_slot?: string;
  alt_text?: string;
}

interface QaResult {
  ok: boolean;
  score: number | null;
  issues: string;
  checked?: boolean;
}

interface Persona {
  name: string;
  description: string;
  reference_image: string | null;
  updated_at: string | null;
}

interface Recipe {
  id: string;
  label: string;
  description: string;
  formats: ReelFormat[];
  uses_model: boolean;
  default_seconds?: number;
}

interface ReelState {
  id: string;
  status: ReelStatus;
  format: ReelFormat;
  recipe?: string;
  poster_cover?: boolean;
  brief: string;
  target_seconds: number;
  video_model: string;
  higgsfield_configured: boolean;
  photos: string[];
  clips: { src: string; duration: number }[];
  storyboard: Storyboard | null;
  estimate: Estimate | null;
  logs: ReelLog[];
  error: string | null;
  results: {
    final_video?: string;
    cover?: string;
    cover_plain?: string;
    cover_qa?: QaResult | null;
    qa_warnings?: { id: string; score: number | null; issues: string }[];
    qa_replaced?: { id: string; issues: string }[];
    copy_markdown?: string;
    shots?: { id: string; video: string; keyframe: string | null; duration: number; engine: string; qa?: QaResult | null }[];
    copy?: ReelCopy;
    preview_only?: boolean;
    fallback_used?: boolean;
  };
}

interface ReelConfig {
  higgsfield_configured: boolean;
  video_models: { id: string; label: string; min_duration: number; max_duration: number }[];
  default_video_model: string;
  formats: Record<ReelFormat, { label: string; min_seconds: number; max_seconds: number; default_seconds: number }>;
  transitions: string[];
  purposes: string[];
  budget_eur: number;
  recipes: Recipe[];
  default_recipe: string;
  keyframe_models: string[];
  default_keyframe_model: string;
  openai_direct_configured?: boolean;
  persona: Persona;
}

interface ReelListItem {
  id: string;
  status: ReelStatus;
  format: ReelFormat;
  title: string;
  created_at: string;
  final_video?: string;
  cover?: string;
}

const PURPOSE_LABELS: Record<string, string> = {
  hook: 'Hook (primi secondi)',
  dettaglio: 'Dettaglio prodotto',
  indossato: 'Indossato',
  lifestyle: 'Lifestyle',
  outfit: 'Outfit',
  cta: 'Chiusura / CTA',
};
const TRANSITION_LABELS: Record<string, string> = {
  cut: 'Stacco netto',
  dissolve: 'Dissolvenza',
  fade: 'Fade',
  slide: 'Scorrimento',
  slide_up: 'Scorrimento in alto',
  zoom: 'Zoom',
  wipe: 'Tendina',
  circle: 'Cerchio',
};
const STATUS_LABELS: Record<ReelStatus, string> = {
  planning: 'Storyboard in preparazione',
  storyboard_ready: 'Storyboard da approvare',
  rendering: 'Video in produzione',
  done: 'Pronto',
  error: 'Errore',
};

const IMAGE_MODEL_LABELS: Record<string, string> = {
  'openai-direct/gpt-image-2.5-flare': 'GPT-Image-2.5 Flare (OpenAI, consigliato)',
  'openai-direct/gpt-image-2.5-sunburst': 'GPT-Image-2.5 Sunburst (OpenAI, massima precisione)',
  'openai-direct/gpt-image-2': 'GPT-Image-2 (OpenAI diretto)',
  'openai/gpt-5.4-image-2': 'GPT-Image-2 via OpenRouter',
  'google/gemini-3.1-flash-image-preview': 'Gemini Flash Image (veloce)',
  'google/gemini-3.1-flash-image': 'Gemini Flash Image',
  'google/gemini-3-pro-image': 'Gemini 3 Pro Image',
};

const fileUrl = (path: string) => `${API_URL}/files/${path}`;

function emptyShot(index: number): Shot {
  return {
    id: `shot_${index + 1}`,
    purpose: 'lifestyle',
    source: 'ai',
    clip_index: null,
    clip_start: 0,
    photo_index: 0,
    keyframe_mode: 'ai',
    use_model: false,
    end_on_product: false,
    duration: 4,
    camera: 'slow push-in',
    angle: '',
    lighting: 'luce naturale calda',
    action: '',
    transition_out: 'dissolve',
    on_screen_text: '',
    keyframe_prompt_en: '',
    motion_prompt_en: '',
  };
}

async function saveFileToDevice(url: string, filename: string) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const blob = await response.blob();
  const file = new File([blob], filename, { type: blob.type || 'video/mp4' });
  const nav = navigator as Navigator & { canShare?: (data?: ShareData) => boolean };
  if (nav.share && nav.canShare?.({ files: [file] })) {
    await nav.share({ files: [file], title: filename });
    return;
  }
  const blobUrl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(blobUrl);
}

async function readError(res: Response) {
  try {
    const data = await res.json();
    return data.error || `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}

// ── COMPONENTI PICCOLI ──────────────────────────────────────────────────────
function CopyButton({ text, label = 'Copia' }: { text: string; label?: string }) {
  const [done, setDone] = useState(false);
  return (
    <button
      type="button"
      className="btn-secondary rs-small-btn"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setDone(true);
          setTimeout(() => setDone(false), 1500);
        } catch {
          /* clipboard non disponibile */
        }
      }}
    >
      {done ? 'Copiato ✓' : label}
    </button>
  );
}

function LogFeed({ logs }: { logs: ReelLog[] }) {
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'nearest' });
  }, [logs.length]);
  return (
    <div className="rs-log">
      {logs.slice(-60).map((line, index) => (
        <div key={index} className={`rs-log-line rs-log-${line.type}`}>
          <span className="rs-log-time">{line.time}</span>
          <span className="rs-log-agent">{line.agent}</span>
          <span>{line.msg}</span>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="rs-field">
      <span className="rs-field-label">{label}</span>
      {children}
    </label>
  );
}

// ── PAGINA ──────────────────────────────────────────────────────────────────
export default function ReelStudioPage() {
  const [config, setConfig] = useState<ReelConfig | null>(null);
  const [reel, setReel] = useState<ReelState | null>(null);
  const [history, setHistory] = useState<ReelListItem[]>([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  // form
  const [photos, setPhotos] = useState<File[]>([]);
  const [clips, setClips] = useState<File[]>([]);
  const [brief, setBrief] = useState('');
  const [format, setFormat] = useState<ReelFormat>('reel');
  const [seconds, setSeconds] = useState(12);
  const [videoModel, setVideoModel] = useState('');
  const [recipe, setRecipe] = useState('libera');
  const [keyframeModel, setKeyframeModel] = useState('');
  const [posterCover, setPosterCover] = useState(true);
  const [persona, setPersona] = useState<Persona | null>(null);

  const photoPreviews = useMemo(() => photos.map((file) => URL.createObjectURL(file)), [photos]);
  useEffect(() => () => photoPreviews.forEach((url) => URL.revokeObjectURL(url)), [photoPreviews]);

  // storyboard in modifica
  const [draft, setDraft] = useState<Storyboard | null>(null);
  const [dirty, setDirty] = useState(false);

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/reels?limit=12`);
      if (res.ok) setHistory((await res.json()).items || []);
    } catch {
      /* backend non raggiungibile */
    }
  }, []);

  const loadReel = useCallback(async (id: string) => {
    const res = await fetch(`${API_URL}/reel/${encodeURIComponent(id)}`, { cache: 'no-store' });
    if (res.status === 404) {
      try { localStorage.removeItem(ACTIVE_REEL_KEY); } catch { /* storage non disponibile */ }
      setReel(null);
      return null;
    }
    if (!res.ok) throw new Error(await readError(res));
    const data: ReelState = await res.json();
    setReel(data);
    return data;
  }, []);

  // avvio: config + recupero reel attivo
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_URL}/reel/config`);
        if (res.ok) {
          const cfg: ReelConfig = await res.json();
          setConfig(cfg);
          setVideoModel(cfg.default_video_model);
          setRecipe(cfg.default_recipe || 'libera');
          setKeyframeModel(cfg.default_keyframe_model || '');
          setPersona(cfg.persona || null);
        } else {
          setError('Backend raggiungibile ma Reel Studio non attivo: aggiorna il backend.');
        }
      } catch {
        setError(`Backend non raggiungibile su ${API_URL}`);
      }
      let saved = '';
      try { saved = localStorage.getItem(ACTIVE_REEL_KEY) || ''; } catch { /* storage non disponibile */ }
      if (saved) {
        try { await loadReel(saved); } catch { /* reel non piu disponibile */ }
      }
      loadHistory();
    })();
  }, [loadReel, loadHistory]);

  // polling mentre il backend lavora
  useEffect(() => {
    if (!reel || (reel.status !== 'planning' && reel.status !== 'rendering')) return;
    const timer = setInterval(() => {
      loadReel(reel.id).catch(() => undefined);
    }, POLL_MS);
    return () => clearInterval(timer);
  }, [reel, loadReel]);

  // sincronizza la bozza quando arriva un nuovo storyboard
  useEffect(() => {
    if (reel?.storyboard && !dirty) setDraft(JSON.parse(JSON.stringify(reel.storyboard)));
    if (reel?.status === 'done') loadHistory();
  }, [reel?.storyboard, reel?.status, dirty, loadHistory]);

  useEffect(() => {
    if (!config) return;
    const spec = config.formats[format];
    setSeconds(spec.default_seconds);
  }, [format, config]);

  const openReel = async (id: string) => {
    setError('');
    setDirty(false);
    try { localStorage.setItem(ACTIVE_REEL_KEY, id); } catch { /* storage non disponibile */ }
    try {
      await loadReel(id);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (exc) {
      setError(String(exc));
    }
  };

  const newReel = () => {
    try { localStorage.removeItem(ACTIVE_REEL_KEY); } catch { /* storage non disponibile */ }
    setReel(null);
    setDraft(null);
    setDirty(false);
    setError('');
    setPhotos([]);
    setClips([]);
    setBrief('');
    loadHistory();
  };

  const createReel = async () => {
    if (!photos.length) {
      setError('Carica almeno una foto del prodotto.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const form = new FormData();
      photos.forEach((file) => form.append('photos', file));
      clips.forEach((file) => form.append('clips', file));
      form.append('brief', brief);
      form.append('format', format);
      form.append('target_seconds', String(seconds));
      form.append('video_model', videoModel);
      form.append('recipe', recipe);
      if (keyframeModel) form.append('keyframe_model', keyframeModel);
      form.append('poster_cover', posterCover ? 'true' : 'false');
      const res = await fetch(`${API_URL}/reel/create`, { method: 'POST', body: form });
      if (!res.ok) throw new Error(await readError(res));
      const data: ReelState = await res.json();
      try { localStorage.setItem(ACTIVE_REEL_KEY, data.id); } catch { /* storage non disponibile */ }
      setDirty(false);
      setReel(data);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  };

  const saveDraft = async (): Promise<ReelState | null> => {
    if (!reel || !draft) return null;
    const res = await fetch(`${API_URL}/reel/${reel.id}/storyboard`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ storyboard: draft, video_model: reel.video_model }),
    });
    if (!res.ok) throw new Error(await readError(res));
    const data: ReelState = await res.json();
    setReel(data);
    setDirty(false);
    return data;
  };

  const recalc = async () => {
    setBusy(true);
    setError('');
    try {
      await saveDraft();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  };

  const changeVideoModel = async (model: string) => {
    if (!reel || !draft) return;
    setBusy(true);
    try {
      const res = await fetch(`${API_URL}/reel/${reel.id}/storyboard`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ storyboard: draft, video_model: model }),
      });
      if (!res.ok) throw new Error(await readError(res));
      setReel(await res.json());
      setDirty(false);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  };

  const render = async () => {
    if (!reel) return;
    setBusy(true);
    setError('');
    try {
      let current = reel;
      if (dirty) current = (await saveDraft()) || reel;
      const estimate = current.estimate;
      let confirmOver = false;
      if (estimate?.over_budget) {
        confirmOver = window.confirm(
          `Costo stimato ${estimate.total_eur.toFixed(2)} € — sopra il tuo budget di ${estimate.budget_eur.toFixed(2)} €. Procedo lo stesso?`,
        );
        if (!confirmOver) return;
      }
      const res = await fetch(`${API_URL}/reel/${current.id}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_over_budget: confirmOver }),
      });
      if (!res.ok) throw new Error(await readError(res));
      setReel(await res.json());
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  };

  const updateShot = (index: number, patch: Partial<Shot>) => {
    if (!draft) return;
    const shots = draft.shots.map((shot, i) => (i === index ? { ...shot, ...patch } : shot));
    setDraft({ ...draft, shots });
    setDirty(true);
  };

  const moveShot = (index: number, delta: number) => {
    if (!draft) return;
    const target = index + delta;
    if (target < 0 || target >= draft.shots.length) return;
    const shots = [...draft.shots];
    [shots[index], shots[target]] = [shots[target], shots[index]];
    setDraft({ ...draft, shots });
    setDirty(true);
  };

  const removeShot = (index: number) => {
    if (!draft || draft.shots.length <= 1) return;
    setDraft({ ...draft, shots: draft.shots.filter((_, i) => i !== index) });
    setDirty(true);
  };

  const addShot = () => {
    if (!draft || draft.shots.length >= 6) return;
    setDraft({ ...draft, shots: [...draft.shots, emptyShot(draft.shots.length)] });
    setDirty(true);
  };

  const totalSeconds = draft?.shots.reduce((sum, shot) => sum + Number(shot.duration || 0), 0) ?? 0;
  const hfReady = reel ? reel.higgsfield_configured : config?.higgsfield_configured;
  const editable = reel && (reel.status === 'storyboard_ready' || reel.status === 'error' || reel.status === 'done') && draft;

  return (
    <div className="rs-page">
      <header className="app-header sticky top-0 z-50">
        <div className="rs-header">
          <span className="rs-header-links">
            <a href="/" className="rs-back">← Foto</a>
            <a href="/skills" className="rs-back">Skill</a>
            <a href="/risultati" className="rs-back">Risultati</a>
          </span>
          <div className="rs-brand">
            <span className="rs-brand-title">Reel Studio</span>
            <span className="rs-brand-sub">I Monili · video-first</span>
          </div>
          <span className={`rs-engine ${hfReady ? 'rs-engine-on' : 'rs-engine-off'}`}>
            {hfReady ? 'Higgsfield attivo' : 'Modalità anteprima'}
          </span>
        </div>
      </header>

      <main className="rs-main">
        {!hfReady && config && (
          <div className="rs-banner">
            <strong>Higgsfield non ancora collegato.</strong> Puoi provare tutto il flusso: i video vengono creati
            animando i fotogrammi chiave (anteprima gratuita, solo costi OpenRouter). Quando inserisci la API key nel
            backend, le stesse inquadrature diventano video AI veri.
          </div>
        )}
        {error && <div className="rs-error">{error}</div>}

        {/* ── NUOVO REEL ─────────────────────────────────────────────── */}
        {!reel && (
          <section className="card rs-card">
            <div className="label-eyebrow">Nuovo contenuto video</div>
            <h1 className="rs-h1">Dalla foto al Reel</h1>
            <p className="rs-muted">
              Carica 1-3 foto del prodotto. Se vuoi, aggiungi fino a 3 clip vere girate in negozio: il regista AI le
              mescola con le scene generate. Senza clip, fa tutto l&apos;AI.
            </p>

            <div className="rs-grid-2">
              <Field label={`Foto prodotto (${photos.length}/3)`}>
                <input
                  type="file"
                  accept="image/*,.heic,.heif"
                  multiple
                  onChange={(e) => setPhotos(Array.from(e.target.files || []).slice(0, 3))}
                />
              </Field>
              <Field label={`Clip reali facoltative (${clips.length}/3)`}>
                <input
                  type="file"
                  accept="video/mp4,video/quicktime,.mov,.mp4,.m4v"
                  multiple
                  onChange={(e) => setClips(Array.from(e.target.files || []).slice(0, 3))}
                />
              </Field>
            </div>

            {photos.length > 0 && (
              <div className="rs-thumbs">
                {photoPreviews.map((url, i) => (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img key={url} src={url} alt={`foto ${i + 1}`} />
                ))}
              </div>
            )}

            <Field label="Brief (facoltativo)">
              <textarea
                className="brief-area"
                rows={3}
                value={brief}
                onChange={(e) => setBrief(e.target.value)}
                placeholder="Es. orecchini per le serate di novembre, prezzo 39€, mood elegante ma non troppo"
              />
            </Field>

            <Field label="Ricetta">
              <div className="rs-recipes">
                {(config?.recipes || []).map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={`rs-recipe ${recipe === item.id ? 'rs-recipe-on' : ''}`}
                    onClick={() => {
                      setRecipe(item.id);
                      const nextFormat = item.formats.includes(format) ? format : item.formats[0];
                      if (nextFormat !== format) setFormat(nextFormat);
                      if (item.default_seconds && config) {
                        const spec = config.formats[nextFormat];
                        setTimeout(() => setSeconds(Math.min(spec.max_seconds, Math.max(spec.min_seconds, item.default_seconds!))), 0);
                      }
                    }}
                  >
                    <span className="rs-recipe-title">/{item.id}</span>
                    <span className="rs-recipe-label">{item.label}</span>
                    <span className="rs-recipe-desc">{item.description}</span>
                  </button>
                ))}
              </div>
            </Field>

            {config?.recipes.find((item) => item.id === recipe)?.uses_model && (
              <PersonaPanel persona={persona} onSaved={setPersona} />
            )}

            <div className="rs-grid-3">
              <Field label="Formato">
                <div className="rs-toggle">
                  {(['reel', 'story'] as ReelFormat[]).map((item) => (
                    <button
                      key={item}
                      type="button"
                      className={format === item ? 'btn-mission rs-toggle-btn' : 'btn-secondary rs-toggle-btn'}
                      onClick={() => setFormat(item)}
                    >
                      {item === 'reel' ? 'Reel' : 'Story video'}
                    </button>
                  ))}
                </div>
              </Field>
              <Field label={`Durata: ${seconds}s`}>
                <input
                  type="range"
                  min={config?.formats[format].min_seconds ?? 5}
                  max={config?.formats[format].max_seconds ?? 20}
                  value={seconds}
                  onChange={(e) => setSeconds(Number(e.target.value))}
                />
              </Field>
              <Field label="Motore immagini">
                <select value={keyframeModel} onChange={(e) => setKeyframeModel(e.target.value)} className="rs-input">
                  {(config?.keyframe_models || []).map((model) => (
                    <option key={model} value={model}>{IMAGE_MODEL_LABELS[model] || model}</option>
                  ))}
                </select>
              </Field>
              <Field label="Motore video">
                <select value={videoModel} onChange={(e) => setVideoModel(e.target.value)} className="rs-input">
                  {config?.video_models.map((model) => (
                    <option key={model.id} value={model.id}>{model.label}</option>
                  ))}
                </select>
              </Field>
            </div>

            <label className="rs-check">
              <input type="checkbox" checked={posterCover} onChange={(e) => setPosterCover(e.target.checked)} />
              <span>Copertina poster in stile Monili (serif su fondo crema, ~0,12 €)</span>
            </label>

            <button type="button" className="btn-mission rs-cta" disabled={busy || !photos.length || !config} onClick={createReel}>
              {busy ? 'Caricamento...' : 'Crea storyboard'}
            </button>
            <p className="rs-hint">Prima vedi lo storyboard e il costo stimato: i crediti video si spendono solo quando approvi.</p>
          </section>
        )}

        {/* ── REEL ATTIVO ────────────────────────────────────────────── */}
        {reel && (
          <section className="card rs-card">
            <div className="rs-reel-head">
              <div>
                <div className="label-eyebrow">
                  {reel.format === 'story' ? 'Story video' : 'Reel'}
                  {reel.recipe && reel.recipe !== 'libera' ? ` · /${reel.recipe}` : ''} · {STATUS_LABELS[reel.status]}
                </div>
                <h1 className="rs-h1">{reel.storyboard?.title || 'Nuovo reel'}</h1>
                {reel.storyboard?.concept && <p className="rs-muted">{reel.storyboard.concept}</p>}
              </div>
              <button type="button" className="btn-secondary rs-small-btn" onClick={newReel}>+ Nuovo</button>
            </div>

            {(reel.status === 'planning' || reel.status === 'rendering') && (
              <div className="rs-working">
                <span className="status-dot active" />
                {reel.status === 'planning'
                  ? 'Il regista sta analizzando il prodotto e scrivendo lo storyboard (1-2 minuti)...'
                  : 'Produzione in corso: fotogrammi, video, montaggio e testi. Con Higgsfield servono alcuni minuti per inquadratura.'}
              </div>
            )}

            {reel.status === 'error' && reel.error && <div className="rs-error">{reel.error}</div>}

            {/* risultato */}
            {reel.status === 'done' && reel.results.final_video && (
              <ResultView reel={reel} onPersona={setPersona} />
            )}

            {/* storyboard */}
            {editable && draft && (
              <details className="rs-storyboard-wrap" open={reel.status !== 'done'}>
              <summary className="rs-storyboard-summary">{reel.status === 'done' ? 'Modifica lo storyboard e rigenera' : `Storyboard · ${draft.shots.length} inquadrature · ${totalSeconds.toFixed(0)}s`}</summary>
              <div className="rs-storyboard">
                <div className="rs-grid-2">
                  <Field label="Hook (primi 1,5 secondi)">
                    <input className="rs-input" value={draft.hook} onChange={(e) => { setDraft({ ...draft, hook: e.target.value }); setDirty(true); }} />
                  </Field>
                  <Field label="Testo copertina">
                    <input className="rs-input" value={draft.cover_text} onChange={(e) => { setDraft({ ...draft, cover_text: e.target.value }); setDirty(true); }} />
                  </Field>
                </div>
                <Field label="Scena unica del video (vale per tutte le inquadrature AI)">
                  <textarea
                    className="brief-area"
                    rows={3}
                    value={draft.scene_bible || ''}
                    onChange={(e) => { setDraft({ ...draft, scene_bible: e.target.value }); setDirty(true); }}
                  />
                </Field>
                <div className="rs-muted rs-small">Audio consigliato: {draft.music_mood || '—'} (sceglilo tra gli audio di tendenza su Instagram)</div>

                <div className="rs-shots">
                  {draft.shots.map((shot, index) => (
                    <ShotEditor
                      key={`${shot.id}-${index}`}
                      shot={shot}
                      index={index}
                      count={draft.shots.length}
                      reel={reel}
                      config={config}
                      onChange={(patch) => updateShot(index, patch)}
                      onMove={(delta) => moveShot(index, delta)}
                      onRemove={() => removeShot(index)}
                    />
                  ))}
                </div>
                {draft.shots.length < 6 && (
                  <button type="button" className="btn-secondary rs-small-btn" onClick={addShot}>+ Aggiungi inquadratura</button>
                )}

                <EstimatePanel
                  estimate={reel.estimate}
                  dirty={dirty}
                  totalSeconds={totalSeconds}
                  videoModel={reel.video_model}
                  config={config}
                  busy={busy}
                  onModelChange={changeVideoModel}
                  onRecalc={recalc}
                />

                <button type="button" className="btn-mission rs-cta" disabled={busy} onClick={render}>
                  {busy ? 'Attendi...' : reel.status === 'done' ? 'Rigenera il video' : reel.higgsfield_configured ? 'Approva e genera il video' : 'Genera anteprima video'}
                </button>
              </div>
              </details>
            )}

            {reel.logs.length > 0 && (
              <details className="rs-details" open={reel.status === 'planning' || reel.status === 'rendering' || reel.status === 'error'}>
                <summary>Diario di produzione ({reel.logs.length})</summary>
                <LogFeed logs={reel.logs} />
              </details>
            )}
          </section>
        )}

        {/* ── ARCHIVIO ───────────────────────────────────────────────── */}
        {history.length > 0 && (
          <section className="rs-history">
            <div className="rs-section-title">Archivio video</div>
            <div className="rs-history-grid">
              {history.map((item) => (
                <button key={item.id} type="button" className="rs-history-item" onClick={() => openReel(item.id)}>
                  {item.cover ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={fileUrl(item.cover)} alt={item.title} />
                  ) : (
                    <div className="rs-history-placeholder">{item.format === 'story' ? 'Story' : 'Reel'}</div>
                  )}
                  <span className="rs-history-title">{item.title || item.id}</span>
                  <span className="rs-history-status">{STATUS_LABELS[item.status] || item.status}</span>
                </button>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

// ── EDITOR INQUADRATURA ─────────────────────────────────────────────────────
function ShotEditor({
  shot, index, count, reel, config, onChange, onMove, onRemove,
}: {
  shot: Shot;
  index: number;
  count: number;
  reel: ReelState;
  config: ReelConfig | null;
  onChange: (patch: Partial<Shot>) => void;
  onMove: (delta: number) => void;
  onRemove: () => void;
}) {
  const produced = reel.results.shots?.find((item) => item.id === shot.id);
  const thumb = produced?.keyframe || (shot.source === 'ai' ? reel.photos[shot.photo_index] : null);
  const purposes = config?.purposes || Object.keys(PURPOSE_LABELS);
  const transitions = config?.transitions || Object.keys(TRANSITION_LABELS);
  return (
    <div className="rs-shot">
      <div className="rs-shot-head">
        <span className="step-badge">{index + 1}</span>
        <select className="rs-input rs-shot-purpose" value={shot.purpose} onChange={(e) => onChange({ purpose: e.target.value })}>
          {purposes.map((p) => <option key={p} value={p}>{PURPOSE_LABELS[p] || p}</option>)}
        </select>
        <div className="rs-shot-tools">
          <button type="button" className="btn-ghost" disabled={index === 0} onClick={() => onMove(-1)} aria-label="Sposta su">↑</button>
          <button type="button" className="btn-ghost" disabled={index === count - 1} onClick={() => onMove(1)} aria-label="Sposta giu">↓</button>
          <button type="button" className="btn-ghost" disabled={count <= 1} onClick={onRemove} aria-label="Elimina">✕</button>
        </div>
      </div>

      <div className="rs-shot-body">
        {thumb && (
          // eslint-disable-next-line @next/next/no-img-element
          <img className="rs-shot-thumb" src={fileUrl(thumb)} alt={`inquadratura ${index + 1}`} />
        )}
        <div className="rs-shot-fields">
          <div className="rs-grid-3">
            <Field label="Fonte">
              <select
                className="rs-input"
                value={shot.source}
                onChange={(e) => {
                  const source = e.target.value as Shot['source'];
                  onChange({ source, clip_index: source === 'clip' ? (shot.clip_index ?? 0) : null });
                }}
              >
                <option value="ai">Scena AI</option>
                {reel.clips.length > 0 && <option value="clip">Clip reale</option>}
              </select>
            </Field>
            {shot.source === 'clip' ? (
              <Field label="Quale clip">
                <select className="rs-input" value={shot.clip_index ?? 0} onChange={(e) => onChange({ clip_index: Number(e.target.value) })}>
                  {reel.clips.map((clip, i) => <option key={i} value={i}>Clip {i + 1} ({clip.duration}s)</option>)}
                </select>
              </Field>
            ) : (
              <Field label="Fotogramma">
                <select className="rs-input" value={shot.keyframe_mode} onChange={(e) => onChange({ keyframe_mode: e.target.value as Shot['keyframe_mode'] })}>
                  <option value="ai">Scena AI dal prodotto</option>
                  <option value="original_photo">Foto reale (massima fedeltà)</option>
                </select>
              </Field>
            )}
            <Field label="Durata (s)">
              <input
                className="rs-input"
                type="number"
                min={1}
                max={15}
                step={shot.source === 'clip' ? 0.5 : 1}
                value={shot.duration}
                onChange={(e) => onChange({ duration: Number(e.target.value) })}
              />
            </Field>
          </div>
          {shot.source === 'ai' && shot.keyframe_mode === 'ai' && (
            <label className="rs-check">
              <input type="checkbox" checked={!!shot.use_model} onChange={(e) => onChange({ use_model: e.target.checked })} />
              <span>Con la Modella Monili</span>
            </label>
          )}
          {shot.source === 'ai' && (
            <label className="rs-check">
              <input type="checkbox" checked={!!shot.end_on_product} onChange={(e) => onChange({ end_on_product: e.target.checked })} />
              <span>Finisci la scena sulla foto vera del prodotto</span>
            </label>
          )}
          {shot.source === 'clip' && (
            <Field label="Parti dal secondo">
              <input className="rs-input" type="number" min={0} max={Math.max(0, (reel.clips[shot.clip_index ?? 0]?.duration ?? 1) - 1)} step={0.5} value={shot.clip_start} onChange={(e) => onChange({ clip_start: Number(e.target.value) })} />
            </Field>
          )}
          {shot.source === 'ai' && reel.photos.length > 1 && (
            <Field label="Foto di partenza">
              <select className="rs-input" value={shot.photo_index} onChange={(e) => onChange({ photo_index: Number(e.target.value) })}>
                {reel.photos.map((_, i) => <option key={i} value={i}>Foto {i + 1}</option>)}
              </select>
            </Field>
          )}
          <Field label="Cosa succede">
            <textarea className="brief-area" rows={2} value={shot.action} onChange={(e) => onChange({ action: e.target.value })} />
          </Field>
          <Field label="Testo a schermo">
            <input className="rs-input" value={shot.on_screen_text} onChange={(e) => onChange({ on_screen_text: e.target.value })} />
          </Field>
          <details className="rs-details">
            <summary>Regia: {[shot.camera, shot.lighting, index < count - 1 ? TRANSITION_LABELS[shot.transition_out] || shot.transition_out : ''].filter(Boolean).join(' · ') || 'camera, luce, transizione'}</summary>
          {shot.source === 'ai' && (
            <div className="rs-grid-3">
              <Field label="Camera">
                <input className="rs-input" value={shot.camera} onChange={(e) => onChange({ camera: e.target.value })} />
              </Field>
              <Field label="Angolazione">
                <input className="rs-input" value={shot.angle} onChange={(e) => onChange({ angle: e.target.value })} />
              </Field>
              <Field label="Luce">
                <input className="rs-input" value={shot.lighting} onChange={(e) => onChange({ lighting: e.target.value })} />
              </Field>
            </div>
          )}
          {index < count - 1 && (
            <Field label="Transizione verso la prossima">
              <select className="rs-input" value={shot.transition_out} onChange={(e) => onChange({ transition_out: e.target.value })}>
                {transitions.map((t) => <option key={t} value={t}>{TRANSITION_LABELS[t] || t}</option>)}
              </select>
            </Field>
          )}
          {shot.source === 'ai' && (
            <>
              <Field label="Prompt fotogramma chiave (inglese)">
                <textarea className="brief-area" rows={3} value={shot.keyframe_prompt_en} onChange={(e) => onChange({ keyframe_prompt_en: e.target.value })} />
              </Field>
              <Field label="Prompt movimento video (inglese)">
                <textarea className="brief-area" rows={3} value={shot.motion_prompt_en} onChange={(e) => onChange({ motion_prompt_en: e.target.value })} />
              </Field>
            </>
          )}
          </details>
        </div>
      </div>
    </div>
  );
}

// ── STIMA ───────────────────────────────────────────────────────────────────
function EstimatePanel({
  estimate, dirty, totalSeconds, videoModel, config, busy, onModelChange, onRecalc,
}: {
  estimate: Estimate | null;
  dirty: boolean;
  totalSeconds: number;
  videoModel: string;
  config: ReelConfig | null;
  busy: boolean;
  onModelChange: (model: string) => void;
  onRecalc: () => void;
}) {
  return (
    <div className={`rs-estimate ${estimate?.over_budget ? 'rs-estimate-over' : ''}`}>
      <div className="rs-estimate-top">
        <div>
          <div className="label-eyebrow">Costo stimato di questo video</div>
          <div className="rs-estimate-total">
            {dirty ? '—' : `${(estimate?.total_eur ?? 0).toFixed(2)} €`}
            <span className="rs-muted rs-small"> · budget {estimate?.budget_eur?.toFixed(2) ?? config?.budget_eur?.toFixed(2)} € · durata {totalSeconds.toFixed(1)}s</span>
          </div>
        </div>
        <select className="rs-input rs-model-select" value={videoModel} disabled={busy} onChange={(e) => onModelChange(e.target.value)}>
          {config?.video_models.map((model) => <option key={model.id} value={model.id}>{model.label}</option>)}
        </select>
      </div>
      {dirty ? (
        <button type="button" className="btn-secondary rs-small-btn" disabled={busy} onClick={onRecalc}>Salva modifiche e ricalcola</button>
      ) : (
        estimate && (
          <>
            <ul className="rs-estimate-lines">
              {estimate.lines.map((line, i) => (
                <li key={i}>
                  <span>{line.shot !== '-' ? `${line.shot.replace('shot_', '#')} · ` : ''}{line.label}</span>
                  <span>{line.eur.toFixed(2)} €</span>
                </li>
              ))}
            </ul>
            <div className="rs-muted rs-small">{estimate.note}{estimate.preview_mode ? ' In modalità anteprima il video AI non viene addebitato.' : ''}</div>
            {estimate.over_budget && <div className="rs-warn">Sopra il budget: accorcia o riduci le scene AI, oppure usa una clip reale.</div>}
          </>
        )
      )}
    </div>
  );
}

// ── RISULTATO ───────────────────────────────────────────────────────────────
function ResultView({ reel, onPersona }: { reel: ReelState; onPersona: (p: Persona) => void }) {
  const results = reel.results;
  const copy = results.copy || {};
  const [saving, setSaving] = useState('');
  const hashtags = (copy.hashtags || []).join(' ');
  const fullCaption = [copy.caption, hashtags].filter(Boolean).join('\n\n');

  const save = async (path: string, filename: string) => {
    setSaving(filename);
    try {
      await saveFileToDevice(fileUrl(path), filename);
    } catch {
      window.open(fileUrl(path), '_blank');
    } finally {
      setSaving('');
    }
  };

  return (
    <div className="rs-result">
      {results.preview_only && (
        <div className="rs-banner">Questa è un&apos;<strong>anteprima</strong>: le scene AI sono fotogrammi animati. Con Higgsfield collegato diventano video AI veri.</div>
      )}
      {results.qa_warnings && results.qa_warnings.length > 0 && (
        <div className="rs-error">
          <strong>Controlla prima di pubblicare:</strong> il controllo qualità ha trovato possibili differenze dal prodotto vero.
          <ul className="rs-list">
            {results.qa_warnings.map((w) => (
              <li key={w.id}>{w.id.replace('shot_', 'Inquadratura ')}: {w.score != null ? `${w.score}/10 — ` : ''}{w.issues || 'prodotto diverso'}</li>
            ))}
          </ul>
        </div>
      )}
      {results.qa_replaced && results.qa_replaced.length > 0 && (
        <div className="rs-banner">
          <strong>Prodotto protetto:</strong> in {results.qa_replaced.length === 1 ? 'una scena' : `${results.qa_replaced.length} scene`} l&apos;AI non era fedele al 100% e l&apos;app ha usato la tua foto reale.
        </div>
      )}
      {results.cover_qa && !results.cover_qa.ok && (
        <div className="rs-warn">Copertina poster da controllare: {results.cover_qa.issues || 'testo o prodotto non perfetti'}. C&apos;è anche la copertina foto.</div>
      )}
      {results.fallback_used && (
        <div className="rs-warn">Alcune inquadrature non sono riuscite con il video AI e sono state sostituite da un&apos;animazione del fotogramma. Vedi il diario.</div>
      )}
      <div className="rs-result-grid">
        <div className="rs-video-wrap">
          <video src={fileUrl(results.final_video!)} poster={results.cover ? fileUrl(results.cover) : undefined} controls playsInline loop />
          <div className="rs-actions">
            <button type="button" className="btn-mission rs-small-btn" onClick={() => save(results.final_video!, `monili-${reel.format}.mp4`)}>
              {saving.endsWith('.mp4') ? 'Salvo...' : 'Salva video'}
            </button>
          </div>
          <div className="rs-covers">
            {[results.cover, results.cover_plain].filter((c, i, arr): c is string => !!c && arr.indexOf(c) === i).map((cover, i) => (
              <button key={cover} type="button" className="rs-cover" onClick={() => save(cover, i === 0 ? 'copertina.jpg' : 'copertina-foto.jpg')}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={fileUrl(cover)} alt="copertina" />
                <span>{saving === (i === 0 ? 'copertina.jpg' : 'copertina-foto.jpg') ? 'Salvo...' : i === 0 && reel.poster_cover ? 'Salva copertina poster' : 'Salva copertina foto'}</span>
              </button>
            ))}
          </div>
          <ModelPicker reel={reel} onPersona={onPersona} />
        </div>

        <div className="rs-copy">
          <div className="rs-copy-block">
            <div className="rs-copy-head"><span>Caption + hashtag</span><CopyButton text={fullCaption} /></div>
            <pre>{fullCaption}</pre>
          </div>
          {copy.first_comment && (
            <div className="rs-copy-block">
              <div className="rs-copy-head"><span>Primo commento</span><CopyButton text={copy.first_comment} /></div>
              <pre>{copy.first_comment}</pre>
            </div>
          )}
          <div className="rs-copy-meta">
            {copy.best_slot && <div><strong>Quando:</strong> {copy.best_slot}</div>}
            {(copy.music_suggestion || reel.storyboard?.music_mood) && <div><strong>Audio:</strong> {copy.music_suggestion || reel.storyboard?.music_mood}</div>}
            {(copy.cover_text || reel.storyboard?.cover_text) && <div><strong>Copertina:</strong> {copy.cover_text || reel.storyboard?.cover_text}</div>}
          </div>
          {reel.storyboard?.shots.some((s) => s.on_screen_text) && (
            <div className="rs-copy-block">
              <div className="rs-copy-head"><span>Testi a schermo (aggiungili nell&apos;editor Instagram)</span></div>
              <ol className="rs-list">
                {reel.storyboard.shots.filter((s) => s.on_screen_text).map((s) => <li key={s.id}>{s.on_screen_text}</li>)}
              </ol>
            </div>
          )}
          {copy.story_stickers && copy.story_stickers.length > 0 && (
            <div className="rs-copy-block">
              <div className="rs-copy-head"><span>Sticker per le stories</span></div>
              <ul className="rs-list">{copy.story_stickers.map((s, i) => <li key={i}>{s}</li>)}</ul>
            </div>
          )}
          {copy.caption_short && (
            <div className="rs-copy-block">
              <div className="rs-copy-head"><span>Versione breve</span><CopyButton text={copy.caption_short} /></div>
              <pre>{copy.caption_short}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── MODELLA MONILI ──────────────────────────────────────────────────────────
function PersonaPanel({ persona, onSaved }: { persona: Persona | null; onSaved: (p: Persona) => void }) {
  const [description, setDescription] = useState(persona?.description || '');
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState('');
  useEffect(() => setDescription(persona?.description || ''), [persona?.description]);

  const save = async () => {
    setState('Salvo...');
    try {
      const form = new FormData();
      form.append('description', description);
      if (file) form.append('photo', file);
      const res = await fetch(`${API_URL}/reel/persona`, { method: 'POST', body: form });
      if (!res.ok) throw new Error(await readError(res));
      onSaved(await res.json());
      setFile(null);
      setState('Salvata ✓');
    } catch (exc) {
      setState(exc instanceof Error ? exc.message : String(exc));
    }
  };

  return (
    <div className="rs-persona">
      <div className="rs-persona-head">
        {persona?.reference_image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={`${fileUrl(persona.reference_image)}?v=${encodeURIComponent(persona.updated_at || '')}`} alt="Modella Monili" />
        ) : (
          <div className="rs-persona-empty">Nessuna foto</div>
        )}
        <div>
          <div className="rs-persona-title">La Modella Monili</div>
          <p className="rs-muted rs-small">
            Sempre la stessa donna in ogni video. Descrivila una volta (in inglese funziona meglio) e, appena hai un
            fotogramma che ti piace, usalo come foto di riferimento.
          </p>
        </div>
      </div>
      <textarea className="brief-area" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
      <div className="rs-actions">
        <label className="btn-secondary rs-small-btn rs-file-btn">
          {file ? file.name : persona?.reference_image ? 'Cambia foto di riferimento' : 'Carica foto di riferimento'}
          <input type="file" accept="image/*,.heic,.heif" hidden onChange={(e) => setFile(e.target.files?.[0] || null)} />
        </label>
        <button type="button" className="btn-secondary rs-small-btn" onClick={save}>Salva modella</button>
        {state && <span className="rs-muted rs-small">{state}</span>}
      </div>
    </div>
  );
}

function ModelPicker({ reel, onPersona }: { reel: ReelState; onPersona: (p: Persona) => void }) {
  const [saved, setSaved] = useState('');
  const modelShots = (reel.results.shots || []).filter(
    (item) => item.keyframe && reel.storyboard?.shots.find((s) => s.id === item.id)?.use_model,
  );
  if (!modelShots.length) return null;
  const choose = async (shotId: string) => {
    const res = await fetch(`${API_URL}/reel/persona/from-keyframe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reel_id: reel.id, shot_id: shotId }),
    });
    if (res.ok) {
      onPersona(await res.json());
      setSaved(shotId);
    }
  };
  return (
    <div className="rs-copy-block">
      <div className="rs-copy-head"><span>Ti piace questa modella? Rendila ufficiale</span></div>
      <div className="rs-covers">
        {modelShots.map((item) => (
          <button key={item.id} type="button" className="rs-cover" onClick={() => choose(item.id)}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={fileUrl(item.keyframe!)} alt={item.id} />
            <span>{saved === item.id ? 'Modella Monili ✓' : 'Usa come Modella Monili'}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
