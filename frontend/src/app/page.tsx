'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import AgentCard from '@/components/AgentCard';
import TerminalLog from '@/components/TerminalLog';
import PhotoDropzone from '@/components/PhotoDropzone';
import ResultsPanel from '@/components/ResultsPanel';

// â”€â”€ TIPI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export type AgentStatus = 'offline' | 'standby' | 'active' | 'done' | 'error';
export type MissionState = 'idle' | 'running' | 'complete' | 'error';

export interface AgentDef {
  id: string;
  name: string;
  role: string;
  icon: string;
  status: AgentStatus;
  progress: number;
  log?: string;
}

export interface LogEntry {
  time: string;
  agent: string;
  msg: string;
  type: 'info' | 'success' | 'warn' | 'data';
}

// â”€â”€ CONFIGURAZIONE AGENTI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const INITIAL_AGENTS: AgentDef[] = [
  { id: 'supervising-agency',    name: 'SUPERVISOR',  role: 'Direttore Creativo', icon: 'S', status: 'offline', progress: 0 },
  { id: 'researching-trends',    name: 'TREND',       role: 'Intelligence P/E',   icon: 'T', status: 'offline', progress: 0 },
  { id: 'analyzing-products',    name: 'ANALISTA',    role: 'Vision AI',          icon: 'A', status: 'offline', progress: 0 },
  { id: 'planning-strategy',     name: 'STRATEGIST',  role: 'Scelta formato',     icon: 'S', status: 'offline', progress: 0 },
  { id: 'directing-photography', name: 'FOTO DIR.',   role: 'Foto reali',         icon: 'F', status: 'offline', progress: 0 },
  { id: 'visual-ai',             name: 'VISUAL AI',   role: 'Try-on realistico',  icon: 'V', status: 'offline', progress: 0 },
  { id: 'planning-carousel',     name: 'CAROUSEL',    role: 'Statici utili',      icon: 'C', status: 'offline', progress: 0 },
  { id: 'local-visibility',      name: 'LOCAL SEO',   role: 'Ravenna & AI search', icon: 'L', status: 'offline', progress: 0 },
  { id: 'distribution-plan',     name: 'DISTRIB.',    role: 'Caption & canali',   icon: 'D', status: 'offline', progress: 0 },
  { id: 'optimizing-photos',     name: 'FOTO OTT.',   role: 'Foto Instagram',     icon: 'O', status: 'offline', progress: 0 },
  { id: 'updating-memory',       name: 'MEMORIA',     role: 'Auto-Learning',      icon: 'M', status: 'offline', progress: 0 },
];

