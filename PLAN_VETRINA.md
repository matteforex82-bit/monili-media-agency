# Piano — Sito Vetrina I Monili Ravenna

> Stato: **approvato, in lavorazione** (siamo alla Fase 5, messa online, per la prima prova del weekend) · Creato il 27/10/2026 · Ultimo aggiornamento: 30/10/2026, foto del sito e donne AI decise nello Studio
> **Per ripartire leggi prima la sezione 10.**
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

### 1.5 Problemi nello Studio (questo repo) — ✅ tutti risolti il 27/10/2026
- ~~Fallback `web-five-theta-58` nel link "review" di `ResultsPanel.tsx`~~ ✅ rimosso: il link compare solo se `NEXT_PUBLIC_SHOWCASE_REVIEW_URL` è impostata
- ~~`` `r`n `` letterale nell'hero di `page.tsx`~~ ✅ commit `dc2e34a`
- Commenti con caratteri corrotti in `frontend/src/app/globals.css`: cosmetico, non blocca niente
- ~~Branch `claude/determined-knuth-zp63a6` non unito~~ ✅ Reel Studio unito in `master` (`99cdd3b`)

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
**Deciso il 27/10/2026: 3 pagine al lancio** (dettaglio in "Scelte del 27/10/2026 (2)" nella sezione 6). Mobile (390 px) e desktop (1440 px), partendo dai wireframe esistenti:
- `/` Home "Al bancone" (feed "Appena arrivati" + filtri + striscia Reel + "Vieni a trovarci")
- `/p/[slug]` Scheda pezzo: una tavola per stato (disponibile · pezzo unico · su richiesta · venduto "Questo ha già trovato casa")
- `/negozi` (o `/contatti`) Negozi e contatti
- `/admin/review` solo come ritocco: deve essere comodissima da iPhone
- Contenuti **veri**: 6–8 prodotti reali dalle foto `07_SHOWCASE` dello Studio, prezzi veri
- **Massimo 2 giri di revisione per pagina.** Il rischio vero è restare settimane a limare i design invece di andare online
- Le pagine esistenti non incluse (`/collezioni`, `/pezzi-unici`, `/outfit-della-settimana`, `/instagram`, `/laboratorio`, `/chi-siamo`) si nascondono dal menu e dalla sitemap al lancio, il codice resta

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
| `frontend-design` (plugin ufficiale Anthropic) | Fase 4 | Installato. Alternativa a Impeccable, non insieme |
| **SEO-AEO-GEO Ultimate** (`seo-aeo-geo-ultimate:*`, installato 27/10) | Fasi 2 e 4 | Ingresso `seo-aeo-geo-ultimate:seo`; nello specifico `seo-local`, `seo-schema`, `seo-images`, `seo-geo`, `seo-aeo`, `seo-technical`, `seo-commerce` |
| **AI SEO** (`ai-seo:*`, installato 27/10) | Fase 4 e dopo il lancio | `llms-txt-ai-crawler-access` (llms.txt + robots.txt), `ai-page-audit` sulla scheda pezzo, `ai-seo-audit` e `brand-monitoring-ai-visibility-report` dopo il lancio |

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

### Fase 1 — Pulizia e collegamento ✅ quasi completata
- [x] Studio: branch `claude/determined-knuth-zp63a6` (Reel Studio) unito
- [x] Studio: tolto `` `r`n `` da `page.tsx` (i commenti di `globals.css` restano, cosmetici)
- [x] Studio: tolto il fallback `web-five-theta-58` da `ResultsPanel.tsx`
- [x] Studio: variabili `SHOWCASE_*` documentate
- [x] Studio: max 4 foto per invio
- [ ] Prova in locale sul PC: Studio (porta 3000/8000) → vetrina (porta 3100) → bozza visibile in `/admin/review` (si fa insieme a Matteo, serve il PC)

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
- [x] Branch uniti in `master` il 27/10/2026: Studio `99cdd3b` (con Reel Studio e la protezione del 13/10 recuperata dal PC), vetrina `7f438be`
- [x] `git pull` sul PC in `monili-deploy-temp` e `Ecosistema Monili` (27/10/2026, entrambi fast-forward)
- [ ] Database di produzione pulito (Neon nuovo o branch Neon)
- [ ] Compilare le variabili su Vercel e nello Studio con gli stessi token

### Scelte del 27/10/2026: parti dinamiche e skill
Parti dinamiche scelte da Matteo:
- [ ] **Reel dallo Studio al sito**: il Reel Studio invia video MP4 9:16 + copertina + prodotto collegato alla vetrina (nuovo endpoint di ingest video, file su Vercel Blob). Compaiono nella sala Reel e nella scheda prodotto, senza lavoro manuale
- [ ] **Passaggi e filtri animati**: card → scheda con View Transitions, filtri per pietra con riordino animato, "Aperto ora" dagli orari, "Novità della settimana" automatiche dalla data di pubblicazione
- Regola: un solo momento forte per pagina, tutto il resto discreto; video con copertina e caricamento leggero su telefono; `prefers-reduced-motion` rispettato

