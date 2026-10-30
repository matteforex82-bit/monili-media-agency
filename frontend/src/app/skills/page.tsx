'use client';

import { useCallback, useEffect, useState } from 'react';
import { API_URL } from '@/lib/apiUrl';

interface SkillItem {
  id: string;
  label: string;
  description: string;
  formats: string[];
  uses_model: boolean;
  default_seconds: number;
  source: 'originale' | 'modificata';
  has_original: boolean;
}

interface RawSkill {
  id: string;
  base: boolean;
  text: string;
  source: 'originale' | 'modificata';
  has_original: boolean;
}

const BASE_LABELS: Record<string, string> = {
  fotogramma: 'Base · fotogrammi (immagine di partenza di ogni scena)',
  movimento: 'Base · movimento video',
  copertina: 'Base · copertina poster',
  testi: 'Base · regole dei testi',
  donne: 'Base · donne (la inventa l’AI, una per pezzo)',
  divieti: 'Mai nei contenuti (cose da non mostrare mai)',
};

const NEW_SKILL_TEMPLATE = `---
label: Nuova skill
description: a cosa serve, in una riga
formats: reel, story
uses_model: false
default_seconds: 10
---
## Struttura
1. HOOK (2s): ...
2. DETTAGLIO (3s): macro dalla foto reale (keyframe_mode original_photo, end_on_product true).
3. CHIUSURA (2s): testo con invito al DM.

## Fotogramma
(note extra per le immagini, in inglese)

## Movimento
(note extra per l'animazione, in inglese)

## Testi
(note extra per caption e testi a schermo)
`;

