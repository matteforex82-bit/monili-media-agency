'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import InstagramShare from '@/components/InstagramShare';
import type { PieceSummary } from '@/lib/pieces';

interface Props {
  results: Record<string, string>;
  apiUrl: string;
  runId: string;
  summary: PieceSummary | null;
  onChanged: () => void;
}

type PublishPack = {
  product_name?: string;
  seo_title?: string;
  seo_description?: string;
  whatsapp_share?: string;
  gmb_title?: string;
  gmb_text?: string;
  caption?: string;
  hashtags?: string[];
  cta?: string;
  // Missioni vecchie
  selected_caption?: string;
  selected_hashtags?: string[];
  selected_whatsapp?: string;
  selected_gmb_title?: string;
  selected_gmb_text?: string;
  selected_cta?: string;
};

type ShowcaseCandidate = {
  src: string;
  available: boolean;
  recommended?: boolean;
  kind?: string;
  note?: string;
  error?: string;
};

// Vuoto finché il sito non è online: il link resta nascosto invece di puntare a un dominio non nostro.
const SHOWCASE_REVIEW_URL = process.env.NEXT_PUBLIC_SHOWCASE_REVIEW_URL || '';
// Deve combaciare con SHOWCASE_MAX_IMAGES in api/server.py (limite di Vercel).
const SHOWCASE_MAX_IMAGES = 4;

// Il tipo di foto si legge dal nome del file, mai dalla posizione: la foto vera può mancare.
const SITE_IMAGE_KINDS: Array<{ match: string; label: string; slug: string }> = [
  { match: 'site_01_product_clean', label: 'Catalogo (AI)', slug: 'catalogo-ai' },
  { match: 'site_02_worn', label: 'Indossata (AI)', slug: 'indossata-ai' },
  { match: 'site_03_real_photo', label: 'Foto vera ripulita', slug: 'foto-vera-ripulita' },
];

function siteImageLabel(src: string) {
  return SITE_IMAGE_KINDS.find((kind) => src.includes(kind.match))?.label ?? 'Foto (vecchio kit)';
}

function siteImageSlug(src: string) {
  return SITE_IMAGE_KINDS.find((kind) => src.includes(kind.match))?.slug ?? 'foto';
}

function parseJsonObject<T>(raw: string | undefined, fallback: T): T {
  if (!raw) return fallback;
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : fallback;
  } catch {
    return fallback;
  }
}

