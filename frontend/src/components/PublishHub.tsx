'use client';

import { useEffect, useMemo, useState } from 'react';
import InstagramShare from '@/components/InstagramShare';
import PostMaker from '@/components/PostMaker';

type ReelData = {
  id: string;
  format?: string;
  storyboard?: { shots?: Array<{ use_model?: boolean }> } | null;
  results?: {
    final_video?: string;
    cover?: string;
    copy?: {
      caption?: string;
      caption_short?: string;
      hashtags?: string[];
      first_comment?: string;
      story_stickers?: string[];
      best_slot?: string;
    };
  };
};

export interface PublishTexts {
  caption: string;
  hashtags: string[];
  cta: string;
  whatsapp: string;
  gmb: string;
  seo: string;
  tripadvisor: string;
}

interface Props {
  apiUrl: string;
  reelIds: string[];
  photos: Array<{ src: string; label: string; slug: string }>;
  texts: PublishTexts;
  siteState: 'none' | 'draft' | 'published';
  hasAiWomanPhoto: boolean;
  onGoTo: (stage: 'sito' | 'video') => void;
  runId?: string;
}

type PlatformId = 'sito' | 'reel' | 'storia' | 'post' | 'google' | 'whatsapp';

async function copyText(text: string) {
  try {
    if (window.isSecureContext && navigator.clipboard) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* si prova il metodo vecchio */
  }
  try {
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(area);
    return ok;
  } catch {
    return false;
  }
}

function CopyButton({ text, label = 'Copia' }: { text: string; label?: string }) {
  const [done, setDone] = useState(false);
  return (
    <button
      type="button"
      className="btn-secondary pub-copy"
      onClick={async () => {
        if (await copyText(text)) {
          setDone(true);
          setTimeout(() => setDone(false), 1600);
        }
      }}
      aria-live="polite"
    >
      {done ? 'Copiato' : label}
    </button>
  );
}

function Block({ title, text, copyLabel }: { title: string; text: string; copyLabel?: string }) {
  if (!text.trim()) return null;
  return (
    <section className="pub-block">
      <header>
        <h3>{title}</h3>
        <CopyButton text={text} label={copyLabel} />
      </header>
      <pre>{text}</pre>
    </section>
  );
}

function Hashtags({ tags }: { tags: string[] }) {
  if (!tags.length) return null;
  const joined = tags.join(' ');
  return (
    <section className="pub-block">
      <header>
        <h3>Hashtag</h3>
        <CopyButton text={joined} />
      </header>
      <p className="pub-tags">
        {tags.map((tag) => (
          <span key={tag}>{tag}</span>
        ))}
      </p>
    </section>
  );
}

function Missing({ children, action, onClick }: { children: React.ReactNode; action: string; onClick: () => void }) {
  return (
    <div className="pub-missing">
      <p>{children}</p>
      <button type="button" className="btn-mission" onClick={onClick}>{action}</button>
    </div>
  );
}

