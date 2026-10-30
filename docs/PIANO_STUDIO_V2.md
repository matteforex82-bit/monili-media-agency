# Piano — Studio AI v2: più bello, più semplice dal telefono, fino a Instagram

> Creato il 30/10/2026 dopo il controllo dello Studio in formato iPhone. Stato: **approvato da Matteo per la Fase A** (le decisioni della sezione 0 sono ancora aperte).
> Strumenti di design: skill **Impeccable** (guide `shape` e `operate`; il suo programma di controllo resta non autorizzato) e **frontend-design**.
> **Chi esegue questo piano legga prima la sezione 7.**

## 0. Decisioni che spettano a Matteo

1. **Ordine di lavoro**: Fase A (correzioni) prima della prova del weekend, tutto il resto dopo la prova? *Consiglio: sì.*
2. **I "bot" con i nomi** (Anna, Dario, Vera, Carla, Paolo) nei risultati: li teniamo o li sostituiamo con i passaggi in chiaro (Analisi, Foto, Testi)? *Consiglio: passaggi in chiaro, meno rumore sul telefono.*
3. **Instagram**: prima il pulsante "Condividi su Instagram" (funziona subito, nessuna configurazione), poi la pubblicazione automatica? *Consiglio: sì, in quest'ordine.*
4. **Carosello di slide** come facevi su ChatGPT: lo vogliamo nello Studio? I numeri dicono che i post statici fanno il 3,7% delle visualizzazioni, ma servono per il feed e per chi ti segue già. *Consiglio: dopo Reel e Storie, come formato in più.*

---

## 1. Cosa non va oggi (controllo del 30/10, iPhone 375 px)

Funziona: carica foto → Scheda pezzo → risultati → pubblica sul sito (anche "Pubblica subito") → "Fai il Reel di questo pezzo" con la stessa donna → Skill.

Da correggere:
1. **"Invia bozza" sta in cima**, sopra prezzo e negozio: si compilano i campi e si deve risalire.
2. **Etichette delle foto generiche** ("Foto dedicata sito 4:5" due volte, "Foto sito 1/2"): non si capisce quale controllare per la fedeltà.
3. **Le foto del pannello sito occupano ognuna tutto lo schermo**: sul telefono servono due per riga.
4. **"Pubblica subito" ha il testo più grande** del resto del pannello.
5. **Reel partito dalla scheda: la foto del prodotto va ricaricata** a mano, anche se lo Studio ce l'ha già.
6. **Testi vecchi**: Home "lascia scegliere al team AI il contenuto più adatto" (ora è sempre la Scheda pezzo), accenti mancanti ("piu", "Il flusso e semplice"), `/indossato` dice "diversa in ogni Reel" invece di "una per pezzo", cronologia con nomi tecnici (`single_post`, `scheda_pezzo`, nome del file).
7. **"È un altro pezzo"** spezza il testo del riquadro nel Reel.

Problemi più grandi, di struttura:
- **Non c'è una casa del pezzo.** Scheda, sito, Reel e Instagram sono in pagine separate e il collegamento si perde (la cronologia mostra missioni, non pezzi).
- **Navigazione incoerente**: dalla Home non si arriva a Skill e Risultati; nel Reel Studio c'è una barra diversa ("← Foto · Skill · Risultati").
- **Due mondi grafici**: lo Studio usa Instrument Serif + Manrope, il sito usa Cormorant + Outfit (Design System v2).
- **Campi file nativi** ("Scegli file") nel Reel Studio, mentre in Home c'è il bel riquadro di caricamento.
- **Instagram manca del tutto**: lo Studio prepara video e testi, poi tocca salvarli e incollarli a mano.

---

## 2. Direzione di design

**Lavoro e persona**: Matteo, in negozio o in giro, dal telefono, spesso con una mano sola e poco tempo. Modalità *Operate*: deve finire un compito (pubblicare un pezzo) senza pensarci. La bellezza sta nei dettagli precisi, non negli effetti.

