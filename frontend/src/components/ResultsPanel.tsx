'use client';

import { useState } from 'react';

interface Props {
  results: Record<string, string>;
  apiUrl: string;
}

const SECTIONS = [
  { id: 'strategy',         label: 'Strategia 2.0',    icon: 'S', filename: 'strategia_2_0.txt',    desc: 'Obiettivo, formato, canali e angolo locale' },
  { id: 'carousel',         label: 'Carousel Statici', icon: 'C', filename: 'carousel_statici.txt', desc: 'Carousel prodotto e informativo pronti da impaginare' },
  { id: 'local_visibility', label: 'Local Visibility', icon: 'L', filename: 'local_visibility.txt', desc: 'Google Business, sito vetrina, SEO locale e AI search' },
  { id: 'distribution',     label: 'Distribuzione',    icon: 'D', filename: 'distribuzione.txt',    desc: 'Caption, hashtag, WhatsApp, Stories e piano 7 giorni' },
  { id: 'visual_prompts',   label: 'Prompt Visual AI', icon: 'V', filename: 'prompt_visual_ai.txt', desc: 'Brief fotorealistici per indossato, sfondo e contesto' },
  { id: 'shooting',         label: 'Guida Foto Reale', icon: 'F', filename: 'guida_foto_reale.txt', desc: 'Scatti reali, tagli e visual per post/carousel/GMB' },
  { id: 'analisi',          label: 'Analisi Prodotto', icon: 'A', filename: 'analisi_prodotto.txt', desc: 'Scheda completa, mood, occasione e posizionamento' },
];

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

function ContentCard({
  id, label, icon, filename, desc, content,
}: typeof SECTIONS[0] & { content: string }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied]     = useState(false);
  const preview = content.slice(0, 320);
  const hasMore = content.length > 320;

  const handleCopy = () => {
    navigator.clipboard.writeText(content).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>

      {/* Header */}
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
        {/* Actions */}
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

      {/* Content */}
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

export default function ResultsPanel({ results, apiUrl }: Props) {
  const hasImages = results.image_feed || results.image_stories;
  const aiImageKeys = Object.keys(results)
    .filter(key => key.startsWith('image_ai_') && results[key])
    .sort((a, b) => Number(a.replace('image_ai_', '')) - Number(b.replace('image_ai_', '')));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {aiImageKeys.length > 0 && (
        <div>
          <div style={{
            fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700,
            textTransform: 'uppercase', letterSpacing: '0.10em',
            color: 'var(--terracotta-dark)', marginBottom: 14,
          }}>
            Visual AI fotorealistici
          </div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {aiImageKeys.map((key, index) => (
              <div key={key} className="card" style={{ flex: '1 1 220px', padding: 16, textAlign: 'center', minWidth: 0 }}>
                <div style={{ fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700, color: 'var(--espresso-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
                  Visual {index + 1}
                </div>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`${apiUrl}/files/${results[key]}`}
                  alt={`Visual AI ${index + 1}`}
                  style={{ width: '100%', maxWidth: 220, borderRadius: 10, border: '1px solid var(--border)', display: 'block', margin: '0 auto 12px' }}
                />
                <a
                  href={`${apiUrl}/files/${results[key]}`}
                  download={`visual_ai_${index + 1}.png`}
                  className="btn-mission"
                  style={{ display: 'inline-block', padding: '9px 20px', fontSize: 13, textDecoration: 'none' }}
                >
                  Scarica Visual
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* â”€â”€ IMMAGINI OTTIMIZZATE â”€â”€ */}
      {hasImages && (
        <div>
          <div style={{
            fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700,
            textTransform: 'uppercase', letterSpacing: '0.10em',
            color: 'var(--terracotta-dark)', marginBottom: 14,
          }}>
            Foto ottimizzate per Instagram
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

      {/* â”€â”€ TESTI â”€â”€ */}
      <div>
        <div style={{
          fontFamily: 'DM Sans', fontSize: 11, fontWeight: 700,
          textTransform: 'uppercase', letterSpacing: '0.10em',
          color: 'var(--terracotta-dark)', marginBottom: 14,
        }}>
          Contenuti generati
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {SECTIONS.map(s => (
            <ContentCard key={s.id} {...s} content={results[s.id] || ''} />
          ))}
        </div>
      </div>

    </div>
  );
}

