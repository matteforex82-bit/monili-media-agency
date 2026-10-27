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

### API della vetrina
- `POST /api/ingest` — riceve la `product_fiche`, valida, salva immagini su Blob, crea/aggiorna il record come `draft`. Idempotente sullo stesso `id`.
- `PATCH /api/admin/products/[id]` — modifiche e cambio stato (protetta)
- `DELETE /api/admin/products/[id]` (protetta)
- `GET /sitemap.xml`, `/robots.txt` generati da Next

---

## 5. Fasi di lavoro

### Fase 0 — Pulizia (½ giornata)
- [ ] Decidere cosa fare del branch `claude/determined-knuth-zp63a6` (unire o archiviare)
- [ ] Togliere `` `r`n `` dall'hero di `frontend/src/app/page.tsx`
- [ ] Ripulire i commenti corrotti in `frontend/src/app/globals.css`
- [ ] Rimuovere il fallback `web-five-theta-58.vercel.app` da `ResultsPanel.tsx`: se `NEXT_PUBLIC_SHOWCASE_REVIEW_URL` manca, nascondere il link invece di puntare a un sito sbagliato
- [ ] Aggiungere `SHOWCASE_INGEST_URL`, `SHOWCASE_ADMIN_TOKEN`, `NEXT_PUBLIC_SHOWCASE_REVIEW_URL` a `.env.example` e `render.yaml` (`sync: false`)

### Fase 1 — Scheletro vetrina (1 giornata)
- [ ] `vetrina/` con Next.js 15 + TypeScript + Tailwind (stesse versioni di `frontend/`)
- [ ] Design tokens riusati da `frontend/src/app/globals.css` (`--bot-bg #f8f3e6`, `--bot-accent #c8593a`, `--bot-gold #c79849`, Instrument Serif + Manrope) con sfondo più chiaro, verso il bianco ottico, per la parte pubblica
- [ ] Tipo `ProductFiche` condiviso + validazione con `zod`
- [ ] Layout base: header, footer con negozi/Instagram, bottone WhatsApp fisso

### Fase 2 — Ingest e dati (1 giornata)
- [ ] Schema DB `products` (campi del contratto + `status: draft|published|hidden`, `images` come URL Blob)
- [ ] `POST /api/ingest` con controllo `x-admin-token`
- [ ] Modifica `api/server.py`: max 4 immagini per invio (vedi §3)
- [ ] Test end-to-end: Studio locale → "Pubblica sul sito vetrina" → bozza visibile nel DB

### Fase 3 — Admin review (1 giornata)
- [ ] Login con password + cookie
- [ ] `/admin/review` con approva / modifica / venduto / nascondi
- [ ] `revalidatePath` su home, catalogo e scheda dopo ogni azione

### Fase 4 — Pagine pubbliche (2 giornate)
- [ ] Home, Catalogo, Scheda prodotto, Negozi (vedi §4)
- [ ] Messaggi WhatsApp per i 4 preset
- [ ] Empty state gentile quando il catalogo è vuoto ("Stiamo allestendo la vetrina ✨")

### Fase 5 — SEO locale e rifinitura (1 giornata)
- [ ] Metadata per pagina, Open Graph, JSON-LD `Product` e `LocalBusiness` (×2 negozi)
- [ ] `sitemap.xml`, `robots.txt`
- [ ] `next/image` con dimensioni 4:5, Lighthouse mobile ≥ 90
- [ ] Controllo da iPhone reale (il target guarda da telefono)

### Fase 6 — Messa online (½ giornata)
- [ ] Progetto Vercel con root `vetrina/`, env `DATABASE_URL`, `BLOB_READ_WRITE_TOKEN`, `SHOWCASE_ADMIN_TOKEN`, `ADMIN_PASSWORD`
- [ ] Dominio personalizzato
- [ ] Impostare su Render/locale `SHOWCASE_INGEST_URL=https://<dominio>/api/ingest` e `NEXT_PUBLIC_SHOWCASE_REVIEW_URL=https://<dominio>/admin/review`
- [ ] Collegare il link al sito nel profilo Google Business e nella bio Instagram

**Totale stimato: 6–7 giornate di lavoro.**

---

## 6. Criteri di "fatto"

- Dallo Studio premo "Pubblica sul sito vetrina" e in < 1 minuto la bozza compare in `/admin/review`
- Con "Approva" il prodotto è online su home, catalogo e scheda, senza rideploy
- Una scheda si apre su iPhone in < 2 s e il bottone WhatsApp apre il messaggio giusto
- Un prodotto venduto resta indicizzato e propone "simili"
- Nessun link nello Studio punta più a domini che non sono nostri

---

## 7. Domande aperte (da decidere tu)

1. **Branch `determined-knuth`**: lo uniamo a `master` prima di partire? (consiglio: sì, se il Reel Studio lo usi davvero)
2. **Dominio**: ne hai già uno (es. `imoniliravenna.it`) o lo compriamo?
3. **Prezzi**: vuoi mostrarli sul sito o sempre "Chiedi in negozio"? Oggi lo Studio manda sempre `price: null`, quindi andrebbero inseriti a mano in admin.
4. **Orari e numero WhatsApp** dei due negozi di via Cavour: servono i dati veri.
5. **Esisteva un vecchio progetto vetrina** (quello deployato su `web-five-theta-58.vercel.app`) in un altro repository? Se sì, valutiamo se recuperarlo invece di ripartire da zero.
