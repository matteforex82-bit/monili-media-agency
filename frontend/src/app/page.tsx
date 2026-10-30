'use client';

import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useRef, useState } from 'react';
import MosaicTiles, { type TileItem } from '@/components/MosaicTiles';
import PhotoDropzone from '@/components/PhotoDropzone';
import { API_URL } from '@/lib/apiUrl';
import { photoPalette } from '@/lib/palette';
import { loadSettings } from '@/lib/settings';

type MissionState = 'idle' | 'running' | 'error';

const ACTIVE_JOB_STORAGE_KEY = 'monili_active_job_id';

// Le parole chiave dei log del backend -> a che punto è il lavoro (0 analisi, 1 piano, 2 foto, 3 testi).
const STAGE_KEYWORDS: Array<[string, number]> = [
  ['ANALISTA', 0],
  ['PIANO SCHEDA', 1],
  ['SITO VISUAL', 2],
  ['PUBLISH PACK', 3],
  ['MEMORIA', 3],
];

function stepTiles(stage: number): TileItem[] {
  return [
    { label: 'Analisi', state: stage >= 2 ? 'done' : 'working' },
    { label: 'Foto', state: stage >= 3 ? 'done' : stage === 2 ? 'working' : 'none' },
    { label: 'Testi', state: stage >= 3 ? 'working' : 'none' },
  ];
}

const STAGE_TEXT = [
  'Guardo il pezzo e ne descrivo i materiali.',
  'Preparo lo stile e le foto.',
  'Creo le foto per il sito.',
  'Scrivo i testi.',
];

