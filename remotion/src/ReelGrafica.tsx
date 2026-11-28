import {AbsoluteFill, Easing, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import {loadFont as loadSerif} from '@remotion/google-fonts/CormorantGaramond';
import {loadFont as loadSans} from '@remotion/google-fonts/Outfit';

export const FPS = 30;
export const CLOSING_SECONDS = 2.5;

const serif = loadSerif('normal', {weights: ['500', '600'], subsets: ['latin']});
const sans = loadSans('normal', {weights: ['400', '500'], subsets: ['latin']});

// Colori del negozio (gli stessi dello Studio e del sito).
const CREAM = '#fbf7ed';
const INK = '#1a1a1a';
const TERRACOTTA = '#b84e32';

export type ReelGraficaProps = {
  video: string; // nome del file in public/
  videoSeconds: number;
  hook: string; // frase d'apertura, in alto
  title: string; // nome del pezzo
  detail?: string; // riga sotto il nome: materiale e pietre
  price: string; // es. "39 €"; vuoto = non mostrare
  place: string; // es. "Via Cavour 21, Ravenna"
  closing: boolean;
  titleFrom: number; // secondi a cui entra la targhetta in basso
  // Facoltativi: senza, il Reel esce come prima.
  plateUntil?: number; // secondi a cui la targhetta sparisce (es. quando il gioiello è in primo piano)
  closingSeconds?: number; // durata della chiusura (default 2,5)
  zoom?: number; // zoom lento finale sul video, es. 1.1 (default nessuno)
  layout?: 'reel' | 'story'; // zone sicure di Instagram: Reel (default) o Storia
};

// Zone sicure: nei Reel Instagram copre il fondo e la colonna di icone a destra, nelle Storie alto e basso.
const LAYOUTS = {
  reel: {hookTop: 250, hookSize: 68, plateBottom: 380, plateRight: 190, closingLift: 0, sticker: false},
  story: {hookTop: 300, hookSize: 68, plateBottom: 560, plateRight: 90, closingLift: 150, sticker: true},
};

const rise = (frame: number, start: number, duration = 14) =>
  interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

const Hook = ({text, until, top, size}: {text: string; until: number; top: number; size: number}) => {
  const frame = useCurrentFrame();
  const box = rise(frame, 4, 16);
  const out = interpolate(frame, [until - 10, until], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const words = text.split(/\s+/).filter(Boolean);
  return (
    <div
      style={{
        position: 'absolute',
        left: 70,
        right: 70,
        top,
        opacity: box * out,
        clipPath: `inset(0 ${(1 - box) * 100}% 0 0 round 18px)`, // si apre da sinistra come una striscia
        background: CREAM,
        borderRadius: 18,
        padding: '26px 38px 30px',
        borderLeft: `10px solid ${TERRACOTTA}`,
      }}
    >
      <div style={{fontFamily: serif.fontFamily, fontWeight: 500, fontSize: size, lineHeight: 1.06, color: INK}}>
        {words.map((w, i) => {
          const t = rise(frame, 10 + i * 4, 14); // le parole entrano una dopo l'altra
          return (
            <span key={i} style={{display: 'inline-block', marginRight: '0.28em', opacity: t, transform: `translateY(${(1 - t) * 26}px)`}}>
              {w}
            </span>
          );
        })}
      </div>
    </div>
  );
};

const NamePlate = ({title, detail, price, place, bottom, right, until}: {title: string; detail: string; price: string; place: string; bottom: number; right: number; until: number}) => {
  const frame = useCurrentFrame();
  const wipe = rise(frame, 0, 16);
  const out = interpolate(frame, [until - 10, until], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const l1 = rise(frame, 8, 14);
  const l2 = rise(frame, 14, 14);
  const l3 = rise(frame, 20, 14);
  const shine = interpolate(frame, [18, 38], [-30, 130], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}); // riflesso che attraversa la targhetta
  return (
    <div
      style={{
        position: 'absolute',
        left: 70,
        right,
        bottom,
        opacity: out,
        transform: `translateY(${(1 - wipe) * 50}px)`,
        clipPath: `inset(0 ${(1 - wipe) * 100}% 0 0 round 18px)`,
        background: CREAM,
        borderRadius: 18,
        padding: '24px 32px 26px 42px',
        display: 'grid',
        gap: 8,
        overflow: 'hidden',
      }}
    >
      <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 10, background: TERRACOTTA, transform: `scaleY(${wipe})`, transformOrigin: 'top'}} />
      <div style={{position: 'absolute', top: 0, bottom: 0, width: '18%', left: `${shine}%`, background: 'linear-gradient(100deg, transparent, rgba(255,255,255,0.75), transparent)'}} />
      <div style={{fontFamily: serif.fontFamily, fontWeight: 600, fontSize: 58, lineHeight: 1.05, color: INK, opacity: l1, transform: `translateX(${(1 - l1) * -30}px)`}}>{title}</div>
      {detail && (
        <div style={{fontFamily: sans.fontFamily, fontSize: 30, lineHeight: 1.25, color: INK, opacity: l2, transform: `translateX(${(1 - l2) * -30}px)`}}>{detail}</div>
      )}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 24, fontFamily: sans.fontFamily, fontSize: 30, color: '#5a544c', opacity: l3, transform: `translateX(${(1 - l3) * -30}px)`}}>
        <span>{place}</span>
        {price && <strong style={{fontWeight: 500, color: TERRACOTTA, fontSize: 48}}>{price}</strong>}
      </div>
    </div>
  );
};

