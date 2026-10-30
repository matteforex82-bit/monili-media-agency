'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const ICONS = {
  nuovo: <path d="M12 5v14M5 12h14" />,
  pezzi: (
    <>
      <rect x="4" y="4" width="7" height="7" />
      <rect x="13" y="4" width="7" height="7" />
      <rect x="4" y="13" width="7" height="7" />
      <rect x="13" y="13" width="7" height="7" />
    </>
  ),
  reel: (
    <>
      <rect x="6" y="3" width="12" height="18" rx="2" />
      <path d="M10.5 9.5v5l4-2.5z" />
    </>
  ),
  altro: (
    <>
      <circle cx="6" cy="12" r="1.2" />
      <circle cx="12" cy="12" r="1.2" />
      <circle cx="18" cy="12" r="1.2" />
    </>
  ),
};

const ITEMS: Array<{ href: string; label: string; icon: keyof typeof ICONS; match: (path: string) => boolean }> = [
  { href: '/', label: 'Nuovo pezzo', icon: 'nuovo', match: (p) => p === '/' },
  { href: '/pezzi', label: 'Pezzi', icon: 'pezzi', match: (p) => p.startsWith('/pezzi') },
  { href: '/reel', label: 'Reel', icon: 'reel', match: (p) => p.startsWith('/reel') },
  { href: '/altro', label: 'Altro', icon: 'altro', match: (p) => ['/altro', '/skills', '/risultati'].some((base) => p.startsWith(base)) },
];

// Stessa barra su tutte le pagine: in basso sul telefono, colonna a sinistra sul computer.
export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname() || '/';
  return (
    <div className="shell">
      <nav className="shell-nav" aria-label="Studio">
        <div className="shell-brand">
          <strong>I Monili</strong>
          <span>Studio</span>
        </div>
        {ITEMS.map((item) => (
          <Link key={item.href} href={item.href} className="nav-item" aria-current={item.match(pathname) ? 'page' : undefined}>
            <svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[item.icon]}</svg>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
      <main className="shell-main">{children}</main>
    </div>
  );
}
