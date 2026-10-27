# Piano — Sito Vetrina I Monili Ravenna

> Stato: **bozza da approvare** · Creato il 27/10/2026 · Aggiornato il 27/10/2026 dopo il ritrovamento del progetto "Ecosistema Monili"
> Obiettivo: **riprendere** il sito vetrina già iniziato (frontend + backend), metterlo al sicuro, ridisegnare il frontend con Claude Design e portarlo online collegato allo Studio AI.

---

## 1. Cosa c'è davvero oggi (stato verificato)

Il sito vetrina **esiste**, frontend e backend. Dal 27/10/2026 è al sicuro su GitHub nel repo privato **[`monili-vetrina`](https://github.com/matteforex82-bit/monili-vetrina)** (Fase 0 completata).

### 1.1 I due pezzi dell'ecosistema

| Pezzo | Dove | Cosa fa |
|---|---|---|
| **Studio AI** (mittente) | Questo repo `monili-media-agency` su GitHub (copia locale: `Desktop\PROGETTI AI\monili-deploy-temp`) | Genera contenuti e foto, prepara la `product_fiche`, la invia con "Pubblica sul sito vetrina" |
| **Sito vetrina** (ricevente) | Repo `monili-vetrina` → `apps/web` (copia locale: `C:\Users\matte\Desktop\PROGETTI AI\Ecosistema Monili`) | Riceve le schede, admin review, pagine pubbliche |

### 1.2 Il sito vetrina: `Ecosistema Monili\apps\web`

- **Stack**: Next.js 16.2.4 (App Router), React 19.2.4, `pg`, `@vercel/blob`
- **Dati** (`src/lib/persistence-driver.ts`):
  - schede: `PRODUCT_STORE_DRIVER` = `json-file` (`data/products.json`) oppure `postgres` → in `.env.local` è **postgres (Neon)**
  - immagini: `IMAGE_STORAGE_DRIVER` = `local-public` (`public/media`) oppure `vercel-blob` → in `.env.local` è **vercel-blob**
  - log eventi: `data/ops-events.ndjson`, backup in `data/backups/`
- **API**
  - `POST /api/ingest/internal-webapp`: riceve le schede (header `x-admin-token`, controllo in `src/lib/admin-auth.ts`). Accetta `product_fiche` (modalità `product-fiche-v1`) e un adattatore legacy `buildProductFicheFromMissionPayload`
  - `GET/POST /api/products`, `GET/PATCH /api/products/[id]` (cambio `publicationStatus`, incluso `published`)
  - `POST /api/admin/login`, `/api/admin/logout`, `/api/admin/ops/events`
  - `/api/media/reference/[...path]`
- **Pagine admin**: `/admin/login`, `/admin/review` (`src/components/admin-review-client.tsx`), `/admin/ops`
- **Pagine pubbliche**: `/`, `/collezioni`, `/pezzi-unici`, `/instagram`, `/outfit-della-settimana`, `/laboratorio`, `/chi-siamo`, `/contatti`, `/p/[slug]`, `sitemap.ts`. Mostrano solo i prodotti `published`
- **Logica scheda** (`src/lib/`): `product-fiche.ts`, `product-fiche-store.ts`, `product-fiche-validation.ts`, `internal-mission-adapter.ts`, `ingest-image-archive.ts`, `auto-copy-humanizer.ts`, `publish-readiness.ts`
- **Script**: `scripts/ops-report.mjs`, `ops-archive-by-run.mjs`, `ops-clean-nightly.mjs`
- **Vercel**: `apps/web/.vercel/project.json` → progetto **`web`** (nessun `vercel.json`)
- **Variabili d'ambiente** (solo nomi): `ADMIN_API_TOKEN`, `ADMIN_DASH_USER`, `ADMIN_DASH_PASSWORD`, `ADMIN_SESSION_SECRET`, `BLOB_READ_WRITE_TOKEN`, `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `IMAGE_STORAGE_DRIVER`, `NEON_PROJECT_ID`, `NEXT_PUBLIC_SITE_URL`, `PG*`, `POSTGRES_*`, `PRODUCT_STORE_DRIVER`, `VERCEL_OIDC_TOKEN`

### 1.3 Materiale di design già esistente (in `Ecosistema Monili\reference\`)
- `showcase-wireframe-claude-design/`: **wireframe già fatti con Claude Design**
- `hi fi sito/`: versione hi-fi del sito
- `humanizer-skill/`, `internal-web-app-original/` (copia dello Studio), `tmp-outfit-import/`
- In `docs/`: `agents`, `project-memory` (changelog, current-state, integrations), `superpowers`

### 1.4 ⚠️ Problemi seri da sapere subito

1. ~~**Il sito non ha nessun backup.**~~ ✅ Risolto il 27/10/2026: push su `monili-vetrina`, `master` = `80ebde9`, identico al PC.
2. ~~**Git è collegato al repository sbagliato.**~~ ✅ Risolto: il remote `origin` di `Ecosistema Monili` ora è `monili-vetrina`; `monili-media-agency` non è stato toccato.
3. **Il dominio Vercel è stato preso da un altro progetto.** Il progetto Vercel del sito si chiama `web`, come quello di Alfred/Jarvis. Molto probabilmente un deploy di Alfred è finito nello stesso progetto e ha sostituito la vetrina: per questo `web-five-theta-58.vercel.app` oggi mostra Alfred e `/admin/review` dà 404. Va verificato nella dashboard Vercel.
4. **Lo Studio punta all'indirizzo sbagliato.** La vetrina riceve su `/api/ingest/internal-webapp`, ma `SHOWCASE_INGEST_URL` nello Studio non è configurata da nessuna parte. I due token devono coincidere: `SHOWCASE_ADMIN_TOKEN` (Studio) = `ADMIN_API_TOKEN` (vetrina).
5. ~~**Modifiche non salvate**~~ ✅ Salvate nel commit `80ebde9`. Resta solo `.claude/settings.local.json` (locale, voluto).
6. **File da togliere dal repo più avanti** (Fase 3, nessun segreto dentro): `.claude/settings.local.json` del primo commit, `apps/web/data/backups/*.json`, `apps/web/data/ops-events.ndjson`. Sono già in `.gitignore` ma ancora tracciati.

### 1.5 Problemi nello Studio (questo repo)
- Il link "review" in `frontend/src/components/ResultsPanel.tsx` ha come fallback `https://web-five-theta-58.vercel.app/admin/review` (oggi è Alfred, 404)
- Bug visibile: `` `r`n `` letterale nell'hero di `frontend/src/app/page.tsx` (~riga 663)
- Commenti con caratteri corrotti in `frontend/src/app/globals.css`
- Il branch `claude/determined-knuth-zp63a6` ha **9 commit non uniti** (Reel Studio, skills, test) che toccano gli stessi file del frontend: va unito o archiviato prima di lavorarci

### 1.6 Altre cartelle "Monili" sul PC (da fare ordine, non urgenti)
`Desktop\PROGETTI AI\`: `app monili post` (+ `- Copia`), `INSTAGRMA MONILI`, `NUOVA APP PER MONILI RAVENNA` · `Desktop\I MONILI BUROCRAZIA` · `OneDrive\Desktop\Monili Dash`, `OneDrive\Desktop\Sito Monili` · `C:\Users\matte\MoniliStorage` (storage locale dello Studio).
`OneDrive\Desktop\Sito Monili` verificata: **non** è un'altra versione del sito, è un archivio foto/logo/vecchio tema Shopify (nov 2025). Utile solo per il **logo** del Design System.

---

## 2. Il contratto tra Studio e vetrina (già implementato da entrambi i lati)

```http
POST https://<dominio-vetrina>/api/ingest/internal-webapp
Content-Type: application/json
x-admin-token: <SHOWCASE_ADMIN_TOKEN = ADMIN_API_TOKEN>
```

```jsonc
{
  "run_id": "20261027_1830",
  "product_fiche": {
    "id": "orecchini-cerchio-dorati-20261027-1830",
    "title": "Orecchini a cerchio dorati",
    "category": "gioielli | bijoux | accessori | abbigliamento",
    "state": "disp | unique | req | sold",
    "price": null,
    "currency": "EUR",
    "summary": "…", "story": "…", "materials": ["argento 925"],
    "images": [{ "src": "data:image/jpeg;base64,…", "alt": "…" }],   // max 8, 1200×1500
    "availability": { "inStore": true, "reservable": true, "shipsFrom": "Ravenna" },
    "availableAt": ["via-cavour-17"],          // via-cavour-17 | via-cavour-21
    "whatsappPreset": "prodotto | negozio | richiesta | simili",
    "relatedTags": ["imoniliravenna"],
    "seo": { "title": "…", "description": "…" },
    "updatedAt": "ISO-8601",
    "publicationStatus": "draft",
    "sourceSystem": "internal-web-app",
    "sourceRunId": "20261027_1830"
  }
}
```

Tutto arriva come `draft`: niente va online senza un "Approva" in `/admin/review`. Va bene così.

**Rischio tecnico da verificare**: le funzioni Vercel accettano body di **max ~4,5 MB**. Lo Studio può inviare fino a 8 foto in base64 da ~650 KB (~7 MB) → l'ingest fallirebbe proprio sui prodotti con più foto. Rimedio semplice: max 4 foto per invio in `api/server.py` (`selected_images[:4]`).

---

## 3. Decisioni di architettura

| Tema | Scelta | Note |
|---|---|---|
| Stack vetrina | **Si tiene quello esistente**: Next.js 16 + Neon Postgres + Vercel Blob | È già la scelta giusta: non si riscrive niente |
| Repository | **Nuovo repo privato `monili-vetrina`** per `Ecosistema Monili` | La sua storia git non c'entra con lo Studio: mescolarle crea solo guai. Lo Studio resta in `monili-media-agency` |
| Hosting | **Nuovo progetto Vercel `monili-vetrina`** (non più `web`) + dominio personalizzato | Nome univoco: non deve più succedere che Alfred lo sovrascriva |
| Pagamenti | Nessun checkout, prenotazione via WhatsApp | Coerente con il tono del brand |

---

## 4. Frontend: prima Claude Design, poi le skill

Scelta di Matteo: il frontend va rifatto con **Claude Design** e con le **migliori skill disponibili**.
Regola: **prima si disegna e si approva, poi si scrive codice.**
Buona notizia: c'è già una base, cioè `reference/showcase-wireframe-claude-design` e `reference/hi fi sito`. **Si parte da lì, non da un foglio bianco.**

### 4.1 Design System "I Monili Ravenna" (tipo *Design System* di Claude)
Oggi non c'è nessun design system salvato nell'account: lo creiamo e lo impostiamo come **predefinito**.
- **README del brand**: tono e regole visive da `CLAUDE.md` (caldo, complice, mai formale; foto luminose, niente filtri esagerati)
- **Token**: neutri caldi, bianco ottico, terracotta `#c8593a`, oro `#c79849`; Instrument Serif + Manrope; spaziature, raggi, ombre. Si confrontano con quelli già usati in `apps/web` e nell'hi-fi
- **Componenti**: `ProductCard` 4:5, `BadgeStato` (disponibile · pezzo unico · su richiesta · già adottato), `BottoneWhatsApp`, filtri collezione, `CardNegozio` (via Cavour 17 e 21), header, footer, empty state
- **Asset**: logo e favicon (servono i file originali)

### 4.2 Tavole delle pagine (tipo *Design* di Claude)
In mobile (390 px) e desktop (1440 px), partendo dai wireframe esistenti:
- `/` · `/collezioni` · `/pezzi-unici` · `/p/[slug]` (una tavola per ognuno dei 4 stati) · `/outfit-della-settimana` · `/instagram` · `/laboratorio` · `/chi-siamo` · `/contatti`
- `/admin/review` (deve essere comodissima da iPhone: è lì che approvi ogni giorno)
- Contenuti **veri**: 6–8 prodotti reali dalle foto `07_SHOWCASE` dello Studio
- **Massimo 2 giri di revisione per pagina.** Il rischio vero è restare settimane a limare i design invece di andare online

Prima di disegnare, decidiamo se servono **tutte** queste pagine al lancio. Il mio consiglio: lancia con Home, Collezioni, Pezzi unici, Scheda prodotto e Contatti; le altre arrivano dopo.

### 4.3 Dal design al codice
- I token del Design System diventano le CSS variables / il tema di `apps/web`: una sola fonte
- I componenti del Design System diventano componenti React con lo stesso nome
- **Si cambia solo la parte visiva.** API, store, validazione e ingest non si toccano durante il restyling
- Dopo ogni pagina: screenshot mobile e desktop dell'app vera, confrontati con la tavola approvata

### 4.4 Skill da usare e quando

| Skill | Quando | A cosa serve |
|---|---|---|
| **Design System** (tipo artifact) | Fase 2 | Design system del brand (4.1) |
| **Design** (tipo artifact, "Claude Design") | Fase 2 | Tavole delle pagine (4.2) |
| `artifact-design` | Fase 2 | Regole base per design curati, non generici |
| `anthropic-skills:artifact-emulator` | Fase 2 | Vedere i design come li vedrai tu prima di approvarli |
| `instagram-agent:ig-human` | Fasi 2 e 4 | Testi del sito e messaggi WhatsApp che non sanno di AI |
| `run` | Fase 4 | Avviare la vetrina e fare gli screenshot da confrontare |
| `code-review` · `simplify` | Fine di ogni fase | Bug e pulizia |
| `security-review` | Prima della messa online | Ingest con token, login admin, upload immagini |
| `frontend-design` (plugin ufficiale Anthropic) | Fase 4 | **Non installato oggi**: verificare che sia nel marketplace e installarlo prima della Fase 4 |

---

## 5. Backend: cosa c'è e cosa va controllato

Il backend **esiste**: non si costruisce, si **verifica e si rende affidabile**.

| Da controllare | Perché |
|---|---|
| Ingest end-to-end Studio → `/api/ingest/internal-webapp` → bozza in `/admin/review` | Non sappiamo se ha mai funzionato online |
| Limite 4,5 MB del body su Vercel (sezione 2) | Prodotti con più foto falliscono |
| Reinvio dello stesso prodotto già pubblicato | Non deve sovrascrivere automaticamente una scheda online |
| `data/products.json` e `data/ops-events.ndjson` su Vercel | Il disco Vercel non è persistente: in produzione **tutto** deve stare su Postgres/Blob, log compresi |
| Confronto del token a tempo costante, limite di dimensione, limite di richieste | Sicurezza minima dell'ingest |
| Testi AI (`story`, `summary`) mostrati come testo semplice, mai come HTML | Evitare HTML/script iniettati |
| Test di contratto: una scheda vera generata dallo Studio, salvata come fixture, che deve passare `product-fiche-validation.ts` | Se uno dei due lati cambia il formato, ce ne accorgiamo subito |

---

## 6. Fasi di lavoro

### Fase 0 — Mettere al sicuro ✅ completata il 27/10/2026
- [x] Audit sicurezza: nessun segreto nella storia, nessun file > 50 MB (~15 MB in tutto)
- [x] Modifiche aperte salvate + `Avvia Agenzia Monili.bat` aggiunto (commit `80ebde9`), `.gitignore` aggiornato
- [x] Repo privato [`matteforex82-bit/monili-vetrina`](https://github.com/matteforex82-bit/monili-vetrina) creato
- [x] Remote cambiato e push di `master` senza force: GitHub = PC (`80ebde9`), verificato anche dal cloud
- [x] `OneDrive\Desktop\Sito Monili` controllata: solo archivio foto/asset, nessun codice

### Fase 1 — Pulizia e collegamento (½ giornata)
- [ ] Studio: unire o archiviare il branch `claude/determined-knuth-zp63a6`
- [ ] Studio: togliere `` `r`n `` da `page.tsx`, ripulire i commenti di `globals.css`
- [ ] Studio: togliere il fallback `web-five-theta-58` da `ResultsPanel.tsx` (se manca la variabile, il link si nasconde)
- [ ] Studio: aggiungere `SHOWCASE_INGEST_URL`, `SHOWCASE_ADMIN_TOKEN`, `NEXT_PUBLIC_SHOWCASE_REVIEW_URL` a `.env.example` e `render.yaml` (`sync: false`)
- [ ] Studio: max 4 foto per invio (`api/server.py`)
- [ ] Prova in locale: Studio (porta 3000/8000) → vetrina (porta 3100) → bozza visibile in `/admin/review`

### Fase 1b — Vetrina funzionante online (repo `monili-vetrina`)
Problemi bloccanti 🔴, risolti il 27/10/2026 sul branch `claude/blissful-darwin-7tnrfd` (commit `71cd6cc`) e verificati con il sito avviato in produzione:
- [x] "Approva" ora fa comparire subito il prodotto su home, collezioni, scheda e sitemap (prima serviva un nuovo deploy). Verificato: prima 0, dopo 1
- [x] Admin chiuso in produzione se mancano credenziali o se sono deboli (`1234` rifiutato). Verificato: 401 / 503 / rinvio al login
- [x] Niente prodotti di test online: il database vuoto non si riempie più da solo; telefono da `NEXT_PUBLIC_SHOP_PHONE`; il deploy di produzione si ferma se mancano URL, telefono o storage di produzione
- [ ] Unire il branch in `master` di `monili-vetrina` (poi `git pull` sul PC)
- [ ] Database di produzione **pulito** (nuovo database o branch Neon): quello attuale potrebbe contenere le schede di test

Punti 🟠, risolti il 27/10/2026 e provati (anche contro un Postgres 16 reale):
- [x] Limite 4,5 MB: lo Studio invia max 4 foto e blocca prima dell'invio le schede oltre 4,2 MB (`monili-media-agency` commit `8c414d9`)
- [x] `/api/products` pubblica: solo prodotti pubblicati, senza storico modifiche; l'admin vede tutto (`monili-vetrina` commit `7f438be`)
- [x] Registro eventi `/admin/ops` salvato su Postgres (tabella `ops_events`) quando il sito usa Neon
- [x] Studio: variabili `SHOWCASE_INGEST_URL`, `SHOWCASE_ADMIN_TOKEN`, `SHOWCASE_MAX_IMAGES`, `NEXT_PUBLIC_SHOWCASE_REVIEW_URL` documentate; link ad Alfred rimosso (il link review compare solo se configurato)
- [x] Prezzo inserito nello Studio (o "Su richiesta"); il sito mostra i centesimi (`22,50 €`)

Restano da fare al momento del deploy:
- [ ] Unire i branch `claude/blissful-darwin-7tnrfd` in `master` (vetrina e Studio), poi `git pull` sul PC
- [ ] Database di produzione pulito (Neon nuovo o branch Neon)
- [ ] Compilare le variabili su Vercel e nello Studio con gli stessi token

### Fase 2 — Design con Claude Design (1–2 giornate)
- [ ] Rileggere i wireframe in `reference/showcase-wireframe-claude-design` e `reference/hi fi sito`
- [ ] Decidere le pagine del lancio (4.2)
- [ ] Design System "I Monili Ravenna" impostato come predefinito (4.1)
- [ ] Tavole mobile + desktop (4.2), testi passati con `ig-human`
- [ ] **Approvazione di Matteo**, max 2 giri per pagina

### Fase 3 — Backend affidabile (1 giornata)
- [ ] Tutti i punti della sezione 5
- [ ] In produzione `PRODUCT_STORE_DRIVER=postgres` e `IMAGE_STORAGE_DRIVER=vercel-blob`, log su Postgres

### Fase 4 — Restyling frontend (2–3 giornate)
- [ ] Token e componenti dal Design System in `apps/web`
- [ ] Pagine del lancio fedeli alle tavole, screenshot di confronto con `run`
- [ ] `/admin/review` comoda da iPhone
- [ ] SEO locale: metadata, Open Graph, JSON-LD `Product` + `LocalBusiness` (×2 negozi), `sitemap`, Lighthouse mobile ≥ 90
- [ ] `code-review` + `security-review`

### Fase 5 — Messa online (½ giornata)
- [ ] Nuovo progetto Vercel `monili-vetrina` collegato al nuovo repo, root `apps/web`
- [ ] Variabili d'ambiente su Vercel (Neon, Blob, `ADMIN_*`), `NEXT_PUBLIC_SITE_URL` = dominio vero (oggi punta a `http://127.0.0.1:3100`)
- [ ] Dominio personalizzato
- [ ] Studio: `SHOWCASE_INGEST_URL=https://<dominio>/api/ingest/internal-webapp`, `NEXT_PUBLIC_SHOWCASE_REVIEW_URL=https://<dominio>/admin/review`, stesso token dei due lati
- [ ] Link nel profilo Google Business e nella bio Instagram

**Totale stimato: 6–8 giornate.** Meno di prima, perché il backend e buona parte del sito esistono già.

---

## 7. Criteri di "fatto"

- Il codice della vetrina è su GitHub, in un repo suo
- Dallo Studio premo "Pubblica sul sito vetrina" e in meno di 1 minuto la bozza compare in `/admin/review`
- Con "Approva" il prodotto è online, senza rideploy
- Una scheda si apre su iPhone in meno di 2 secondi e il bottone WhatsApp apre il messaggio giusto
- Un prodotto venduto resta indicizzato e propone "simili"
- Le pagine online corrispondono alle tavole approvate in Claude Design
- Nessun link nello Studio punta più a domini che non sono nostri

---

## 8. Domande aperte (da decidere Matteo)

1. ~~Nuovo repo `monili-vetrina`~~ ✅ fatto
2. **Vercel**: nella dashboard il progetto `web` oggi è Alfred? Vuoi tenere Alfred lì e creare `monili-vetrina` da zero? (consiglio: sì)
3. **Branch `determined-knuth`** dello Studio: unire o archiviare?
4. **Pagine del lancio**: va bene partire con Home, Collezioni, Pezzi unici, Scheda prodotto e Contatti?
5. **Dominio**: ne hai già uno?
6. **Prezzi**: li mostriamo? Oggi lo Studio manda sempre `price: null`
7. **Orari e numero WhatsApp** veri dei due negozi di via Cavour
8. **Logo**: file originali (SVG o PNG ad alta risoluzione)
9. **Plugin `frontend-design`**: lo installiamo prima della Fase 4?