**Idea guida: "il bancone"**. Il protagonista di ogni schermata è **il pezzo** (la sua foto vera, grande), come quando lo appoggi sul bancone per mostrarlo. Tutto il resto è attrezzatura discreta intorno.

**Un solo elemento memorabile: la tessera di mosaico.** L'avanzamento di un pezzo (Scheda → Sito → Reel → Instagram) è una fila di 4 tessere che si colorano con i colori della foto del pezzo quando ogni passaggio è fatto. Richiama Ravenna, dice a colpo d'occhio a che punto sei, ed è l'unica decorazione. Niente altre animazioni d'ingresso, niente gradienti decorativi.

**Stessa famiglia del sito** (non un mondo nuovo):
| Ruolo | Scelta |
|---|---|
| Titoli e nome del pezzo | Cormorant Garamond (come il sito) |
| Testi, pulsanti, campi | Outfit (come il sito) |
| Fondo | avorio caldo del sito |
| Azione principale | terracotta `#c8593a`, testo su terracotta `#9e4128` per il contrasto |
| Fatto / venduto | verde e rosso del sito (`#3a6b3a`, `#b3261e`), oro `#c79849` solo per "Pezzo unico" |

Regole di scrittura: frasi brevi, verbi chiari, lo stesso nome per la stessa azione in tutto il flusso ("Pubblica" → "Pubblicato"); niente etichette maiuscole sopra ogni blocco, niente frecce "→" appese ai pulsanti, niente nomi tecnici.

Qualità minima: tutto usabile con il pollice (pulsanti ≥ 44 px), focus visibile, contrasto AA, `prefers-reduced-motion` rispettato, nessuno scroll orizzontale a 375 px.

---

## 3. Nuova struttura

### 3.1 Barra in basso (telefono), sempre uguale

```
┌─────────────────────────────────┐
│                                 │
│          (schermata)            │
│                                 │
├────────┬────────┬───────┬───────┤
│ Nuovo  │ Pezzi  │ Reel  │ Altro │
│ pezzo  │        │       │       │
└────────┴────────┴───────┴───────┘
```
- **Nuovo pezzo**: foto → Scheda pezzo (la Home di oggi, semplificata).
- **Pezzi**: tutti i pezzi, dal più recente, con le 4 tessere di stato. Sostituisce la cronologia.
- **Reel**: Reel Studio (anche senza scheda).
- **Altro**: Skill (Base donne, Mai nei contenuti, ricette), Risultati, impostazioni.
Su computer la stessa barra diventa una colonna a sinistra.

### 3.2 La pagina del pezzo (il cuore della v2)

```
┌─────────────────────────────────┐
│ ‹ Pezzi                         │
│ ┌─────────────────────────────┐ │
│ │      foto vera del pezzo    │ │
│ └─────────────────────────────┘ │
│ Borsa a tracolla in cuoio       │  ← Cormorant
│ ■ ■ □ □   Scheda · Sito fatti   │  ← tessere di mosaico
│                                 │
│ 1  Foto per il sito             │
│   [Catalogo AI] [Indossata AI]  │  ← 2 per riga, spunta grande
│   [Foto vera ripulita]          │
│ 2  Prezzo, negozio, taglia      │
│ 3  [ ] Pubblica subito          │
│   ( Invia bozza )               │  ← pulsante SOTTO i campi
│                                 │
│ Testi: WhatsApp · Google · IG   │  ← copia con un tocco
│                                 │
│ Reel di questo pezzo            │
│   ( Fai il Reel )  stessa donna │  ← riusa la foto, niente upload
│                                 │
│ Instagram                       │
│   ( Condividi su Instagram )    │
└─────────────────────────────────┘
```
Qui i numeri 1-2-3 hanno senso perché sono davvero una sequenza.

