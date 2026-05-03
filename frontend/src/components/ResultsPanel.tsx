'use client';

import { useState } from 'react';

interface Props {
  results: Record<string, string>;
  apiUrl: string;
}

const SECTIONS = [
  { id: 'publish_pack', label: 'Pronto Pubblicazione', icon: 'P', filename: 'publish_pack.txt', desc: 'Versione finale gia selezionata e pronta da copiare' },
  { id: 'carousel', label: 'Carousel Testi', icon: 'C', filename: 'carousel_statici.txt', desc: 'Testi slide (solo supporto, non output principale)' },
  { id: 'strategy', label: 'Strategia 2.0', icon: 'S', filename: 'strategia_2_0.txt', desc: 'Scelta strategica usata dal team AI' },
  { id: 'local_visibility', label: 'Local Visibility', icon: 'L', filename: 'local_visibility.txt', desc: 'SEO locale Ravenna e Google Business' },
  { id: 'distribution', label: 'Distribuzione', icon: 'D', filename: 'distribuzione.txt', desc: 'Piano di distribuzione completo' },
];

type PublishPack = {
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

function CopyBox({
  title,
  value,
  filename,
  compact = false,
}: {
  title: string;
  value: string;
  filename: string;
  compact?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const safeValue = value.trim();

  const copyValue = () => {
    navigator.clipboard.writeText(safeValue).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        <div style={{ fontFamily: 'DM Sans', fontSize: 12, fontWeight: 700, color: 'var(--espresso)' }}>{title}</div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button onClick={copyValue} className="btn-secondary" style={{ padding: '5px 10px', fontSize: 11 }}>
            {copied ? 'Copiato' : 'Copia'}
          </button>
          <button onClick={() => downloadBlob(safeValue, filename)} className="btn-secondary" style={{ padding: '5px 10px', fontSize: 11 }}>
            .txt
          </button>
        </div>
      </div>
      <pre style={{
        margin: 0,
        fontFamily: 'DM Sans',
        fontSize: compact ? 12 : 12.5,
        lineHeight: compact ? 1.55 : 1.65,
        color: 'var(--espresso-mid)',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
      }}>
        {safeValue || 'Non disponibile'}
      </pre>
    </div>
  );
}

function ContentCard({
  id,
  label,
  icon,
  filename,
  desc,
  content,
}: typeof SECTIONS[0] & { content: string }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const preview = content.slice(0, 320);
  const hasMore = content.length > 320;

  const handleCopy = () => {
    navigator.clipboard.writeText(content).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '14px 18px',
        background: 'var(--cream-2)',
        borderBottom: '1px solid var(--border)',
      }}>
        <span style={{ fontSize: 18, lineHeight: 1 }}>{icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: 'DM Sans', fontWeight: 700, fontSize: 13, color: 'var(--espresso)' }}>
            {label}
          </div>
          <div style={{ fontFamily: 'DM Sans', fontSize: 11, color: 'var(--espresso-dim)' }}>
            {desc}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            onClick={handleCopy}
            className="btn-secondary"
            style={{ padding: '5px 12px', fontSize: 11 }}
          >
            {copied ? 'Copiato' : 'Copia'}
          </button>
          <button
            onClick={() => downloadBlob(content, filename)}
            className="btn-secondary"
            style={{ padding: '5px 12px', fontSize: 11 }}
          >
            .txt
          </button>
        </div>
      </div>

      <div style={{ padding: '14px 18px' }}>
        {content ? (
          <>
            <pre style={{
              fontFamily: 'DM Sans',
              fontSize: 12.5,
              lineHeight: 1.7,
              color: 'var(--espresso-mid)',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              margin: 0,
              maxHeight: expanded ? 'none' : 220,
              overflow: 'hidden',
            }}>
              {expanded ? content : preview}
              {!expanded && hasMore && '...'}
            </pre>
            {hasMore && (
              <button
                onClick={() => setExpanded(v => !v)}
                style={{
                  marginTop: 10,
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontFamily: 'DM Sans',
                  fontSize: 12,
                  color: 'var(--terracotta)',
                  fontWeight: 600,
                  padding: 0,
                }}
              >
                {expanded ? 'Mostra meno' : 'Leggi tutto'}
              </button>
            )}
          </>
        ) : (
          <p style={{ fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-dim)', margin: 0 }}>
            Contenuto non disponibile.
          </p>
        )}
      </div>
    </div>
  );
}