// â”€â”€ SIMULAZIONE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const SIMULATION: Array<{
  agentIdx: number;
  duration: number;
  logs: Array<{ delay: number; msg: string; type: LogEntry['type'] }>;
}> = [
  {
    agentIdx: 0, duration: 1200,
    logs: [
      { delay: 0,   msg: 'Missione ricevuta. Analisi foto prodotto in corso...', type: 'info' },
      { delay: 400, msg: 'Orchestrazione team avviata. 9 agenti in standby.', type: 'info' },
    ],
  },
  {
    agentIdx: 1, duration: 3500,
    logs: [
      { delay: 0,    msg: 'Ricerca trend hashtag bijoux Italia P/E 2026...', type: 'info' },
      { delay: 800,  msg: '#bijouxdonna +340% reach ultimi 7gg', type: 'data' },
      { delay: 1400, msg: '#gioiellihandmade trending su Reel Italia', type: 'data' },
      { delay: 2000, msg: 'Audio Reel top: "Espresso" â€” Sabrina Carpenter (â†‘ moda)', type: 'data' },
      { delay: 2800, msg: 'Competitor Ravenna: 3 negozi analizzati', type: 'data' },
      { delay: 3200, msg: 'Intelligence completata. Dati pronti per team.', type: 'success' },
    ],
  },
  {
    agentIdx: 2, duration: 2800,
    logs: [
      { delay: 0,    msg: 'Analisi multimodale foto prodotto...', type: 'info' },
      { delay: 600,  msg: 'Prodotto identificato: Orecchini a cerchio dorati', type: 'data' },
      { delay: 1100, msg: 'Materiale: metallo dorato, superficie liscia', type: 'data' },
      { delay: 1600, msg: 'Colori: #D4AF37 (78%), #FAD5A5 (22%)', type: 'data' },
      { delay: 2000, msg: 'Mood: elegante minimal, boho chic â€” Stagione: P/E 2026', type: 'data' },
      { delay: 2400, msg: 'Formato consigliato: REEL (impatto visivo alto)', type: 'success' },
    ],
  },
  {
    agentIdx: 3, duration: 3000,
    logs: [
      { delay: 0,    msg: 'Generazione 8 prompt shooting professionali...', type: 'info' },
      { delay: 500,  msg: '[1/8] Hero shot â€” sfondo neutro bianco, studio lighting', type: 'data' },
      { delay: 900,  msg: '[2/8] Vista 3/4 â€” angolazione 45Â°, soft shadows', type: 'data' },
      { delay: 1300, msg: '[3/8] Close-up texture â€” macro, bokeh background', type: 'data' },
      { delay: 1700, msg: '[4/8] Modella â€” lifestyle, centro storico Ravenna', type: 'data' },
      { delay: 2100, msg: '[5/8] Flat lay P/E â€” abbinamenti fiori, tessuti leggeri', type: 'data' },
      { delay: 2600, msg: '8 prompt con image reference pronti per Gemini/MJ', type: 'success' },
    ],
  },
  {
    agentIdx: 4, duration: 4000,
    logs: [
      { delay: 0,    msg: 'Chiamata Gemini Image API con image reference...', type: 'info' },
      { delay: 800,  msg: 'Generazione hero_shot.jpg...', type: 'info' },
      { delay: 1600, msg: 'Generazione detail_closeup.jpg...', type: 'info' },
      { delay: 2400, msg: 'Generazione worn_by_model.jpg...', type: 'info' },
      { delay: 3200, msg: '4 immagini professionali salvate in 02_SHOOTING/generated/', type: 'success' },
    ],
  },
  {
    agentIdx: 5, duration: 2500,
    logs: [
      { delay: 0,    msg: 'Struttura Reel: hook 3s + 3 scene + CTA', type: 'info' },
      { delay: 600,  msg: '[Frame 1] Hook: "Questi orecchini valgono una serata..." â€” testo bold', type: 'data' },
      { delay: 1100, msg: '[Frame 2-4] Product scenes con audio "Espresso"', type: 'data' },
      { delay: 1700, msg: '[Frame 5] CTA: "Trovali solo da noi Â· Ravenna centro"', type: 'data' },
      { delay: 2200, msg: 'Script + 5 frame prompt AI generati', type: 'success' },
    ],
  },
  {
    agentIdx: 6, duration: 2200,
    logs: [
      { delay: 0,    msg: 'Scrittura 3 varianti caption...', type: 'info' },
      { delay: 700,  msg: '[Casual] "Questi orecchini hanno giÃ  scelto il tuo outfit ðŸŒ¿"', type: 'data' },
      { delay: 1200, msg: '[Elegante] "Oro che accarezza. Luce che racconta."', type: 'data' },
      { delay: 1700, msg: '[Urgency] "Nuovi arrivi â€” solo pochi pezzi disponibili âœ¨"', type: 'data' },
      { delay: 2000, msg: 'Stories, WhatsApp, GMB pronti', type: 'success' },
    ],
  },
  {
    agentIdx: 7, duration: 1800,
    logs: [
      { delay: 0,    msg: 'Costruzione set 30 hashtag in 4 tier...', type: 'info' },
      { delay: 500,  msg: 'Tier 1 (broad): #bijouxdonna #gioielli #moda', type: 'data' },
      { delay: 900,  msg: 'Tier 3 (local): #ravenna #romagnastyle #imoniliravenna', type: 'data' },
      { delay: 1400, msg: '3 hashtag "scommessa settimana" identificati', type: 'success' },
    ],
  },
  {
    agentIdx: 8, duration: 1400,
    logs: [
      { delay: 0,    msg: 'Ottimizzazione foto per Instagram...', type: 'info' },
      { delay: 500,  msg: 'Feed 1080x1080 con padding bianco generata', type: 'data' },
      { delay: 900,  msg: 'Stories 1080x1920 con sfondo blurrato generata', type: 'data' },
      { delay: 1200, msg: 'Feed e Stories salvate in 05_FOTO_OTTIMIZZATE', type: 'success' },
    ],
  },
  {
    agentIdx: 9, duration: 900,
    logs: [
      { delay: 0,   msg: 'Sessione loggata in performance_log.json', type: 'info' },
      { delay: 500, msg: 'Sistema aggiornato. Memoria persistente.', type: 'success' },
    ],
  },
];