### 3.3 Nuovo pezzo (Home)
Riquadro di caricamento grande, nota facoltativa, un pulsante "Crea la scheda". I motori immagine finiscono in "Altro → Impostazioni" (si sceglie una volta, non a ogni pezzo). Durante la creazione: la foto del pezzo al centro e le tessere che si colorano mentre lavorano Analisi, Foto, Testi.

---

## 4. Fasi di lavoro

### Fase A — Correzioni prima della prova (½ giornata) ← **prima del weekend**
- [ ] Pulsante "Invia bozza / Pubblica subito" sotto i campi (punto 1)
- [ ] Etichette: "Catalogo (AI)", "Indossata (AI)", "Foto vera ripulita", anche nei download (punto 2)
- [ ] Foto del pannello sito 2 per riga sul telefono (punto 3)
- [ ] Testo di "Pubblica subito" allineato agli altri (punto 4)
- [ ] Reel dalla scheda riusa la foto della scheda: la backend copia la foto di origine della missione se non ne carichi altre (punto 5)
- [ ] Testi: Home, accenti, `/indossato` "una per pezzo", cronologia con nome del pezzo e data leggibile (punto 6)
- [ ] "È un altro pezzo" su una riga sua (punto 7)
- [ ] Test + controllo dei tipi + giro di screenshot a 375 px

### Fase B — Restyling e pagina del pezzo (1½–2 giornate, dopo la prova)
- [ ] Token comuni con il sito (font Cormorant + Outfit, colori del Design System v2) in `globals.css`; via i token dei bot non più usati
- [ ] Barra in basso / colonna a sinistra comune a tutte le pagine
- [ ] Pagina **Pezzi** con le tessere di stato (dati: missioni + bozze inviate + Reel collegati + post Instagram)
- [ ] Pagina **del pezzo** (3.2): unisce risultati, pubblicazione sul sito, Reel e Instagram
- [ ] Nuovo pezzo semplificato (3.3); motori in Impostazioni
- [ ] Reel Studio: caricamento foto/clip con lo stesso riquadro della Home, ricette in una lista compatta
- [ ] Stati vuoti, di attesa e di errore scritti bene ("Nessun pezzo ancora: fotografa il primo")
- [ ] Revisione con `design:accessibility-review` e una critica finale (Impeccable `critique`/`polish`, solo guide)

### Fase C — Instagram
**C1. "Condividi su Instagram" (½ giornata, subito dopo la prova)**
- [ ] Nel risultato del Reel e nella pagina del pezzo: un pulsante apre il menu di condivisione dell'iPhone con il video (o le foto) già pronti; la caption con gli hashtag viene copiata negli appunti. Scegli Instagram → Reel/Storia/Post e incolli la caption.
- [ ] Promemoria "Attiva *Info sull'AI*" se ci sono donne generate.
- Nessun account sviluppatore, nessun token. Limite: un tocco in più dentro Instagram.

**C2. Pubblicazione automatica dallo Studio (1–1½ giornate, quando C1 è rodato)**
- Strada ufficiale: **Instagram API con login Instagram** (account professionale Business o Creator; permessi `instagram_business_basic` e `instagram_business_content_publish`). Supporta Reel, Storie, post singoli e caroselli. I file devono stare a un indirizzo pubblico: usiamo l'archivio Blob del sito, dove i Reel e le foto finiscono già.
- [ ] Matteo: account Instagram professionale (se non lo è già) e app Meta per sviluppatori, con lui come tester (lo guido io)
- [ ] Studio: collegamento dell'account (token a lunga durata, rinnovo automatico), pulsanti "Pubblica Reel / Storia / Post", eventuale programmazione all'orario scelto
- [ ] Limiti da rispettare: massimo di post al giorno fissato da Meta (verificare il numero sulla documentazione), formati video
- Da verificare prima di costruire: se l'API permette l'etichetta "Info sull'AI" (se no, si pubblica da C1 per i contenuti con donne AI) e l'audio dei Reel con il login Instagram.