export default function NewPiecePage() {
  const router = useRouter();
  const [state, setState] = useState<MissionState>('idle');
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [palette, setPalette] = useState<string[]>([]);
  const [brief, setBrief] = useState('');
  const [stage, setStage] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState('');
  const stopRef = useRef<() => void>(() => undefined);

  const addLog = useCallback((msg: string) => setLogs((prev) => [...prev.slice(-80), msg]), []);

  useEffect(() => {
    return () => {
      if (photoPreview?.startsWith('blob:')) URL.revokeObjectURL(photoPreview);
    };
  }, [photoPreview]);

  useEffect(() => () => stopRef.current(), []);

  const handlePhotoSelect = useCallback((file: File, url: string) => {
    setPhoto(file);
    setPhotoPreview((prev) => {
      if (prev?.startsWith('blob:')) URL.revokeObjectURL(prev);
      return url;
    });
    void photoPalette(url).then(setPalette);
  }, []);

  const handlePhotoClear = useCallback(() => {
    setPhoto(null);
    setPalette([]);
    setPhotoPreview((prev) => {
      if (prev?.startsWith('blob:')) URL.revokeObjectURL(prev);
      return null;
    });
  }, []);

  const finish = useCallback(
    (jobId: string) => {
      fetch(`${API_URL}/mission/${jobId}/status`)
        .then(async (res) => {
          const data = await res.json();
          if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
          return data;
        })
        .then((data) => {
          const runId = data?.results?.run_id;
          if (!runId) throw new Error('La missione si è chiusa senza foto né testi.');
          try { localStorage.removeItem(ACTIVE_JOB_STORAGE_KEY); } catch { /* storage non disponibile */ }
          router.push(`/pezzi/${encodeURIComponent(runId)}`);
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : String(err));
          setState('error');
        });
    },
    [router],
  );

  // Segue il lavoro del backend: aggiornamenti in diretta, con controllo periodico se la diretta cade.
  const follow = useCallback(
    (jobId: string) => {
      let closed = false;
      let timer: ReturnType<typeof setTimeout> | undefined;
      let source: EventSource | undefined;

      const fail = (message: string) => {
        if (closed) return;
        closed = true;
        source?.close();
        try { localStorage.removeItem(ACTIVE_JOB_STORAGE_KEY); } catch { /* storage non disponibile */ }
        setError(message);
        setState('error');
      };

      const poll = async () => {
        if (closed) return;
        try {
          const res = await fetch(`${API_URL}/mission/${jobId}/status`);
          const data = await res.json();
          if (!res.ok) return fail('Non trovo più questo lavoro: carica di nuovo la foto e riprova.');
          if (data.status === 'running') {
            timer = setTimeout(poll, 2500);
          } else if (data.status === 'done' && data.results) {
            closed = true;
            finish(jobId);
          } else {
            fail('Il lavoro si è fermato prima di finire.');
          }
        } catch {
          timer = setTimeout(poll, 3500);
        }
      };

      source = new EventSource(`${API_URL}/mission/${jobId}/stream`);
      source.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'log') {
            const msg = String(payload.msg || '');
            addLog(msg);
            for (const [keyword, idx] of STAGE_KEYWORDS) {
              if (msg.toLowerCase().includes(keyword.toLowerCase())) {
                setStage((prev) => Math.max(prev, idx));
                break;
              }
            }
          } else if (payload.type === 'status') {
            source?.close();
            if (payload.status === 'done') {
              closed = true;
              setStage(4);
              finish(jobId);
            } else {
              fail('Qualcosa è andato storto durante il lavoro. Controlla la chiave OpenRouter e riprova.');
            }
          }
        } catch {
          /* riga non leggibile: si ignora */
        }
      };
      source.onerror = () => {
        source?.close();
        timer = setTimeout(poll, 2000);
      };

      stopRef.current = () => {
        closed = true;
        source?.close();
        if (timer) clearTimeout(timer);
      };
    },
    [addLog, finish],
  );

  const start = useCallback(async () => {
    if (!photo) return;
    stopRef.current();
    setState('running');
    setStage(0);
    setLogs([]);
    setError('');
    const settings = loadSettings();
    const form = new FormData();
    form.append('foto', photo);
    form.append('brief', brief);
    form.append('text_model', settings.textModel);
    form.append('image_model', settings.imageModel);
    try {
      const res = await fetch(`${API_URL}/mission/start`, { method: 'POST', body: form });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
      try { localStorage.setItem(ACTIVE_JOB_STORAGE_KEY, data.job_id); } catch { /* storage non disponibile */ }
      follow(data.job_id);
    } catch (err) {
      setError(`Non riesco ad avviare il lavoro: ${err instanceof Error ? err.message : err}`);
      setState('error');
    }
  }, [photo, brief, follow]);

  // Se la pagina viene riaperta mentre il lavoro è in corso, lo riprende.
  useEffect(() => {
    let stored = '';
    try { stored = localStorage.getItem(ACTIVE_JOB_STORAGE_KEY) || ''; } catch { /* storage non disponibile */ }
    if (!stored) return;
    setState('running');
    follow(stored);
  }, [follow]);

  if (state === 'running') {
    return (
      <div className="page working" aria-live="polite">
        <h1 className="page-title">Sto preparando la scheda</h1>
        {photoPreview && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={photoPreview} alt="Il pezzo che stai caricando" />
        )}
        <MosaicTiles items={stepTiles(stage)} palette={palette} large />
        <p className="working-steps">{STAGE_TEXT[Math.min(stage, STAGE_TEXT.length - 1)]}</p>
        <p className="page-lead" style={{ margin: 0 }}>
          Ci vogliono alcuni minuti. Puoi lasciare la pagina aperta: quando è pronta si apre da sola.
        </p>
        {logs.length > 0 && (
          <details style={{ width: '100%', textAlign: 'left' }}>
            <summary className="btn-secondary details-toggle">Cosa sta succedendo</summary>
            <pre className="text-card" style={{ whiteSpace: 'pre-wrap', fontSize: 12, marginTop: 8 }}>{logs.slice(-12).join('\n')}</pre>
          </details>
        )}
      </div>
    );
  }

  return (
    <div className="page new-piece">
      <div>
        <h1 className="page-title">Nuovo pezzo</h1>
        <p className="page-lead">Carica la foto del pezzo, aggiungi una nota se serve: lo Studio prepara la scheda per il sito, WhatsApp e Google.</p>
      </div>

      {state === 'error' && (
        <div className="notice error" role="alert">
          <strong>Qualcosa è andato storto.</strong> {error}
          {logs.length > 0 && (
            <details style={{ marginTop: 6 }}>
              <summary>Dettagli</summary>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{logs.slice(-8).join('\n')}</pre>
            </details>
          )}
        </div>
      )}

      <PhotoDropzone photo={photo} photoPreview={photoPreview} onFile={handlePhotoSelect} onClear={handlePhotoClear} />

      <div>
        <label className="field-label" htmlFor="brief">
          Nota <small>facoltativa</small>
        </label>
        <textarea
          id="brief"
          className="brief-area"
          rows={4}
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          placeholder="Es. orecchini a cerchio, 22 euro, nuovi arrivi, per cerimonia o aperitivo."
        />
      </div>

      <div className="cta-bar">
        <button type="button" className="btn-mission" onClick={start} disabled={!photo}>
          Crea la scheda
        </button>
        {!photo && <p className="page-lead" style={{ margin: 0, textAlign: 'center' }}>Carica una foto per cominciare.</p>}
      </div>
    </div>
  );
}
