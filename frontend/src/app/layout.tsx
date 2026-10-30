import type { Metadata, Viewport } from 'next';
import './globals.css';
import './studio.css';
import AppShell from '@/components/AppShell';

export const metadata: Metadata = {
  title: 'I Monili · Studio',
  description: 'Dalla foto di un pezzo alla scheda per il sito e al Reel — I Monili Ravenna',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body className="min-h-screen">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