Skill (una sola guida principale per volta, per non avere istruzioni in conflitto):
- **Impeccable** (`monili-vetrina/.claude/skills/impeccable`, v4.8.0): guida principale per design, rifinitura e animazioni. Il suo programma di controllo (scaricato al primo uso) non è ancora autorizzato
- **Design** (Anthropic): `design-critique` sulle tavole, `accessibility-review` prima del codice
- **audit-suite**: `web-animation-design` e `make-interfaces-feel-better` come riferimento per i movimenti
- **frontend-design** (Anthropic): alternativa a Impeccable, non insieme
- Verifica sempre nel browser, su telefono e desktop

### Scelte del 27/10/2026 (2): cosa è il sito
Niente e-commerce e niente "collezioni": il negozio lavora a **novità** (Matteo fotografa quello che arriva e lo pubblica). Il sito è una vetrina di brand che fa tre cose che Instagram fa male: farsi trovare (Google **e** risposte AI), dare un link fisso a ogni pezzo da girare su WhatsApp, portare in negozio. La vendita resta su WhatsApp e DM Instagram.

Struttura del lancio, **3 pagine** (approvata):
- **Home "Al bancone"**: titolo editoriale come i post migliori, griglia "Appena arrivati" per data (stile feed), filtri leggeri *Tutto · Bijoux · Accessori · Abbigliamento · Pezzi unici*, striscia Reel, blocco "Vieni a trovarci" (via Cavour 17 e 21, orari, "Aperto ora", mappa, WhatsApp)
- **Scheda pezzo** `/p/[slug]`: foto, storia breve, materiali, **prezzo visibile**, bottone WhatsApp con messaggio già scritto e link al pezzo, "Scrivici in DM su Instagram", "Te lo mettiamo da parte". Venduto: la pagina resta con *"Questo ha già trovato casa. Guarda i simili"*
- **Negozi e contatti**: i due negozi, orari, mappa, telefono, due righe su chi siete
- Rimandate a dopo il lancio: Collezioni, Outfit della settimana, Laboratorio, Chi siamo (pagina a sé), Instagram
- Dopo 6–8 settimane un pezzo esce da "Appena arrivati" e va in archivio (la pagina resta per Google)

**Trovati su Google e dalle AI (SEO + GEO)**, obiettivo dichiarato di Matteo: essere in cima a ogni ricerca pertinente.
- Sul sito: JSON-LD `LocalBusiness` ×2 e `Product` con prezzo e disponibilità, testi che rispondono a domande vere ("dove comprare bijoux in argento a Ravenna"), `robots.txt` che lascia entrare i crawler AI, `llms.txt`, foto con testo alternativo
- Fuori dal sito, che per le AI conta quanto il sito: profilo Google Business completo e recensioni, menzioni su siti locali, stesso nome/indirizzo/telefono ovunque
- Contenuti dello Studio: caption e Reel con le parole che la gente cerca (Instagram è indicizzato da Google)
- Plugin proposti: **SEO-AEO-GEO Ultimate** (lavoro sul sito) e **AI Search Visibility & Brand Mentions** (controllo dopo il lancio: ChatGPT/Gemini/Perplexity ci nominano?). Entrambi community, da installare

**"Venduto" senza lavoro manuale** (canale deciso: **Telegram, bot dedicato**):
- Matteo non vuole segnarlo a mano. Proposta: ogni 2–3 giorni un messaggio a Matteo con le foto dei pezzi online e due bottoni, *Disponibile* / *Venduto*; un tocco e il sito si aggiorna
- Canale: **bot Telegram dedicato** (es. "Monili Vetrina"), separato da Hermes per non mescolare i messaggi del sito con quelli dell'agente. Gratis, bottoni pronti. Il bot parla solo con Matteo (chat ID fisso), mai con i clienti
- Sconsigliato: un bot che risponde da solo ai clienti. La risposta a chi scrive resta di Matteo: è il momento della vendita e il tono "da amica" non si automatizza
- Il messaggio WhatsApp precompilato contiene nome e link del pezzo, così Matteo sa subito di cosa si parla

