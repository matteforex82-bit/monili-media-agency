# Piano — Sito Vetrina I Monili Ravenna

> Stato: **approvato, in lavorazione** (siamo alla Fase 2, Design) · Creato il 27/10/2026 · Ultimo aggiornamento: 28/10/2026, Design System v2 pubblicato
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

### Fase 2 — Design con Claude Design (1–2 giornate) ← **SIAMO QUI**
- [ ] Rileggere i wireframe in `reference/showcase-wireframe-claude-design` e `reference/hi fi sito` (repo `monili-vetrina`)
- [x] Pagine del lancio decise: 3 pagine (4.2)
- [x] Design System v1 creato il 27/10/2026: https://claude.ai/artifact/62dgz9RcfeetzXXfVZpFvq (token "Avorio caldo", stile editoriale del feed Instagram, sala Reel, pietre, 11 componenti)
- [x] Proposta v2 approvata da Matteo ("ok", 27/10/2026 sera), vedi sezione 10
- [x] **Design System v2** pubblicato il 28/10/2026 sullo stesso artifact (versione 5): Outfit, terracotta `#c8593a` + `terracotta-deep` `#9e4128` per il testo, oro `#c79849`, token di movimento, 8 componenti nuovi (SiteHeader, MegaMenu, TileGrid, CtaLink, ArrivalCard, FilterBar, VisitBlock, SoldNotice). Il prezzo del cartellino passa a Cormorant corsivo (Outfit non ha il corsivo). Orari e telefono nelle anteprime sono d'esempio
- [ ] Impostarlo come **predefinito**: lo fa Matteo dalla pagina dell'artifact su claude.ai (non si può da Claude Code)
- [x] Tavole mobile + desktop delle 3 pagine (4.2), 28/10/2026, giro 1: https://claude.ai/artifact/NNmcN1Y1goYwFfZHfDexjP (9 tavole: Home desktop/telefono con filtri funzionanti, Scheda pezzo nei 4 stati + telefono, Negozi desktop/telefono con FAQ per Google e AI). Foto e pezzi veri (outfit della settimana, Studio, foto del negozio); **mancano** e sono segnati `[tra parentesi]`: prezzi, orari, telefono, foto di via Cavour 17, spedizioni, taglie. Solo 6 pezzi veri trovati (un solo bijou: l'anello). I Reel sono copertine d'esempio: non ci sono ancora video
- [x] Giro 1b (28/10/2026): orari e spedizioni veri, tolto lo stato "Su richiesta" (ogni pezzo ha un prezzo)
- [ ] Approvazione di Matteo sulle tavole (max 2 giri per pagina)
- [ ] **Foto della vetrina di via Cavour 17**: Matteo la manda appena può, va nella pagina Negozi (oggi c'è un riquadro segnaposto)
- [ ] `design:design-critique` sulle tavole, poi **approvazione di Matteo**, max 2 giri per pagina
- [ ] `design:accessibility-review` prima di passare al codice

### Fase 3 — Backend affidabile (1 giornata)
- [ ] Tutti i punti della sezione 5
- [ ] Regola di Matteo (28/10/2026) anche sul sito: l'ingest rifiuta schede senza prezzo e capi d'abbigliamento senza `size`. Nello Studio il controllo c'è già (prezzo obbligatorio, taglia obbligatoria per l'abbigliamento, categoria scelta a mano); oggi la vetrina accetta ancora `price: null`
- [ ] In produzione `PRODUCT_STORE_DRIVER=postgres` e `IMAGE_STORAGE_DRIVER=vercel-blob`, log su Postgres
- [ ] Stato **venduto** e uscita automatica da "Appena arrivati" dopo 6–8 settimane (campo data di pubblicazione già presente → filtro, niente cron)
- [ ] Prezzo nel modello scheda già presente (Studio lo invia): verificarlo fino al JSON-LD

### Fase 3b — Bot Telegram "Venduto" (½ giornata)
- [ ] Matteo crea il bot con @BotFather e passa il token (variabili `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_CHAT_ID` su Vercel, mai nel codice)
- [ ] Ogni 2–3 giorni (Vercel Cron) il bot manda a Matteo le foto dei pezzi pubblicati e non venduti, ognuna con i bottoni *Disponibile* / *Venduto*
- [ ] Webhook `POST /api/telegram/webhook` con controllo del secret token di Telegram e del chat ID: "Venduto" → `publicationStatus` resta `published`, `state = sold`; la pagina mostra "Questo ha già trovato casa. Guarda i simili"
- [ ] Il bot non scrive mai ai clienti e non legge WhatsApp. Separato da Hermes