async function saveImageToDevice(imageUrl: string, filename: string) {
  const response = await fetch(imageUrl, { cache: 'no-store' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const blob = await response.blob();
  const file = new File([blob], filename, { type: blob.type || 'image/jpeg' });
  const nav = navigator as Navigator & { canShare?: (data?: ShareData) => boolean };
  if (nav.share && nav.canShare?.({ files: [file] })) {
    await nav.share({ files: [file], title: filename });
    return 'shared';
  }
  const blobUrl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(blobUrl);
  return 'downloaded';
}

function SaveButton({ imageUrl, filename }: { imageUrl: string; filename: string }) {
  const [status, setStatus] = useState<'idle' | 'saving' | 'done'>('idle');
  const onSave = async () => {
    if (status === 'saving') return;
    setStatus('saving');
    try {
      await saveImageToDevice(imageUrl, filename);
      setStatus('done');
    } catch {
      window.open(imageUrl, '_blank', 'noopener,noreferrer');
      setStatus('done');
    } finally {
      setTimeout(() => setStatus('idle'), 2200);
    }
  };
  return (
    <button type="button" onClick={onSave} className="btn-secondary">
      {status === 'saving' ? 'Salvo...' : status === 'done' ? 'Fatto' : 'Salva'}
    </button>
  );
}

function TextCard({ title, value }: { title: string; value: string }) {
  const [copied, setCopied] = useState(false);
  const text = value.trim();
  if (!text) return null;
  const copy = () => {
    navigator.clipboard.writeText(text).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };
  return (
    <section className="text-card">
      <header>
        <h3>{title}</h3>
        <button type="button" onClick={copy} className="btn-secondary" aria-live="polite">
          {copied ? 'Copiato' : 'Copia'}
        </button>
      </header>
      <pre>{text}</pre>
    </section>
  );
}

function ShowcaseSection({
  apiUrl,
  runId,
  published,
  onSent,
}: {
  apiUrl: string;
  runId: string;
  published: PieceSummary['steps']['sito'];
  onSent: () => void;
}) {
  const [candidates, setCandidates] = useState<ShowcaseCandidate[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<{ published?: boolean; product_url?: string | null } | null>(null);
  const [price, setPrice] = useState('');
  const [size, setSize] = useState('');
  const [category, setCategory] = useState('');
  const [location, setLocation] = useState('');
  // Spenta di default: nelle prime settimane si controlla la bozza sul sito prima di pubblicarla.
  const [publishNow, setPublishNow] = useState(false);
  // Deve combaciare con i controlli di api/server.py: niente pezzo sul sito senza prezzo e negozio,
  // né abbigliamento senza taglia.
  const sizeRequired = category === 'abbigliamento';
  const missing = [
    !price.trim() && 'il prezzo',
    !location && 'il negozio',
    sizeRequired && !size.trim() && 'la taglia',
  ].filter(Boolean) as string[];

  useEffect(() => {
    if (!runId) return;
    let alive = true;
    setLoading(true);
    fetch(`${apiUrl}/missions/${encodeURIComponent(runId)}/showcase/candidates`)
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
        return data;
      })
      .then((data) => {
        if (!alive) return;
        const items: ShowcaseCandidate[] = (Array.isArray(data?.items) ? data.items : [])
          .map((item: Record<string, unknown>) => {
            const src = typeof item?.src === 'string' ? item.src : '';
            if (!src) return null;
            return {
              src,
              available: Boolean(item.available),
              recommended: Boolean(item.recommended),
              error: typeof item.error === 'string' ? item.error : undefined,
              kind: typeof item.kind === 'string' ? item.kind : undefined,
              note: typeof item.note === 'string' ? item.note : undefined,
            };
          })
          .filter(Boolean) as ShowcaseCandidate[];
        setCandidates(items);
        if (typeof data?.category === 'string') setCategory((prev) => prev || data.category);
        const recommended = items.filter((item) => item.available && item.recommended).map((item) => item.src);
        const fallback = items.filter((item) => item.available).map((item) => item.src);
        setSelected((recommended.length ? recommended : fallback).slice(0, SHOWCASE_MAX_IMAGES));
      })
      .catch((err) => alive && setError(`Non riesco a leggere le foto: ${err instanceof Error ? err.message : err}`))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [runId, apiUrl]);

  const publish = async () => {
    if (!selected.length) {
      setError('Spunta almeno una foto da inviare.');
      return;
    }
    if (missing.length) {
      setError(`Per inviare manca ${missing.join(', ')}.`);
      return;
    }
    setPublishing(true);
    setError('');
    setResult(null);
    try {
      const res = await fetch(`${apiUrl}/missions/${encodeURIComponent(runId)}/showcase/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selected_images: selected,
          price: price.trim(),
          size: size.trim(),
          category,
          location,
          publish_now: publishNow,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || data?.details?.error || `HTTP ${res.status}`);
      setResult(data);
      onSent();
    } catch (err) {
      setError(`Invio non riuscito: ${err instanceof Error ? err.message : err}`);
    } finally {
      setPublishing(false);
    }
  };

  const toggle = (src: string) =>
    setSelected((prev) => (prev.includes(src) ? prev.filter((item) => item !== src) : [...prev, src]));

  return (
    <>
      <section className="step" aria-labelledby="step-foto">
        <h2 className="step-title" id="step-foto"><span className="step-num">1</span>Foto per il sito</h2>
        <p className="step-hint">
          Spunta quelle da mandare ({selected.length} su {SHOWCASE_MAX_IMAGES}). Controlla che il pezzo sia identico al vero.
        </p>
        {loading && <p className="step-hint">Controllo le foto...</p>}
        {!loading && candidates.length === 0 && !error && (
          <div className="notice">Questa scheda non ha foto per il sito.</div>
        )}
        {candidates.length > 0 && (
          <div className="pick-grid">
            {candidates.map((item) => (
              <div key={item.src} className="pick">
                <label className="pick-main">
                  <input
                    type="checkbox"
                    checked={selected.includes(item.src)}
                    disabled={!item.available || (!selected.includes(item.src) && selected.length >= SHOWCASE_MAX_IMAGES)}
                    onChange={() => toggle(item.src)}
                    aria-label={`Invia al sito: ${siteImageLabel(item.src)}`}
                  />
                  {item.available ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={`${apiUrl}/files/${item.src}`} alt={siteImageLabel(item.src)} />
                  ) : (
                    <span className="pick-note">{item.error || 'File non disponibile'}</span>
                  )}
                  <span className="pick-name">{siteImageLabel(item.src)}</span>
                </label>
                {item.note && <span className="pick-note">Attenzione: {item.note}</span>}
                {item.available && <SaveButton imageUrl={`${apiUrl}/files/${item.src}`} filename={`${siteImageSlug(item.src)}.jpg`} />}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="step" aria-labelledby="step-dati">
        <h2 className="step-title" id="step-dati"><span className="step-num">2</span>Prezzo, negozio, taglia</h2>
        <div className="form-grid">
          <label>
            Categoria
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="bijoux">Bijoux</option>
              <option value="gioielli">Gioielli</option>
              <option value="accessori">Accessori</option>
              <option value="abbigliamento">Abbigliamento</option>
            </select>
          </label>
          <label>
            Negozio
            <select value={location} required onChange={(e) => setLocation(e.target.value)}>
              <option value="">Scegli il negozio</option>
              <option value="via-cavour-17">Via Cavour 17 (argento e bijoux)</option>
              <option value="via-cavour-21">Via Cavour 21 (abbigliamento e accessori)</option>
            </select>
          </label>
          <label>
            Prezzo in euro
            <input type="text" inputMode="decimal" placeholder="es. 22,50" value={price} required onChange={(e) => setPrice(e.target.value)} />
          </label>
          <label>
            {sizeRequired ? 'Taglia' : 'Taglia o misura (facoltativa)'}
            <input
              type="text"
              placeholder={sizeRequired ? 'es. S, M, L oppure 42' : 'es. 16 per un anello'}
              value={size}
              required={sizeRequired}
              onChange={(e) => setSize(e.target.value)}
            />
          </label>
        </div>
      </section>

      <section className="step" aria-labelledby="step-invio">
        <h2 className="step-title" id="step-invio"><span className="step-num">3</span>Manda al sito</h2>
        <label className="check-row">
          <input type="checkbox" checked={publishNow} onChange={(e) => setPublishNow(e.target.checked)} />
          <span>
            <strong>Pubblica subito</strong>: il pezzo va online senza passare dalla revisione sul sito. Lascialo spento
            se vuoi controllare prima la bozza.
          </span>
        </label>
        <button
          type="button"
          onClick={() => void publish()}
          className="btn-mission publish-btn"
          disabled={publishing || loading || !selected.length || missing.length > 0}
        >
          {publishing ? 'Invio...' : publishNow ? 'Pubblica subito' : 'Invia bozza'}
        </button>
        {!publishing && missing.length > 0 && <p className="state-line">Per inviare manca {missing.join(', ')}.</p>}
        {error && <p className="state-line err" role="alert">{error}</p>}
        {result?.published && (
          <p className="state-line ok" role="status">
            Pubblicato sul sito.{' '}
            {result.product_url && <a href={result.product_url} target="_blank" rel="noreferrer">Apri la pagina del pezzo</a>}
          </p>
        )}
        {result && !result.published && (
          <p className="state-line ok" role="status">Bozza inviata: pubblicala dalla revisione sul sito.</p>
        )}
        {!result && published !== 'none' && (
          <p className="state-line ok">
            {published === 'published' ? 'Già pubblicato sul sito.' : 'Bozza già inviata al sito.'} Se invii di nuovo, il pezzo si aggiorna.
          </p>
        )}
        {SHOWCASE_REVIEW_URL && !result?.published && (
          <a href={SHOWCASE_REVIEW_URL} target="_blank" rel="noreferrer" className="back-link">Apri la revisione sul sito</a>
        )}
      </section>
    </>
  );
}


type ReelForShare = {
  format?: string;
  storyboard?: { shots?: Array<{ use_model?: boolean }> } | null;
  results?: { final_video?: string; copy?: { caption?: string; hashtags?: string[] } };
};

// Se il pezzo ha un Reel pronto si condivide quello; altrimenti le foto, come post.
function InstagramSection({
  apiUrl,
  reelId,
  photos,
  postCaption,
}: {
  apiUrl: string;
  reelId: string;
  photos: string[];
  postCaption: string;
}) {
  const [reel, setReel] = useState<ReelForShare | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!reelId) return;
    let alive = true;
    setReel(null);
    setFailed(false);
    fetch(`${apiUrl}/reel/${encodeURIComponent(reelId)}`, { cache: 'no-store' })
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`HTTP ${res.status}`))))
      .then((data) => alive && setReel(data))
      .catch(() => alive && setFailed(true));
    return () => {
      alive = false;
    };
  }, [apiUrl, reelId]);

  const video = reel?.results?.final_video;
  const reelCaption = [reel?.results?.copy?.caption, (reel?.results?.copy?.hashtags || []).join(' ')].filter(Boolean).join('\n\n');
  const reelFiles = useMemo(
    () => (video ? [{ url: `${apiUrl}/files/${video}`, filename: `monili-${reel?.format === 'story' ? 'storia' : 'reel'}.mp4` }] : []),
    [apiUrl, video, reel?.format],
  );
  const photoFiles = useMemo(
    () => photos.map((src) => ({ url: `${apiUrl}/files/${src}`, filename: `${siteImageSlug(src)}.jpg` })),
    [apiUrl, photos],
  );

  if (reelId && !failed && !reel) return <p className="step-hint">Preparo il Reel...</p>;
  if (reelId && reel && reelFiles.length) {
    return (
      <>
        <p className="step-hint">Condividi il Reel pronto di questo pezzo.</p>
        <InstagramShare
          files={reelFiles}
          caption={reelCaption}
          kind={reel.format === 'story' ? 'Storia' : 'Reel'}
          hasAiWoman={Boolean(reel.storyboard?.shots?.some((shot) => shot.use_model))}
        />
      </>
    );
  }
  if (!photoFiles.length) return <p className="step-hint">Non ci sono foto o Reel da condividere.</p>;
  return (
    <>
      <p className="step-hint">Non c&apos;è ancora un Reel pronto: puoi condividere le foto come post. I Reel arrivano di più a chi non ti segue.</p>
      <InstagramShare
        files={photoFiles}
        caption={postCaption}
        kind="Post"
        hasAiWoman={photos.some((src) => src.includes('site_02_worn'))}
      />
    </>
  );
}

export default function PieceView({ results, apiUrl, runId, summary, onChanged }: Props) {
  const pack = parseJsonObject<PublishPack>(results.publish_pack_json, {});
  const hashtags = (pack.hashtags || pack.selected_hashtags || []).join(' ');
  const whatsapp = pack.whatsapp_share || pack.selected_whatsapp || '';
  const cta = pack.cta || pack.selected_cta || '';
  const caption = pack.caption || pack.selected_caption || '';
  const gmb = `${(pack.gmb_title || pack.selected_gmb_title || '').trim()}\n\n${(pack.gmb_text || pack.selected_gmb_text || '').trim()}`.trim();
  const seo = `${(pack.seo_title || '').trim()}\n\n${(pack.seo_description || '').trim()}`.trim();
  // Le missioni fatte prima della "scheda pezzo" hanno ancora le foto Instagram: si mostrano, mai vuoto.
  const legacyKeys = useMemo(
    () =>
      Object.keys(results)
        .filter((key) => /^(image_feed|image_stories|image_story_\d+|image_carousel_\d+|image_ai_\d+)$/.test(key) && results[key]),
    [results],
  );
  const reels = summary?.reels ?? [];
  const doneReel = reels.find((reel) => reel.status === 'done');
  const sitePhotos = useMemo(
    () =>
      ['image_site_1', 'image_site_2', 'image_site_3']
        .map((key) => results[key])
        .filter((src): src is string => Boolean(src) && !(src.includes('site_03_real_photo') && results.real_photo_check?.includes('"ok": false'))),
    [results],
  );
  const postCaption = [caption, cta, hashtags].filter(Boolean).join('\n\n');

  return (
    <>
      <ShowcaseSection apiUrl={apiUrl} runId={runId} published={summary?.steps.sito ?? 'none'} onSent={onChanged} />

      <section className="step" aria-labelledby="step-testi">
        <h2 className="step-title" id="step-testi">Testi pronti</h2>
        <p className="step-hint">Un tocco su Copia e incolli dove serve.</p>
        <div className="stack">
          <TextCard title="WhatsApp" value={whatsapp} />
          <TextCard title="Google Business" value={gmb} />
          <TextCard title="Instagram" value={[caption, hashtags, cta].filter(Boolean).join('\n\n')} />
          <TextCard title="Titolo e descrizione per Google" value={seo} />
        </div>
      </section>

      <section className="step" aria-labelledby="step-reel">
        <h2 className="step-title" id="step-reel">Reel di questo pezzo</h2>
        <p className="step-hint">Parte dalla foto di questa scheda e usa la stessa donna della foto indossata.</p>
        <div className="reel-links">
          <Link href={`/reel?pezzo=${encodeURIComponent(runId)}`} className="btn-mission">Fai il Reel</Link>
          {reels.map((reel) => (
            <Link key={reel.id} href={`/reel?reel=${encodeURIComponent(reel.id)}`} className="reel-row">
              <span>{reel.title || 'Reel senza titolo'}</span>
              <span>{reel.status === 'done' ? 'Pronto' : reel.status === 'error' ? 'Da riprovare' : 'In lavorazione'}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="step" aria-labelledby="step-ig">
        <h2 className="step-title" id="step-ig">Instagram</h2>
        <InstagramSection apiUrl={apiUrl} reelId={doneReel?.id || ''} photos={sitePhotos} postCaption={postCaption} />
      </section>

      <section className="step">
        <details>
          <summary className="btn-secondary details-toggle">Dettagli</summary>
          <div className="stack" style={{ marginTop: 10 }}>
            <TextCard title="Cosa fare ora" value={results.decision_summary || ''} />
            <TextCard title="Analisi del pezzo" value={results.analisi || ''} />
            <TextCard title="Piano della scheda" value={results.scheda_plan || results.strategy_plan || ''} />
            <TextCard title="Report foto" value={results.asset_report_json || ''} />
            {legacyKeys.length > 0 && (
              <>
                <h3 className="display" style={{ fontSize: 20, margin: '8px 0 0' }}>Foto Instagram (vecchio kit)</h3>
                <div className="pick-grid">
                  {legacyKeys.map((key, index) => (
                    <div key={key} className="pick">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={`${apiUrl}/files/${results[key]}`} alt={`Immagine ${index + 1}`} style={{ width: '100%', aspectRatio: '4 / 5', objectFit: 'cover', borderRadius: 4 }} />
                      <SaveButton imageUrl={`${apiUrl}/files/${results[key]}`} filename={`instagram-${index + 1}.jpg`} />
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </details>
      </section>
    </>
  );
}
