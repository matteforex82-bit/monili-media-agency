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
  price: string; // es. "39 €"; vuoto = non mostrare
  place: string; // es. "Via Cavour 21, Ravenna"
  closing: boolean;
  titleFrom: number; // secondi a cui entra la targhetta in basso
};

const rise = (frame: number, start: number, duration = 14) =>
  interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

const Hook = ({text, until}: {text: string; until: number}) => {
  const frame = useCurrentFrame();
  const t = rise(frame, 8);
  const out = interpolate(frame, [until - 10, until], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div
      style={{
        position: 'absolute',
        left: 70,
        right: 70,
        top: 330,
        opacity: t * out,
        transform: `translateY(${(1 - t) * 30}px)`,
        background: CREAM,
        borderRadius: 18,
        padding: '34px 44px 38px',
        borderLeft: `10px solid ${TERRACOTTA}`,
      }}
    >
      <div style={{fontFamily: serif.fontFamily, fontWeight: 500, fontSize: 84, lineHeight: 1.04, color: INK}}>{text}</div>
    </div>
  );
};

const NamePlate = ({title, price, place}: {title: string; price: string; place: string}) => {
  const frame = useCurrentFrame();
  const t = rise(frame, 0, 18);
  return (
    <div
      style={{
        position: 'absolute',
        left: 70,
        right: 190, // lascia libera la colonna di icone a destra
        bottom: 470, // sopra la zona coperta dall'interfaccia di Instagram
        opacity: t,
        transform: `translateY(${(1 - t) * 40}px)`,
        background: CREAM,
        borderRadius: 18,
        padding: '28px 36px 30px',
        display: 'grid',
        gap: 10,
      }}
    >
      <div style={{fontFamily: serif.fontFamily, fontWeight: 600, fontSize: 64, lineHeight: 1.05, color: INK}}>{title}</div>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 24, fontFamily: sans.fontFamily, fontSize: 34, color: '#5a544c'}}>
        <span>{place}</span>
        {price && <strong style={{fontWeight: 500, color: TERRACOTTA, fontSize: 48}}>{price}</strong>}
      </div>
    </div>
  );
};

const Closing = ({place}: {place: string}) => {
  const frame = useCurrentFrame();
  const a = rise(frame, 4, 16);
  const b = rise(frame, 14, 16);
  return (
    <AbsoluteFill style={{background: CREAM, justifyContent: 'center', alignItems: 'center', padding: '0 90px', textAlign: 'center'}}>
      <div style={{opacity: a, transform: `translateY(${(1 - a) * 24}px)`, fontFamily: serif.fontFamily, fontWeight: 600, fontSize: 150, color: INK, lineHeight: 1}}>
        Ti piace?
      </div>
      <div style={{width: 120, height: 6, background: TERRACOTTA, margin: '48px 0', opacity: a}} />
      <div style={{opacity: b, transform: `translateY(${(1 - b) * 24}px)`, fontFamily: serif.fontFamily, fontWeight: 500, fontSize: 78, color: INK, lineHeight: 1.1}}>
        Scrivici, ti diciamo se è disponibile.
      </div>
      <div style={{opacity: b, marginTop: 70, fontFamily: sans.fontFamily, fontSize: 36, letterSpacing: 4, color: '#5a544c', textTransform: 'uppercase'}}>
        I Monili Ravenna · {place}
      </div>
    </AbsoluteFill>
  );
};

export const ReelGrafica = ({video, videoSeconds, hook, title, price, place, closing, titleFrom}: ReelGraficaProps) => {
  const {fps} = useVideoConfig();
  const bodyFrames = Math.round(videoSeconds * fps);
  const hookEnd = Math.min(bodyFrames, Math.round(2.6 * fps));
  const plateFrom = Math.min(Math.round(titleFrom * fps), Math.max(0, bodyFrames - fps));
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Sequence name="Video" durationInFrames={bodyFrames}>
        <Video name="Video del Reel" src={staticFile(video)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        {hook.trim() && (
          <Sequence name="Frase d'apertura" durationInFrames={hookEnd}>
            <Hook text={hook} until={hookEnd} />
          </Sequence>
        )}
        {title.trim() && (
          <Sequence name="Targhetta del pezzo" from={plateFrom} durationInFrames={Math.max(1, bodyFrames - plateFrom)}>
            <NamePlate title={title} price={price} place={place} />
          </Sequence>
        )}
      </Sequence>
      {closing && (
        <Sequence name="Chiusura" from={bodyFrames}>
          <Closing place={place} />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
