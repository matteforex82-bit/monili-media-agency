'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import AgentCard from '@/components/AgentCard';
import TerminalLog from '@/components/TerminalLog';
import PhotoDropzone from '@/components/PhotoDropzone';
import ResultsPanel from '@/components/ResultsPanel';

// ── TIPI ─────────────────────────────────────────────────────────
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

// ── CONFIGURAZIONE AGENTI ──────────────────────────────────────────
const INITIAL_AGENTS: AgentDef[] = [
  { id: 'supervising-agency',    name: 'SUPERVISOR',  role: 'Direttore Creativo', icon: '🎯', status: 'offline', progress: 0 },
  { id: 'researching-trends',    name: 'TREND',       role: 'Intelligence P/E',   icon: '📊', status: 'offline', progress: 0 },
  { id: 'analyzing-products',    name: 'ANALISTA',    role: 'Vision AI',          icon: '🔍', status: 'offline', progress: 0 },
  { id: 'directing-photography', name: 'FOTO DIR.',   role: 'Shooting AI',        icon: '📷', status: 'offline', progress: 0 },
  { id: 'generating-visuals',    name: 'VISUAL GEN',  role: 'Image AI',           icon: '✨', status: 'offline', progress: 0 },
  { id: 'directing-reels',       name: 'REEL DIR.',   role: 'Video AI',           icon: '🎬', status: 'offline', progress: 0 },
  { id: 'writing-copy',          name: 'COPY',        role: 'Testi & Caption',    icon: '📝', status: 'offline', progress: 0 },
  { id: 'optimizing-hashtags',   name: 'HASHTAG',     role: 'Strategy',           icon: '📌', status: 'offline', progress: 0 },
  { id: 'optimizing-photos',     name: 'FOTO OTT.',   role: 'Foto Instagram',     icon: '🖼️', status: 'offline', progress: 0 },
  { id: 'updating-memory',       name: 'MEMORIA',     role: 'Auto-Learning',      icon: '🧠', status: 'offline', progress: 0 },
];