export default function PublishHub({ apiUrl, reelIds, photos, texts, siteState, hasAiWomanPhoto, onGoTo, runId }: Props) {
  const [reels, setReels] = useState<ReelData[]>([]);
  const [loadingReels, setLoadingReels] = useState(reelIds.length > 0);
  const [platform, setPlatform] = useState<PlatformId>('reel');

  const idsKey = reelIds.join('|');
  useEffect(() => {
    if (!reelIds.length) {
      setReels([]);
      setLoadingReels(false);
      return;
    }
    let alive = true;
    setLoadingReels(true);
    Promise.all(
      reelIds.slice(0, 4).map((id) =>
        fetch(`${apiUrl}/reel/${encodeURIComponent(id)}`, { cache: 'no-store' })
          .then((res) => (res.ok ? (res.json() as Promise<ReelData>) : null))
          .catch(() => null),
      ),
    ).then((rows) => {
      if (!alive) return;
      setReels(rows.filter((row): row is ReelData => Boolean(row?.results?.final_video)));
      setLoadingReels(false);
    });
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiUrl, idsKey]);

  const reel = reels.find((row) => row.format !== 'story') || reels[0];
  const storyReel = reels.find((row) => row.format === 'story') || reel;
  const url = (src: string) => `${apiUrl}/files/${src}`;
  const hasAiReel = (row?: ReelData) => Boolean(row?.storyboard?.shots?.some((shot) => shot.use_model));
  const cover = photos[0];

  const reelTags = reel?.results?.copy?.hashtags?.length ? reel.results.copy.hashtags : texts.hashtags;
  const storyCopy = storyReel?.results?.copy;
  // La CTA spesso contiene già il riferimento (es. "Rif. M-XXXX") presente nella didascalia: non ripeterla.
  const postText = useMemo(() => {
    const cap = (texts.caption || '').trim();
    const cta = (texts.cta || '').trim();
    if (!cta || cap.includes(cta)) return cap;
    return [cap, cta].filter(Boolean).join('\n\n');
  }, [texts.caption, texts.cta]);

  const platforms: Array<{ id: PlatformId; label: string; ready: boolean }> = [
    { id: 'reel', label: 'Instagram Reel', ready: Boolean(reel) },
    { id: 'storia', label: 'Instagram Storia', ready: Boolean(storyReel) },
    { id: 'post', label: 'Instagram Post', ready: photos.length > 0 && Boolean(texts.caption) },
    { id: 'sito', label: 'Sito', ready: siteState !== 'none' },
    { id: 'google', label: 'Google Business', ready: Boolean(texts.gmb) },
    { id: 'whatsapp', label: 'WhatsApp', ready: Boolean(texts.whatsapp) },
  ];

  return (
    <div className="pub">
      <div className="pub-chips" role="tablist" aria-label="Dove pubblicare">
        {platforms.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={platform === item.id}
            className="pub-chip"
            data-ready={item.ready}
            onClick={() => setPlatform(item.id)}
          >
            <span className="pub-dot" aria-hidden="true" />
            {item.label}
            <span className="sr-only">{item.ready ? ': pronto' : ': manca qualcosa'}</span>
          </button>
        ))}
      </div>

      {platform === 'reel' && (
        <div className="pub-panel">
          {loadingReels && <p className="step-hint">Preparo il Reel...</p>}
          {!loadingReels && !reel && (
            <Missing action="Crea un video" onClick={() => onGoTo('video')}>
              Non c&apos;è ancora un video per questo pezzo. Crealo dalle foto, oppure carica uno già pronto.
            </Missing>
          )}
          {reel?.results?.final_video && (
            <div className="pub-grid">
              <div className="pub-media">
                <video src={url(reel.results.final_video)} poster={reel.results.cover ? url(reel.results.cover) : undefined} controls playsInline loop />
                <InstagramShare
                  files={[{ url: url(reel.results.final_video), filename: 'monili-reel.mp4' }]}
                  caption={[reel.results.copy?.caption, reelTags.join(' ')].filter(Boolean).join('\n\n')}
                  kind="Reel"
                  hasAiWoman={hasAiReel(reel) || hasAiWomanPhoto}
                />
              </div>
              <div className="pub-texts">
                <Block title="Caption" text={reel.results.copy?.caption || texts.caption} />
                <Hashtags tags={reelTags} />
                <Block title="Primo commento" text={reel.results.copy?.first_comment || ''} />
                {reel.results.copy?.best_slot && <p className="pub-meta"><strong>Quando:</strong> {reel.results.copy.best_slot}</p>}
              </div>
            </div>
          )}
        </div>
      )}

      {platform === 'storia' && (
        <div className="pub-panel">
          {loadingReels && <p className="step-hint">Preparo la Storia...</p>}
          {!loadingReels && !storyReel && (
            <Missing action="Crea un video" onClick={() => onGoTo('video')}>
              La Storia riusa il video del pezzo. Prima serve il video.
            </Missing>
          )}
          {storyReel?.results?.final_video && (
            <div className="pub-grid">
              <div className="pub-media">
                <video src={url(storyReel.results.final_video)} poster={storyReel.results.cover ? url(storyReel.results.cover) : undefined} controls playsInline loop />
                <InstagramShare
                  files={[{ url: url(storyReel.results.final_video), filename: 'monili-storia.mp4' }]}
                  caption={[storyCopy?.caption_short || storyCopy?.caption, texts.hashtags.join(' ')].filter(Boolean).join('\n\n')}
                  kind="Storia"
                  hasAiWoman={hasAiReel(storyReel) || hasAiWomanPhoto}
                />
              </div>
              <div className="pub-texts">
                <Block title="Testo breve" text={storyCopy?.caption_short || storyCopy?.caption || ''} />
                <Hashtags tags={texts.hashtags.slice(0, 5)} />
                {(storyCopy?.story_stickers || []).length > 0 && (
                  <Block title="Idee per gli sticker" text={(storyCopy?.story_stickers || []).map((item) => `• ${item}`).join('\n')} />
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {platform === 'post' && (
        <div className="pub-panel">
          {photos.length === 0 ? (
            <Missing action="Vai al sito" onClick={() => onGoTo('sito')}>Non ci sono foto per questo pezzo.</Missing>
          ) : (
            <div className="pub-grid">
              <div className="pub-media">
                <div className="pub-photos">
                  {photos.map((photo) => (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img key={photo.src} src={url(photo.src)} alt={photo.label} loading="lazy" />
                  ))}
                </div>
                <InstagramShare
                  files={photos.map((photo) => ({ url: url(photo.src), filename: `${photo.slug}.jpg` }))}
                  caption={[postText, texts.hashtags.join(' ')].filter(Boolean).join('\n\n')}
                  kind="Post"
                  hasAiWoman={hasAiWomanPhoto}
                />
                <p className="pub-meta">I Reel arrivano di più a chi non ti segue: se puoi, pubblica prima il video.</p>
              </div>
              <div className="pub-texts">
                <Block title="Caption" text={postText} />
                <Hashtags tags={texts.hashtags} />
              </div>
            </div>
          )}
          {runId && <PostMaker apiUrl={apiUrl} runId={runId} caption={postText} hashtags={texts.hashtags} />}
        </div>
      )}

      {platform === 'sito' && (
        <div className="pub-panel">
          <p className="pub-status" data-state={siteState}>
            {siteState === 'published' ? 'Pubblicato sul sito.' : siteState === 'draft' ? 'Bozza inviata: pubblicala dalla revisione sul sito.' : 'Non ancora mandato al sito.'}
          </p>
          {photos.length > 0 && (
            <div className="pub-photos">
              {photos.map((photo) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img key={photo.src} src={url(photo.src)} alt={photo.label} loading="lazy" />
              ))}
            </div>
          )}
          <Block title="Titolo e descrizione per Google" text={texts.seo} />
          <button type="button" className="btn-secondary" onClick={() => onGoTo('sito')}>
            {siteState === 'none' ? 'Prepara il pezzo per il sito' : 'Cambia foto o prezzo'}
          </button>
        </div>
      )}

      {platform === 'google' && (
        <div className="pub-panel">
          <div className="pub-grid">
            <div className="pub-media">
              {cover && (
                // eslint-disable-next-line @next/next/no-img-element
                <img className="pub-single" src={url(cover.src)} alt={cover.label} />
              )}
              <p className="pub-meta">Su Google Business: Aggiornamenti → Aggiungi post, con questa foto.</p>
            </div>
            <div className="pub-texts">
              <Block title="Testo per Google Business" text={texts.gmb} />
              {texts.tripadvisor && <Block title="Tripadvisor" text={texts.tripadvisor} />}
            </div>
          </div>
        </div>
      )}

      {platform === 'whatsapp' && (
        <div className="pub-panel">
          <div className="pub-grid">
            <div className="pub-media">
              {cover && (
                // eslint-disable-next-line @next/next/no-img-element
                <img className="pub-single" src={url(cover.src)} alt={cover.label} />
              )}
              <p className="pub-meta">Il messaggio parte dal numero del 21 (375 771 3966).</p>
            </div>
            <div className="pub-texts">
              <Block title="Messaggio" text={texts.whatsapp} />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}