// â”€â”€ CONFIG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://monili-media-agency.onrender.com';
const OPENROUTER_TEXT_MODELS = [
  'openai/gpt-4.1-mini',
  'google/gemini-2.5-flash',
  'google/gemini-2.5-pro',
  'anthropic/claude-3.7-sonnet',
] as const;
const OPENROUTER_IMAGE_MODELS = [
  'google/gemini-3.1-flash-image-preview',
  'black-forest-labs/flux.2-klein-4b',
  'bytedance-seed/seedream-4.5',
] as const;

// Estrae sezioni di testo dai log grezzi del backend
function estrai(logs: string, keyword: string): string {
  const lines = logs.split('\n');
  const relevant = lines.filter(l => l.toLowerCase().includes(keyword.toLowerCase()));
  return relevant.length > 0 ? relevant.join('\n') : '';
}

// â”€â”€ HELPER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function now() {
  return new Date().toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// â”€â”€ COMPONENTE PRINCIPALE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export default function Home() {
  const [missionState, setMissionState] = useState<MissionState>('idle');
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [brief, setBrief] = useState('');
  const [agents, setAgents] = useState<AgentDef[]>(INITIAL_AGENTS);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [results, setResults] = useState<Record<string, string>>({});
  const [countdown, setCountdown] = useState<number | null>(null);
  const [textModel, setTextModel] = useState('openai/gpt-4.1-mini');
  const [imageModel, setImageModel] = useState('google/gemini-3.1-flash-image-preview');
  const [modelsDialogOpen, setModelsDialogOpen] = useState(false);
  const [checkingOpenRouter, setCheckingOpenRouter] = useState(false);
  const briefRef = useRef<HTMLTextAreaElement>(null);

  // Boot: offline â†’ standby
  useEffect(() => {
    const t = setTimeout(() => {
      setAgents(prev => prev.map(a => ({ ...a, status: 'standby' })));
    }, 600);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    return () => {
      if (photoPreview?.startsWith('blob:')) {
        URL.revokeObjectURL(photoPreview);
      }
    };
  }, [photoPreview]);

  const updateAgent = useCallback((idx: number, patch: Partial<AgentDef>) => {
    setAgents(prev => prev.map((a, i) => i === idx ? { ...a, ...patch } : a));
  }, []);

  const addLog = useCallback((agent: string, msg: string, type: LogEntry['type']) => {
    setLogs(prev => [...prev, { time: now(), agent, msg, type }]);
  }, []);

  const handlePhotoSelect = useCallback((file: File, url: string) => {
    setPhoto(file);
    setPhotoPreview(prev => {
      if (prev?.startsWith('blob:')) {
        URL.revokeObjectURL(prev);
      }
      return url;
    });
  }, []);

  const handlePhotoClear = useCallback(() => {
    setPhoto(null);
    setPhotoPreview(prev => {
      if (prev?.startsWith('blob:')) {
        URL.revokeObjectURL(prev);
      }
      return null;
    });
  }, []);

  const runReal = useCallback(async () => {
    if (!photo) return;
    setMissionState('running');
    setLogs([]);
    setOverallProgress(0);

    // â”€â”€ Invia foto + brief al backend â”€â”€
    const formData = new FormData();
    formData.append('foto', photo);
    formData.append('brief', brief);
    formData.append('text_model', textModel);
    formData.append('image_model', imageModel);

    let jobId: string;
    let resolvedTextModel = textModel;
    let resolvedImageModel = imageModel;
    try {
      const res = await fetch(`${API_URL}/mission/start`, { method: 'POST', body: formData });
      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(errorData?.error || `HTTP ${res.status}`);
      }
      const data = await res.json();
      jobId = data.job_id;
      resolvedTextModel = data.text_model || textModel;
      resolvedImageModel = data.image_model || imageModel;
    } catch (err) {
      addLog('SISTEMA', `Errore avvio missione: ${err}`, 'warn');
      setMissionState('error');
      return;
    }

    addLog('SISTEMA', `Missione avviata (job: ${jobId})`, 'info');
    addLog('SISTEMA', `Modello testo: ${resolvedTextModel}`, 'data');
    addLog('SISTEMA', `Modello immagini: ${resolvedImageModel}`, 'data');

    // â”€â”€ SSE stream: aggiornamenti in tempo reale â”€â”€
    const agentKeywords: [string, number][] = [
      ['SUPERVISOR',    0], ['Trend',       1], ['Analisi',  2],
      ['STRATEGIST',    3], ['FOTO DIR',    4], ['VISUAL',   5],
      ['CAROUSEL',      6], ['LOCAL SEO',   7], ['DISTRIBUZIONE', 8],
      ['FOTO OTT',      9], ['performance', 10],
    ];

    let currentAgentIdx = 0;
    let progressInterval: ReturnType<typeof setInterval>;

    const startAgentProgress = (idx: number) => {
      if (progressInterval) clearInterval(progressInterval);
      updateAgent(idx, { status: 'active', progress: 0 });
      let p = 0;
      progressInterval = setInterval(() => {
        p = Math.min(p + 2, 95);
        updateAgent(idx, { progress: p });
      }, 300);
    };

    startAgentProgress(0);

    const es = new EventSource(`${API_URL}/mission/${jobId}/stream`);

    es.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);

        if (payload.type === 'log') {
          const msg: string = payload.msg;

          // Rileva quale agente Ã¨ attivo dal testo del log
          for (const [keyword, idx] of agentKeywords) {
            if (msg.toLowerCase().includes(keyword.toLowerCase()) && idx !== currentAgentIdx) {
              updateAgent(currentAgentIdx, { status: 'done', progress: 100 });
              currentAgentIdx = idx;
              startAgentProgress(idx);
              setOverallProgress(Math.round((idx / INITIAL_AGENTS.length) * 100));
              break;
            }
          }

          // Classifica il tipo di log
          const type: LogEntry['type'] =
            msg.includes('[OK]') || msg.includes('completat') ? 'success' :
            msg.toLowerCase().includes('errore')              ? 'warn'    :
            msg.match(/#\w+|trend|reach|\d+\s?(EUR|euro)/i)   ? 'data'    : 'info';

          addLog(INITIAL_AGENTS[currentAgentIdx]?.name || 'SISTEMA', msg, type);
        }

        if (payload.type === 'status') {
          clearInterval(progressInterval);
          es.close();

          if (payload.status === 'done') {
            INITIAL_AGENTS.forEach((_, i) => updateAgent(i, { status: 'done', progress: 100 }));
            setOverallProgress(100);

            fetch(`${API_URL}/mission/${jobId}/status`)
              .then(r => r.json())
              .then(data => {
                if (data.results) {
                  setResults(data.results);
                } else {
                  // fallback se results non disponibili
                  setResults({
                    analisi:  '# Analisi completata\nVedi cartella output sul server.',
                    strategy: '# Strategia 2.0 completata\nVedi cartella output sul server.',
                    shooting: '# Guida foto reale generata\nVedi cartella output sul server.',
                    visual_prompts: '# Prompt visual AI generati\nVedi cartella output sul server.',
                    carousel: '# Carousel statici generati\nVedi cartella output sul server.',
                    local_visibility: '# Local visibility generata\nVedi cartella output sul server.',
                    distribution: '# Caption, WhatsApp e piano generati\nVedi cartella output sul server.',
                  });
                }
                setMissionState('complete');
                addLog('SISTEMA', 'Missione completata. Kit marketing pronto.', 'success');
              });
          } else {
            setMissionState('error');
            addLog('SISTEMA', 'Errore durante la missione. Controlla le API keys su Render.', 'warn');
          }
        }
      } catch {
        // ignora errori parse SSE
      }
    };

    es.onerror = () => {
      clearInterval(progressInterval);
      es.close();
      // Polling fallback se SSE non supportato
      setTimeout(() => pollStatus(jobId), 2000);
    };
  }, [photo, brief, textModel, imageModel, updateAgent, addLog]);

  const pollStatus = useCallback(async (jobId: string) => {
    try {
      const res = await fetch(`${API_URL}/mission/${jobId}/status`);
      const data = await res.json();
      if (data.status === 'running') {
        setTimeout(() => pollStatus(jobId), 2000);
      } else {
        INITIAL_AGENTS.forEach((_, i) => updateAgent(i, { status: 'done', progress: 100 }));
        setOverallProgress(100);
        if (data.results) setResults(data.results);
        setMissionState(data.status === 'error' ? 'error' : 'complete');
        addLog('SISTEMA', data.status === 'error' ? 'Missione terminata con errore.' : 'Missione completata.', data.status === 'error' ? 'warn' : 'success');
      }
    } catch {
      setTimeout(() => pollStatus(jobId), 3000);
    }
  }, [updateAgent, addLog]);

  const checkOpenRouter = useCallback(async () => {
    setCheckingOpenRouter(true);
    try {
      const res = await fetch(
        `${API_URL}/openrouter/check?image_model=${encodeURIComponent(imageModel)}&text_model=${encodeURIComponent(textModel)}`
      );
      const data = await res.json();
      if (!res.ok) {
        addLog('VISUAL GEN', `OpenRouter KO: ${data.error || `HTTP ${res.status}`}`, 'warn');
      } else if (data.image_model_supported && data.text_model_supported) {
        addLog('SISTEMA', `OpenRouter OK. Text: ${data.selected_text_model}`, 'success');
        addLog('SISTEMA', `OpenRouter OK. Image: ${data.selected_image_model}`, 'success');
      } else {
        if (!data.text_model_supported) {
          addLog('SISTEMA', `Modello testo non trovato su OpenRouter: ${data.selected_text_model}`, 'warn');
        }
        if (!data.image_model_supported) {
          addLog('VISUAL GEN', `Modello immagini non trovato su OpenRouter: ${data.selected_image_model}`, 'warn');
        }
      }
    } catch (err) {
      addLog('VISUAL GEN', `Errore check OpenRouter: ${err}`, 'warn');
    } finally {
      setCheckingOpenRouter(false);
    }
  }, [imageModel, textModel, addLog]);

  const handleLaunch = useCallback(() => {
    if (!photo) return;
    setCountdown(3);
    const tick = (n: number) => {
      if (n <= 0) { setCountdown(null); runReal(); return; }
      setTimeout(() => { setCountdown(n - 1); tick(n - 1); }, 800);
    };
    tick(3);
  }, [photo, runReal]);

  const handleReset = useCallback(() => {
    setMissionState('idle');
    setPhoto(null);
    setPhotoPreview(prev => {
      if (prev?.startsWith('blob:')) {
        URL.revokeObjectURL(prev);
      }
      return null;
    });
    setBrief('');
    setLogs([]);
    setOverallProgress(0);
    setResults({});
    setCountdown(null);
    setModelsDialogOpen(false);
    setCheckingOpenRouter(false);
    setTextModel('openai/gpt-4.1-mini');
    setImageModel('google/gemini-3.1-flash-image-preview');
    setAgents(INITIAL_AGENTS.map(a => ({ ...a, status: 'standby' })));
  }, []);

  const doneCount  = agents.filter(a => a.status === 'done').length;
  const activeAgent = agents.find(a => a.status === 'active');

  return (
    <div className="min-h-screen flex flex-col">

      {/* â”€â”€ HEADER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <header className="app-header sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between gap-4">

          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              border: '1px solid var(--terracotta-light)',
              background: 'var(--terracotta-pale)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'DM Sans',
              fontSize: 12,
              fontWeight: 800,
              color: 'var(--terracotta-dark)',
              letterSpacing: 0,
            }}>
              IM
            </span>
            <div>
              <div style={{ fontFamily: 'Playfair Display', fontWeight: 700, fontSize: 17, color: 'var(--espresso)', lineHeight: 1.1 }}>
                I Monili
              </div>
              <div style={{ fontFamily: 'DM Sans', fontSize: 10, color: 'var(--espresso-dim)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                Studio AI
              </div>
            </div>
          </div>

          {/* Center: progress bar when running */}
          {missionState === 'running' && (
            <div style={{ flex: 1, maxWidth: 320, display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ flex: 1, height: 6, background: 'var(--cream-3)', borderRadius: 99, overflow: 'hidden' }}>
                <div className="progress-bar-fill" style={{ width: `${overallProgress}%`, height: '100%' }} />
              </div>
              <span style={{ fontFamily: 'DM Mono', fontSize: 12, color: 'var(--terracotta-dark)', fontWeight: 500, minWidth: 36 }}>
                {overallProgress}%
              </span>
            </div>
          )}

          {/* Right: status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className={`status-dot ${missionState === 'idle' ? 'online' : missionState === 'running' ? 'active' : 'done'}`} />
            <span style={{ fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-mid)', fontWeight: 500 }}>
              {missionState === 'idle' && 'Pronta'}
              {missionState === 'running' && 'In elaborazione'}
              {missionState === 'complete' && 'Completata'}
            </span>
          </div>
        </div>

        {/* Thin progress line */}
        {missionState === 'running' && (
          <div className="overall-progress-bar">
            <div className="overall-progress-fill" style={{ width: `${overallProgress}%` }} />
          </div>
        )}
      </header>

      {/* â”€â”€ MAIN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">

        {/* â•â• IDLE â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        {(missionState === 'idle' || countdown !== null) && (
          <div className="fade-up">

            {/* Hero */}
            <div style={{ textAlign: 'center', marginBottom: 40 }}>
              <div style={{
                fontFamily: 'DM Sans',
                fontSize: 11,
                letterSpacing: '0.20em',
                textTransform: 'uppercase',
                color: 'var(--terracotta)',
                fontWeight: 600,
                marginBottom: 14,
              }}>
                Mini reparto marketing
              </div>
              <h1 style={{
                fontFamily: 'Playfair Display',
                fontSize: 38,
                fontWeight: 700,
                color: 'var(--espresso)',
                lineHeight: 1.18,
                margin: '0 auto 14px',
                maxWidth: 560,
              }}>
                Carica una foto.<br />
                <span className="text-terracotta-gradient">Ottieni il kit giusto.</span>
              </h1>
              <p style={{
                fontFamily: 'DM Sans',
                fontSize: 15,
                color: 'var(--espresso-mid)',
                lineHeight: 1.6,
                maxWidth: 440,
                margin: '0 auto',
              }}>
                Usa questa schermata: carica la foto prodotto, aggiungi due note se servono, poi genera visual realistici, carousel, caption e contenuti locali.
              </p>
            </div>

            {/* Step cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">

              {/* Step 1 */}
              <div className="card fade-up fade-up-d1" style={{ padding: '22px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                  <div className="step-badge">1</div>
                  <div>
                    <div style={{ fontFamily: 'DM Sans', fontWeight: 700, fontSize: 15, color: 'var(--espresso)', marginBottom: 2 }}>
                      1. Carica la foto base
                    </div>
                    <div style={{ fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-dim)' }}>
                      Anche una foto semplice va bene: l'AI la usa come riferimento reale.
                    </div>
                  </div>
                </div>
                <PhotoDropzone
                  photo={photo}
                  photoPreview={photoPreview}
                  onFile={handlePhotoSelect}
                  onClear={handlePhotoClear}
                />
              </div>

              {/* Step 2 */}
              <div className="card fade-up fade-up-d2" style={{ padding: '22px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                  <div className="step-badge" style={{ opacity: 0.6 }}>2</div>
                  <div>
                    <div style={{ fontFamily: 'DM Sans', fontWeight: 700, fontSize: 15, color: 'var(--espresso)', marginBottom: 2 }}>
                      2. Aggiungi contesto
                      <span style={{
                        marginLeft: 8,
                        fontFamily: 'DM Sans',
                        fontSize: 11,
                        fontWeight: 500,
                        color: 'var(--espresso-dim)',
                        background: 'var(--cream-2)',
                        border: '1px solid var(--border)',
                        borderRadius: 99,
                        padding: '2px 9px',
                        verticalAlign: 'middle',
                      }}>
                        Opzionale
                      </span>
                    </div>
                    <div style={{ fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-dim)' }}>
                      Prezzo, occasione, materiale o obiettivo. Puoi lasciarlo vuoto.
                    </div>
                  </div>
                </div>
                <textarea
                  ref={briefRef}
                  className="brief-area"
                  value={brief}
                  onChange={e => setBrief(e.target.value)}
                  placeholder="Esempio: orecchini a cerchio dorati, 22 EUR, nuovi arrivi, perfetti per cerimonia o aperitivo. Vorrei farli vedere indossati e creare un carousel su come abbinarli."
                  style={{ minHeight: 200 }}
                />
                <div style={{
                  marginTop: 14,
                  padding: '12px 14px',
                  borderRadius: 12,
                  background: 'var(--cream-2)',
                  border: '1px solid var(--border)',
                }}>
                  <div style={{ fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso)', marginBottom: 8, fontWeight: 700 }}>
                    Cosa riceverai
                  </div>
                  <div style={{ display: 'grid', gap: 6, fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-mid)', lineHeight: 1.45 }}>
                    <span>Visual AI fotorealistici: sfondo migliore, indossato, lifestyle.</span>
                    <span>Carousel statico con testi slide e guida visuale.</span>
                    <span>Caption, WhatsApp, Google Business e local SEO Ravenna.</span>
                  </div>
                  <details style={{ marginTop: 12 }}>
                    <summary style={{ cursor: 'pointer', fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)', fontWeight: 600 }}>
                      Impostazioni tecniche
                    </summary>
                    <div style={{ marginTop: 8, fontFamily: 'DM Mono', fontSize: 10.5, color: 'var(--espresso-mid)', lineHeight: 1.6 }}>
                      <div>Text: {textModel}</div>
                      <div>Image: {imageModel}</div>
                    </div>
                    <button
                      type="button"
                      onClick={checkOpenRouter}
                      disabled={checkingOpenRouter}
                      style={{
                        marginTop: 10,
                        padding: '8px 11px',
                        borderRadius: 10,
                        border: '1px solid var(--terracotta-light)',
                        background: 'var(--cream-2)',
                        color: 'var(--espresso)',
                        fontFamily: 'DM Sans',
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: checkingOpenRouter ? 'not-allowed' : 'pointer',
                        opacity: checkingOpenRouter ? 0.7 : 1,
                      }}
                    >
                      {checkingOpenRouter ? 'Verifica in corso...' : 'Verifica OpenRouter'}
                    </button>
                  </details>
                </div>
                {brief.length > 0 && (
                  <div style={{ marginTop: 8, fontFamily: 'DM Mono', fontSize: 10, color: 'var(--espresso-dim)' }}>
                    {brief.length} caratteri
                  </div>
                )}
              </div>
            </div>

            {/* Team ready strip */}
            <div className="fade-up fade-up-d3 card" style={{ padding: '16px 20px', marginBottom: 32, display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{
                width: 30,
                height: 30,
                borderRadius: 8,
                background: 'var(--terracotta-pale)',
                color: 'var(--terracotta-dark)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: 'DM Sans',
                fontWeight: 800,
                fontSize: 12,
                flexShrink: 0,
              }}>AI</span>
              <div>
                <div style={{ fontFamily: 'DM Sans', fontWeight: 600, fontSize: 13, color: 'var(--espresso)', marginBottom: 2 }}>
                  Il flusso e semplice
                </div>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)' }}>
                  1. Carichi la foto  2. Aggiungi note opzionali  3. Generi il kit  4. Scarichi testi e immagini
                </div>
              </div>
              <div style={{ marginLeft: 'auto', display: 'flex', gap: 4 }}>
                {agents.map(a => (
                  <div key={a.id} className="agent-strip-dot" title={a.name} />
                ))}
              </div>
            </div>

            {/* CTA */}
            <div className="fade-up fade-up-d4" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
              {countdown !== null ? (
                <div style={{ textAlign: 'center' }}>
                  <div
                    key={countdown}
                    className="countdown-pop"
                    style={{
                      fontFamily: 'Playfair Display',
                      fontSize: 72,
                      fontWeight: 700,
                      color: 'var(--terracotta)',
                      lineHeight: 1,
                      marginBottom: 12,
                    }}
                  >
                    {countdown === 0 ? 'Via' : countdown}
                  </div>
                  <div style={{ fontFamily: 'DM Sans', fontSize: 14, color: 'var(--espresso-mid)', fontWeight: 500 }}>
                    {countdown === 0 ? 'Avvio del team...' : 'Il team si sta preparando...'}
                  </div>
                </div>
              ) : (
                <>
                  <button
                    onClick={handleLaunch}
                    disabled={!photo}
                    className="btn-mission"
                    style={{ padding: '18px 52px', fontSize: 16 }}
                  >
                    Genera kit marketing
                  </button>

                  {!photo && (
                    <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: 'var(--espresso-dim)' }}>
                      Carica prima una foto prodotto per continuare
                    </p>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {/* â•â• RUNNING â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        {missionState === 'running' && (
          <div className="fade-up">

            {/* Status banner */}
            <div className="card fade-up" style={{ padding: '20px 24px', marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{
                width: 48, height: 48,
                borderRadius: '50%',
                background: 'var(--terracotta-pale)',
                border: '2px solid var(--terracotta-light)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 22,
                flexShrink: 0,
              }}>
                <span className="spin-slow" style={{ display: 'inline-block' }}>...</span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'DM Sans', fontWeight: 700, fontSize: 16, color: 'var(--espresso)', marginBottom: 4 }}>
                  Il team sta lavorando al tuo prodotto...
                </div>
                <div style={{ fontFamily: 'DM Sans', fontSize: 13, color: 'var(--espresso-mid)' }}>
                  {activeAgent
                    ? <span>Ora attivo: <strong style={{ color: 'var(--terracotta-dark)' }}>{activeAgent.name}</strong> - {activeAgent.role}</span>
                    : 'Finalizzazione in corso...'}
                </div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontFamily: 'Playfair Display', fontSize: 36, fontWeight: 700, color: 'var(--terracotta)', lineHeight: 1 }}>
                  {overallProgress}%
                </div>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)', marginTop: 2 }}>
                  {doneCount} di 11 completati
                </div>
              </div>
            </div>

            {/* Agent grid */}
            <div style={{ marginBottom: 6 }}>
              <div style={{ fontFamily: 'DM Sans', fontSize: 12, fontWeight: 600, color: 'var(--espresso-dim)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Il team
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-6">
                {agents.map((agent, i) => (
                  <AgentCard key={agent.id} agent={agent} index={i} />
                ))}
              </div>
            </div>

            {/* Activity feed */}
            <div>
              <div style={{ fontFamily: 'DM Sans', fontSize: 12, fontWeight: 600, color: 'var(--espresso-dim)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Cosa sta succedendo
              </div>
              <TerminalLog logs={logs} />
            </div>
          </div>
        )}

        {/* â•â• ERROR â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        {missionState === 'error' && (
          <div className="fade-up" style={{ textAlign: 'center', padding: '60px 24px' }}>
            <div style={{ fontSize: 32, marginBottom: 16, fontFamily: 'DM Sans', fontWeight: 800 }}>!</div>
            <h2 style={{ fontFamily: 'Playfair Display', fontSize: 24, fontWeight: 700, color: 'var(--espresso)', marginBottom: 12 }}>
              Qualcosa e andato storto
            </h2>
            <p style={{ fontFamily: 'DM Sans', fontSize: 14, color: 'var(--espresso-mid)', maxWidth: 400, margin: '0 auto 28px' }}>
              Errore durante l'elaborazione. Controlla OPENROUTER_API_KEY su Render e riprova.
            </p>
            <div style={{ marginBottom: 20 }}>
              <TerminalLog logs={logs} />
            </div>
            <button onClick={handleReset} className="btn-mission" style={{ padding: '14px 32px', fontSize: 14 }}>
              Riprova con un altro prodotto
            </button>
          </div>
        )}

        {/* â•â• COMPLETE â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        {missionState === 'complete' && (
          <div className="fade-up">

            {/* Success header */}
            <div className="success-banner fade-up" style={{ padding: '22px 28px', marginBottom: 28, display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{
                width: 52, height: 52,
                borderRadius: '50%',
                background: 'var(--sage-pale)',
                border: '2px solid rgba(126,158,114,0.4)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 26,
                flexShrink: 0,
              }}>
                OK
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, fontWeight: 600, color: 'var(--sage)', letterSpacing: '0.10em', textTransform: 'uppercase', marginBottom: 4 }}>
                  Missione completata
                </div>
                <h2 style={{ fontFamily: 'Playfair Display', fontSize: 24, fontWeight: 700, color: 'var(--espresso)', margin: 0 }}>
                  Il kit marketing e pronto!
                </h2>
                <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: 'var(--espresso-mid)', margin: '4px 0 0' }}>
                  Strategia, visual AI, carousel, Google Business, caption, WhatsApp e foto ottimizzate: tutto pronto da usare.
                </p>
              </div>
              <button
                onClick={handleReset}
                className="btn-mission"
                style={{ padding: '12px 22px', fontSize: 13, flexShrink: 0 }}
              >
                + Nuovo prodotto
              </button>
            </div>

            {/* Agent recap */}
            <div style={{ marginBottom: 28 }}>
              <div style={{ fontFamily: 'DM Sans', fontSize: 12, fontWeight: 600, color: 'var(--espresso-dim)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Il team - 11/11 completati
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                {agents.map((agent, i) => (
                  <AgentCard key={agent.id} agent={agent} index={i} />
                ))}
              </div>
            </div>

            <div className="hr-warm" style={{ marginBottom: 28 }} />

            {/* Results â€” download center */}
            <ResultsPanel results={results} apiUrl={API_URL} />
          </div>
        )}
      </main>

      {/* â”€â”€ FOOTER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '14px 24px', marginTop: 40 }}>
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <span style={{ fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)' }}>
            I Monili Ravenna / Studio AI / Powered by OpenRouter
          </span>
          <span style={{ fontFamily: 'DM Mono', fontSize: 11, color: 'var(--cream-border)' }}>
            P/E 2026
          </span>
        </div>
      </footer>
    </div>
  );
}

