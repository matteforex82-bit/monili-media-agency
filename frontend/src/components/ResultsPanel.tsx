'use client';

import { useEffect, useMemo, useState } from 'react';

interface Props {
  results: Record<string, string>;
  apiUrl: string;
  runId: string;
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
  // Older missions
  selected_caption?: string;
  selected_hashtags?: string[];
  selected_whatsapp?: string;
  selected_gmb_title?: string;
  selected_gmb_text?: string;
  selected_cta?: string;
};

type Tab = 'sito' | 'whatsapp' | 'google' | 'instagram';
type ShowcaseCandidate = {
  src: string;
  available: boolean;
  recommended?: boolean;
  kind?: string;
  error?: string;
};

// Empty until the showcase site is online: the link is hidden rather than
// pointing to a domain that is not ours.
const SHOWCASE_REVIEW_URL = process.env.NEXT_PUBLIC_SHOWCASE_REVIEW_URL || '';
// Must match SHOWCASE_MAX_IMAGES in api/server.py (Vercel body size limit).
const SHOWCASE_MAX_IMAGES = 4;

function parseJsonObject<T>(raw: string | undefined, fallback: T): T {
  if (!raw) return fallback;
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : fallback;
  } catch {
    return fallback;
  }
}

function downloadBlob(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
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

function CopyActions({ value, filename }: { value: string; filename: string }) {
  const [copied, setCopied] = useState(false);
  const safeValue = value.trim();

  const copy = () => {
    navigator.clipboard.writeText(safeValue).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  return (
    <div className="result-actions">
      <button type="button" onClick={copy} className="btn-mission result-button">
        {copied ? 'Copiato' : 'Copia'}
      </button>
      <button type="button" onClick={() => downloadBlob(safeValue, filename)} className="btn-secondary result-button">
        .txt
      </button>
    </div>
  );
}

function TextBlock({ title, value, filename }: { title: string; value: string; filename: string }) {
  const safeValue = value.trim();
  const author = title.toLowerCase().includes('caption') || title.toLowerCase().includes('hashtag') || title.toLowerCase().includes('whatsapp') ? 'Carla' : 'Paolo';
  return (
    <section className="result-block">
      <div className="result-block-header">
        <div className="bot-card-title-with-avatar">
          <span className="bot-avatar small">{author[0]}</span>
          <div>
            <h3>{title}</h3>
            <p>{author} ha preparato questo testo, pronto da copiare.</p>
          </div>
        </div>
        <CopyActions value={safeValue} filename={filename} />
      </div>
      <pre className="result-text">{safeValue || 'Non disponibile'}</pre>
    </section>
  );
}

function ImageCard({
  title,
  imageUrl,
  filename,
  note,
}: {
  title: string;
  imageUrl: string;
  filename: string;
  note?: string;
}) {
  const [status, setStatus] = useState<'idle' | 'saving' | 'done' | 'fallback'>('idle');

  const onSave = async () => {
    if (status === 'saving') return;
    setStatus('saving');
    try {
      const mode = await saveImageToDevice(imageUrl, filename);
      setStatus(mode === 'shared' ? 'done' : 'fallback');
    } catch {
      window.open(imageUrl, '_blank', 'noopener,noreferrer');
      setStatus('fallback');
    } finally {
      setTimeout(() => setStatus('idle'), 2200);
    }
  };

  return (
    <article className="result-image-card">
      <div className="result-image-title"><span className="bot-avatar small vera">V</span>{title}</div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={imageUrl} alt={title} className="result-image" />
      {note && <p className="result-image-note">{note}</p>}
      <div className="result-actions">
        <a href={imageUrl} download={filename} className="btn-mission result-button">.jpg</a>
        <button type="button" onClick={onSave} className="btn-secondary result-button">
          {status === 'saving' ? 'Salvo...' : status === 'done' ? 'Salvato' : status === 'fallback' ? 'Aperta' : 'Salva su iPhone'}
        </button>
      </div>
    </article>
  );
}

function getResultImages(results: Record<string, string>, prefix: string) {
  return Object.keys(results)
    .filter((key) => key.startsWith(prefix) && results[key])
    .sort((a, b) => Number(a.replace(prefix, '')) - Number(b.replace(prefix, '')));
}

function ShowcasePublishPanel({ apiUrl, runId }: { apiUrl: string; runId: string }) {
  const [candidates, setCandidates] = useState<ShowcaseCandidate[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any | null>(null);
  const [price, setPrice] = useState('');
  const [onRequest, setOnRequest] = useState(false);

  const loadCandidates = async () => {
    if (!runId) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${apiUrl}/missions/${encodeURIComponent(runId)}/showcase/candidates`);
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
      const rawItems = Array.isArray(data?.items) ? data.items : [];
      const items: ShowcaseCandidate[] = rawItems
        .map((item: unknown) => {
          if (!item || typeof item !== 'object') return null;
          const obj = item as Record<string, unknown>;
          const src = typeof obj.src === 'string' ? obj.src : '';
          if (!src) return null;
          return {
            src,
            available: Boolean(obj.available),
            recommended: Boolean(obj.recommended),
            error: typeof obj.error === 'string' ? obj.error : undefined,
            kind: typeof obj.kind === 'string' ? obj.kind : undefined,
          };
        })
        .filter((item: ShowcaseCandidate | null): item is ShowcaseCandidate => Boolean(item));
      setCandidates(items);
      const recommended = items.filter((item) => item.available && item.recommended).map((item) => item.src);
      const fallback = items.filter((item) => item.available).map((item) => item.src);
      setSelected((recommended.length ? recommended : fallback).slice(0, SHOWCASE_MAX_IMAGES));
    } catch (err) {
      setError(`Analisi immagini non disponibile: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadCandidates();
  }, [runId, apiUrl]);

  const publish = async () => {
    if (!selected.length) {
      setError('Seleziona almeno una foto da inviare.');
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
          price: onRequest ? null : price.trim(),
          on_request: onRequest,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || data?.details?.error || `HTTP ${res.status}`);
      setResult(data);
    } catch (err) {
      setError(`Invio non riuscito: ${err}`);
    } finally {
      setPublishing(false);
    }
  };

  if (!runId) return null;

  return (
    <section className="result-block">
      <div className="result-block-header">
        <h3>Pubblica sul sito vetrina</h3>
        <div className="result-actions">
          <button type="button" onClick={() => void loadCandidates()} className="btn-secondary result-button" disabled={loading || publishing}>
            {loading ? 'Analisi...' : 'Rianalizza'}
          </button>
          <button type="button" onClick={() => void publish()} className="btn-mission result-button" disabled={publishing || !selected.length}>
            Invia draft
          </button>
        </div>
      </div>
      {error && <p className="result-error">{error}</p>}
      <div className="showcase-price">
        <label>
          Prezzo (€)
          <input
            type="text"
            inputMode="decimal"
            placeholder="es. 22,50"
            value={price}
            disabled={onRequest}
            onChange={(e) => setPrice(e.target.value)}
          />
        </label>
        <label className="showcase-price-check">
          <input type="checkbox" checked={onRequest} onChange={(e) => setOnRequest(e.target.checked)} />
          Su richiesta (senza prezzo)
        </label>
        {!onRequest && !price.trim() && (
          <small>Senza prezzo la scheda arriva come bozza da completare nell&apos;admin del sito.</small>
        )}
      </div>
      <p className="result-image-note">
        Foto per il sito: {selected.length}/{SHOWCASE_MAX_IMAGES} selezionate.
      </p>
      {candidates.length > 0 && (
        <div className="result-image-grid compact">
          {candidates.map((item, index) => (
            <label key={`${item.src}-${index}`} className="showcase-pick">
              <input
                type="checkbox"
                checked={selected.includes(item.src)}
                disabled={
                  !item.available ||
                  (!selected.includes(item.src) && selected.length >= SHOWCASE_MAX_IMAGES)
                }
                onChange={() =>
                  setSelected((prev) => (prev.includes(item.src) ? prev.filter((src) => src !== item.src) : [...prev, item.src]))
                }
              />
              {item.available ? (
                // eslint-disable-next-line @next/next/no-img-element
                  <img src={`${apiUrl}/files/${item.src}`} alt={`Foto sito ${index + 1}`} />
              ) : (
                <span>{item.error || 'File non disponibile'}</span>
              )}
              <small>{item.src.includes('real_photo') ? 'Foto reale 4:5' : item.kind?.startsWith('image_site_') ? 'Foto dedicata sito 4:5' : 'Adattabile al sito'}</small>
            </label>
          ))}
        </div>
      )}
      {result && <p className="result-ok">Draft creato: {result.ingest?.created_id || 'invio completato'}</p>}
      {SHOWCASE_REVIEW_URL && (
        <a href={SHOWCASE_REVIEW_URL} target="_blank" rel="noreferrer" className="result-link">
          Apri review admin
        </a>
      )}
    </section>
  );
}

export default function ResultsPanel({ results, apiUrl, runId }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('sito');
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const publishPack = parseJsonObject<PublishPack>(results.publish_pack_json, {});

  const hashtags = Array.isArray(publishPack.hashtags || publishPack.selected_hashtags)
    ? (publishPack.hashtags || publishPack.selected_hashtags || []).join(' ')
    : '';
  const whatsapp = publishPack.whatsapp_share || publishPack.selected_whatsapp || '';
  const cta = publishPack.cta || publishPack.selected_cta || '';
  const caption = publishPack.caption || publishPack.selected_caption || '';
  const gmbFinal = `${(publishPack.gmb_title || publishPack.selected_gmb_title || '').trim()}\n\n${(publishPack.gmb_text || publishPack.selected_gmb_text || '').trim()}`.trim();
  const seoFinal = `${(publishPack.seo_title || '').trim()}\n\n${(publishPack.seo_description || '').trim()}`.trim();
  const siteImageKeys = useMemo(() => getResultImages(results, 'image_site_'), [results]);
  // Missions made before the "scheda pezzo" still carry Instagram images: show them, never empty tabs.
  const legacyImageKeys = useMemo(
    () => [
      ...['image_feed', 'image_stories'].filter((key) => results[key]),
      ...getResultImages(results, 'image_story_'),
      ...getResultImages(results, 'image_carousel_'),
      ...getResultImages(results, 'image_ai_'),
    ],
    [results],
  );

  const tabs: Array<{ id: Tab; label: string }> = [
    { id: 'sito', label: 'Sito' },
    { id: 'whatsapp', label: 'WhatsApp e negozio' },
    { id: 'google', label: 'Google' },
    ...(legacyImageKeys.length ? [{ id: 'instagram' as Tab, label: 'Instagram (vecchio kit)' }] : []),
  ];

  return (
    <div className="results-shell">
      <div className="bot-kit-banner">
        <div className="bot-avatar-stack" aria-hidden="true">
          <span className="bot-avatar">A</span>
          <span className="bot-avatar vera">V</span>
          <span className="bot-avatar carla">C</span>
        </div>
        <div>
          <div className="label-eyebrow">Scheda pezzo pronta</div>
          <h2>{publishPack.product_name || 'La scheda del pezzo è pronta.'}</h2>
          <p>Foto per il sito, messaggio WhatsApp e post Google. Per Instagram fai il Reel di questo pezzo.</p>
          <a href="/reel" className="result-link">Fai il Reel di questo pezzo →</a>
        </div>
      </div>
      <nav className="results-tabs" aria-label="Risultati scheda pezzo">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`result-tab ${activeTab === tab.id ? 'active' : ''}`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="results-body">
        {activeTab === 'sito' && (
          <div className="result-stack">
            {results.decision_summary && (
              <TextBlock title="Cosa fare ora" value={results.decision_summary} filename="cosa-fare-ora.txt" />
            )}
            {siteImageKeys.length > 0 && (
              <div className="result-image-grid">
                {siteImageKeys.map((key, index) => (
                  <ImageCard
                    key={key}
                    title={results[key].includes('real_photo') ? 'Foto reale' : `Foto sito ${index + 1}`}
                    imageUrl={`${apiUrl}/files/${results[key]}`}
                    filename={`foto-sito-${index + 1}.jpg`}
                  />
                ))}
              </div>
            )}
            <ShowcasePublishPanel apiUrl={apiUrl} runId={runId} />
          </div>
        )}

        {activeTab === 'whatsapp' && (
          <div className="result-stack">
            <TextBlock title="WhatsApp (da mandare con il link del pezzo)" value={whatsapp} filename="whatsapp.txt" />
            <TextBlock title="Invito" value={cta} filename="invito.txt" />
            <TextBlock title="Caption storia" value={[caption, hashtags].filter(Boolean).join('\n\n')} filename="caption-storia.txt" />
          </div>
        )}

        {activeTab === 'google' && (
          <div className="result-stack">
            <TextBlock title="Google Business" value={gmbFinal} filename="google-business.txt" />
            {seoFinal && <TextBlock title="Titolo e descrizione per Google" value={seoFinal} filename="seo.txt" />}
          </div>
        )}

        {activeTab === 'instagram' && (
          <div className="result-image-grid">
            {legacyImageKeys.map((key, index) => (
              <ImageCard key={key} title={`Immagine ${index + 1}`} imageUrl={`${apiUrl}/files/${results[key]}`} filename={`instagram-${index + 1}.jpg`} />
            ))}
          </div>
        )}
      </div>

      <section className="result-block advanced">
        <button type="button" onClick={() => setAdvancedOpen((value) => !value)} className="btn-secondary result-button full">
          {advancedOpen ? 'Nascondi dettagli' : 'Mostra dettagli'}
        </button>
        {advancedOpen && (
          <div className="result-stack spaced">
            <TextBlock title="Analisi prodotto" value={results.analisi || ''} filename="analisi-prodotto.txt" />
            <TextBlock title="Piano scheda" value={results.scheda_plan || results.strategy_plan || ''} filename="piano-scheda.json" />
            <TextBlock title="Report foto" value={results.asset_report_json || ''} filename="report-foto.json" />
          </div>
        )}
      </section>
    </div>
  );
}
