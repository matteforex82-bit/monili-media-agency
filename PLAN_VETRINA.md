# Piano — Sito Vetrina I Monili Ravenna

> Stato: **bozza da approvare** · Creato il 27/10/2026
> Obiettivo: completare il frontend pubblico della vetrina, che finora è stato solo "predisposto" dal lato Studio AI.

---

## 1. Cosa c'è davvero oggi (stato verificato)

Partiamo dalla verità, perché cambia tutto il piano: **in questo repository il sito vetrina pubblico non esiste.**
Quello che è stato costruito è solo il lato che *invia* i prodotti alla vetrina.

### ✅ Esiste ed è funzionante

| Pezzo | Dove | Cosa fa |
|---|---|---|
| Agente "SITO VISUAL" | `main.py` (`agent_showcase_visual_prompts`, `generate_showcase_images`) | Genera 3 foto dedicate al sito in 4:5 dentro `output/<run>/07_SHOWCASE/` |
| Pacchetto SEO pagina vetrina | `main.py` (sezione `## PAGINA VETRINA / SHOPIFY / SITO`) | Titolo SEO, meta description, H1, descrizione 120 parole, alt text, 5 FAQ |
| Candidati foto | `GET /missions/{run_id}/showcase/candidates` in `api/server.py` | Elenca le foto del run utilizzabili per il sito, con quality report |
| Preparazione scheda prodotto | `_build_showcase_payload` in `api/server.py` | Quality gate, resize a 1200×1500 JPEG, crea la `product_fiche` |
| Invio alla vetrina | `POST /missions/{run_id}/showcase/publish` | Salva un audit in `showcase-drafts/` e fa POST a `SHOWCASE_INGEST_URL` |
| Pannello "Pubblica sul sito vetrina" | `frontend/src/components/ResultsPanel.tsx` (`ShowcasePublishPanel`, tab `sito`) | Scelta foto e invio dallo Studio |

### ❌ Manca / è rotto

1. **Il sito vetrina vero e proprio** (catalogo pubblico, schede prodotto, negozi). Nessun codice nel repo.
2. **L'endpoint di ingest** che riceve la `product_fiche`. `SHOWCASE_INGEST_URL` non è configurata da nessuna parte (né `.env.example`, né `render.yaml`): oggi ogni "Pubblica" finisce in errore 502.
3. **Il link "review"** in `ResultsPanel.tsx` punta a `https://web-five-theta-58.vercel.app/admin/review`.
   Verificato oggi: quel dominio Vercel ora serve un altro progetto ("Alfred — Il tuo coach personale") e `/admin/review` risponde **404**. Va sostituito.
4. **Bug visibile nello Studio**: in `frontend/src/app/page.tsx` (hero, ~riga 663) c'è il testo letterale `` `r`n `` (residuo di uno script PowerShell) tra "Cosa lanciamo" e "oggi in vetrina?". Si vede a schermo.
5. Commenti di `globals.css` con caratteri corrotti (`â•â•…`): problema di encoding, innocuo ma da ripulire.

### ⚠️ Attenzione: lavoro non unito

Esiste il branch `claude/determined-knuth-zp63a6` con **9 commit non uniti a `master`** (Reel Studio, skills, risultati, test) che tocca anche `frontend/src/app/page.tsx` e `globals.css`.
Va deciso **prima** di iniziare: unirlo o archiviarlo. Se lo lasciamo lì e lavoriamo sul frontend, poi i conflitti li paghiamo con gli interessi.

---

## 2. Il contratto già deciso (da rispettare)

Lo Studio manda già questo JSON. La vetrina deve accettarlo così com'è, senza costringerci a riscrivere il backend.

```http
POST {SHOWCASE_INGEST_URL}
Content-Type: application/json
x-admin-token: {SHOWCASE_ADMIN_TOKEN}
```

```jsonc
{
  "run_id": "20261027_1830",
  "product_fiche": {
    "id": "orecchini-cerchio-dorati-20261027-1830",   // slug
    "title": "Orecchini a cerchio dorati",
    "category": "gioielli | bijoux | accessori | abbigliamento",
    "state": "disp | unique | req | sold",
    "price": null,                                      // sempre presente, anche null
    "currency": "EUR",
    "summary": "…",                                     // opzionale
    "story": "…",                                       // opzionale (caption scelta)
    "materials": ["argento 925"],                       // opzionale
    "images": [{ "src": "data:image/jpeg;base64,…", "alt": "…" }],  // max 8, 1200×1500
    "availability": { "inStore": true, "reservable": true, "shipsFrom": "Ravenna" },
    "availableAt": ["via-cavour-17"],                   // via-cavour-17 (bijoux/gioielli) | via-cavour-21 (abbigliamento/accessori)
    "whatsappPreset": "prodotto | negozio | richiesta | simili",
    "relatedTags": ["imoniliravenna", "…"],             // opzionale
    "seo": { "title": "…", "description": "…" },        // opzionale
    "updatedAt": "ISO-8601",
    "publicationStatus": "draft",
    "sourceSystem": "internal-web-app",
    "sourceRunId": "20261027_1830"
  }
}
```

