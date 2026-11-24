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
  const [googlePhoto, setGooglePhoto] = useState('');
  const [googleText, setGoogleText] = useState(texts.gmb);
  const [googleInfo, setGoogleInfo] = useState<{product_url: string | null; creatives?: string[]; creative_details?: Record<string, {label: string}>; zernio_configured: boolean; account_configured: boolean} | null>(null);
  const [creativeStyle, setCreativeStyle] = useState("personalizzato");
  const [creativeProvider, setCreativeProvider] = useState("chatgpt");
  const [flowModel, setFlowModel] = useState("nano2");
  const [creativeSource, setCreativeSource] = useState("");
  const [creativePrompt, setCreativePrompt] = useState("");
  const [creativeFormat, setCreativeFormat] = useState("auto");
  const [creativeBusy, setCreativeBusy] = useState(false);
  const [creativeMessage, setCreativeMessage] = useState("");
  const [creativeZoom, setCreativeZoom] = useState(false);
  const [creativeRemoving, setCreativeRemoving] = useState(false);
  useEffect(() => {
    if (!creativeZoom) return;
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') setCreativeZoom(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [creativeZoom]);
  const [googleMessage, setGoogleMessage] = useState('');
  const [googleBusy, setGoogleBusy] = useState(false);
  const [googleWriting, setGoogleWriting] = useState(false);
  const [googleAttempted, setGoogleAttempted] = useState(false);
  const generateGoogleText = async (replace = false) => {
    if (!runId) return;
    setGoogleWriting(true); setGoogleMessage('');
    try {
      const response = await fetch(`${apiUrl}/missions/${encodeURIComponent(runId)}/google/generate-text`, { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Generazione non riuscita.');
      setGoogleText(current => replace || !current.trim() ? data.text : current);
    } catch (error) { setGoogleMessage(error instanceof Error ? error.message : 'Generazione non riuscita.'); }
    finally { setGoogleWriting(false); }
  };
  useEffect(() => {
    if (platform === 'google' && runId && !googleText.trim() && !googleAttempted) {
      setGoogleAttempted(true); void generateGoogleText();
    }
    // Generate only once on opening an empty post; further attempts are manual.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [platform, runId, googleAttempted]);
  useEffect(() => { setGoogleText(texts.gmb); }, [texts.gmb, runId]);
  useEffect(() => { setGooglePhoto(photos[0]?.src || ''); setCreativeSource(photos[0]?.src || ''); }, [runId, photos[0]?.src]);
  useEffect(() => {
    if (!runId || platform !== 'google') return;
    fetch(`${apiUrl}/missions/${encodeURIComponent(runId)}/google/info`).then(r => r.json()).then(setGoogleInfo).catch(() => setGoogleMessage('Impossibile verificare la scheda.'));
  }, [apiUrl, runId, platform]);

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
              {googlePhoto && runId && <button type="button" className="google-zoom-trigger" onClick={() => setCreativeZoom(true)} aria-label="Ingrandisci foto"><img className="pub-single google-preview" src={`${apiUrl}/missions/${encodeURIComponent(runId)}/google/prepare?photo=${encodeURIComponent(googlePhoto)}`} alt="Anteprima della foto nel formato Google Business 4:3" /><span>Ingrandisci foto</span></button>}
              {creativeZoom && googlePhoto && <div className="google-lightbox" role="dialog" aria-modal="true" aria-label="Foto ingrandita" onClick={() => setCreativeZoom(false)}><button className="google-lightbox-close" type="button" onClick={() => setCreativeZoom(false)} aria-label="Chiudi anteprima">Chiudi ×</button><img src={url(googlePhoto)} alt="Foto ingrandita in formato originale" onClick={e => e.stopPropagation()} /></div>}
              <label htmlFor="google-photo">Foto del pezzo</label>
              <select id="google-photo" value={googlePhoto} onChange={e => setGooglePhoto(e.target.value)}>
                {photos.map(photo => <option key={photo.src} value={photo.src}>{photo.label}</option>)}
                {(googleInfo?.creatives || []).map((src, index) => <option key={src} value={src}>{googleInfo?.creative_details?.[src]?.label || "Generatore sconosciuto"} · {index + 1}</option>)}
              </select>
              {googleInfo?.creatives?.includes(googlePhoto) && <div><p className="pub-meta"><a href={url(googlePhoto)} target="_blank" rel="noreferrer" download>Apri o scarica l’originale</a></p><button type="button" className="btn-secondary" disabled={creativeRemoving || creativeBusy} onClick={async () => {
                setCreativeRemoving(true); setCreativeMessage('');
                try {
                  const response = await fetch(`${apiUrl}/missions/${encodeURIComponent(runId || '')}/google/creative/remove`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({photo:googlePhoto})});
                  const data = await response.json();
                  if (!response.ok) throw new Error(data.error || 'Rimozione non riuscita.');
                  setGoogleInfo(current => current ? {...current, creatives:data.creatives, creative_details:data.creative_details} : current);
                  setGooglePhoto(photos[0]?.src || ''); setCreativeMessage('Creativa rimossa.');
                } catch (error) { setCreativeMessage(error instanceof Error ? error.message : 'Rimozione non riuscita.'); }
                finally { setCreativeRemoving(false); }
              }}>{creativeRemoving ? 'Rimuovo…' : 'Elimina questa creativa'}</button></div>}
              <p className="pub-meta">Questa anteprima mostra il formato Google Business 4:3. Per una Storia, apri o scarica l’immagine originale.</p>
              <div className="google-create">
                <h3>Crea una foto con AI</h3>
                <p className="pub-meta">Parti da una foto della scheda: la creativa viene salvata qui.</p>
                <label htmlFor="creative-provider">Generatore</label>
                <select id="creative-provider" value={creativeProvider} onChange={e => setCreativeProvider(e.target.value)}><option value="chatgpt">ChatGPT · Codex</option><option value="flow">Google Flow · Nano Banana</option></select>
                {creativeProvider === 'flow' ? <><label htmlFor="flow-model">Modello Google Flow</label><select id="flow-model" value={flowModel} onChange={e => setFlowModel(e.target.value)}><option value="nano2">Nano Banana 2</option><option value="nano-pro">Nano Banana Pro</option><option value="nano2-lite">Nano Banana 2 Lite</option></select><p className="pub-meta">Usa l’account Google collegato a Flow; disponibilità e quota dipendono dal tuo account.</p></> : <p className="pub-meta">Usa l’accesso Codex collegato, nei limiti del piano.</p>}
                <label htmlFor="creative-source">Foto di riferimento</label>
                <select id="creative-source" value={creativeSource} onChange={e => setCreativeSource(e.target.value)}>{photos.map(photo => <option key={photo.src} value={photo.src}>{photo.label}</option>)}</select>
                <label htmlFor="creative-style">Stile della foto</label>
                <select id="creative-style" value={creativeStyle} onChange={e => setCreativeStyle(e.target.value)}>
                  <option value="personalizzato">Prompt libero</option><option value="catalogo">Catalogo luminoso</option><option value="editoriale">Editoriale moda</option><option value="lifestyle">Lifestyle naturale</option><option value="dettaglio">Dettaglio prodotto</option>
                </select>
                <label htmlFor="creative-format">Formato della creativa</label>
                <select id="creative-format" value={creativeFormat} onChange={e => setCreativeFormat(e.target.value)}>
                  <option value="auto">Automatico dal prompt</option><option value="google">Google Business · 4:3</option><option value="story">Storia Instagram · 9:16</option>
                </select>
                <label htmlFor="creative-prompt">Il tuo prompt {creativeStyle === 'personalizzato' ? '' : '(facoltativo)'}</label>
                <textarea id="creative-prompt" rows={5} maxLength={4000} value={creativePrompt} onChange={e => setCreativePrompt(e.target.value)} placeholder="Descrivi ambientazione, luce, inquadratura e atmosfera…" />
                <p className="pub-meta">{creativeStyle === 'personalizzato' ? 'La foto seguirà le tue indicazioni.' : 'Le indicazioni si aggiungono allo stile scelto.'} </p>
                <button type="button" className="btn-secondary" disabled={creativeBusy || !creativeSource || (creativeStyle === 'personalizzato' && !creativePrompt.trim())} onClick={async () => {
                  setCreativeBusy(true); setCreativeMessage('Creo la foto: possono volerci alcuni minuti…');
                  try {
                    const response = await fetch(`${apiUrl}/missions/${encodeURIComponent(runId || '')}/google/creative`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({photo:creativeSource, style:creativeStyle, prompt:creativePrompt, format:creativeFormat, provider:creativeProvider, flow_model:flowModel})});
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.error || 'Generazione non riuscita.');
                    setGoogleInfo(current => current ? {...current, creatives:data.creatives, creative_details:data.creative_details} : current); setGooglePhoto(data.photo);
                    setCreativeMessage('Creativa pronta.');
                  } catch (error) { setCreativeMessage(error instanceof Error ? error.message : 'Generazione non riuscita.'); }
                  finally { setCreativeBusy(false); }
                }}>{creativeBusy ? 'Creo la foto…' : creativeProvider === 'flow' ? 'Genera creativa con Google Flow' : 'Genera creativa con ChatGPT'}</button>
                <p className="pub-meta" aria-live="polite">{creativeMessage}</p>
              </div>
            </div>
            <div className="pub-texts">
              <label htmlFor="google-text">Testo per Google Business</label>
              <button type="button" className="btn-secondary" disabled={googleWriting} onClick={() => { if (!googleText.trim() || window.confirm("Sostituire il testo attuale con una nuova proposta?")) void generateGoogleText(true); }}>{googleWriting ? "Scrivo il testo…" : googleText.trim() ? "Riscrivi il testo con AI" : "Genera il testo con AI"}</button>
              <textarea id="google-text" rows={8} maxLength={1500} value={googleText} onChange={e => setGoogleText(e.target.value)} />
              <p className="pub-meta">{googleText.length}/1500 caratteri · Controlla materiali, prezzo e disponibilità prima dell’invio. Il link sarà nel pulsante del post.</p>
              <div className="pub-block"><h3>Pulsante nel post Google</h3><strong>Scopri di più</strong>{googleInfo?.product_url ? <p className="pub-meta">Destinazione: <a href={googleInfo.product_url} target="_blank" rel="noreferrer">apri la scheda prodotto</a>. Il pulsante viene aggiunto alla bozza Zernio.</p> : <p className="pub-meta">Pubblica prima la scheda sul sito: il pulsante porterà alla pagina del prodotto.</p>}</div>
              {googleInfo && (!googleInfo.zernio_configured || !googleInfo.account_configured) && <p className="pub-meta">Per inviare la bozza serve configurare Zernio nello Studio.</p>}
              <button className="btn-mission" type="button" disabled={googleBusy || !googleText.trim() || !googlePhoto || !googleInfo?.product_url || !googleInfo.zernio_configured || !googleInfo.account_configured} onClick={async () => {
                setGoogleBusy(true); setGoogleMessage('');
                try {
                  const response = await fetch(`${apiUrl}/missions/${encodeURIComponent(runId || '')}/google/draft`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({photo: googlePhoto, content: googleText})});
                  const data = await response.json();
                  setGoogleMessage(response.ok ? 'Bozza inviata a Zernio. Non è ancora pubblicata su Google.' : (data.error || 'Invio non riuscito.'));
                } catch { setGoogleMessage('Connessione interrotta. Controlla le bozze su Zernio prima di riprovare.'); }
                finally { setGoogleBusy(false); }
              }}>{googleBusy ? 'Invio in corso…' : 'Invia la bozza a Zernio'}</button>
              <p aria-live="polite">{googleMessage}</p>
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