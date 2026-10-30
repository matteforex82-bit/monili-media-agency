'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';
import { IMAGE_ENGINES, loadSettings, saveSettings, type StudioSettings } from '@/lib/settings';

export default function SettingsPage() {
  const [settings, setSettings] = useState<StudioSettings | null>(null);
  const [check, setCheck] = useState<{ busy: boolean; ok?: boolean; text: string }>({ busy: false, text: '' });

  useEffect(() => setSettings(loadSettings()), []);

  const pick = (imageModel: string) => {
    if (!settings) return;
    const next = { ...settings, imageModel };
    setSettings(next);
    saveSettings(next);
  };

  const verify = async () => {
    if (!settings) return;
    setCheck({ busy: true, text: '' });
    try {
      const res = await fetch(
        `${API_URL}/openrouter/check?image_model=${encodeURIComponent(settings.imageModel)}&text_model=${encodeURIComponent(settings.textModel)}`,
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
      const ok = Boolean(data.image_model_supported && data.text_model_supported);
      setCheck({
        busy: false,
        ok,
        text: ok ? 'Tutto collegato: testi e immagini rispondono.' : 'Il motore scelto non risulta disponibile su OpenRouter.',
      });
    } catch (err) {
      setCheck({ busy: false, ok: false, text: `Verifica non riuscita: ${err instanceof Error ? err.message : err}` });
    }
  };

  return (
    <div className="page">
      <Link href="/altro" className="back-link">‹ Altro</Link>
      <h1 className="page-title">Impostazioni</h1>
      <section className="step">
        <h2 className="step-title">Motore delle foto</h2>
        <p className="step-hint">Lo scegli una volta: vale per tutti i pezzi nuovi.</p>
        <div className="seg" role="group" aria-label="Motore delle foto">
          {IMAGE_ENGINES.map((engine) => (
            <button
              key={engine.id}
              type="button"
              className="btn-secondary"
              aria-pressed={settings?.imageModel === engine.id}
              onClick={() => pick(engine.id)}
            >
              {engine.label}
            </button>
          ))}
        </div>
        <p className="step-hint" style={{ marginTop: 10 }}>
          {IMAGE_ENGINES.find((engine) => engine.id === settings?.imageModel)?.hint}
        </p>
      </section>
      <section className="step">
        <h2 className="step-title">Collegamento</h2>
        <p className="step-hint">Controlla che la chiave OpenRouter funzioni. Non crea niente e non spende.</p>
        <button type="button" className="btn-secondary" onClick={verify} disabled={check.busy || !settings}>
          {check.busy ? 'Controllo...' : 'Verifica OpenRouter'}
        </button>
        {check.text && <p className={`state-line ${check.ok ? 'ok' : 'err'}`} role="status">{check.text}</p>}
      </section>
    </div>
  );
}
