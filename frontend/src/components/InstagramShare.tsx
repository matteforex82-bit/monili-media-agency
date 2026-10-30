'use client';

import { useEffect, useState } from 'react';

export interface ShareFile {
  url: string;
  filename: string;
}

interface Props {
  files: ShareFile[];
  caption: string;
  kind: 'Reel' | 'Storia' | 'Post';
  // Se nei contenuti c'è una donna creata dall'AI: promemoria per l'etichetta "Info sull'AI".
  hasAiWoman: boolean;
}

type Shareable = { share?: (data: ShareData) => Promise<void>; canShare?: (data?: ShareData) => boolean };

function mimeOf(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase();
  if (ext === 'mp4' || ext === 'm4v') return 'video/mp4';
  if (ext === 'mov') return 'video/quicktime';
  if (ext === 'png') return 'image/png';
  return 'image/jpeg';
}

// Copia con un tocco anche su pagine non sicure (http): la Clipboard API serve https, execCommand no.
async function copyText(text: string): Promise<boolean> {
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

// Apre il menu di condivisione dell'iPhone con i file già pronti e copia la caption:
// in Instagram si sceglie Reel, Storia o Post e si incolla. Nessun account sviluppatore, nessun token.
export default function InstagramShare({ files, caption, kind, hasAiWoman }: Props) {
  const [ready, setReady] = useState<File[] | null>(null);
  const [prepFailed, setPrepFailed] = useState(false);
  const [message, setMessage] = useState('');
  const [fallback, setFallback] = useState(false);

  // I file si scaricano prima del tocco: il menu di condivisione deve partire subito dal tocco,
  // altrimenti l'iPhone lo rifiuta dopo un'attesa.
  const filesKey = files.map((file) => file.url).join('|');
  useEffect(() => {
    let alive = true;
    setReady(null);
    setPrepFailed(false);
    Promise.all(
      files.map(async (file) => {
        const res = await fetch(file.url, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const blob = await res.blob();
        return new File([blob], file.filename, { type: mimeOf(file.filename) });
      }),
    )
      .then((prepared) => alive && setReady(prepared))
      .catch(() => alive && setPrepFailed(true));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filesKey]);

  const nav = (typeof navigator !== 'undefined' ? navigator : undefined) as (Navigator & Shareable) | undefined;
  const canShare = Boolean(ready && nav?.share && nav.canShare?.({ files: ready }));

  const onShare = () => {
    if (!ready) return;
    // La caption va negli appunti nello stesso tocco, prima di aprire il menu.
    const copied = copyText(caption);
    const where = kind === 'Post' ? 'Post' : kind;
    if (canShare && nav?.share) {
      setFallback(false);
      nav.share({ files: ready }).then(
        async () => setMessage((await copied) ? `Caption copiata. In Instagram scegli ${where} e incolla la caption.` : 'Non sono riuscito a copiare la caption: usa "Copia" nei testi.'),
        async (err: unknown) => {
          const cancelled = err instanceof DOMException && err.name === 'AbortError';
          const ok = await copied;
          setMessage(cancelled ? `Condivisione annullata.${ok ? ' La caption resta copiata.' : ''}` : 'Il menu di condivisione non si è aperto. Salva i file qui sotto.');
          if (!cancelled) setFallback(true);
        },
      );
      return;
    }
    // Pagina non sicura (http, come l'indirizzo Tailscale) o computer: il menu coi file non esiste.
    setFallback(true);
    void copied.then((ok) =>
      setMessage(
        `${ok ? 'Caption copiata. ' : 'Non sono riuscito a copiare la caption: usa "Copia" nei testi. '}Salva ${files.length > 1 ? 'i file' : 'il file'} qui sotto, poi in Instagram scegli ${where} dalla libreria e incolla la caption.`,
      ),
    );
  };

  return (
    <div className="ig-share">
      <button type="button" className="btn-mission ig-share-btn" onClick={onShare} disabled={!ready}>
        {prepFailed ? 'File non disponibile' : !ready ? 'Preparo i file...' : 'Condividi su Instagram'}
      </button>
      {hasAiWoman && (
        <p className="ig-note">
          C&apos;è una donna creata dall&apos;AI: in Instagram, prima di pubblicare, attiva l&apos;etichetta <strong>Info sull&apos;AI</strong>.
        </p>
      )}
      {ready && !canShare && !fallback && !message && (
        <p className="ig-note">
          Da qui il menu di condivisione non si apre da solo: il tocco copia la caption e ti mostra i file da salvare.
        </p>
      )}
      {message && <p className="ig-note" role="status">{message}</p>}
      {fallback && (
        <div className="ig-files">
          {files.map((file) => (
            <a key={file.url} href={file.url} target="_blank" rel="noreferrer" className="btn-secondary">
              Salva {file.filename}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
