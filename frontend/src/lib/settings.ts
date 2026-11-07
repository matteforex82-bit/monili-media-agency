// Scelte che si fanno una volta sola (motore delle immagini): restano nel browser.
const KEY = 'monili_settings_v1';

export const IMAGE_ENGINES = [
  { id: 'google/gemini-nano-banana-2.1', label: 'Nano Banana 2.1', hint: 'Il predefinito: veloce, mantiene bene pietre e riflessi.' },
  { id: 'openai/gpt-image-2.6-sunburst', label: 'GPT Image 2.6', hint: 'Il più recente di OpenAI: molto fedele alla struttura del pezzo, più lento.' },
] as const;

export const DEFAULT_TEXT_MODEL = 'openai/gpt-5.5';

export interface StudioSettings {
  imageModel: string;
  textModel: string;
}

const DEFAULTS: StudioSettings = { imageModel: IMAGE_ENGINES[0].id, textModel: DEFAULT_TEXT_MODEL };

export function loadSettings(): StudioSettings {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return DEFAULTS;
    const parsed = JSON.parse(raw);
    return {
      imageModel: IMAGE_ENGINES.some((engine) => engine.id === parsed?.imageModel) ? parsed.imageModel : DEFAULTS.imageModel,
      textModel: typeof parsed?.textModel === 'string' && parsed.textModel ? parsed.textModel : DEFAULTS.textModel,
    };
  } catch {
    return DEFAULTS;
  }
}

export function saveSettings(settings: StudioSettings) {
  try {
    localStorage.setItem(KEY, JSON.stringify(settings));
  } catch {
    /* storage non disponibile: vale per questa sessione */
  }
}
