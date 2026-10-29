# Fase 5 — Messa online del sito vetrina (passo per passo)

Decisioni di Matteo (29/10/2026): progetto Vercel **nuovo e separato** da quello di Alfred; **database Neon nuovo e pulito** (quello attuale ha solo prodotti venduti: resta come archivio); dominio ancora da scegliere.

## Cosa fa Claude, cosa fa Matteo

| Passo | Chi |
|---|---|
| Generare password, token e segreto admin (valori lunghi, casuali) | Claude, li dà a Matteo una sola volta |
| Creare il progetto Vercel (account di Matteo) | Matteo clicca, Claude guida |
| Creare database Neon e archivio Blob dal pannello Vercel (Storage) | Matteo clicca |
| Incollare le variabili d'ambiente | Matteo incolla, Claude prepara l'elenco |
| Comprare il dominio | **Solo Matteo** (pagamento) |
| Collegare il dominio e impostare `NEXT_PUBLIC_SITE_URL` | Matteo + Claude |
| Impostare le variabili nello Studio e provare l'invio | Claude |
| Lighthouse sul sito online (obiettivo performance ≥ 90) | Claude |

## 1. Progetto Vercel

1. vercel.com → Add New → Project → repo `matteforex82-bit/monili-vetrina`.
2. **Root Directory: `apps/web`**. Framework: Next.js (rilevato da solo).
3. Nome progetto: `monili-vetrina`. Non collegarlo al progetto di Alfred.

## 2. Storage (dal pannello del progetto, scheda Storage)

- **Neon (Postgres)**: crea un database nuovo → Vercel aggiunge `DATABASE_URL`.
- **Blob**: crea un archivio → Vercel aggiunge `BLOB_READ_WRITE_TOKEN`.

## 3. Variabili d'ambiente (Production)

| Nome | Valore |
|---|---|
| `NEXT_PUBLIC_SITE_URL` | l'indirizzo vero, con `https://` (provvisorio: quello `.vercel.app`) |
| `PRODUCT_STORE_DRIVER` | `postgres` |
| `IMAGE_STORAGE_DRIVER` | `vercel-blob` |
| `DATABASE_URL`, `BLOB_READ_WRITE_TOKEN` | messi da Vercel al passo 2 |
| `POSTGRES_SEED_SOURCE` | **vuoto** (un database vuoto resta vuoto) |
| `ADMIN_DASH_USER` | `admin` (o un nome a scelta) |
| `ADMIN_DASH_PASSWORD` | almeno 12 caratteri |
| `ADMIN_SESSION_SECRET` | almeno 24 caratteri |
| `ADMIN_API_TOKEN` | almeno 24 caratteri; stesso valore nello Studio come `SHOWCASE_ADMIN_TOKEN` |

Senza queste il deploy si ferma da solo: è voluto.

## 4. Primo deploy e prova

- Home, `/negozi` e `/admin` aprono; il sito parte senza prodotti (è normale: va riempito).
- `https://<indirizzo>/admin/reels` e `/admin/review` chiedono la password.

## 5. Dominio

- Vercel → Settings → Domains → cerca il nome. Se Vercel non vende il `.it`, comprarlo da un registrar italiano e aggiungere i record che Vercel indica.
- Poi cambiare `NEXT_PUBLIC_SITE_URL` e ripubblicare (sitemap, `robots.txt`, `llms.txt` e dati per Google usano questo indirizzo).

## 6. Studio (file `.env` dello Studio sul PC)

```
SHOWCASE_INGEST_URL=https://<dominio>/api/ingest/internal-webapp
SHOWCASE_REEL_INGEST_URL=https://<dominio>/api/ingest/reel
SHOWCASE_ADMIN_TOKEN=<lo stesso di ADMIN_API_TOKEN>
NEXT_PUBLIC_SHOWCASE_REVIEW_URL=https://<dominio>/admin/review
```

Prova: dallo Studio "Pubblica sul sito vetrina" con un pezzo vero; la bozza deve comparire in `/admin/review` in meno di un minuto.

## 7. Dopo

Link in bio Instagram e Google Business, poi Lighthouse online, poi riempire il sito con i pezzi nuovi (vedi `docs/foto-prodotti.md`).