### Fase D — Motori per le immagini (decisione dopo la prova)
Oggi: **OpenRouter con la tua chiave**. Foto della scheda e fotogrammi del Reel con **"Images 2"** (`openai/gpt-5.4-image-2`, predefinito); in alternativa **Gemini** (`google/gemini-3.1-flash-image`, `google/gemini-3-pro-image`, cioè Nano Banana). Se un giorno metti `OPENAI_API_KEY`, i fotogrammi possono usare GPT-Image-2.5 direttamente. **Higgsfield** oggi serve solo ai video (Kling, Seedance).
- Higgsfield sa fare anche immagini (ospita Nano Banana Pro, GPT Image, Seedream e il suo Soul), ma a crediti con abbonamento mensile; OpenRouter si paga a immagine, senza abbonamento.
- [ ] Alla prima Scheda pezzo vera: stesso pezzo con Images 2 e con Gemini 3 Pro, confronto di fedeltà e costo
- [ ] Decisione: restare su OpenRouter per le foto (consiglio, se la fedeltà regge) o spostare tutto su Higgsfield se l'abbonamento conviene con i volumi reali

### Fase E — Libreria di movimenti per i Reel (½ giornata, dal PDF "Gemini video codes")
Il PDF di John Savage contiene 163 idee di video pubblicitari per **Gemini/Veo** (video, non foto). I "codici" con la barra non sono comandi segreti: è la descrizione dopo il codice che fa il lavoro. Si usa come ispirazione, non come regole fisse.
- [ ] In `skills/_base/movimento.md` una lista breve di movimenti adatti allo stile del negozio, scritti da noi (es. seta che avvolge il pezzo e lo libera, luce che scorre sulla pietra, riflessi d'acqua, foglie e fiori che si muovono intorno, sipario che si apre, il pezzo in mano, vetrina del negozio, tavolino di un caffè, regalo con nastro e luci calde, passaggio da una scena all'altra seguendo il pezzo). Il regista ne può scegliere uno per Reel, libero di inventare altro
- [ ] Esclusi perché contro "Mai nei contenuti" o lo stile: fuoco, neon, cyberpunk, mascotte, gatti e cani, esplosioni, scritte TV
- [ ] Tre consigli del PDF nei prompt: pezzo grande e intero nell'inquadratura; partire dalla foto vera, non da un render; per le "rivelazioni" usare la foto come riferimento e non come primo fotogramma (il controllo qualità che rigenera se il pezzo cambia forma c'è già)

### Fase F — Carosello editoriale (facoltativa, 1 giornata)
- [ ] Formato "Carosello" nello Studio: 3–5 slide 4:5 nello stile dei post migliori del feed (serif su avorio: "Non sono semplici orecchini."), foto del pezzo + slide di testo + chiusura con invito
- [ ] Riusa il motore della copertina poster del Reel Studio e il controllo del testo scritto giusto
- [ ] Si pubblica con C1 o C2

---

## 5. Come verifichiamo ogni fase
- `python -m pytest tests` e `npx tsc --noEmit` verdi prima di ogni commit
- Giro di screenshot a 375 px (iPhone) e a computer su: Nuovo pezzo, Pezzi, pagina del pezzo, Reel, Altro
- Missione di prova con AI simulata (gratis), poi cancellata, per vedere i risultati senza spendere
- Nessun invio vero al sito o a Instagram durante i test, salvo prova esplicita con Matteo

## 6. Rischi
- **Restyling durante la prova**: per questo la Fase B parte dopo il weekend, la Fase A tocca solo testi e posizioni.
- **Instagram API**: Meta cambia spesso regole e limiti; per questo prima C1 (non dipende da Meta).
- **Piano Hobby di Vercel**: la pubblicazione automatica su Instagram usa l'archivio Blob del sito; prima del lancio pubblico serve la decisione su Vercel Pro (vedi `PLAN_VETRINA.md`, Fase 5).

---

## 7. Istruzioni per chi esegue (qualunque modello, anche in una sessione nuova)

