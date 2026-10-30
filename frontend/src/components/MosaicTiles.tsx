export type TileState = 'none' | 'working' | 'draft' | 'done';

export interface TileItem {
  label: string;
  state: TileState;
}

const STATE_WORDS: Record<TileState, string> = {
  none: 'da fare',
  working: 'in corso',
  draft: 'bozza',
  done: 'fatto',
};

// Una fila di tessere che si colorano coi colori della foto del pezzo: dice a che punto sei.
export default function MosaicTiles({
  items,
  palette,
  large = false,
}: {
  items: TileItem[];
  palette: string[];
  large?: boolean;
}) {
  const summary = items.map((item) => `${item.label}: ${STATE_WORDS[item.state]}`).join(', ');
  return (
    <div className={`tiles${large ? ' large' : ''}`} role="img" aria-label={summary}>
      {items.map((item, index) => (
        <div key={item.label} className="tile-wrap">
          <span
            className="tile"
            data-state={item.state}
            style={palette.length ? ({ '--tile': palette[index % palette.length] } as React.CSSProperties) : undefined}
          />
          <span className="tile-label">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

export interface PieceSteps {
  scheda: boolean;
  sito: 'none' | 'draft' | 'published';
  reel: 'none' | 'working' | 'done';
  instagram: 'none' | 'draft' | 'published';
}

export function stepTiles(steps: PieceSteps): TileItem[] {
  return [
    { label: 'Scheda', state: steps.scheda ? 'done' : 'none' },
    { label: 'Sito', state: steps.sito === 'published' ? 'done' : steps.sito === 'draft' ? 'draft' : 'none' },
    { label: 'Reel', state: steps.reel },
    { label: 'Instagram', state: steps.instagram === 'published' ? 'done' : steps.instagram === 'draft' ? 'draft' : 'none' },
  ];
}