### Fase 2 — Design con Claude Design (1–2 giornate) ✅ tavole approvate
- [ ] Rileggere i wireframe in `reference/showcase-wireframe-claude-design` e `reference/hi fi sito` (repo `monili-vetrina`)
- [x] Pagine del lancio decise: 3 pagine (4.2)
- [x] Design System v1 creato il 27/10/2026: https://claude.ai/artifact/62dgz9RcfeetzXXfVZpFvq (token "Avorio caldo", stile editoriale del feed Instagram, sala Reel, pietre, 11 componenti)
- [x] Proposta v2 approvata da Matteo ("ok", 27/10/2026 sera), vedi sezione 10
- [x] **Design System v2** pubblicato il 28/10/2026 sullo stesso artifact (versione 5): Outfit, terracotta `#c8593a` + `terracotta-deep` `#9e4128` per il testo, oro `#c79849`, token di movimento, 8 componenti nuovi (SiteHeader, MegaMenu, TileGrid, CtaLink, ArrivalCard, FilterBar, VisitBlock, SoldNotice). Il prezzo del cartellino passa a Cormorant corsivo (Outfit non ha il corsivo). Orari e telefono nelle anteprime sono d'esempio
- [x] ~~Impostarlo come predefinito~~: nel menu dell'artifact di Matteo la voce non esiste (28/10/2026). Basta sceglierlo a mano nei design nuovi; si può "Fissare" nella barra laterale
- [x] Tavole mobile + desktop delle 3 pagine (4.2), 28/10/2026, giro 1: https://claude.ai/artifact/NNmcN1Y1goYwFfZHfDexjP (9 tavole: Home desktop/telefono con filtri funzionanti, Scheda pezzo nei 4 stati + telefono, Negozi desktop/telefono con FAQ per Google e AI). Foto e pezzi veri (outfit della settimana, Studio, foto del negozio); **mancano** e sono segnati `[tra parentesi]`: prezzi, orari, telefono, foto di via Cavour 17, spedizioni, taglie. Solo 6 pezzi veri trovati (un solo bijou: l'anello). I Reel sono copertine d'esempio: non ci sono ancora video
- [x] Giro 1b (28/10/2026): orari e spedizioni veri, tolto lo stato "Su richiesta" (ogni pezzo ha un prezzo)
- [x] Giro 2 dai commenti di Matteo (28/10/2026), da portare nel codice in Fase 4:
  - logo originale scontornato: chiaro (solo scritta avorio) sulle foto, a colori sull'header pieno, completo con lo slogan nel footer
  - prezzi **fuori dalla foto**, sulla riga del nome, in corsivo serif **verde smeraldo `#2e6a4b`** (il rosso sembrava uno stop); nella scheda prezzo grande allo stesso modo
  - card prodotto in rilievo (foglio avorio, ombra calda, angoli 14 px, si solleva al passaggio del mouse)
  - stato: Disponibile verde `#3a6b3a`, Pezzo unico giallo brillante `#ffc928` con scritta scura, venduto rosso `#b3261e` con "Ha già trovato casa"; sulla foto "Pezzo Unico" in giallo
  - WhatsApp in inchiostro scuro (niente verde acceso), terracotta al passaggio del mouse; bottone della scheda "Scrivici su WhatsApp per prenotarlo/a o acquistarlo/a", su telefono largo quanto il testo e centrato
  - WhatsApp e Chiama generici aprono un menu per scegliere il negozio; nella scheda vanno al negozio del pezzo
  - "Potrebbero piacerti anche" scorre da solo (una card ogni 3 s, una card intera alla volta su telefono)
  - tessere della Home 4:5 su telefono; "Vieni a trovarci" su fondo avorio chiaro