Risposta attesa dallo Studio: `2xx` con `{ "item": { "id": "…" } }`.

**Regola chiave**: tutto arriva come `draft`. Niente va online senza un tuo "Approva" nella pagina admin. È giusto così: l'AI sbaglia categoria/prezzo abbastanza spesso da non meritare la pubblicazione automatica.

---

## 3. Decisioni di architettura (la mia raccomandazione)

| Tema | Scelta consigliata | Perché |
|---|---|---|
| Dove vive il codice | Nuova app Next.js in **`vetrina/`** in questo repo (accanto a `frontend/`) | Contratto e brand stanno nello stesso posto; ma app separata dallo Studio, che è uno strumento interno **senza login** e non deve finire sul dominio pubblico |
| Hosting | **Vercel** (progetto nuovo, dominio tipo `imoniliravenna.it`) | Next.js nativo, gratis per questo volume, Render free va in sleep e farebbe aprire il sito in 30–50 s |
| Database | **Vercel Postgres / Neon** (tabella `products`) | Su Vercel il disco non è persistente: un file JSON non sopravvive |
| Immagini | **Vercel Blob** (decodifico i `data:` URL all'ingest e salvo URL pubblico) | Le immagini non devono stare in base64 nel DB |
| Rendering | Pagine statiche con **ISR** (`revalidate` + `revalidatePath` all'approvazione) | Veloce, ottimo per SEO locale |
| Pagamenti | **Nessun checkout**: prenotazione via WhatsApp | Coerente con "un'amica che consiglia", e zero complessità di e-commerce |

### ⚠️ Problema tecnico da risolvere subito
Le funzioni serverless di Vercel accettano body di **max ~4,5 MB**. Lo Studio manda fino a 8 foto in base64 da ~650 KB → fino a **~7 MB**: l'ingest fallirebbe proprio con i prodotti con più foto.
Soluzione (piccola modifica in `api/server.py`): limitare a **4 immagini per invio** (`selected_images[:4]`) oppure inviare la scheda senza immagini e poi caricarle una per una su `/api/ingest/{id}/images`. Consiglio la prima: 4 foto bastano per una scheda.

---

## 4. Pagine del sito vetrina

Tono e visual da `CLAUDE.md`: caldo, complice, mai formale; neutri caldi, bianco ottico, terracotta e oro; foto luminose e naturali.

1. **Home `/`**
   - Hero con 1 foto forte + claim breve ("Il tuo prossimo dettaglio preferito è in via Cavour")
   - "Nuovi arrivi" (ultimi 8 approvati)
   - 4 tessere categoria: Bijoux · Gioielli · Accessori · Abbigliamento
   - I due negozi (via Cavour 17 e 21) con orari e "Come arrivare"
   - CTA WhatsApp fissa + link Instagram

2. **Catalogo `/prodotti`**
   - Griglia 4:5 (2 colonne mobile, 3–4 desktop)
   - Filtri: categoria, disponibilità (`disp` / `unique` / `sold` come "Già adottato 💛")
   - Ordinamento: più recenti

3. **Scheda prodotto `/prodotti/[id]`**
   - Galleria swipe 4:5, alt text dal payload
   - Titolo, prezzo (o "Chiedi il prezzo" se `null`), badge stato ("Pezzo unico", "Su richiesta", ecc.)
   - `story` come testo "da amica", materiali in chip
   - "Dove lo trovi": negozio da `availableAt`
   - Bottone WhatsApp con messaggio precompilato secondo `whatsappPreset`
   - Prodotto venduto → resta online con "Ti trovo qualcosa di simile?" (preset `simili`): non perdi l'indicizzazione
   - SEO: `seo.title`/`seo.description`, Open Graph con prima foto, **JSON-LD `Product` + `LocalBusiness`**

4. **Negozi `/negozi`**
   - Via Cavour 17 (bijoux/gioielli) e via Cavour 21 (abbigliamento/accessori), orari, mappa statica, telefono/WhatsApp

5. **Admin `/admin/review`** (protetta)
   - Lista bozze arrivate dallo Studio con anteprima
   - Azioni: **Approva**, **Modifica** (titolo, prezzo, categoria, stato, testo), **Segna venduto**, **Nascondi**, **Elimina**
   - Accesso: password unica via env (`ADMIN_PASSWORD`) con cookie firmato; non serve di più per un negozio

Le API della vetrina sono descritte nella sezione 6 (Backend).

---

## 5. Come costruiamo il frontend: prima Claude Design, poi le skill

Scelta tua: il frontend deve essere fatto con **Claude Design** e con le **migliori skill disponibili**.
La regola che ne deriva: **prima si disegna e si approva, poi si scrive codice.** Nessuna pagina va in Next.js finché il suo design non è approvato.

### 5.1 Design System "I Monili Ravenna" (tipo *Design System* di Claude)
Oggi non hai nessun design system salvato: lo creiamo per primo e lo impostiamo come **predefinito**, così ogni design e ogni pagina successiva partono dalla stessa base.
- **README del brand**: tono di voce e regole visive prese da `CLAUDE.md` (caldo, complice, mai formale; foto luminose, niente filtri esagerati)
- **Token**: palette neutri caldi + bianco ottico + terracotta `#c8593a` + oro `#c79849` (partendo da `frontend/src/app/globals.css`), scala tipografica Instrument Serif + Manrope, spaziature, raggi, ombre
- **Componenti con anteprima**: `ProductCard` 4:5, `BadgeStato` (disponibile · pezzo unico · su richiesta · già adottato), `BottoneWhatsApp`, `FiltroCategoria`, `CardNegozio`, header, footer, empty state
- **Asset**: logo e favicon (servono i file originali del logo)

### 5.2 Design delle pagine (tipo *Design* di Claude)
Un canvas con le tavole di ogni pagina della sezione 4, in **mobile (390 px)** e **desktop (1440 px)**:
Home · Catalogo · Scheda prodotto (una per ognuno dei 4 stati) · Negozi · Admin review · catalogo vuoto.
- Contenuti **veri**, non segnaposto: 6–8 prodotti reali presi dalle foto `07_SHOWCASE` dello Studio
- Revisione con i commenti direttamente sul canvas
- **Massimo 2 giri di revisione per pagina.** Te lo dico chiaro: il rischio vero qui è restare settimane a limare i design invece di andare online

### 5.3 Dal design al codice
- I token del Design System diventano CSS variables + `tailwind.config.ts` di `vetrina/`: una sola fonte, niente colori scritti a mano nelle pagine
- Ogni componente del Design System diventa un componente React con lo stesso nome
- Dopo ogni pagina: screenshot mobile e desktop dell'app vera, confrontati con la tavola approvata

### 5.4 Skill da usare e quando

| Skill | Quando | A cosa serve |
|---|---|---|
| **Design System** (tipo artifact) | Fase 1 | Il design system del brand (5.1) |
| **Design** (tipo artifact, "Claude Design") | Fase 1 | Le tavole delle pagine (5.2) |
| `artifact-design` | Fase 1 | Le regole base per design curati, non generici |
| `anthropic-skills:artifact-emulator` | Fase 1 | Vedere i design come li vedrai tu prima di approvarli |
| `instagram-agent:ig-human` | Fasi 1 e 5 | Claim, microcopy e messaggi WhatsApp che non sanno di AI |
| `run` | Fasi 5–6 | Avviare la vetrina e fare gli screenshot da confrontare col design |
| `code-review` · `simplify` | Fine di ogni fase | Bug e pulizia del codice |
| `security-review` | Prima della messa online | Controllo di ingest con token e login admin |
| `frontend-design` (plugin ufficiale Anthropic) | Fasi 5–6 | **Oggi non è installato**: verificare che sia nel marketplace dei plugin e installarlo prima della Fase 5. Serve a evitare l'effetto "sito fatto con l'AI" nel codice |

---

## 6. Backend della vetrina

### 6.1 Ricerca del backend originale: esito
Volevi recuperare il backend che riceve le schede. Ho cercato ovunque fosse possibile il 27/10/2026:

| Dove | Esito |
|---|---|
| Tutte le chat Claude Code (35 sessioni, nov 2025 → oggi) | Nessuna traccia di vetrina, ingest o `admin/review` |
| Repo `App-Post-per-Instagram-` | No: è l'app AI Studio per i post |
| Repo `foto2post-easy` | No |
| Repo `azzurra-romagna` | No: è l'app dell'allenatore |
| `web-five-theta-58.vercel.app` | Oggi serve "Alfred"; `/admin/review` → 404 |
| Repo `jarvis-ai-coach`, `hermes-memory`, `automation-city-control-room` | **Non controllati**: l'accesso dalla sessione non è andato a buon fine. Da ricontrollare |
| "Ecosistema Monili" | Non esiste su GitHub, Google Drive o tra gli artifact: è una **cartella sul tuo PC**, da aprire con una sessione locale |

**Conclusione onesta:** il backend molto probabilmente **non è mai stato scritto**. Nel progetto è stato preparato solo il lato che invia (maggio 2026, commit `showcase`), con un indirizzo di destinazione "in attesa".
Ultimo controllo che puoi fare solo tu: nella **dashboard Vercel**, lo storico dei deploy del progetto dietro `web-five-theta-58`. Se prima di Alfred c'era la vetrina, lì si vede in un minuto.
Se non salta fuori niente, **lo costruiamo noi**: il contratto c'è già (sezione 2), quindi è lavoro definito, non un salto nel buio.

### 6.2 Dove vive
Dentro `vetrina/` come **Route Handlers di Next.js**, nello stesso progetto Vercel del sito.
Alternativa scartata: allargare il backend FastAPI dello Studio (`api/server.py`) su Render. Il piano free va in sleep e ha il disco temporaneo (è il motivo per cui esiste `docs/local-mode.md`), e il sito pubblico dipenderebbe dallo Studio acceso.

### 6.3 Cosa fa
1. **Riceve** le schede dallo Studio (`POST /api/ingest`)
2. **Conserva** prodotti e foto (Postgres + Blob)
3. **Serve** le pagine pubbliche (solo prodotti `published`)
4. **Ti fa decidere** cosa pubblicare (admin)

### 6.4 Dati
- **`products`**: tutti i campi della `product_fiche` + `status` (`draft` · `published` · `hidden`) + `published_at`, `created_at`, `updated_at`
- **`product_images`**: `product_id`, `url` Blob, `alt`, `position`
- **`ingest_log`**: ogni invio ricevuto (`run_id`, esito, errore, data), per capire subito perché un "Pubblica" non è arrivato

### 6.5 API

| Metodo | Percorso | Accesso | Cosa fa |
|---|---|---|---|
| `POST` | `/api/ingest` | `x-admin-token` | Valida la scheda, salva le foto su Blob, crea la bozza. Risponde `{ item: { id } }` |
| `GET` | `/api/admin/products?status=draft` | admin | Elenco per la pagina review |
| `PATCH` | `/api/admin/products/[id]` | admin | Modifica campi, approva, segna venduto, nasconde |
| `DELETE` | `/api/admin/products/[id]` | admin | Elimina prodotto e foto |
| `POST` | `/api/admin/login` · `/api/admin/logout` | pubblico | Password → cookie `httpOnly` firmato |
| `GET` | `/sitemap.xml` · `/robots.txt` | pubblico | Generati da Next |

### 6.6 Regole che non si toccano
- **Reinvio dello stesso prodotto**: se è ancora bozza si aggiorna; se è già pubblicato **non** si sovrascrive, si crea un "aggiornamento da approvare"
- **Token**: confronto a tempo costante, mai nei log; limite di dimensione del body e limite di richieste
- **Validazione** con `zod` sullo stesso schema del contratto; i testi scritti dall'AI (`story`, `summary`) si mostrano come testo semplice, mai come HTML
- **Test di contratto**: una scheda vera generata dallo Studio salvata come fixture, che deve passare la validazione della vetrina. Se uno dei due lati cambia il formato, il test si rompe subito

---

## 7. Fasi di lavoro

### Fase 0 — Pulizia (½ giornata)
- [ ] Decidere cosa fare del branch `claude/determined-knuth-zp63a6` (unire o archiviare)
- [ ] Togliere `` `r`n `` dall'hero di `frontend/src/app/page.tsx`
- [ ] Ripulire i commenti corrotti in `frontend/src/app/globals.css`
- [ ] Rimuovere il fallback `web-five-theta-58.vercel.app` da `ResultsPanel.tsx`: se `NEXT_PUBLIC_SHOWCASE_REVIEW_URL` manca, nascondere il link invece di puntare a un sito sbagliato
- [ ] Aggiungere `SHOWCASE_INGEST_URL`, `SHOWCASE_ADMIN_TOKEN`, `NEXT_PUBLIC_SHOWCASE_REVIEW_URL` a `.env.example` e `render.yaml` (`sync: false`)

### Fase 1 — Design con Claude Design (1–2 giornate)
- [ ] Design System "I Monili Ravenna" impostato come predefinito (5.1)
- [ ] Canvas Design con tutte le tavole mobile + desktop (5.2)
- [ ] Testi del sito passati con `ig-human`
- [ ] **Approvazione tua**, max 2 giri per pagina → solo dopo si passa al codice

### Fase 2 — Scheletro vetrina (1 giornata)
- [ ] `vetrina/` con Next.js 15 + TypeScript + Tailwind (stesse versioni di `frontend/`)
- [ ] Token presi dal Design System approvato → CSS variables + `tailwind.config.ts`
- [ ] Componenti base del Design System in React
- [ ] Tipo `ProductFiche` condiviso + validazione con `zod`
- [ ] Layout base: header, footer con negozi/Instagram, bottone WhatsApp fisso

### Fase 3 — Backend: ingest e dati (1 giornata)
- [ ] Schema DB `products` (campi del contratto + `status: draft|published|hidden`, `images` come URL Blob)
- [ ] `POST /api/ingest` con controllo `x-admin-token`
- [ ] Modifica `api/server.py`: max 4 immagini per invio (vedi §3)
- [ ] Test end-to-end: Studio locale → "Pubblica sul sito vetrina" → bozza visibile nel DB

### Fase 4 — Admin review (1 giornata)
- [ ] Login con password + cookie
- [ ] `/admin/review` con approva / modifica / venduto / nascondi
- [ ] `revalidatePath` su home, catalogo e scheda dopo ogni azione

### Fase 5 — Pagine pubbliche (2 giornate)
- [ ] Home, Catalogo, Scheda prodotto, Negozi (vedi §4), fedeli alle tavole approvate in Fase 1
- [ ] Screenshot mobile + desktop con `run`, confronto con il design
- [ ] Messaggi WhatsApp per i 4 preset
- [ ] Empty state gentile quando il catalogo è vuoto ("Stiamo allestendo la vetrina ✨")

### Fase 6 — SEO locale e rifinitura (1 giornata)
- [ ] Metadata per pagina, Open Graph, JSON-LD `Product` e `LocalBusiness` (×2 negozi)
- [ ] `sitemap.xml`, `robots.txt`
- [ ] `next/image` con dimensioni 4:5, Lighthouse mobile ≥ 90
- [ ] Controllo da iPhone reale (il target guarda da telefono)
- [ ] `code-review` + `security-review` sul codice della vetrina

### Fase 7 — Messa online (½ giornata)
- [ ] Progetto Vercel con root `vetrina/`, env `DATABASE_URL`, `BLOB_READ_WRITE_TOKEN`, `SHOWCASE_ADMIN_TOKEN`, `ADMIN_PASSWORD`
- [ ] Dominio personalizzato
- [ ] Impostare su Render/locale `SHOWCASE_INGEST_URL=https://<dominio>/api/ingest` e `NEXT_PUBLIC_SHOWCASE_REVIEW_URL=https://<dominio>/admin/review`
- [ ] Collegare il link al sito nel profilo Google Business e nella bio Instagram

**Totale stimato: 7–9 giornate di lavoro** (la fase design aggiunge 1–2 giornate, ma riduce i rifacimenti dopo).

---

## 8. Criteri di "fatto"

- Dallo Studio premo "Pubblica sul sito vetrina" e in < 1 minuto la bozza compare in `/admin/review`
- Con "Approva" il prodotto è online su home, catalogo e scheda, senza rideploy
- Una scheda si apre su iPhone in < 2 s e il bottone WhatsApp apre il messaggio giusto
- Un prodotto venduto resta indicizzato e propone "simili"
- Nessun link nello Studio punta più a domini che non sono nostri
- Le pagine online corrispondono alle tavole approvate in Claude Design

---

## 9. Domande aperte (da decidere tu)

1. **Branch `determined-knuth`**: lo uniamo a `master` prima di partire? (consiglio: sì, se il Reel Studio lo usi davvero)
2. **Dominio**: ne hai già uno (es. `imoniliravenna.it`) o lo compriamo?
3. **Prezzi**: vuoi mostrarli sul sito o sempre "Chiedi in negozio"? Oggi lo Studio manda sempre `price: null`, quindi andrebbero inseriti a mano in admin.
4. **Orari e numero WhatsApp** dei due negozi di via Cavour: servono i dati veri.
5. **Backend originale**: due controlli che puoi fare solo tu (vedi 6.1):
   - la cartella **"Ecosistema Monili"** sul tuo PC (non è su GitHub né su Google Drive, quindi dal cloud non la vedo)
   - lo storico deploy su Vercel di `web-five-theta-58`
   Se non salta fuori niente, lo costruiamo noi.
6. **Logo**: hai i file originali (SVG o PNG ad alta risoluzione) per il Design System?
7. **Plugin `frontend-design`**: lo installiamo prima della Fase 5?
