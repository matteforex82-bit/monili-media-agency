import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'I Monili · Studio AI',
  description: 'Crea il kit marketing per i tuoi prodotti in 30 secondi — I Monili Ravenna',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body className="min-h-screen">
        {children}
      </body>
    </html>
  );
}
