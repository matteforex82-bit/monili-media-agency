'use client';

import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { API_URL } from '@/lib/apiUrl';

// Every call to the Studio API carries the PIN session cookie (backend:
// studio_auth.py). Patched once, at import, so the pages' own fetch calls need
// no change; a 401 tells this screen to ask for the PIN again.
type PatchedWindow = Window & { __studioFetchPatched?: boolean };
if (typeof window !== 'undefined' && !(window as PatchedWindow).__studioFetchPatched) {
  (window as PatchedWindow).__studioFetchPatched = true;
  const original = window.fetch.bind(window);
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
    if (!url.startsWith(API_URL)) return original(input, init);
    const res = await original(input, { ...init, credentials: 'include' });
    if (res.status === 401 && !url.startsWith(`${API_URL}/auth/`)) {
      window.dispatchEvent(new Event('studio-locked'));
    }
    return res;
  };
}

type Gate = 'checking' | 'open' | 'setup' | 'login' | 'setup-elsewhere';

export default function StudioAccess({ children }: { children: React.ReactNode }) {
  const [gate, setGate] = useState<Gate>('checking');
  const [pin, setPin] = useState('');
  const [again, setAgain] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const check = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/auth/status`, { cache: 'no-store' });
      // A backend started before the PIN existed has no /auth: it stays open until restarted.
      if (res.status === 404) {
        setGate('open');
        return;
      }
      const data = await res.json();
      if (data.logged_in) setGate('open');
      else if (!data.configured) setGate(data.can_setup ? 'setup' : 'setup-elsewhere');
      else setGate('login');
    } catch {
      // Backend off: the pages already say "accendi lo Studio sul PC".
      setGate('open');
    }
  }, []);

  useEffect(() => {
    check();
    const locked = () => check();
    window.addEventListener('studio-locked', locked);
    return () => window.removeEventListener('studio-locked', locked);
  }, [check]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    if (gate === 'setup' && pin !== again) {
      setError('I due PIN non sono uguali.');
      return;
    }
    setBusy(true);
    try {
      const res = await fetch(`${API_URL}/auth/${gate === 'setup' ? 'setup' : 'login'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error || 'Non sono riuscito a entrare. Riprova.');
        return;
      }
      setPin('');
      setAgain('');
      // Full reload: the page that was locked reads its data again, now with the session.
      window.location.reload();
    } catch {
      setError('Lo Studio sul PC non risponde. Controlla che sia acceso e riprova.');
    } finally {
      setBusy(false);
    }
  }

  if (gate === 'open') return <>{children}</>;
  if (gate === 'checking') return <div className="access" aria-busy="true" />;

  return (
    <main className="access">
      <div className="access-card">
        <p className="access-brand">I Monili · Studio</p>
        {gate === 'setup-elsewhere' ? (
          <>
            <h1>Studio protetto</h1>
            <p>
              Manca ancora il PIN. Si sceglie una volta sola dal PC dove gira lo Studio: aprilo lì, scegli il PIN e poi
              torna qui.
            </p>
          </>
        ) : (
          <form onSubmit={submit}>
            <h1>{gate === 'setup' ? 'Scegli il PIN dello Studio' : 'Inserisci il PIN'}</h1>
            <p>
              {gate === 'setup'
                ? 'Da 6 a 12 cifre. Te lo chiederà ogni telefono o computer la prima volta, poi se lo ricorda per 3 mesi.'
                : 'Lo Studio è protetto: senza PIN nessuno vede i pezzi né pubblica sul sito.'}
            </p>
            <label>
              PIN
              <input
                type="password"
                inputMode="numeric"
                pattern="[0-9]*"
                autoComplete={gate === 'setup' ? 'new-password' : 'current-password'}
                minLength={6}
                maxLength={12}
                required
                autoFocus
                value={pin}
                onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
              />
            </label>
            {gate === 'setup' && (
              <label>
                Ripeti il PIN
                <input
                  type="password"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  autoComplete="new-password"
                  minLength={6}
                  maxLength={12}
                  required
                  value={again}
                  onChange={(e) => setAgain(e.target.value.replace(/\D/g, ''))}
                />
              </label>
            )}
            {error && <div className="notice error" role="alert">{error}</div>}
            <button type="submit" className="btn-mission" disabled={busy}>
              {busy ? 'Un attimo...' : gate === 'setup' ? 'Salva il PIN' : 'Entra'}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