const Closing = ({place, lift, sticker, fast}: {place: string; lift: number; sticker: boolean; fast: boolean}) => {
  const frame = useCurrentFrame();
  const k = fast ? 0.5 : 1;
  const a = rise(frame, 4 * k, 16 * k);
  const b = rise(frame, 14 * k, 16 * k);
  const c = rise(frame, 22 * k, 14 * k);
  return (
    <AbsoluteFill style={{background: CREAM, justifyContent: 'center', alignItems: 'center', padding: `0 90px ${lift}px`, textAlign: 'center'}}>
      <div style={{opacity: a, transform: `translateY(${(1 - a) * 24}px)`, fontFamily: serif.fontFamily, fontWeight: 600, fontSize: 150, color: INK, lineHeight: 1}}>
        Ti piace?
      </div>
      <div style={{width: 120 + 140 * b, height: 6, background: TERRACOTTA, margin: '48px 0', opacity: a}} />
      <div style={{opacity: b, transform: `translateY(${(1 - b) * 24}px)`, fontFamily: serif.fontFamily, fontWeight: 500, fontSize: 78, color: INK, lineHeight: 1.1}}>
        Scrivici, ti diciamo se è disponibile.
      </div>
      <div style={{opacity: b, marginTop: 70, fontFamily: sans.fontFamily, fontSize: 36, letterSpacing: 4, color: '#5a544c', textTransform: 'uppercase'}}>
        I Monili Ravenna · {place}
      </div>
      {sticker && (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 380, display: 'flex', justifyContent: 'center', opacity: c, transform: `translateY(${(1 - c) * 20}px)`}}>
          <div style={{transform: `scale(${1 + 0.05 * Math.sin(frame / 4)})`, background: TERRACOTTA, color: CREAM, borderRadius: 60, padding: '24px 64px', fontFamily: sans.fontFamily, fontWeight: 500, fontSize: 46, letterSpacing: 2}}>
            Scrivici ✉
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

export const ReelGrafica = ({video, videoSeconds, hook, title, detail = '', price, place, closing, titleFrom, plateUntil, closingSeconds = CLOSING_SECONDS, zoom = 1, layout = 'reel'}: ReelGraficaProps) => {
  const {fps} = useVideoConfig();
  const L = LAYOUTS[layout] ?? LAYOUTS.reel;
  const frame = useCurrentFrame();
  const bodyFrames = Math.round(videoSeconds * fps);
  const hookEnd = Math.min(bodyFrames, Math.round(2.6 * fps));
  const plateEnd = plateUntil ? Math.min(bodyFrames, Math.round(plateUntil * fps)) : bodyFrames;
  const scale = interpolate(frame, [0, bodyFrames], [1, zoom], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const plateFrom = Math.min(Math.round(titleFrom * fps), Math.max(0, bodyFrames - fps));
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Sequence name="Video" durationInFrames={bodyFrames}>
        <Video name="Video del Reel" src={staticFile(video)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, transformOrigin: '50% 58%'}} />
        {hook.trim() && (
          <Sequence name="Frase d'apertura" durationInFrames={hookEnd}>
            <Hook text={hook} until={hookEnd} top={L.hookTop} size={L.hookSize} />
          </Sequence>
        )}
        {title.trim() && (
          <Sequence name="Targhetta del pezzo" from={plateFrom} durationInFrames={Math.max(1, plateEnd - plateFrom)}>
            <NamePlate title={title} detail={detail} price={price} place={place} bottom={L.plateBottom} right={L.plateRight} until={Math.max(1, plateEnd - plateFrom)} />
          </Sequence>
        )}
      </Sequence>
      {closing && (
        <Sequence name="Chiusura" from={bodyFrames}>
          <Closing place={place} lift={L.closingLift} sticker={L.sticker} fast={closingSeconds < 2} />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
