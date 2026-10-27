const DEFAULT_API_URL = 'https://monili-backend.onrender.com';

// Modalità locale (NEXT_PUBLIC_API_PORT, impostata da scripts/start-local.ps1):
// il backend gira sullo stesso PC del frontend, quindi si usa l'indirizzo con
// cui è stata aperta la pagina. Così funziona da localhost, dal Wi-Fi e da
// Tailscale senza riavviare niente.
export function resolveApiUrl(): string {
  const localPort = process.env.NEXT_PUBLIC_API_PORT;
  if (localPort && typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:${localPort}`;
  }
  return process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;
}

export const API_URL = resolveApiUrl();