### Fase 4 — Restyling frontend + SEO/GEO (2–3 giornate)
- [ ] Token e componenti dal Design System v2 in `apps/web`
- [ ] Le 3 pagine fedeli alle tavole, screenshot di confronto con `run`; pagine fuori lancio nascoste da menu e sitemap
- [ ] Bottone WhatsApp con messaggio precompilato: *"Ciao! Mi piace questo [nome] ([link]), è ancora disponibile?"*; secondario "Scrivici in DM su Instagram"
- [ ] `/admin/review` comoda da iPhone
- [ ] SEO locale (`seo-aeo-geo-ultimate:seo-local`): metadata, Open Graph, JSON-LD `LocalBusiness` ×2 (via Cavour 17 e 21, orari veri) e `Product` con prezzo, `availability` (venduto = `SoldOut`) e, dopo l'ok sulle cifre, `shippingDetails`; `sitemap`
- [ ] GEO (`ai-seo:llms-txt-ai-crawler-access`, `seo-aeo-geo-ultimate:seo-geo`): `robots.txt` che lascia entrare i crawler di ricerca AI, `llms.txt`, testi che rispondono a domande vere, stesso nome/indirizzo/telefono ovunque
- [ ] `ai-seo:ai-page-audit` su una scheda pezzo vera; Lighthouse mobile ≥ 90
- [ ] `code-review` + `security-review`

### Fase 5 — Messa online (½ giornata)
- [ ] Nuovo progetto Vercel `monili-vetrina` collegato al nuovo repo, root `apps/web`
- [ ] Variabili d'ambiente su Vercel (Neon, Blob, `ADMIN_*`), `NEXT_PUBLIC_SITE_URL` = dominio vero (oggi punta a `http://127.0.0.1:3100`)
- [ ] Dominio personalizzato
- [ ] Studio: `SHOWCASE_INGEST_URL=https://<dominio>/api/ingest/internal-webapp`, `NEXT_PUBLIC_SHOWCASE_REVIEW_URL=https://<dominio>/admin/review`, stesso token dei due lati
- [ ] Link nel profilo Google Business e nella bio Instagram
- [ ] Fuori dal sito (conta per Google e per le AI): profilo Google Business completo per entrambi i negozi, richiesta recensioni ai clienti, stessi dati ovunque
- [ ] Dopo 2–4 settimane: `ai-seo:ai-seo-audit` (ChatGPT/Gemini/Perplexity ci nominano per "bijoux Ravenna"?)

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
7. ~~Orari~~ ✅ tutti i giorni 9:30–13:00 e 15:00–19:30, uguali nei due negozi (28/10/2026). Manca ancora il **numero WhatsApp/telefono**
8. **Logo**: file originali (SVG o PNG ad alta risoluzione); esiste un monogramma "iM"?
9. ~~Plugin `frontend-design`~~ ✅ installato
10. ~~Spedizioni~~ ✅ Italia 8 €, gratis sopra 99 € (28/10/2026). Europa: non deciso
11. **Database Neon**: contiene prodotti veri o solo test? Per la produzione serve comunque un database pulito
12. ~~Canale "Venduto"~~ ✅ bot Telegram dedicato, separato da Hermes
13. ~~Design System v2~~ ✅ ok

---

## 10. Punto della situazione e ripartenza (aggiornato 27/10/2026 sera)

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
- **Studio + Reel Studio**: repo `matteforex82-bit/monili-media-agency`, `master` (sul PC: `Desktop\PROGETTI AI\monili-deploy-temp`, avvio con `Avvia Agenzia Monili.bat`). **Scelta del 27/10/2026: lo Studio resta in locale sul PC e Matteo lo usa dal telefono ovunque con Tailscale** (gratis; guida in `docs/local-mode.md`). Render non ha password: va sospeso finché non c'è. Lo Studio online "fatto bene" (Vercel + Render a pagamento con disco, ~8–10 €/mese, password) si valuta con la Fase 5. Questo piano è su `master` (unito il 27/10/2026 sera); il branch di lavoro precedente era `claude/blissful-darwin-7tnrfd`
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
1. ~~Design System v2~~ ✅ 28/10/2026 (resta solo "imposta come predefinito", lo fa Matteo)
2. **Tavole delle 3 pagine**: giro 1 pubblicato il 28/10/2026 (https://claude.ai/artifact/NNmcN1Y1goYwFfZHfDexjP). Ora: commenti di Matteo, giro 2, ok finale; poi `design:accessibility-review`
3. **Backend**: stato venduto, archivio automatico dopo 6–8 settimane, punti della sezione 5 (Fase 3)
4. **Codice del frontend** nel repo `monili-vetrina` con Impeccable, passaggi e filtri animati, SEO/GEO completo (Fase 4)
5. **Bot Telegram "Venduto"** (Fase 3b)
6. **Ingest dei video Reel** dallo Studio alla vetrina (parte dinamica n.1)
7. **Deploy** su Vercel: progetto nuovo `monili-vetrina`, database pulito, dominio (Fase 5)
8. Google Business, recensioni, controllo visibilità AI, contenuti dello Studio orientati alla ricerca (Fasi 5 e 6)