function ImageStrip({
  title,
  keys,
  results,
  apiUrl,
  filePrefix,
}: {
  title: string;
  keys: string[];
  results: Record<string, string>;
  apiUrl: string;
  filePrefix: string;
}) {
  if (keys.length === 0) return null;

  return (
    <div>
      <div style={{
        fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700,
        textTransform: 'uppercase', letterSpacing: '0.10em',
        color: 'var(--terracotta-dark)', marginBottom: 14,
      }}>
        {title}
      </div>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {keys.map((key, index) => (
          <div key={key} className="card" style={{ flex: '1 1 220px', padding: 16, textAlign: 'center', minWidth: 0 }}>
            <div style={{ fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700, color: 'var(--espresso-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
              {filePrefix === 'carousel_slide' ? `Slide ${index + 1}` : `Visual ${index + 1}`}
            </div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`${apiUrl}/files/${results[key]}`}
              alt={`${filePrefix} ${index + 1}`}
              style={{ width: '100%', maxWidth: 220, borderRadius: 10, border: '1px solid var(--border)', display: 'block', margin: '0 auto 12px' }}
            />
            <a
              href={`${apiUrl}/files/${results[key]}`}
              download={`${filePrefix}_${index + 1}.png`}
              className="btn-mission"
              style={{ display: 'inline-block', padding: '9px 20px', fontSize: 13, textDecoration: 'none' }}
            >
              Scarica
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ResultsPanel({ results, apiUrl }: Props) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const publishPack = parsePublishPack(results.publish_pack_json);
  const selectedCaption = (publishPack.selected_caption || '').trim();
  const selectedHashtags = Array.isArray(publishPack.selected_hashtags) ? publishPack.selected_hashtags.join(' ') : '';
  const selectedWhatsapp = (publishPack.selected_whatsapp || '').trim();
  const gmbFinal = `${(publishPack.selected_gmb_title || '').trim()}\n\n${(publishPack.selected_gmb_text || '').trim()}`.trim();
  const storyFrames = Array.isArray(publishPack.selected_story_frames) ? publishPack.selected_story_frames : [];
  const storyFinal = storyFrames.map((frame, idx) => `Frame ${idx + 1}: ${frame}`).join('\n');
  const postingFinal = `${(publishPack.selected_posting_time || '').trim()}\n${(publishPack.selected_cta || '').trim()}`.trim();

  const hasImages = Boolean(results.image_feed || results.image_stories);
  const carouselImageKeys = Object.keys(results)
    .filter(key => key.startsWith('image_carousel_') && results[key])
    .sort((a, b) => Number(a.replace('image_carousel_', '')) - Number(b.replace('image_carousel_', '')));
  const aiImageKeys = Object.keys(results)
    .filter(key => key.startsWith('image_ai_') && results[key])
    .sort((a, b) => Number(a.replace('image_ai_', '')) - Number(b.replace('image_ai_', '')));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div className="card" style={{ padding: 18 }}>
        <div style={{
          fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700,
          textTransform: 'uppercase', letterSpacing: '0.10em',
          color: 'var(--terracotta-dark)', marginBottom: 14,
        }}>
          Pronto da pubblicare
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 12 }}>
          <CopyBox title="Caption finale Instagram" value={selectedCaption} filename="caption_finale_instagram.txt" />
          <CopyBox title="Hashtag finali" value={selectedHashtags} filename="hashtag_finali.txt" compact />
          <CopyBox title="Messaggio WhatsApp" value={selectedWhatsapp} filename="whatsapp_broadcast.txt" />
          <CopyBox title="Post Google Business" value={gmbFinal} filename="post_google_business.txt" />
          <CopyBox title="Stories (3 frame)" value={storyFinal} filename="stories_3_frame.txt" compact />
          <CopyBox title="Orario + CTA" value={postingFinal} filename="orario_e_cta.txt" compact />
        </div>
      </div>

      <ImageStrip title="Carousel pronto (immagini AI)" keys={carouselImageKeys} results={results} apiUrl={apiUrl} filePrefix="carousel_slide" />
      <ImageStrip title="Visual extra (opzionali)" keys={aiImageKeys} results={results} apiUrl={apiUrl} filePrefix="visual_ai" />

      {hasImages && (
        <div>
          <div style={{
            fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700,
            textTransform: 'uppercase', letterSpacing: '0.10em',
            color: 'var(--terracotta-dark)', marginBottom: 14,
          }}>
            Foto ottimizzate da foto reale
          </div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {results.image_feed && (
              <div className="card" style={{ flex: '1 1 200px', padding: 16, textAlign: 'center', minWidth: 0 }}>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700, color: 'var(--espresso-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
                  Feed 1:1 - 1080x1080
                </div>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`${apiUrl}/files/${results.image_feed}`}
                  alt="Feed Instagram"
                  style={{ width: '100%', maxWidth: 200, borderRadius: 10, border: '1px solid var(--border)', display: 'block', margin: '0 auto 12px' }}
                />
                <a
                  href={`${apiUrl}/files/${results.image_feed}`}
                  download="feed_1080x1080.jpg"
                  className="btn-mission"
                  style={{ display: 'inline-block', padding: '9px 20px', fontSize: 13, textDecoration: 'none' }}
                >
                  Scarica Feed
                </a>
              </div>
            )}

            {results.image_stories && (
              <div className="card" style={{ flex: '0 1 160px', padding: 16, textAlign: 'center', minWidth: 0 }}>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700, color: 'var(--espresso-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
                  Stories 9:16 - 1080x1920
                </div>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`${apiUrl}/files/${results.image_stories}`}
                  alt="Stories Instagram"
                  style={{ width: '100%', maxWidth: 120, borderRadius: 10, border: '1px solid var(--border)', display: 'block', margin: '0 auto 12px' }}
                />
                <a
                  href={`${apiUrl}/files/${results.image_stories}`}
                  download="stories_1080x1920.jpg"
                  className="btn-mission"
                  style={{ display: 'inline-block', padding: '9px 20px', fontSize: 13, textDecoration: 'none' }}
                >
                  Scarica Stories
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="card" style={{ padding: 14 }}>
        <button
          onClick={() => setAdvancedOpen(v => !v)}
          className="btn-secondary"
          style={{ width: '100%', justifyContent: 'center', padding: '9px 12px', fontSize: 12, fontWeight: 700 }}
        >
          {advancedOpen ? 'Nascondi dettagli avanzati' : 'Mostra dettagli avanzati (testi lunghi)'}
        </button>

        {advancedOpen && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 14 }}>
            {SECTIONS.map(s => (
              <ContentCard key={s.id} {...s} content={results[s.id] || ''} />
            ))}
          </div>
        )}

        {!advancedOpen && (
          <p style={{ margin: '12px 2px 0', fontFamily: 'DM Sans', fontSize: 12, color: 'var(--espresso-dim)' }}>
            Qui sopra trovi gia il kit operativo. Apri i dettagli solo se vuoi analizzare la strategia completa.
          </p>
        )}
      </div>

      {Object.keys(publishPack).length === 0 && (
        <div className="card" style={{ padding: 14, borderColor: 'var(--gold-light)', background: 'var(--cream-2)' }}>
          <p style={{ margin: 0, fontFamily: 'DM Sans', fontSize: 12.5, color: 'var(--espresso-mid)', lineHeight: 1.6 }}>
            Il blocco pronto pubblicazione non e arrivato in formato strutturato. Usa i dettagli avanzati e rilancia la missione per ricostruirlo automaticamente.
          </p>
        </div>
      )}
    </div>
  );
}