// ── SIMULAZIONE ───────────────────────────────────────────────────
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
      { delay: 2000, msg: 'Audio Reel top: "Espresso" — Sabrina Carpenter (↑ moda)', type: 'data' },
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
      { delay: 2000, msg: 'Mood: elegante minimal, boho chic — Stagione: P/E 2026', type: 'data' },
      { delay: 2400, msg: 'Formato consigliato: REEL (impatto visivo alto)', type: 'success' },
    ],
  },
  {
    agentIdx: 3, duration: 3000,
    logs: [
      { delay: 0,    msg: 'Generazione 8 prompt shooting professionali...', type: 'info' },
      { delay: 500,  msg: '[1/8] Hero shot — sfondo neutro bianco, studio lighting', type: 'data' },
      { delay: 900,  msg: '[2/8] Vista 3/4 — angolazione 45°, soft shadows', type: 'data' },
      { delay: 1300, msg: '[3/8] Close-up texture — macro, bokeh background', type: 'data' },
      { delay: 1700, msg: '[4/8] Modella — lifestyle, centro storico Ravenna', type: 'data' },
      { delay: 2100, msg: '[5/8] Flat lay P/E — abbinamenti fiori, tessuti leggeri', type: 'data' },
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
      { delay: 600,  msg: '[Frame 1] Hook: "Questi orecchini valgono una serata..." — testo bold', type: 'data' },
      { delay: 1100, msg: '[Frame 2-4] Product scenes con audio "Espresso"', type: 'data' },
      { delay: 1700, msg: '[Frame 5] CTA: "Trovali solo da noi · Ravenna centro"', type: 'data' },
      { delay: 2200, msg: 'Script + 5 frame prompt AI generati', type: 'success' },
    ],
  },
  {
    agentIdx: 6, duration: 2200,
    logs: [
      { delay: 0,    msg: 'Scrittura 3 varianti caption...', type: 'info' },
      { delay: 700,  msg: '[Casual] "Questi orecchini hanno già scelto il tuo outfit 🌿"', type: 'data' },
      { delay: 1200, msg: '[Elegante] "Oro che accarezza. Luce che racconta."', type: 'data' },
      { delay: 1700, msg: '[Urgency] "Nuovi arrivi — solo pochi pezzi disponibili ✨"', type: 'data' },
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

// ── CONFIG ────────────────────────────────────────────────────────
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://monili-media-agency.onrender.com';

// Estrae sezioni di testo dai log grezzi del backend
function estrai(logs: string, keyword: string): string {
  const lines = logs.split('\n');
  const relevant = lines.filter(l => l.toLowerCase().includes(keyword.toLowerCase()));
  return relevant.length > 0 ? relevant.join('\n') : '';
}

// ── HELPER ────────────────────────────────────────────────────────
function now() {
  return new Date().toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// ── COMPONENTE PRINCIPALE ─────────────────────────────────────────
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
  const briefRef = useRef<HTMLTextAreaElement>(null);

  // Boot: offline → standby
  useEffect(() => {
    const t = setTimeout(() => {
      setAgents(prev => prev.map(a => ({ ...a, status: 'standby' })));
    }, 600);
    return () => clearTimeout(t);
  }, []);

  const updateAgent = useCallback((idx: number, patch: Partial<AgentDef>) => {
    setAgents(prev => prev.map((a, i) => i === idx ? { ...a, ...patch } : a));
  }, []);

  const addLog = useCallback((agent: string, msg: string, type: LogEntry['type']) => {
    setLogs(prev => [...prev, { time: now(), agent, msg, type }]);
  }, []);

  const runReal = useCallback(async () => {
    if (!photo) return;
    setMissionState('running');
    setLogs([]);
    setOverallProgress(0);

    // ── Invia foto + brief al backend ──
    const formData = new FormData();
    formData.append('foto', photo);
    formData.append('brief', brief);

    let jobId: string;
    try {
      const res = await fetch(`${API_URL}/mission/start`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      jobId = data.job_id;
    } catch (err) {
      addLog('SISTEMA', `Errore connessione backend: ${err}`, 'warn');
      setMissionState('error');
      return;
    }

    addLog('SISTEMA', `Missione avviata (job: ${jobId})`, 'info');

    // ── SSE stream: aggiornamenti in tempo reale ──
    const agentKeywords: [string, number][] = [
      ['SUPERVISOR',    0], ['Trend',       1], ['Analisi',  2],
      ['SHOOTING',      3], ['Gemini',      4], ['Reel',     5],
      ['Caption',       6], ['Hashtag',     7], ['FOTO OTT', 8],
      ['performance',   9],
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

          // Rileva quale agente è attivo dal testo del log
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
            msg.includes('✅') || msg.includes('completat') ? 'success' :
            msg.includes('❌') || msg.includes('errore')    ? 'warn'    :
            msg.match(/#\w+|trend|reach|\d+€/)             ? 'data'    : 'info';

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
                    shooting: '# Prompt shooting generati\nVedi cartella output sul server.',
                    reel:     '# Script Reel generato\nVedi cartella output sul server.',
                    copy:     '# Copy generato\nVedi cartella output sul server.',
                    hashtag:  '# Hashtag generati\nVedi cartella output sul server.',
                    piano:    '# Piano editoriale generato\nVedi cartella output sul server.',
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
  }, [photo, brief, updateAgent, addLog]);

  const pollStatus = useCallback(async (jobId: string) => {
    try {
      const res = await fetch(`${API_URL}/mission/${jobId}/status`);
      const data = await res.json();
      if (data.status === 'running') {
        setTimeout(() => pollStatus(jobId), 2000);
      } else {
        INITIAL_AGENTS.forEach((_, i) => updateAgent(i, { status: 'done', progress: 100 }));
        setOverallProgress(100);
        setMissionState('complete');
        addLog('SISTEMA', 'Missione completata.', 'success');
      }
    } catch {
      setTimeout(() => pollStatus(jobId), 3000);
    }
  }, [updateAgent, addLog]);

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
    setPhotoPreview(null);
    setBrief('');
    setLogs([]);
    setOverallProgress(0);
    setResults({});
    setCountdown(null);
    setAgents(INITIAL_AGENTS.map(a => ({ ...a, status: 'standby' })));
  }, []);

  const doneCount  = agents.filter(a => a.status === 'done').length;
  const activeAgent = agents.find(a => a.status === 'active');

  return (
    <div className="min-h-screen flex flex-col">

      {/* ── HEADER ─────────────────────────────────────────────── */}
      <header className="app-header sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between gap-4">

          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 22 }}>💎</span>
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

      {/* ── MAIN ───────────────────────────────────────────────── */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">

        {/* ══ IDLE ══════════════════════════════════════════════ */}
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
                Crea il kit marketing
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
                Dal prodotto al post<br />
                <span className="text-terracotta-gradient">in 30 secondi</span>
              </h1>
              <p style={{
                fontFamily: 'DM Sans',
                fontSize: 15,
                color: 'var(--espresso-mid)',
                lineHeight: 1.6,
                maxWidth: 440,
                margin: '0 auto',
              }}>
                Scatta una foto al prodotto e il tuo team AI crea analisi, foto, caption, hashtag e calendario editoriale.
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
                      Foto del prodotto
                    </div>
                    <div style={{ fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-dim)' }}>
                      Trascina o clicca per caricare
                    </div>
                  </div>
                </div>
                <PhotoDropzone
                  photo={photo}
                  photoPreview={photoPreview}
                  onFile={(file, url) => { setPhoto(file); setPhotoPreview(url); }}
                  onClear={() => { setPhoto(null); setPhotoPreview(null); }}
                />
              </div>

              {/* Step 2 */}
              <div className="card fade-up fade-up-d2" style={{ padding: '22px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                  <div className="step-badge" style={{ opacity: 0.6 }}>2</div>
                  <div>
                    <div style={{ fontFamily: 'DM Sans', fontWeight: 700, fontSize: 15, color: 'var(--espresso)', marginBottom: 2 }}>
                      Note aggiuntive
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
                      Prezzo, dettagli, istruzioni speciali
                    </div>
                  </div>
                </div>
                <textarea
                  ref={briefRef}
                  className="brief-area"
                  value={brief}
                  onChange={e => setBrief(e.target.value)}
                  placeholder="es: orecchini cerchio dorati, 22€, nuovi arrivi P/E 2026, perfetti per la primavera..."
                  style={{ minHeight: 200 }}
                />
                {brief.length > 0 && (
                  <div style={{ marginTop: 8, fontFamily: 'DM Mono', fontSize: 10, color: 'var(--espresso-dim)' }}>
                    {brief.length} caratteri
                  </div>
                )}
              </div>
            </div>

            {/* Team ready strip */}
            <div className="fade-up fade-up-d3 card" style={{ padding: '14px 20px', marginBottom: 32, display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{ fontSize: 16 }}>👥</span>
              <div>
                <div style={{ fontFamily: 'DM Sans', fontWeight: 600, fontSize: 13, color: 'var(--espresso)', marginBottom: 2 }}>
                  Team di 10 specialisti AI — pronti
                </div>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)' }}>
                  Supervisor · Trend · Analista · Foto · Visual · Reel · Copy · Hashtag · Foto Ott. · Memoria
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
                    {countdown === 0 ? '✨' : countdown}
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
                    <span style={{ fontSize: 18 }}>✨</span>
                    Avvia il team AI
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

        {/* ══ RUNNING ═══════════════════════════════════════════ */}
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
                <span className="spin-slow" style={{ display: 'inline-block' }}>⟳</span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'DM Sans', fontWeight: 700, fontSize: 16, color: 'var(--espresso)', marginBottom: 4 }}>
                  Il team sta lavorando al tuo prodotto...
                </div>
                <div style={{ fontFamily: 'DM Sans', fontSize: 13, color: 'var(--espresso-mid)' }}>
                  {activeAgent
                    ? <span>Ora attivo: <strong style={{ color: 'var(--terracotta-dark)' }}>{activeAgent.name}</strong> — {activeAgent.role}</span>
                    : 'Finalizzazione in corso...'}
                </div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontFamily: 'Playfair Display', fontSize: 36, fontWeight: 700, color: 'var(--terracotta)', lineHeight: 1 }}>
                  {overallProgress}%
                </div>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)', marginTop: 2 }}>
                  {doneCount} di 9 completati
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

        {/* ══ ERROR ═════════════════════════════════════════════ */}
        {missionState === 'error' && (
          <div className="fade-up" style={{ textAlign: 'center', padding: '60px 24px' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
            <h2 style={{ fontFamily: 'Playfair Display', fontSize: 24, fontWeight: 700, color: 'var(--espresso)', marginBottom: 12 }}>
              Qualcosa è andato storto
            </h2>
            <p style={{ fontFamily: 'DM Sans', fontSize: 14, color: 'var(--espresso-mid)', maxWidth: 400, margin: '0 auto 28px' }}>
              Errore durante l'elaborazione. Controlla che le API key siano configurate su Render e riprova.
            </p>
            <div style={{ marginBottom: 20 }}>
              <TerminalLog logs={logs} />
            </div>
            <button onClick={handleReset} className="btn-mission" style={{ padding: '14px 32px', fontSize: 14 }}>
              Riprova con un altro prodotto
            </button>
          </div>
        )}

        {/* ══ COMPLETE ══════════════════════════════════════════ */}
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
                ✅
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, fontWeight: 600, color: 'var(--sage)', letterSpacing: '0.10em', textTransform: 'uppercase', marginBottom: 4 }}>
                  Missione completata
                </div>
                <h2 style={{ fontFamily: 'Playfair Display', fontSize: 24, fontWeight: 700, color: 'var(--espresso)', margin: 0 }}>
                  Il kit marketing è pronto!
                </h2>
                <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: 'var(--espresso-mid)', margin: '4px 0 0' }}>
                  Analisi, prompt shooting, script reel, caption, hashtag e foto ottimizzate — tutto pronto da usare.
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
                Il team — 9/9 completati
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                {agents.map((agent, i) => (
                  <AgentCard key={agent.id} agent={agent} index={i} />
                ))}
              </div>
            </div>

            <div className="hr-warm" style={{ marginBottom: 28 }} />

            {/* Results — download center */}
            <ResultsPanel results={results} apiUrl={API_URL} />
          </div>
        )}
      </main>

      {/* ── FOOTER ─────────────────────────────────────────────── */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '14px 24px', marginTop: 40 }}>
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <span style={{ fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)' }}>
            I Monili Ravenna · Studio AI — Powered by Claude
          </span>
          <span style={{ fontFamily: 'DM Mono', fontSize: 11, color: 'var(--cream-border)' }}>
            P/E 2026
          </span>
        </div>
      </footer>
    </div>
  );
}
