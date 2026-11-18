// Bozze veloci: foto e nota salvate in negozio, la Scheda pezzo si crea dopo (backend: bozze.py).
export interface DraftFacts {
  prezzo?: number;
  misura?: string;
  pietre?: string[];
}

export interface Progress {
  stage: 'prompt' | 'crea' | 'carica' | 'valuta' | 'fatto';
  label: string;
  done: { prompt: boolean; generare: boolean; valutare: boolean };
}

export interface Draft {
  id: string;
  created_at: string;
  note: string;
  photos: string[];
  main: string;
  detail: string;
  status: 'da_lavorare' | 'in_corso' | 'scheda_pronta';
  job_id: string;
  run_id: string;
  error: string;
  facts: DraftFacts;
  progress?: Progress;
}

export const ACTIVE_JOB_STORAGE_KEY = 'monili_active_job_id';

export function formatDraftTime(value: string) {
  const date = value ? new Date(value) : null;
  if (!date || Number.isNaN(date.getTime())) return '';
  const sameDay = new Date().toDateString() === date.toDateString();
  const time = date.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
  return sameDay ? `Oggi, ${time}` : `${date.toLocaleDateString('it-IT', { day: 'numeric', month: 'long' })}, ${time}`;
}

// A phone photo is 4000 px and several MB: for the Studio 2400 px is plenty and the upload stays quick
// (also over 4G). If the browser cannot read the file, the original goes up unchanged.
export async function shrinkPhoto(file: File, maxSide = 2400): Promise<File> {
  try {
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
    if (scale === 1 && file.type === 'image/jpeg') {
      bitmap.close();
      return file;
    }
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    canvas.getContext('2d')?.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close();
    const blob: Blob | null = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.9));
    if (!blob) return file;
    return new File([blob], file.name.replace(/\.[^.]+$/, '') + '.jpg', { type: 'image/jpeg' });
  } catch {
    return file;
  }
}