async function readError(res: Response) {
  try {
    const data = await res.json();
    return data.error || `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}

export default function SkillsPage() {
  const [items, setItems] = useState<SkillItem[]>([]);
  const [base, setBase] = useState<RawSkill[]>([]);
  const [open, setOpen] = useState<{ id: string; base: boolean } | null>(null);
  const [text, setText] = useState('');
  const [current, setCurrent] = useState<RawSkill | null>(null);
  const [newId, setNewId] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/skills`, { cache: 'no-store' });
      if (!res.ok) throw new Error(await readError(res));
      const data = await res.json();
      setItems(data.items || []);
      setBase((data.base || []).filter(Boolean));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openSkill = async (id: string, isBase: boolean) => {
    setMessage('');
    setError('');
    const res = await fetch(`${API_URL}/skills/${id}?base=${isBase}`, { cache: 'no-store' });
    if (!res.ok) {
      setError(await readError(res));
      return;
    }
    const data: RawSkill = await res.json();
    setOpen({ id, base: isBase });
    setCurrent(data);
    setText(data.text);
    setTimeout(() => document.getElementById('sk-editor')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  const save = async () => {
    if (!open) return;
    setMessage('');
    setError('');
    const res = await fetch(`${API_URL}/skills/${open.id}?base=${open.base}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) {
      setError(await readError(res));
      return;
    }
    setCurrent(await res.json());
    setMessage('Salvata ✓ — dal prossimo video l’app usa questa versione.');
    load();
  };

  const resetSkill = async () => {
    if (!open || !current?.has_original) return;
    if (!window.confirm('Torno alla versione originale? Le tue modifiche a questa skill verranno cancellate.')) return;
    const res = await fetch(`${API_URL}/skills/${open.id}?base=${open.base}`, { method: 'DELETE' });
    if (!res.ok) {
      setError(await readError(res));
      return;
    }
    const data = await res.json();
    setCurrent(data);
    setText(data.text || '');
    setMessage('Ripristinata la versione originale.');
    load();
  };

  const createSkill = () => {
    const id = newId.trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '');
    if (!id) {
      setError('Scrivi un nome per la nuova skill, es. saldi-inverno');
      return;
    }
    setOpen({ id, base: false });
    setCurrent(null);
    setText(NEW_SKILL_TEMPLATE);
    setMessage('Nuova skill: modifica il testo e premi Salva.');
    setNewId('');
    setTimeout(() => document.getElementById('sk-editor')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  return (
    <div className="rs-page">
      <header className="app-header sticky top-0 z-50">
        <div className="rs-header">
          <a href="/reel" className="rs-back">← Reel Studio</a>
          <div className="rs-brand">
            <span className="rs-brand-title">Skill</span>
            <span className="rs-brand-sub">ricette dei contenuti</span>
          </div>
          <span />
        </div>
      </header>

      <main className="rs-main">
        <section className="card rs-card">
          <div className="label-eyebrow">Come funzionano</div>
          <p className="rs-muted">
            Ogni skill è una ricetta che il regista AI segue alla lettera: scaletta delle inquadrature, note per le
            immagini, per il movimento e per i testi. Cambi il testo, salvi, e dal prossimo video l’app usa la nuova
            versione. Puoi sempre tornare all’originale.
          </p>
        </section>

        {error && <div className="rs-error">{error}</div>}

        <section className="rs-history">
          <div className="rs-section-title">Ricette</div>
          <div className="sk-grid">
            {items.map((item) => (
              <button key={item.id} type="button" className={`rs-recipe ${open?.id === item.id && !open.base ? 'rs-recipe-on' : ''}`} onClick={() => openSkill(item.id, false)}>
                <span className="rs-recipe-title">/{item.id}</span>
                <span className="rs-recipe-label">{item.label}</span>
                <span className="rs-recipe-desc">{item.description}</span>
                <span className="sk-tags">
                  {item.formats.join(' · ')}
                  {item.uses_model ? ' · modella' : ''}
                  {item.source === 'modificata' ? ' · ✎ modificata' : ''}
                </span>
              </button>
            ))}
          </div>
          <div className="sk-new">
            <input className="rs-input" placeholder="nome nuova skill, es. saldi-inverno" value={newId} onChange={(e) => setNewId(e.target.value)} />
            <button type="button" className="btn-secondary rs-small-btn" onClick={createSkill}>+ Nuova skill</button>
          </div>
        </section>

        <section className="rs-history">
          <div className="rs-section-title">Basi comuni</div>
          <p className="rs-muted rs-small">Valgono per tutte le ricette. Le parole tra graffe, es. {'{scene}'}, le riempie l’app: non cancellarle.</p>
          <div className="sk-grid">
            {base.map((item) => (
              <button key={item.id} type="button" className={`rs-recipe ${open?.id === item.id && open.base ? 'rs-recipe-on' : ''}`} onClick={() => openSkill(item.id, true)}>
                <span className="rs-recipe-label">{BASE_LABELS[item.id] || item.id}</span>
                <span className="sk-tags">{item.source === 'modificata' ? '✎ modificata' : 'originale'}</span>
              </button>
            ))}
          </div>
        </section>

        {open && (
          <section id="sk-editor" className="card rs-card">
            <div className="rs-reel-head">
              <div>
                <div className="label-eyebrow">{open.base ? 'Base comune' : 'Ricetta'} · {current?.source || 'nuova'}</div>
                <h1 className="rs-h1">{open.base ? BASE_LABELS[open.id] || open.id : `/${open.id}`}</h1>
              </div>
            </div>
            <textarea className="sk-editor" value={text} onChange={(e) => setText(e.target.value)} spellCheck={false} />
            {message && <div className="rs-banner">{message}</div>}
            <div className="rs-actions">
              <button type="button" className="btn-mission rs-small-btn" onClick={save}>Salva</button>
              {current?.source === 'modificata' && current.has_original && (
                <button type="button" className="btn-secondary rs-small-btn" onClick={resetSkill}>Ripristina originale</button>
              )}
              <button type="button" className="btn-secondary rs-small-btn" onClick={() => { setOpen(null); setMessage(''); }}>Chiudi</button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
