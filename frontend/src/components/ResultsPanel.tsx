'use client';

import { useEffect, useState } from 'react';
import CarouselWithTextOverlay from './CarouselWithTextOverlay';

interface Props {
  results: Record<string, string>;
  apiUrl: string;
  runId: string;
}

const SHOWCASE_REVIEW_URL =
  process.env.NEXT_PUBLIC_SHOWCASE_REVIEW_URL ||
  'https://web-five-theta-58.vercel.app/admin/review';

type PublishPack = {
  selected_format?: string;
  selected_caption?: string;
  caption_alternatives?: string[];
  selected_hashtags?: string[];
  hashtags_alternative_set?: string[];
  selected_whatsapp?: string;
  selected_gmb_title?: string;
  selected_gmb_text?: string;
  selected_story_frames?: string[];
  selected_cta?: string;
  selected_posting_time?: string;
  notes_for_owner?: string;
  selected_tripadvisor_title?: string;
  selected_tripadvisor_text?: string;
};

type CarouselSlideCopy = {
  carousel_caption?: string;
  slide_texts?: string[];
};

type Tab = 'instagram' | 'gmb' | 'tripadvisor' | 'sito';
type ShowcaseCandidate = {
  src: string;
  available: boolean;
  recommended?: boolean;
  error?: string;
};

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

