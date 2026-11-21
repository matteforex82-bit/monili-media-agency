'use client';

import { useCallback, useEffect, useState } from 'react';
import InstagramShare from '@/components/InstagramShare';
import { loadSettings } from '@/lib/settings';

// Post con testo (PRD prompt completi, T5): etichette su foto vera, titolo editoriale, look con Aurora, carosello.
type Mode = 'etichette' | 'titolo' | 'look' | 'carosello';

interface PostItem {
  id: string;
  kind: Mode;
  files: Array<{ src: string; aiGenerated: boolean }>;
  aiGenerated: boolean;
  model?: string;
  caption?: string;
  text_written_by?: 'ai' | 'codice';
  text_problems?: string[];
  slide_titles?: string[];
  created_at?: string;
}

interface PostInfo {
  items: PostItem[];
  price: string;
  reference: string;
  location: string;
  models: string[];
  themes: Record<string, string>;
}

interface Piece {
  name: string;
  price: string;
  reference: string;
  shop: '' | '17' | '21';
}

const MODES: Array<{ id: Mode; title: string; hint: string }> = [
  { id: 'etichette', title: 'Outfit con prezzi', hint: 'Foto vera, nomi e prezzi scritti dallo Studio' },
  { id: 'titolo', title: 'Titolo editoriale', hint: 'Il pezzo con una frase in serif' },
  { id: 'look', title: 'Look con Aurora', hint: 'La testimonial con il pezzo' },
  { id: 'carosello', title: 'Carosello', hint: '3 slide, una didascalia' },
];
const KIND_LABEL: Record<Mode, string> = { etichette: 'Outfit con prezzi', titolo: 'Titolo editoriale', look: 'Look con Aurora', carosello: 'Carosello' };
const EMPTY_PIECE: Piece = { name: '', price: '', reference: '', shop: '' };

interface Props {
  apiUrl: string;
  runId: string;
  caption: string;
  hashtags: string[];
}

