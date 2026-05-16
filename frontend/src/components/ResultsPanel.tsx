'use client';

import { useEffect, useMemo, useState } from 'react';

interface Props {
  results: Record<string, string>;
  apiUrl: string;
  runId: string;
}

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

type CarouselCopy = {
  carousel_caption?: string;
  slide_texts?: string[];
};

type Tab = 'today' | 'stories' | 'carousel' | 'photos' | 'google' | 'sito';
type ShowcaseCandidate = {
  src: string;
  available: boolean;
  recommended?: boolean;
  error?: string;
};

const SHOWCASE_REVIEW_URL =
  process.env.NEXT_PUBLIC_SHOWCASE_REVIEW_URL ||
  'https://web-five-theta-58.vercel.app/admin/review';

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
  return (
    <section className="result-block">
      <div className="result-block-header">
        <h3>{title}</h3>
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
      <div className="result-image-title">{title}</div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={imageUrl} alt={title} className="result-image" />
      {note && <p className="result-image-note">{note}</p>}
      <div className="result-actions">
        <a href={imageUrl} download={filename} className="btn-mission result-button">
          Scarica
        </a>
        <button type="button" onClick={onSave} className="btn-secondary result-button">
          {status === 'saving' ? 'Salvo...' : status === 'done' ? 'Apri Condividi' : status === 'fallback' ? 'Aperta' : 'Salva su iPhone'}
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
        body: JSON.stringify({ selected_images: selected }),
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
      {candidates.length > 0 && (
        <div className="result-image-grid compact">
          {candidates.map((item, index) => (
            <label key={`${item.src}-${index}`} className="showcase-pick">
              <input
                type="checkbox"
                checked={selected.includes(item.src)}
                disabled={!item.available}
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
            </label>
          ))}
        </div>
      )}
      {result && <p className="result-ok">Draft creato: {result.ingest?.created_id || 'invio completato'}</p>}
      <a href={SHOWCASE_REVIEW_URL} target="_blank" rel="noreferrer" className="result-link">
        Apri review admin
      </a>
    </section>
  );
}

export default function ResultsPanel({ results, apiUrl, runId }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('today');
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const publishPack = parseJsonObject<PublishPack>(results.publish_pack_json, {});
  const carouselCopy = parseJsonObject<CarouselCopy>(results.carousel_slide_texts_json, {});

  const hashtags = Array.isArray(publishPack.selected_hashtags) ? publishPack.selected_hashtags.join(' ') : '';
  const gmbFinal = `${(publishPack.selected_gmb_title || '').trim()}\n\n${(publishPack.selected_gmb_text || '').trim()}`.trim();
  const storyFrames = Array.isArray(publishPack.selected_story_frames) ? publishPack.selected_story_frames : [];
  const storyImageKeys = useMemo(() => getResultImages(results, 'image_story_'), [results]);
  const carouselImageKeys = useMemo(() => getResultImages(results, 'image_carousel_'), [results]);
  const aiImageKeys = useMemo(() => getResultImages(results, 'image_ai_'), [results]);

  const tabs: Array<{ id: Tab; label: string }> = [
    { id: 'today', label: 'Oggi' },
    { id: 'stories', label: 'Stories' },
    { id: 'carousel', label: 'Carousel' },
    { id: 'photos', label: 'Foto' },
    { id: 'google', label: 'Google' },
    { id: 'sito', label: 'Sito' },
  ];

  return (
    <div className="results-shell">
      <nav className="results-tabs" aria-label="Risultati contenuti">
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
        {activeTab === 'today' && (
          <div className="result-stack">
            {results.image_feed && (
              <ImageCard title="Post Instagram" imageUrl={`${apiUrl}/files/${results.image_feed}`} filename="post-instagram.jpg" />
            )}
            <TextBlock title="Caption Instagram" value={publishPack.selected_caption || ''} filename="caption-instagram.txt" />
            <TextBlock title="Hashtag" value={hashtags} filename="hashtag.txt" />
            <TextBlock title="WhatsApp" value={publishPack.selected_whatsapp || ''} filename="whatsapp.txt" />
          </div>
        )}

        {activeTab === 'stories' && (
          <div className="result-stack">
            <div className="result-image-grid stories">
              {storyImageKeys.map((key, index) => (
                <ImageCard
                  key={key}
                  title={`Story ${index + 1}`}
                  imageUrl={`${apiUrl}/files/${results[key]}`}
                  filename={`story-${index + 1}.jpg`}
                  note={storyFrames[index]}
                />
              ))}
              {storyImageKeys.length === 0 && results.image_stories && (
                <ImageCard title="Story 9:16" imageUrl={`${apiUrl}/files/${results.image_stories}`} filename="story-verticale.jpg" />
              )}
            </div>
            <TextBlock title="Testi stories" value={storyFrames.map((frame, idx) => `Story ${idx + 1}: ${frame}`).join('\n')} filename="testi-stories.txt" />
          </div>
        )}

        {activeTab === 'carousel' && (
          <div className="result-stack">
            <div className="result-image-grid">
              {carouselImageKeys.map((key, index) => (
                <ImageCard
                  key={key}
                  title={`Slide ${index + 1}`}
                  imageUrl={`${apiUrl}/files/${results[key]}`}
                  filename={`carousel-slide-${index + 1}.jpg`}
                  note={carouselCopy.slide_texts?.[index]}
                />
              ))}
            </div>
            <TextBlock title="Caption carousel" value={carouselCopy.carousel_caption || publishPack.selected_caption || ''} filename="caption-carousel.txt" />
          </div>
        )}

        {activeTab === 'photos' && (
          <div className="result-image-grid">
            {results.image_feed && <ImageCard title="Feed 1:1" imageUrl={`${apiUrl}/files/${results.image_feed}`} filename="feed-1080.jpg" />}
            {results.image_stories && <ImageCard title="Story ottimizzata" imageUrl={`${apiUrl}/files/${results.image_stories}`} filename="story-1080x1920.jpg" />}
            {aiImageKeys.map((key, index) => (
              <ImageCard key={key} title={`Visual ${index + 1}`} imageUrl={`${apiUrl}/files/${results[key]}`} filename={`visual-${index + 1}.jpg`} />
            ))}
          </div>
        )}

        {activeTab === 'google' && (
          <div className="result-stack">
            <TextBlock title="Google Business" value={gmbFinal} filename="google-business.txt" />
            {publishPack.selected_tripadvisor_text && (
              <TextBlock
                title="TripAdvisor"
                value={`${publishPack.selected_tripadvisor_title || ''}\n\n${publishPack.selected_tripadvisor_text || ''}`.trim()}
                filename="tripadvisor.txt"
              />
            )}
          </div>
        )}

        {activeTab === 'sito' && (
          <div className="result-stack">
            <ShowcasePublishPanel apiUrl={apiUrl} runId={runId} />
          </div>
        )}
      </div>

      <section className="result-block advanced">
        <button type="button" onClick={() => setAdvancedOpen((value) => !value)} className="btn-secondary result-button full">
          {advancedOpen ? 'Nascondi dettagli avanzati' : 'Mostra strategia completa'}
        </button>
        {advancedOpen && (
          <div className="result-stack spaced">
            <TextBlock title="Piano statico JSON" value={results.strategy_plan || ''} filename="piano-statico.json" />
            <TextBlock title="Analisi prodotto" value={results.analisi || ''} filename="analisi-prodotto.txt" />
            <TextBlock title="Prompt immagini" value={results.instagram_visual_prompts || ''} filename="prompt-images-2.txt" />
          </div>
        )}
      </section>
    </div>
  );
}
