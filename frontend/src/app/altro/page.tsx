import Link from 'next/link';

const ITEMS = [
  { href: '/skills', title: 'Skill', text: 'Le regole dei contenuti: donne, cose da non fare, ricette dei Reel.' },
  { href: '/risultati', title: 'Risultati', text: 'I numeri di quello che hai pubblicato.' },
  { href: '/altro/impostazioni', title: 'Impostazioni', text: 'Il motore delle immagini e la verifica del collegamento.' },
];

export default function MorePage() {
  return (
    <div className="page">
      <h1 className="page-title">Altro</h1>
      <p className="page-lead">Quello che non serve ogni giorno.</p>
      <ul className="menu-list">
        {ITEMS.map((item) => (
          <li key={item.href}>
            <Link href={item.href}>
              <strong>{item.title}</strong>
              <span>{item.text}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