function parsePublishPack(raw: string | undefined): PublishPack {
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

function parseCarouselSlideCopy(raw: string | undefined): CarouselSlideCopy {
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

async function saveImageToDevice(imageUrl: string, filename: string) {
  const response = await fetch(imageUrl, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const blob = await response.blob();
  const file = new File([blob], filename, {
    type: blob.type || 'image/jpeg',
  });

  const nav = navigator as Navigator & {
    canShare?: (data?: ShareData) => boolean;
  };
  if (nav.share && nav.canShare && nav.canShare({ files: [file] })) {
    await nav.share({
      files: [file],
      title: 'Salva foto',
      text: 'Salva questa immagine nella galleria',
    });
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

function SaveImageButton({
  imageUrl,
  filename,
}: {
  imageUrl: string;
  filename: string;
}) {
  const [status, setStatus] = useState<'idle' | 'saving' | 'done' | 'fallback' | 'error'>('idle');

  const onSave = async () => {
    if (status === 'saving') return;
    setStatus('saving');
    try {
      const mode = await saveImageToDevice(imageUrl, filename);
      setStatus(mode === 'shared' ? 'done' : 'fallback');
      setTimeout(() => setStatus('idle'), 2200);
    } catch {
      window.open(imageUrl, '_blank', 'noopener,noreferrer');
      setStatus('fallback');
      setTimeout(() => setStatus('idle'), 2200);
    }
  };

  let label = 'Salva su iPhone';
  if (status === 'saving') label = 'Salvataggio...';
  if (status === 'done') label = 'Apri Condividi e salva';
  if (status === 'fallback') label = 'Aperta immagine';
  if (status === 'error') label = 'Riprova';

  return (
    <button
      onClick={onSave}
      disabled={status === 'saving'}
      className="btn-secondary"
      style={{ padding: '9px 12px', fontSize: 12 }}
    >
      {label}
    </button>
  );
}

function CopyButton({
  value,
  filename,
}: {
  value: string;
  filename: string;
}) {
  const [copied, setCopied] = useState(false);
  const safeValue = value.trim();

  const copyValue = () => {
    navigator.clipboard.writeText(safeValue).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div style={{ display: 'flex', gap: 6 }}>
      <button
        onClick={copyValue}
        className="btn-mission"
        style={{ padding: '8px 14px', fontSize: 12, fontWeight: 600 }}
      >
        {copied ? '✓ Copiato' : 'Copia testo'}
      </button>
      <button
        onClick={() => downloadBlob(safeValue, filename)}
        className="btn-secondary"
        style={{ padding: '8px 14px', fontSize: 12 }}
      >
        .txt
      </button>
    </div>
  );
}

function TextDisplay({ value, compact = false }: { value: string; compact?: boolean }) {
  const safeValue = value.trim();
  if (!safeValue) return <p style={{ color: 'var(--espresso-dim)', fontStyle: 'italic' }}>Non disponibile</p>;

  return (
    <pre
      style={{
        fontFamily: 'DM Sans',
        fontSize: compact ? 12 : 13,
        lineHeight: 1.6,
        color: 'var(--espresso-mid)',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        margin: 0,
        padding: 0,
      }}
    >
      {safeValue}
    </pre>
  );
}

function ImageStrip({
  title,
  keys,
  results,
  apiUrl,
  filePrefix,
  slideTexts = [],
}: {
  title: string;
  keys: string[];
  results: Record<string, string>;
  apiUrl: string;
  filePrefix: string;
  slideTexts?: string[];
}) {
  if (keys.length === 0) return null;

  return (
    <div>
      <div
        style={{
          fontFamily: 'DM Sans',
          fontSize: 11,
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.10em',
          color: 'var(--terracotta-dark)',
          marginBottom: 14,
        }}
      >
        {title}
      </div>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {keys.map((key, index) => (
          <div
            key={key}
            className="card"
            style={{ flex: '1 1 220px', padding: 16, textAlign: 'center', minWidth: 0 }}
          >
            <div
              style={{
                fontFamily: 'DM Sans',
                fontSize: 11,
                fontWeight: 700,
                color: 'var(--espresso-dim)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: 12,
              }}
            >
              {filePrefix === 'carousel_slide' ? `Slide ${index + 1}` : `Visual ${index + 1}`}
            </div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`${apiUrl}/files/${results[key]}`}
              alt={`${filePrefix} ${index + 1}`}
              style={{
                width: '100%',
                maxWidth: 220,
                borderRadius: 10,
                border: '1px solid var(--border)',
                display: 'block',
                margin: '0 auto 12px',
              }}
            />
            <a
              href={`${apiUrl}/files/${results[key]}`}
              download={`${filePrefix}_${index + 1}.png`}
              className="btn-mission"
              style={{ display: 'inline-block', padding: '9px 20px', fontSize: 13, textDecoration: 'none' }}
            >
              Scarica
            </a>
            <div style={{ marginTop: 8 }}>
              <SaveImageButton
                imageUrl={`${apiUrl}/files/${results[key]}`}
                filename={`${filePrefix}_${index + 1}.png`}
              />
            </div>
            {slideTexts[index] && (
              <div
                style={{
                  marginTop: 12,
                  padding: '9px 10px',
                  borderRadius: 8,
                  background: 'var(--cream-2)',
                  color: 'var(--espresso-mid)',
                  fontFamily: 'DM Sans',
                  fontSize: 12,
                  lineHeight: 1.45,
                  textAlign: 'left',
                }}
              >
                {slideTexts[index]}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function TabContent({
  tab,
  results,
  apiUrl,
  runId,
  publishPack,
  carouselCopy,
}: {
  tab: Tab;
  results: Record<string, string>;
  apiUrl: string;
  runId: string;
  publishPack: PublishPack;
  carouselCopy: CarouselSlideCopy;
}) {
  const selectedCaption = (publishPack.selected_caption || '').trim();
  const selectedHashtags = Array.isArray(publishPack.selected_hashtags)
    ? publishPack.selected_hashtags.join(' ')
    : '';
  const gmbFinal = `${(publishPack.selected_gmb_title || '').trim()}\n\n${(publishPack.selected_gmb_text || '').trim()}`.trim();
  const carouselCaption = (carouselCopy.carousel_caption || '').trim();
  const carouselSlideTexts = Array.isArray(carouselCopy.slide_texts) ? carouselCopy.slide_texts : [];

  const carouselImageKeys = Object.keys(results)
    .filter((key) => key.startsWith('image_carousel_') && results[key])
    .sort((a, b) => Number(a.replace('image_carousel_', '')) - Number(b.replace('image_carousel_', '')));

  if (tab === 'instagram') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {results.image_feed && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, alignItems: 'start' }}>
            <div className="card" style={{ padding: 16, textAlign: 'center' }}>
              <div
                style={{
                  fontFamily: 'DM Sans',
                  fontSize: 11,
                  fontWeight: 700,
                  color: 'var(--espresso-dim)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  marginBottom: 12,
                }}
              >
                Post 1:1 (1080x1080)
              </div>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`${apiUrl}/files/${results.image_feed}`}
                alt="Feed Instagram"
                style={{
                  width: '100%',
                  maxWidth: 220,
                  borderRadius: 10,
                  border: '1px solid var(--border)',
                  display: 'block',
                  margin: '0 auto 12px',
                }}
              />
              <a
                href={`${apiUrl}/files/${results.image_feed}`}
                download="feed_1080x1080.jpg"
                className="btn-mission"
                style={{ display: 'inline-block', padding: '9px 20px', fontSize: 13, textDecoration: 'none' }}
              >
                Scarica
              </a>
              <div style={{ marginTop: 8 }}>
                <SaveImageButton
                  imageUrl={`${apiUrl}/files/${results.image_feed}`}
                  filename="feed_1080x1080.jpg"
                />
              </div>
            </div>

            <div className="card" style={{ padding: 16 }}>
              <div
                style={{
                  fontFamily: 'DM Sans',
                  fontSize: 12,
                  fontWeight: 700,
                  color: 'var(--espresso)',
                  marginBottom: 12,
                }}
              >
                Caption finale
              </div>
              <TextDisplay value={selectedCaption} />
              <CopyButton value={selectedCaption} filename="caption_instagram.txt" />

              <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                <div
                  style={{
                    fontFamily: 'DM Sans',
                    fontSize: 12,
                    fontWeight: 700,
                    color: 'var(--espresso)',
                    marginBottom: 12,
                  }}
                >
                  Hashtag
                </div>
                <TextDisplay value={selectedHashtags} compact />
                <CopyButton value={selectedHashtags} filename="hashtag_instagram.txt" />
              </div>
            </div>
          </div>
        )}

        {carouselImageKeys.length > 0 && (
          <div>
            <ImageStrip
              title="Carousel (con testo)"
              keys={carouselImageKeys}
              results={results}
              apiUrl={apiUrl}
              filePrefix="carousel_slide"
              slideTexts={carouselSlideTexts}
            />
            {carouselCaption && (
              <div className="card" style={{ padding: 16, marginTop: 14 }}>
                <div
                  style={{
                    fontFamily: 'DM Sans',
                    fontSize: 12,
                    fontWeight: 700,
                    color: 'var(--espresso)',
                    marginBottom: 12,
                  }}
                >
                  Caption unica (per tutti gli slide)
                </div>
                <TextDisplay value={carouselCaption} />
                <CopyButton value={carouselCaption} filename="caption_carousel.txt" />
              </div>
            )}

            {/* Text overlay generator for carousel slides */}
            <div className="card" style={{ padding: 16, marginTop: 14 }}>
              <CarouselWithTextOverlay
                slides={carouselImageKeys.map((key, index) => ({
                  imageUrl: `${apiUrl}/files/${results[key]}`,
                  caption: carouselSlideTexts[index] || carouselCaption || 'I Monili',
                  hashtags: selectedHashtags,
                  index,
                }))}
                brand="I Monili"
              />
            </div>
          </div>
        )}

        {results.image_stories && (
          <div className="card" style={{ padding: 16, textAlign: 'center' }}>
            <div
              style={{
                fontFamily: 'DM Sans',
                fontSize: 11,
                fontWeight: 700,
                color: 'var(--espresso-dim)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: 12,
              }}
            >
              Stories 9:16 (1080x1920)
            </div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`${apiUrl}/files/${results.image_stories}`}
              alt="Stories Instagram"
              style={{
                width: '100%',
                maxWidth: 120,
                borderRadius: 10,
                border: '1px solid var(--border)',
                display: 'block',
                margin: '0 auto 12px',
              }}
            />
            <a
              href={`${apiUrl}/files/${results.image_stories}`}
              download="stories_1080x1920.jpg"
              className="btn-mission"
              style={{ display: 'inline-block', padding: '9px 20px', fontSize: 13, textDecoration: 'none' }}
            >
              Scarica Stories
            </a>
            <div style={{ marginTop: 8 }}>
              <SaveImageButton
                imageUrl={`${apiUrl}/files/${results.image_stories}`}
                filename="stories_1080x1920.jpg"
              />
            </div>
          </div>
        )}
      </div>
    );
  }

  if (tab === 'gmb') {
    return (
      <div className="card" style={{ padding: 16 }}>
        <div
          style={{
            fontFamily: 'DM Sans',
            fontSize: 12,
            fontWeight: 700,
            color: 'var(--espresso)',
            marginBottom: 12,
          }}
        >
          Post Google My Business
        </div>
        <TextDisplay value={gmbFinal} />
        <CopyButton value={gmbFinal} filename="post_gmb.txt" />
        <p style={{ marginTop: 16, fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)' }}>
          💡 Copia questo testo direttamente su Google My Business dal tuo account aziendale.
        </p>
      </div>
    );
  }

  if (tab === 'tripadvisor') {
    const tripAdvisorTitle = (publishPack.selected_tripadvisor_title || '').trim();
    const tripAdvisorText = (publishPack.selected_tripadvisor_text || '').trim();
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Titolo */}
        {tripAdvisorTitle && (
          <div className="card" style={{ padding: 16 }}>
            <div
              style={{
                fontFamily: 'DM Sans',
                fontSize: 12,
                fontWeight: 700,
                color: 'var(--espresso)',
                marginBottom: 12,
              }}
            >
              Titolo Review
            </div>
            <TextDisplay value={tripAdvisorTitle} compact />
            <CopyButton value={tripAdvisorTitle} filename="tripadvisor_title.txt" />
          </div>
        )}

        {/* Testo review */}
        {tripAdvisorText && (
          <div className="card" style={{ padding: 16 }}>
            <div
              style={{
                fontFamily: 'DM Sans',
                fontSize: 12,
                fontWeight: 700,
                color: 'var(--espresso)',
                marginBottom: 12,
              }}
            >
              Testo Review TripAdvisor
            </div>
            <TextDisplay value={tripAdvisorText} />
            <CopyButton value={tripAdvisorText} filename="tripadvisor_review.txt" />
          </div>
        )}

        {/* Help text */}
        <div className="card" style={{ padding: 14, background: 'var(--cream-2)', borderColor: 'var(--border)' }}>
          <p style={{ margin: 0, fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-mid)', lineHeight: 1.6 }}>
            💡 <strong>Come usare:</strong> Pubblica questa review nel tuo profilo aziendale su TripAdvisor per aumentare l'engagement e attirare nuovi clienti. Personalizza con dettagli specifici del prodotto se necessario.
          </p>
        </div>
      </div>
    );
  }

  if (tab === 'sito') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div className="card" style={{ padding: 18 }}>
          <div
            style={{
              fontFamily: 'DM Sans',
              fontSize: 11,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.10em',
              color: 'var(--terracotta-dark)',
              marginBottom: 10,
            }}
          >
            Revisione e pubblicazione
          </div>
          <p style={{ margin: '0 0 12px', fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-mid)', lineHeight: 1.6 }}>
            Vai alla pagina di review per approvare il contenuto prima della pubblicazione sul sito.
          </p>
          <a
            href={SHOWCASE_REVIEW_URL}
            target="_blank"
            rel="noreferrer"
            className="btn-mission"
            style={{ display: 'inline-block', padding: '8px 12px', fontSize: 12, textDecoration: 'none' }}
          >
            Apri review admin →
          </a>
        </div>

        {runId && (
          <ShowcasePublishPanel apiUrl={apiUrl} runId={runId} />
        )}
      </div>
    );
  }

  return null;
}

function ShowcasePublishPanel({
  apiUrl,
  runId,
}: {
  apiUrl: string;
  runId: string;
}) {
  const [candidates, setCandidates] = useState<ShowcaseCandidate[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any | null>(null);

  const loadCandidates = async () => {
    if (!runId) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${apiUrl}/missions/${encodeURIComponent(runId)}/showcase/candidates`);
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || `HTTP ${res.status}`);
      }
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
          };
        })
        .filter((item: ShowcaseCandidate | null): item is ShowcaseCandidate => Boolean(item));
      setCandidates(items);
      const recommended = items.filter((item) => item.available && item.recommended).map((item) => item.src);
      const fallback = items.filter((item) => item.available).map((item) => item.src);
      setSelected((recommended.length ? recommended : fallback).slice(0, 6));
    } catch (err) {
      setError(`Analisi immagini non disponibile: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!runId) return;
    void loadCandidates();
  }, [runId, apiUrl]);

  const toggleImage = (src: string) => {
    setSelected((prev) =>
      prev.includes(src) ? prev.filter((item) => item !== src) : [...prev, src],
    );
  };

  const publish = async (dryRun: boolean) => {
    if (!runId) return;
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
          dry_run: dryRun,
          selected_images: selected,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || data?.details?.error || `HTTP ${res.status}`);
      }
      setResult(data);
    } catch (err) {
      setError(`Invio non riuscito: ${err}`);
    } finally {
      setPublishing(false);
    }
  };

  if (!runId) {
    return null;
  }

  return (
    <div className="card" style={{ padding: 18 }}>
      <div
        style={{
          fontFamily: 'DM Sans',
          fontSize: 11,
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.10em',
          color: 'var(--terracotta-dark)',
          marginBottom: 10,
        }}
      >
        Seleziona foto per il sito
      </div>
      <p style={{ margin: '0 0 12px', fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-mid)', lineHeight: 1.6 }}>
        Quality gate automatico: le foto selezionate saranno ottimizzate prima dell'invio in draft.
      </p>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
        <button onClick={() => void loadCandidates()} className="btn-secondary" style={{ padding: '7px 12px', fontSize: 12 }} disabled={loading || publishing}>
          {loading ? 'Analisi in corso...' : 'Rianalizza'}
        </button>
        <button onClick={() => void publish(false)} className="btn-mission" style={{ padding: '7px 12px', fontSize: 12 }} disabled={publishing || !selected.length}>
          Invia draft al sito
        </button>
      </div>

      {error && (
        <div style={{ border: '1px solid #e8b4b4', background: '#fff3f3', color: '#8f2f2f', borderRadius: 10, padding: '8px 10px', fontFamily: 'DM Sans', fontSize: 12, marginBottom: 10 }}>
          {error}
        </div>
      )}

      {candidates.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(165px, 1fr))', gap: 10 }}>
          {candidates.map((item, index) => (
            <label key={`${item.src}-${index}`} className="card" style={{ padding: 10, border: selected.includes(item.src) ? '1px solid var(--terracotta)' : '1px solid var(--border)', opacity: item.available ? 1 : 0.55, cursor: item.available ? 'pointer' : 'default' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700, color: 'var(--espresso-dim)' }}>
                  Foto {index + 1}
                </span>
                <input
                  type="checkbox"
                  checked={selected.includes(item.src)}
                  disabled={!item.available}
                  onChange={() => toggleImage(item.src)}
                />
              </div>
              {item.available ? (
                <>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`${apiUrl}/files/${item.src}`} alt={`Candidate ${index + 1}`} style={{ width: '100%', borderRadius: 8, border: '1px solid var(--border)', marginBottom: 8 }} />
                </>
              ) : (
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, color: '#8f2f2f' }}>
                  {item.error || 'File non disponibile'}
                </div>
              )}
            </label>
          ))}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 12, border: '1px solid var(--border)', background: 'var(--cream-2)', borderRadius: 10, padding: 10, fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-mid)' }}>
          <div style={{ fontWeight: 700, marginBottom: 4 }}>
            {result.mode === 'dry-run' ? 'Test quality completato' : 'Invio completato'}
          </div>
          {result.ingest?.created_id && <div>ID draft creato: {result.ingest.created_id}</div>}
        </div>
      )}
    </div>
  );
}

