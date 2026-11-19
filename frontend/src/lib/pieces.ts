import type { PieceSteps } from '@/components/MosaicTiles';

export interface PieceSummary {
  run_id: string;
  title: string;
  created_at: string;
  cover: string;
  palette: string[];
  steps: PieceSteps;
  reels: Array<{ id: string; status?: string; title?: string }>;
}

export function formatPieceDate(value: string) {
  const date = value ? new Date(value) : null;
  if (!date || Number.isNaN(date.getTime())) return '';
  return date.toLocaleDateString('it-IT', { day: 'numeric', month: 'long', year: 'numeric' });
}

// Il prossimo passo da fare per un pezzo: lo dice la lista Pezzi e porta dritto alla schermata giusta.
export function nextStep(steps: PieceSummary['steps']): { label: string; tab: 'sito' | 'video' | 'pubblica'; done: boolean } {
  if (steps.sito === 'none') return { label: 'Prossimo passo: manda il pezzo al sito', tab: 'sito', done: false };
  if (steps.reel === 'none') return { label: 'Prossimo passo: crea il video', tab: 'video', done: false };
  if (steps.reel === 'working') return { label: 'Il video è in lavorazione', tab: 'video', done: false };
  if (steps.instagram !== 'published') return { label: 'Prossimo passo: pubblica su Instagram', tab: 'pubblica', done: false };
  return { label: 'Tutto pubblicato', tab: 'pubblica', done: true };
}