export default function PostMaker({ apiUrl, runId, caption, hashtags }: Props) {
  const [info, setInfo] = useState<PostInfo | null>(null);
  const [mode, setMode] = useState<Mode>('titolo');
  const [model, setModel] = useState('GPT Image');
  const [format, setFormat] = useState<'post' | 'storia'>('post');
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [showPrice, setShowPrice] = useState(true);
  const [theme, setTheme] = useState('tre-modi');
  const [photo, setPhoto] = useState<File | null>(null);
  const [pieces, setPieces] = useState<Piece[]>([{ ...EMPTY_PIECE }]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const base = `${apiUrl}/missions/${encodeURIComponent(runId)}/post`;
  const url = (src: string) => `${apiUrl}/files/${src}`;

  const load = useCallback(async () => {
    try {
      const res = await fetch(base, { cache: 'no-store' });
      if (res.ok) {
        const data = (await res.json()) as PostInfo;
        setInfo(data);
        setPieces((prev) => (prev.length === 1 && !prev[0].name ? [{ ...EMPTY_PIECE, price: data.price.replace(' €', ''), reference: data.reference }] : prev));
      }
    } catch {
      /* il pezzo non ha ancora una cartella */
    }
  }, [base]);

  useEffect(() => {
    void load();
  }, [load]);

  async function create() {
    setBusy(true);
    setError('');
    try {
      let res: Response;
      if (mode === 'etichette') {
        if (!photo) throw new Error('Carica la foto vera del flat-lay.');
        const form = new FormData();
        form.append('foto', photo);
        form.append('items', JSON.stringify(pieces.filter((p) => p.name.trim())));
        form.append('formato', format);
        res = await fetch(`${base}/etichette`, { method: 'POST', body: form });
      } else if (mode === 'carosello') {
        res = await fetch(`${base}/carosello`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ theme, model, text_model: loadSettings().textModel }),
        });
      } else {
        if (!title.trim()) throw new Error('Scrivi il titolo: è il testo che compare sul post.');
        res = await fetch(`${base}/titolo`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ kind: mode, title, subtitle, model, formato: format, show_price: showPrice, text_model: loadSettings().textModel }),
        });
      }
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  const ai = mode !== 'etichette';
  const setPiece = (index: number, patch: Partial<Piece>) => setPieces((prev) => prev.map((p, i) => (i === index ? { ...p, ...patch } : p)));
  const tags = hashtags.join(' ');

  return (
    <section className="pub-block post-maker" aria-labelledby="post-maker-title">
      <h3 id="post-maker-title">Crea un post con testo</h3>
      <div className="rs-modes post-modes" role="tablist" aria-label="Tipo di post">
        {MODES.map((item) => (
          <button key={item.id} type="button" role="tab" className="rs-mode" aria-selected={mode === item.id} onClick={() => setMode(item.id)}>
            <strong>{item.title}</strong>
            <span>{item.hint}</span>
          </button>
        ))}
      </div>

      {mode === 'etichette' && (
        <div className="post-form">
          <label className="field-label" htmlFor="post-photo">
            Foto vera dei pezzi insieme
          </label>
          <input id="post-photo" type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files?.[0] ?? null)} />
          {pieces.map((piece, index) => (
            <fieldset key={index} className="post-piece">
              <legend>Pezzo {index + 1}</legend>
              <input className="lab-select" placeholder="Nome (es. Orecchini a fiore)" value={piece.name} onChange={(e) => setPiece(index, { name: e.target.value })} />
              <input className="lab-select" placeholder="Prezzo €" inputMode="decimal" value={piece.price} onChange={(e) => setPiece(index, { price: e.target.value })} />
              <input className="lab-select" placeholder="Rif." value={piece.reference} onChange={(e) => setPiece(index, { reference: e.target.value })} />
              <select className="lab-select" value={piece.shop} onChange={(e) => setPiece(index, { shop: e.target.value as Piece['shop'] })} aria-label="Dove si trova">
                <option value="">Sede: non indicata</option>
                <option value="17">Al 17 (argento e pietre)</option>
                <option value="21">Al 21</option>
              </select>
            </fieldset>
          ))}
          <button type="button" className="btn-secondary" onClick={() => setPieces((prev) => [...prev, { ...EMPTY_PIECE }])} disabled={pieces.length >= 8}>
            Aggiungi un pezzo
          </button>
          <p className="pub-meta">Nessuna AI: i prodotti restano quelli della foto. Il prezzo vuoto non compare.</p>
        </div>
      )}

      {(mode === 'titolo' || mode === 'look') && (
        <div className="post-form">
          <label className="field-label" htmlFor="post-title">
            Titolo <small>lo controlli tu prima di generare</small>
          </label>
          <input id="post-title" className="lab-select" maxLength={70} placeholder="Non sono semplici orecchini." value={title} onChange={(e) => setTitle(e.target.value)} />
          <label className="field-label" htmlFor="post-subtitle">
            Sottotitolo <small>facoltativo</small>
          </label>
          <input id="post-subtitle" className="lab-select" maxLength={90} value={subtitle} onChange={(e) => setSubtitle(e.target.value)} />
          <label className="post-check">
            <input type="checkbox" checked={showPrice} onChange={(e) => setShowPrice(e.target.checked)} />
            {info?.price ? `Metti il prezzo della scheda (${info.price})` : 'Nessun prezzo nella scheda: non compare'}
          </label>
          {mode === 'look' && <p className="pub-meta">Il volto di Aurora arriva dalle foto in aurora-riferimenti, se ci sono.</p>}
        </div>
      )}

      {mode === 'carosello' && (
        <div className="post-form">
          <label className="field-label" htmlFor="post-theme">
            Tema
          </label>
          <select id="post-theme" className="lab-select" value={theme} onChange={(e) => setTheme(e.target.value)}>
            {Object.entries(info?.themes ?? { 'tre-modi': '3 modi di indossarlo' }).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="post-options">
        {ai && (
          <label>
            Modello
            <select className="lab-select" value={model} onChange={(e) => setModel(e.target.value)}>
              {(info?.models ?? ['GPT Image', 'Nano Banana']).map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
          </label>
        )}
        {mode !== 'carosello' && (
          <label>
            Formato
            <select className="lab-select" value={format} onChange={(e) => setFormat(e.target.value as 'post' | 'storia')}>
              <option value="post">Post 4:5</option>
              <option value="storia">Storia 9:16</option>
            </select>
          </label>
        )}
      </div>
      {error && (
        <p className="pub-status" role="alert">
          {error}
        </p>
      )}
      <button type="button" className="btn-mission" onClick={create} disabled={busy}>
        {busy ? (ai ? 'Creo e rileggo il testo… (circa un minuto)' : 'Preparo il post…') : 'Crea il post'}
      </button>

      {(info?.items ?? []).map((item) => (
        <div key={item.id} className="post-made">
          <p className="pub-meta">
            <strong>{KIND_LABEL[item.kind] ?? item.kind}</strong>
            {item.model ? ` · fatto con ${item.model}` : ' · foto vera'}
            {item.text_written_by === 'codice' && ' · il titolo l’ha scritto lo Studio (l’AI sbagliava una lettera)'}
          </p>
          <div className="pub-photos">
            {item.files.map((file, index) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={file.src} src={url(file.src)} alt={`${KIND_LABEL[item.kind] ?? 'Post'} ${index + 1}`} loading="lazy" />
            ))}
          </div>
          <InstagramShare
            files={item.files.map((file, index) => ({ url: url(file.src), filename: `monili-${item.kind}-${index + 1}.jpg` }))}
            caption={[item.caption || caption, tags].filter(Boolean).join('\n\n')}
            kind="Post"
            hasAiWoman={item.aiGenerated}
          />
        </div>
      ))}
    </section>
  );
}