export default function ResultsPanel({ results, apiUrl, runId }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('instagram');
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const publishPack = parsePublishPack(results.publish_pack_json);
  const carouselCopy = parseCarouselSlideCopy(results.carousel_slide_texts_json);

  const tabs: Array<{ id: Tab; label: string; icon: string }> = [
    { id: 'instagram', label: 'Instagram', icon: '📸' },
    { id: 'gmb', label: 'Google Business', icon: '🏪' },
    { id: 'tripadvisor', label: 'TripAdvisor', icon: '⭐' },
    { id: 'sito', label: 'Sito Vetrina', icon: '🌐' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div
          style={{
            display: 'flex',
            borderBottom: '1px solid var(--border)',
            background: 'var(--cream-2)',
          }}
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1,
                padding: '14px 16px',
                border: 'none',
                background: activeTab === tab.id ? 'white' : 'transparent',
                borderBottom: activeTab === tab.id ? '2px solid var(--terracotta)' : 'none',
                fontFamily: 'DM Sans',
                fontSize: 13,
                fontWeight: activeTab === tab.id ? 700 : 500,
                color: activeTab === tab.id ? 'var(--espresso)' : 'var(--espresso-dim)',
                cursor: 'pointer',
                transition: 'all 200ms ease',
              }}
            >
              <span style={{ marginRight: 6 }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        <div style={{ padding: 18 }}>
          <TabContent
            tab={activeTab}
            results={results}
            apiUrl={apiUrl}
            runId={runId}
            publishPack={publishPack}
            carouselCopy={carouselCopy}
          />
        </div>
      </div>

      <div className="card" style={{ padding: 14 }}>
        <button
          onClick={() => setAdvancedOpen((v) => !v)}
          className="btn-secondary"
          style={{ width: '100%', justifyContent: 'center', padding: '9px 12px', fontSize: 12, fontWeight: 700 }}
        >
          {advancedOpen ? '▼ Nascondi dettagli avanzati' : '▶ Mostra dettagli avanzati (strategia, JSON)'}
        </button>

        {advancedOpen && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 14 }}>
            <div className="card" style={{ padding: 14 }}>
              <div style={{ fontFamily: 'DM Sans', fontSize: 12, fontWeight: 700, color: 'var(--espresso)', marginBottom: 10 }}>
                Strategia completa (JSON)
              </div>
              <TextDisplay value={results.strategy_plan || ''} compact />
            </div>
            <div className="card" style={{ padding: 14 }}>
              <div style={{ fontFamily: 'DM Sans', fontSize: 12, fontWeight: 700, color: 'var(--espresso)', marginBottom: 10 }}>
                Analisi prodotto
              </div>
              <TextDisplay value={results.publish_pack || ''} compact />
            </div>
          </div>
        )}

        {!advancedOpen && (
          <p style={{ margin: '12px 2px 0', fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-dim)' }}>
            Sopra trovi tutto il kit operativo pronto. Apri i dettagli solo se serve analizzare la strategia completa.
          </p>
        )}
      </div>
    </div>
  );
}
