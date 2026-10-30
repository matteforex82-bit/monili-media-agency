# Piano — Studio AI v2: più bello, più semplice dal telefono, fino a Instagram

> Creato il 30/10/2026 dopo il controllo dello Studio in formato iPhone. Stato: **da approvare** (Matteo).
> Strumenti di design: skill **Impeccable** (guide `shape` e `operate`; il suo programma di controllo resta non autorizzato) e **frontend-design**.

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
