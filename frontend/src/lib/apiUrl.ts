// Lo Studio gira solo sul PC (Render dismesso il 30/10/2026): di base il backend locale.
const DEFAULT_API_URL = 'http://localhost:8000';

// Modalità locale (NEXT_PUBLIC_API_PORT, impostata da scripts/start-local.ps1):
// il backend gira sullo stesso PC del frontend, quindi si usa l'indirizzo con
// cui è stata aperta la pagina. Così funziona da localhost, dal Wi-Fi e da
// Tailscale senza riavviare niente.
export function resolveApiUrl(): string {
  const localPort = process.env.NEXT_PUBLIC_API_PORT;
  if (localPort && typeof window !== 'undefined') {
    // Pagina in https (Tailscale Serve, vedi docs/local-mode.md): anche il backend deve essere in https.
    const port = window.location.protocol === 'https:' ? process.env.NEXT_PUBLIC_API_HTTPS_PORT || '8443' : localPort;
    return `${window.location.protocol}//${window.location.hostname}:${port}`;
  }
  return process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;
}

export const API_URL = resolveApiUrl();
