// I tipi di pezzo dello Studio (stessi nomi di categorie.SUBTYPES nel backend).
export const SUBTYPE_GROUPS: Array<{ label: string; items: Array<[string, string]> }> = [
  {
    label: 'Bijoux',
    items: [
      ['anello', 'Anello'],
      ['orecchini', 'Orecchini'],
      ['collana', 'Collana'],
      ['bracciale', 'Bracciale'],
      ['cavigliera', 'Cavigliera'],
    ],
  },
  {
    label: 'Accessori',
    items: [
      ['borsa', 'Borsa'],
      ['pochette', 'Pochette'],
      ['sciarpa', 'Sciarpa'],
      ['foulard', 'Foulard'],
      ['cintura', 'Cintura'],
      ['cappello', 'Cappello'],
      ['occhiali', 'Occhiali'],
    ],
  },
  { label: 'Abbigliamento', items: [['capo', 'Capo di abbigliamento']] },
];

export const CUT_OPTIONS: Array<[string, string]> = [
  ['', 'Lo capisce lo Studio'],
  ['sopra', 'Sopra (giacca, camicia, maglia)'],
  ['sotto', 'Sotto (gonna, pantaloni)'],
  ['intero', 'Figura intera (abito, cappotto)'],
];

export function subtypeLabel(value: string | undefined): string {
  for (const group of SUBTYPE_GROUPS) {
    const found = group.items.find(([key]) => key === value);
    if (found) return found[1];
  }
  return '';
}