- [x] Approvazione finale di Matteo sulle tavole (28/10/2026, "si approvo")
- [ ] **Foto della vetrina di via Cavour 17**: Matteo la manda appena può, va nella pagina Negozi (oggi c'è un riquadro segnaposto)
- [ ] `design:design-critique` sulle tavole, poi **approvazione di Matteo**, max 2 giri per pagina
- [ ] `design:accessibility-review` prima di passare al codice

### Fase 3 — Backend affidabile ✅ fatta il 28/10/2026 (unita in `master` di `monili-vetrina` il 28/10/2026, con l'ok di Matteo)
- [x] Regola di Matteo anche sul sito: l'ingest rifiuta schede senza prezzo, senza un solo negozio, capi senza `size`, più di 8 foto, body oltre 4,5 MB (413)
- [x] Telefoni dei due negozi nel codice (`site-config.ts`); WhatsApp della scheda al negozio del pezzo; orari veri nel JSON-LD e nel footer; tolto l'obbligo di `NEXT_PUBLIC_SHOP_PHONE`
- [x] Uscita automatica da "Appena arrivati" dopo 8 settimane (`new-arrivals.ts`, home rigenerata ogni ora); il venduto resta nel feed fino ad allora
- [x] JSON-LD: prezzo e `SoldOut` per i venduti; **corretto un buco di sicurezza**: i testi AI potevano chiudere il tag `<script>` del JSON-LD
- [x] Test di contratto con una scheda come quella dello Studio (`npm test`, vitest): 8 test. Build, tipi e lint ok
- [x] Già a posto da prima: token confrontato a tempo costante, testi AI mostrati come testo, reinvio dello stesso id rifiutato (409), immagini solo JPEG/PNG/WebP, log su Postgres
- [ ] Non fatto: limite di richieste sull'ingest (protetto dal token di 24+ caratteri, rischio basso); controllo del contenuto reale delle immagini oltre al tipo dichiarato
- [ ] In produzione `PRODUCT_STORE_DRIVER=postgres` e `IMAGE_STORAGE_DRIVER=vercel-blob` (il deploy si ferma già senza): da impostare in Fase 5

### Fase 3b — Bot Telegram "Venduto" (½ giornata)
- [ ] Matteo crea il bot con @BotFather e passa il token (variabili `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_CHAT_ID` su Vercel, mai nel codice)
- [ ] Ogni 2–3 giorni (Vercel Cron) il bot manda a Matteo le foto dei pezzi pubblicati e non venduti, ognuna con i bottoni *Disponibile* / *Venduto*
- [ ] Webhook `POST /api/telegram/webhook` con controllo del secret token di Telegram e del chat ID: "Venduto" → `publicationStatus` resta `published`, `state = sold`; la pagina mostra "Questo ha già trovato casa. Guarda i simili"
- [ ] Il bot non scrive mai ai clienti e non legge WhatsApp. Separato da Hermes

### Fase 4 — Restyling frontend + SEO/GEO (2–3 giornate)
Fatta il 28/10/2026 e **unita in `master` di `monili-vetrina` (`b5cdabf`, fast-forward, con l'ok di Matteo)**. Su `master` passano tipi, lint, 12 test e build:
- [x] Stili del Design System v2 e delle tavole nel sito (`src/app/vetrina.css`, `site.css`), font Outfit + Cormorant + Caveat con next/font
- [x] Header trasparente sulla foto che diventa pieno scorrendo, logo originale, menu del telefono, footer con il logo completo
- [x] Menu "A quale negozio scrivi/chiami?" per WhatsApp e Chiama generici; nella scheda vanno al negozio del pezzo
- [x] Home: apertura con foto, "Appena arrivati" con filtri (anche nell'indirizzo, `/?tipo=bijoux`), tessere per tipo, "Vieni a trovarci" con "Aperto ora" calcolato nel browser
- [x] Scheda pezzo: galleria, prezzo verde in corsivo, stati colorati, venduto con i simili, simili che scorrono da soli, barra contatti del negozio del pezzo
- [x] Pagina `/negozi` (con `/contatti` reindirizzato), FAQ; JSON-LD `JewelryStore`/`ClothingStore`, `FAQPage`, `Product` con spedizione e `SoldOut`
- [x] Menu e sitemap solo con le 3 pagine (le vecchie restano nel codice); `robots.txt` che apre ai crawler AI; `llms.txt`
- [x] Verificato nel browser in locale (desktop e telefono): niente scroll orizzontale, link WhatsApp giusti, JSON-LD corretto. Build, lint, tipi e 8 test ok
- [x] `/admin/review` comoda da iPhone: campi da 16 px (niente zoom), bottoni Pubblica/Archivia grandi e affiancati, niente footer nell'admin
- [x] Passaggio animato card → scheda (View Transitions di React, `experimental.viewTransition`), spento con "riduci movimento"
- [x] `code-review` (8 punti: 6 corretti, 1 voluto, 1 rimandato: i testi dei negozi ripetuti in 4 file) e `security-review` (nessuna vulnerabilità; il JSON-LD era una XSS su `master`, già chiusa). Corretti: scorrimento dei simili bloccato dopo un tocco, pagine vecchie con `noindex`, limite di 4,5 MB anche senza Content-Length, cmd/ctrl-click sui link negozi, loghi più leggeri, stato "su richiesta" coerente
- [x] Testi dei negozi in un solo posto (`locations` in `product-fiche.ts`: via, CAP, cosa vendono; footer, selettore e mappe lo usano), 28/10/2026
- [x] Lighthouse mobile in locale (build di produzione, 28/10/2026): Accessibilità 100, Best practices 100, SEO 100 su Home, Negozi e scheda; Performance 85–88 (LCP simulato ~4 s, ma il primo disegno reale è a ~0,2 s e la foto della Home pesa 86 KB). Il punteggio non si muove con le correzioni piccole: da rimisurare sul sito online (Fase 5), obiettivo ≥ 90
- [x] **Sala Reel, lato sito** (28/10/2026, commit `519f912` su `claude/fase-4-frontend`): `POST /api/ingest/reel` (multipart `meta` + `video` + `poster`, stesso token delle schede, controllo dei byte reali, bozza); `/admin/reels` per pubblicare o archiviare; striscia "Guarda i Reel" nella Home (fondo scuro) e "Guardalo indossato" nella scheda del pezzo collegato; copertina subito, video al tocco. Provata in locale con un MP4 vero (401, finto MP4, senza copertina, troppo pesante, duplicato, bozza nascosta, pubblicazione, riproduzione); 12 test, build ok
- [x] **Sala Reel, lato Studio** (28/10/2026): `reel_studio.make_web_video` (720×1280, senza audio, prova qualità decrescenti fino a ≤ 4 MB; il caso peggiore, sorgente da 338 MB con rumore, esce a 3,8 MB in 17 s) e `make_web_poster` (≤ 600 KB); `POST /reel/{id}/showcase/publish` (multipart verso `/api/ingest/reel`, dedotto da `SHOWCASE_INGEST_URL` o da `SHOWCASE_REEL_INGEST_URL`; rifiuta le anteprime senza Higgsfield); `GET /showcase/products` per collegare il Reel a un pezzo già inviato (l'audit delle schede ora salva `product_id` e titolo: i pezzi inviati prima di oggi non compaiono nell'elenco); pannello "Pubblica sul sito vetrina" nel risultato del Reel Studio. Provato Studio → vetrina locale (bozza collegata al pezzo, secondo invio 409). 45 test (8 nuovi). Il lint del frontend dello Studio non esiste (solo `tsc`)
- [x] Link "Reel" a `/admin/reels` nella testata di `/admin/review` (28/10/2026)
- [ ] Reel Studio: la prima volta online, prova vera con un Reel Higgsfield (le prove sono state fatte con video sintetici)
- [x] Fase 4 chiusa: tavole approvate e branch uniti (28/10/2026). Resta solo Lighthouse sul sito online (Fase 5)
- [x] `design:accessibility-review` (29/10/2026), WCAG 2.1 AA: nessun problema critico, contrasti tutti ≥ 4,5:1. Corretti e uniti in master di `monili-vetrina` (b47cdee, 29/10/2026): finestra del negozio con focus trattenuto e restituito, bottone "Ferma lo scorrimento" per i simili, link "Vai al contenuto", area cliccabile dei filtri ≥ 44 px. Provati da tastiera nel browser; Lighthouse accessibilità 100 su Home, scheda e Negozi
- [ ] Da fare a mano, non verificabile da Claude: VoiceOver su iPhone, zoom al 200%, leggibilità del testo bianco sulle foto
- [ ] Token e componenti dal Design System v2 in `apps/web`
- [ ] Le 3 pagine fedeli alle tavole, screenshot di confronto con `run`; pagine fuori lancio nascoste da menu e sitemap
- [ ] WhatsApp e "Chiama" della scheda col numero del negozio del pezzo (`availableAt`): oggi la vetrina ha un solo `NEXT_PUBLIC_SHOP_PHONE`, servono due numeri
- [ ] Bottone WhatsApp con messaggio precompilato: *"Ciao! Mi piace questo [nome] ([link]), è ancora disponibile?"*; secondario "Scrivici in DM su Instagram"
- [ ] `/admin/review` comoda da iPhone
- [ ] SEO locale (`seo-aeo-geo-ultimate:seo-local`): metadata, Open Graph, JSON-LD `LocalBusiness` ×2 (via Cavour 17 e 21, orari veri) e `Product` con prezzo, `availability` (venduto = `SoldOut`) e, dopo l'ok sulle cifre, `shippingDetails`; `sitemap`
- [ ] GEO (`ai-seo:llms-txt-ai-crawler-access`, `seo-aeo-geo-ultimate:seo-geo`): `robots.txt` che lascia entrare i crawler di ricerca AI, `llms.txt`, testi che rispondono a domande vere, stesso nome/indirizzo/telefono ovunque
- [ ] `ai-seo:ai-page-audit` su una scheda pezzo vera; Lighthouse mobile ≥ 90
- [ ] `code-review` + `security-review`

### Fase 5 — Messa online (½ giornata) ← **SIAMO QUI**
Decisioni del 29/10/2026: progetto Vercel nuovo e separato da Alfred; database Neon nuovo e pulito (l'attuale ha solo pezzi venduti, resta come archivio); foto prodotto in un formato unico, Instagram solo come extra (`docs/foto-prodotti.md`); dominio da scegliere. Passi dettagliati in `docs/fase-5-messa-online.md`.
**Online dal 30/10/2026: https://monili-vetrina.vercel.app** (piano Hobby per la prova: non ammette siti commerciali, prima del lancio pubblico decidere Pro 20 $/mese o altro)
- [x] Progetto Vercel `monili-vetrina` (`prj_EGZePgAv8yAYaquYykg1nxlDov5Y`) collegato a GitHub, root `apps/web`, produzione da `master`: ogni push su `master` della vetrina va online
- [x] Neon `monili-vetrina-db` (gratis, Francoforte, vuoto) e Blob `monili-vetrina-foto` (pubblico, Francoforte), collegati
- [x] Variabili Production + Preview: `NEXT_PUBLIC_SITE_URL=https://monili-vetrina.vercel.app`, driver `postgres` / `vercel-blob`, `ADMIN_*` generati il 30/10. Password admin e token solo in `C:\Users\matte\MoniliStorage\vetrina-accesso-admin.txt` (da spostare in un gestore di password)
- [x] Controllato online: Home, Negozi, robots, sitemap, llms.txt aprono; `/admin/*` chiede la password; ingest senza token → 401, con il token dello Studio → passa
- [ ] Dominio personalizzato (poi cambiare `NEXT_PUBLIC_SITE_URL` e gli indirizzi nel `.env` dello Studio)
- [x] Studio: `.env` del PC con `SHOWCASE_INGEST_URL`, `SHOWCASE_REEL_INGEST_URL`, `SHOWCASE_ADMIN_TOKEN` (= `ADMIN_API_TOKEN`); `frontend/.env.local` con `NEXT_PUBLIC_SHOWCASE_REVIEW_URL`
- Attenzione: `vercel blob create-store` / `vercel env pull` riscrivono `apps/web/.env.local` della vetrina. Le vecchie impostazioni locali (database archivio, progetto `jarvis-web`) sono salvate in `apps/web/.env.local.prima-del-30-10`
- [ ] Link nel profilo Google Business e nella bio Instagram
- [ ] Fuori dal sito (conta per Google e per le AI): profilo Google Business completo per entrambi i negozi, richiesta recensioni ai clienti, stessi dati ovunque
- [ ] Dopo 2–4 settimane: `ai-seo:ai-seo-audit` (ChatGPT/Gemini/Perplexity ci nominano per "bijoux Ravenna"?)

**Prima prova del weekend (31/10–1/11/2026)**: cosa serve davvero, in ordine
- [x] Fase 5 minima: progetto Vercel `monili-vetrina` + Neon + Blob nuovi, variabili, indirizzo `.vercel.app` (il dominio può aspettare)
- [x] Studio `.env` sul PC: `SHOWCASE_INGEST_URL`, `SHOWCASE_REEL_INGEST_URL` (facoltativa, si deduce), `NEXT_PUBLIC_SHOWCASE_REVIEW_URL`, stesso token dei due lati
- [ ] Matteo: account e API key Higgsfield (`HF_API_KEY_ID` / `HF_API_KEY_SECRET`), senza i Reel restano anteprime
- [ ] Riavviare lo Studio sul PC (codice del 30/10: pulizia foto e donne AI)
- [ ] Prova completa con 1–2 pezzi veri: foto → Scheda pezzo → "Pubblica sul sito vetrina" → `/admin/review` Pubblica → "Fai il Reel di questo pezzo" → Reel sul sito → segnare Venduto
- Possono aspettare: bot Telegram, dominio, foto di via Cavour 17, Google Business

**Decisioni sullo Studio del 29–30/10/2026** (commit `93487c3` di `monili-media-agency`; dettagli in `docs/foto-prodotti.md` e `docs/reel-studio.md`)
- **Foto per pezzo: 2 o 3**, tutte 4:5 su fondo avorio, in quest'ordine: pulita AI (copertina, controllare che sia fedele), indossata da una donna AI, foto vera ripulita. I fotogrammi dei Reel non si pubblicano come foto
- **Foto vera ripulita senza AI sul pezzo** (`photo_cleanup.py`): scontorno BiRefNet sul PC, luce e colore sistemati, fondo avorio. È spuntata solo se lo scontorno è pulito, altrimenti lo Studio scrive il motivo. Pesa ~1 GB di modello e memoria: gira sul PC
- **Niente modella fissa, una donna per pezzo**: la inventa l'AI nella Scheda pezzo (reale ed elegante, non una modella perfetta) e i Reel fatti con "Fai il Reel di questo pezzo" usano lei, con la foto indossata come riferimento del viso. Mai lo stesso pezzo con due donne diverse; il pezzo dopo ne ha un'altra
- **Libertà creativa + divieti**: l'AI inventa luoghi, donne, pose e abiti e riceve donne e scene recenti da non ripetere. L'unico limite fisso è "Mai nei contenuti" (`skills/_base/divieti.md`, pagina Skill): eleganza come linea guida, no sesso, violenza, bambini, cose illegali, uomini, animali, kitsch, marchi, luoghi fuori dalla Romagna. Niente elenchi che rendono i contenuti tutti uguali
- Skill `/modella-monili` → `/indossato` (il vecchio nome funziona ancora)

### Fase 6 — Contenuti che spingono la ricerca (continuo, nello Studio)
- [ ] Caption e Reel con le parole che la gente cerca (pietra, tipo di pezzo, "Ravenna"): regola da aggiungere in `skills/*.md`, non nel codice
- [ ] Ogni contenuto con un pezzo pubblicato sul sito porta il link alla sua scheda

**Totale stimato: 7–9 giornate.**

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
3. ~~Branch `determined-knuth`~~ ✅ unito
4. ~~Pagine del lancio~~ ✅ 3 pagine
5. **Dominio**: ne hai già uno?
6. ~~**Prezzi**~~ ✅ sì, visibili sul sito
7. ~~Orari~~ ✅ tutti i giorni 9:30–13:00 e 15:00–19:30, uguali nei due negozi (28/10/2026). Telefoni: via Cavour 17 → 331 428 5295, via Cavour 21 → 375 771 3966 (28/10/2026). Regola: ogni pezzo scrive e chiama il **suo** negozio (17 argento e bijoux, 21 abbigliamento e accessori); nello Studio il negozio si sceglie a mano ed è obbligatorio. Da decidere: il numero dei WhatsApp generici (header, Home, barra "Chiama" fuori dalle schede)
8. **Logo**: file originali (SVG o PNG ad alta risoluzione); esiste un monogramma "iM"?
9. ~~Plugin `frontend-design`~~ ✅ installato
10. ~~Spedizioni~~ ✅ Italia 8 €, gratis sopra 99 € (28/10/2026). Europa: non deciso
11. **Database Neon**: contiene prodotti veri o solo test? Per la produzione serve comunque un database pulito
12. ~~Canale "Venduto"~~ ✅ bot Telegram dedicato, separato da Hermes
13. ~~Design System v2~~ ✅ ok

---

## 10. Punto della situazione e ripartenza (aggiornato 30/10/2026)

**Per riprendere in una nuova chat**, scrivi:
> Leggi `CLAUDE.md` e `PLAN_VETRINA.md` (sezione 10) nel repo monili-media-agency (`master`) e continua dal primo punto di "Prossimi passi".

### Istruzioni per chi riprende (vale per qualunque modello)
1. **Leggi prima**: `CLAUDE.md` (tono, colori, regole del brand), questo file per intero, poi l'artifact del Design System (Artifact, `action: "read"` sull'URL qui sotto). Non rifare analisi già fatte: feed Instagram e louisemisha.com sono riassunti più sotto
2. **Un passo per volta**, nell'ordine di "Prossimi passi". Alla fine di ogni passo: aggiorna le caselle in questo file, commit, push sul branch di lavoro della sessione
3. **Matteo** preferisce risposte in italiano, dirette e sincere, senza giri di parole; se una scelta è sbagliata diglielo. Fagli domande solo sulle decisioni che spettano a lui (sezione 8), una alla volta, con una raccomandazione. Non tutto in un muro di testo
4. **Il repo della vetrina** (`matteforex82-bit/monili-vetrina`) non è nella sessione di partenza: in una chat cloud va aggiunto con `add_repo` (accesso `push`) e clonato. Lì valgono le sue regole (`.claude/skills/impeccable`)
5. **Non** fare push su `master` senza un ok esplicito di Matteo. **Non** cambiare API, store, validazione o ingest durante il restyling (4.3)
6. **Test**: nello Studio `python -m pytest tests` deve passare prima di ogni push; nella vetrina gli script di `apps/web/package.json` (lint, build, test)
7. Segreti (token Telegram, Neon, Blob, `ADMIN_*`): solo come variabili d'ambiente, mai nel codice né in questo file

### Dove sono le cose
- **Studio + Reel Studio**: repo `matteforex82-bit/monili-media-agency`, `master` (sul PC: `Desktop\PROGETTI AI\monili-deploy-temp`, avvio con `Avvia Agenzia Monili.bat`). **Scelta del 27/10/2026: lo Studio resta in locale sul PC e Matteo lo usa dal telefono ovunque con Tailscale** (gratis; guida in `docs/local-mode.md`). **Render dismesso il 30/10/2026** (senza password e senza memoria per la pulizia foto): `render.yaml` tolto dal repo, servizi `monili-media-agency`, `monili-backend` e `monili-frontend` sospesi (riaccendibili con "Resume"). Lo Studio online "fatto bene" (Vercel + Render a pagamento con disco, ~8–10 €/mese, password) si valuta con la Fase 5. Questo piano è su `master` (unito il 27/10/2026 sera); il branch di lavoro precedente era `claude/blissful-darwin-7tnrfd`
- **Vetrina (frontend + backend)**: repo privato `matteforex82-bit/monili-vetrina`, `master` (`7f438be`), app in `apps/web` (sul PC: `Desktop\PROGETTI AI\Ecosistema Monili`)
- **Design System v2**: https://claude.ai/artifact/62dgz9RcfeetzXXfVZpFvq (tipo Design System, privato; v2 dal 28/10/2026, stesso URL della v1). Sorgenti: `project/tokens.json`, `project/README.md`, `project/components/*`. `tokens.css` va rigenerato da `tokens.json` a ogni modifica dei token
- **Skill e plugin**: Impeccable (guida principale per il codice; il suo programma di controllo NON è autorizzato), frontend-design (alternativa, non insieme), Design (Anthropic: `design-critique`, `accessibility-review`), audit-suite (`web-animation-design`, `make-interfaces-feel-better`), **SEO-AEO-GEO Ultimate** e **AI SEO** (installati il 27/10, vedi tabella 4.4), `instagram-agent:ig-human` per i testi

### Fatto fino a qui
- Fase 0: vetrina messa al sicuro su GitHub
- Fasi 1 e 1b: bug bloccanti risolti, admin protetto, "Approva" pubblica subito senza rideploy, limite 4,5 MB gestito, prezzo nello Studio, link ad Alfred rimosso, branch uniti in `master` e `git pull` fatto sul PC
- Reel Studio unito nello Studio
- Design System v1
- **27/10 sera, decise con Matteo**: cosa è il sito (vetrina di brand a novità, niente e-commerce, niente collezioni), 3 pagine, prezzi visibili, SEO + GEO come obiettivo principale, bot Telegram per "Venduto", spedizioni Italia + Europa, Design System v2 approvato. Dettagli in sezione 6, "Scelte del 27/10/2026 (2)"

- **27/10 sera: la missione dello Studio è diventata "Scheda pezzo"**: produce solo quello che serve al sito, cioè 2 foto AI + la foto reale, testi SEO, WhatsApp e Google Business. Si passa da 7 a 3 chiamate di testo e da 5 a 2 immagini. Instagram passa dal Reel Studio. Dettagli in `docs/STATO_PROGETTO.md`
- Da fare più avanti: il Reel Studio rifà l'analisi del pezzo; potrebbe riusare quella della scheda (una chiamata in meno per ogni Reel)
- **28/10**: tavole approvate, Fasi 3 e 4 fatte e unite in `master` di `monili-vetrina` (backend affidabile, restyling, SEO/GEO, sala Reel), correzioni di accessibilità unite
- **29/10**: checklist della Fase 5 (`docs/fase-5-messa-online.md`) e formato unico delle foto prodotto
- **29–30/10, nello Studio**: foto vera ripulita, una donna AI per pezzo, libertà creativa con l'elenco dei divieti (vedi Fase 5, "Decisioni sullo Studio"). 59 test, commit `93487c3` su `master`, push fatto

### Il sito in una frase
Una vetrina che sembra il feed editoriale di Instagram ma fa quello che Instagram non fa: farsi trovare su Google e dalle AI, dare un link fisso a ogni pezzo da girare su WhatsApp, portare la gente nei due negozi di via Cavour. La vendita avviene su WhatsApp e DM, risponde sempre Matteo.

### Analisi del feed Instagram (base del Design System)
- I post migliori sono **editoriali**: occhiello "I MONILI RAVENNA" maiuscolo spaziato, titolo serif leggero con punto finale ("Un capo che parla di stile.", "Non sono semplici orecchini.", "Colori che illuminano il viso."), filetto, sottotitolo corsivo, chiusa "Ti aspettiamo in boutique". Variante gioielli: titolo in basso al centro + materiali in maiuscolo
- Cartellino prezzo nero con "115€" in corsivo bianco
- Foto: luce dorata da boutique, archi, marmo, modella ricorrente; gioielli in macro su ardesia/seta/pietra
- Colori dai prodotti: pietre (ametista, turchese, citrino, granato, quarzo rosa, opale, lapislazzuli), capi (cammello, oliva, ruggine)
- Da evitare: scritte fumetto rosa dei Reel in negozio ("TEMPO DI SHOPPING")

### Riferimento di stile scelto da Matteo: louisemisha.com (analizzato, NON da copiare)
Si prendono i principi, non codice/logo/foto/layout identico:
- Foto a tutta larghezza con filo bianco di 1-2px, griglie di 3-4 tessere alte
- Header trasparente sopra la foto, bianco pieno al passaggio del mouse; menu maiuscolo 12px peso 500, spaziatura 1px
- Mega menu: pannello bianco, 3 colonne di link grigi (14px leggero, spaziatura 1px), 2 foto con nome categoria maiuscolo, pagina dietro sfocata
- Nomi categoria in serif maiuscolo bianco sulle foto ("ANELLI", "GILET RICAMATI")
- Inviti come testo maiuscolo sottolineato ("SCOPRI", "VEDI TUTTO") invece dei bottoni (bottone solo per WhatsApp)
- Movimento: `cubic-bezier(0.645, 0.045, 0.355, 1)` 0,3–0,5s per gli spostamenti, dissolvenze 0,2–0,3s `ease`; puntino sotto la voce di menu attiva
- Font loro: Forum + Outfit (Google Fonts, liberi) e Pitch Sans (a pagamento, escluso)
- Niente carrello/account/newsletter a comparsa: al loro posto WhatsApp e "Vieni in negozio"

### Design System v2: cosa cambia (approvato da Matteo il 27/10/2026)
1. Inter → **Outfit** per menu e testi (il cambio più visibile)
2. **Cormorant Garamond resta** per i titoli, anche in maiuscolo sulle foto (niente Forum: due serif sono troppi e sembrerebbe Louise Misha)
3. Nuovi componenti: header trasparente, mega menu con foto (al lancio con le 3 voci + filtri per tipo), griglia a tessere da bordo a bordo, invito sottolineato, card "Appena arrivati" con prezzo in stile cartellino, blocco "Vieni a trovarci" con "Aperto ora", stato "Questo ha già trovato casa"
4. Token di movimento (curva e tempi del riferimento sopra), `prefers-reduced-motion` rispettato
5. **Terracotta** `#c8593a` come accento al posto del verde acqua, oro `#c79849` (coerente con CLAUDE.md)

### Dati che mancano (chiederli a Matteo quando servono, non prima)
- Numero WhatsApp/telefono e orari veri dei due negozi → servono per le tavole (si può partire con segnaposto evidenti)
- Logo SVG e monogramma "iM" → servono per il Design System v2 (segnaposto testuale finché mancano)
- Ok sulle cifre di spedizione (7 € / gratis sopra 69 €) → servono solo in Fase 4
- Dominio, contenuto del database Neon → servono in Fase 5

### Prossimi passi, in ordine
1. ~~Design System v2~~ ✅ 28/10/2026
2. ~~Tavole delle 3 pagine~~ ✅ approvate (https://claude.ai/artifact/NNmcN1Y1goYwFfZHfDexjP)
3. ~~Backend (Fase 3)~~ ✅ · ~~Frontend (Fase 4)~~ ✅ · ~~Ingest dei video Reel~~ ✅
4. **Prima prova del weekend**: la lista in Fase 5 ("Prima prova del weekend"). Sito online e Studio collegati il 30/10; restano key Higgsfield, riavvio dello Studio e prova completa con 1–2 pezzi veri
5. Dopo la prova: controllare quanto costa davvero una Scheda pezzo e un Reel, e se donne e scene escono varie; completare "Mai nei contenuti" se serve
6. **Bot Telegram "Venduto"** (Fase 3b)
7. Dominio, Google Business, recensioni, controllo visibilità AI, contenuti dello Studio orientati alla ricerca (Fasi 5 e 6)
