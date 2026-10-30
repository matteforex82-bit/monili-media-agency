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