### 7.1 Prima di cominciare
1. Leggi `CLAUDE.md`, questo file per intero e `docs/STATO_PROGETTO.md`. Il contesto del sito è in `PLAN_VETRINA.md` (Fase 5).
2. Lavora sul repo `monili-media-agency`, branch `master`, cartella sul PC `C:\Users\matte\Desktop\PROGETTI AI\monili-deploy-temp`. `git pull` prima di toccare qualcosa.
3. **Una fase per volta**, nell'ordine. Ora tocca alla **Fase A**. Le Fasi B–F partono solo dopo la prova del weekend e con l'ok di Matteo.
4. **Decisioni della sezione 0**: non deciderle da solo. Per la Fase A non servono. Prima della Fase B chiedile a Matteo, una alla volta, con il consiglio già scritto.
5. Matteo vuole risposte in italiano, brevi, dirette e sincere.

### 7.2 Regole che non si discutono
- **Lo Studio è collegato al sito vero** (`https://monili-vetrina.vercel.app`, impostato nel `.env`). Durante le prove **non premere mai "Invia bozza" o "Pubblica subito"** e non chiamare `/missions/{id}/showcase/publish` né `/reel/{id}/showcase/publish`: un pezzo finto andrebbe online. Per provare l'invio servono Matteo e un pezzo vero.
- **Non spendere**: niente missioni vere (costano OpenRouter) senza ok. Per vedere i risultati usa la missione simulata (7.3).
- **Push su `master` solo con l'ok esplicito di Matteo.** Commit con messaggio chiaro e la riga `Co-Authored-By` del modello.
- Prima di ogni commit: `python -m pytest tests` (senza rete né chiavi) e `npx tsc --noEmit` in `frontend/`. Il lint del frontend non esiste.
- Segreti (chiavi, token, password admin): mai nel codice, nei documenti o in chat. Stanno nel `.env` e in `C:\Users\matte\MoniliStorage\vetrina-accesso-admin.txt`.
- **Impeccable**: le guide sono in `C:\Users\matte\Desktop\PROGETTI AI\Ecosistema Monili\.claude\skills\impeccable\reference\` (per la Fase A bastano `craft-floor.md`, `clarify.md`, `adapt.md`). Il programma `scripts/impeccable` **non** va lanciato.
- Le regole dei contenuti si cambiano in `skills/*.md`, non nel codice.

### 7.3 Come vedere lo Studio senza spendere
1. Avvia backend e frontend: `.claude/launch.json` ha `studio-backend` (porta 8000) e `studio-frontend` (porta 3000). Con l'anteprima del browser: `preview_start` con quei nomi. A mano: `python -m uvicorn api.server:app --port 8000` dalla cartella del progetto e `npm --prefix frontend run dev:local`. Il primo caricamento di ogni pagina richiede 20–30 secondi (modalità sviluppo).
2. Guarda le pagine a **375 px** (iPhone) e a computer: `/` (Nuovo pezzo), risultati di una missione, `/reel`, `/reel?pezzo=<run_id>`, `/skills`, `/risultati`.
3. Missione di prova gratuita: `python scripts/prova_scheda_simulata.py --foto C:/Users/matte/MoniliStorage/input/2026-05-17_083526_4a89af2a.jpeg`. Compare in cronologia come "Prova con AI simulata (PROVA)"; si apre con "Apri". **Alla fine**: `python scripts/prova_scheda_simulata.py --pulisci` (cancella la prova e rimette la memoria com'era).
4. Spegni i server di prova quando hai finito: Matteo avvia lo Studio con l'icona "Avvia Studio Monili" sul Desktop.

### 7.4 Fase A, punto per punto (dove e quando è fatto)
Numeri di riga al 30/10/2026 (commit `08f9007`): verifica sempre con una ricerca prima di modificare.

| # | Dove | Cosa cambiare | Fatto quando |
|---|---|---|---|
| 1 | `frontend/src/components/ResultsPanel.tsx`, `ShowcasePublishPanel` (riga ~180): pulsante alle righe ~287–297 dentro `.result-actions` | Il pulsante "Invia bozza / Pubblica subito" va **sotto** la casella "Pubblica subito" (riga ~342) e sopra le foto; "Rianalizza" può restare in alto | A 375 px compili categoria, negozio, prezzo, casella e premi il pulsante senza risalire |
| 2 | Stesso file: etichetta riga ~373, `alt` riga ~369, titoli dei download riga ~470 (`Foto sito ${index + 1}`) | Etichette per tipo di foto: `site_01_product_clean` → "Catalogo (AI)", `site_02_worn` → "Indossata (AI)", `site_03_real_photo` → "Foto vera ripulita"; foto delle missioni vecchie → "Foto (vecchio kit)". Riconoscile dal nome del file, non dall'ordine | Ogni foto dice cos'è, uguale nel pannello sito e nei download |
| 3 | `frontend/src/app/globals.css`: media query a riga ~699 forza `.result-image-grid.compact` a una colonna | Sul telefono `.compact` a **2 colonne**, spunta grande e facile da toccare (≥ 44 px) | A 375 px le 3 foto stanno in 2 righe e si spuntano col pollice |
| 4 | `globals.css`, `.showcase-publish-now` (cercalo) | Stessa dimensione di testo delle altre etichette del pannello | Il testo non è più grande del resto |
| 5 | `api/server.py`, `reel_create` (riga ~1447: `photos: list[UploadFile] = File(...)`) e `_scheda_woman` (riga ~1427); `frontend/src/app/reel/page.tsx`, `createReel` (riga ~405) e `PieceBanner` (riga ~1248) | Se il Reel parte da una scheda (`scheda_run_id`) e non carichi foto, la backend copia in `input/photo_1.jpg` la foto di origine della missione (`run_manifest.json` → `source_photo`, percorso completo nel manifest). Nel frontend, con un pezzo collegato, il caricamento foto diventa facoltativo e il riquadro dice "Usiamo la foto della scheda" | Da "Fai il Reel di questo pezzo" si crea il Reel senza caricare nulla; senza scheda resta obbligatorio caricare una foto. Test nuovo in `tests/test_scheda_pezzo.py` (sul modello di `test_reel_of_this_piece_keeps_the_same_woman`) |
| 6 | `frontend/src/app/page.tsx`: riga ~557 (testo Home), ~714 ("Il flusso e semplice"), ~374 ("puo", "piu"); cronologia righe ~938–941; `skills/indossato.md` riga 3; `api/server.py` `_history_item_from_payload` (riga ~165) | Home: "Carica la foto del pezzo, aggiungi una nota se serve: lo Studio prepara la scheda per il sito, WhatsApp e Google." Accenti corretti in tutto il file. `/indossato`: "Una donna vera, una per pezzo, indossa il prodotto - hook, dettaglio, look, chiusura." Cronologia: la backend aggiunge `title` (= `product_name` del pacchetto testi) e il frontend mostra titolo (o il brief) + data leggibile, senza `single_post`/`scheda_pezzo`/nome file | Nessun testo senza accento, nessun nome tecnico visibile a Matteo |
| 7 | `frontend/src/app/reel/page.tsx`, `PieceBanner` (riga ~1248) | "È un altro pezzo" su una riga sua, sotto il testo, allineato a sinistra | Il riquadro si legge senza interruzioni a 375 px |

Chiusura della Fase A:
- [ ] `python -m pytest tests` e `npx tsc --noEmit` verdi
- [ ] Giro di screenshot a 375 px con la missione simulata (poi `--pulisci`)
- [ ] Caselle della Fase A spuntate in questo file, riga in `docs/STATO_PROGETTO.md`
- [ ] Commit; push solo dopo l'ok di Matteo
- [ ] Riassunto a Matteo: cosa è cambiato, cosa non è stato verificato
