# STATO DI REALIZZAZIONE — ripresa del lavoro

Aggiornato il 05/11/2026. Implementazione verificata in locale il 02/11; **dal 03–04/11 le pagine legali sono online** (controllato il 05/11: `/privacy`, `/cookie`, `/condizioni-vendita` rispondono 200 su https://monili-vetrina.vercel.app). Le condizioni di vendita sono state riscritte il 4/11 per la nuova prassi (vedi PRD Journey §17.2 voce 5).

## Aggiornamento 05/11/2026 (cosa è cambiato rispetto al 02/11)
- **Pubblicato:** footer, pagine legali, WhatsApp centrale del 21, condizioni di vendita nuove. `/consulenza` è 404 per scelta finché non c'è il link Calendly reale, e privacy/cookie citano Calendly solo con il link attivo.
- **Controllato online il 05/11:** privacy senza paragrafo Calendly (corretto); **conservazione delle richieste ancora generica** («tempo necessario», nessun termine: la decisione sui 6 mesi non è presa); catalogo con **2 pezzi, 6 immagini, nessuna marcata `aiGenerated`** (da classificare foto per foto).
- **Nuovo punto sull'hosting:** le regole Vercel (fair use, letto il 05/11) limitano i team **Hobby all'uso personale non commerciale**; l'uso commerciale richiede Pro o Enterprise. Il sito è su Hobby: la scelta del piano è una decisione e una spesa del titolare.
- **Regola di aggiornamento della privacy per Calendly:** Calendly è un terzo che riceve nome, e-mail e numero WhatsApp di chi prenota; il paragrafo c'è già ma si accende col link. Verificare sull'ambiente reale dopo J07.
- **Decisioni di Matteo del 5/11:** (1) richieste senza ordine conservate **un mese** dalla fine del contatto, poi cancellate: testo della privacy **pubblicato il 5/11** (commit 8d1cf2b del sito, verificato online); resta da scegliere chi cancella e come; (2) hosting: **resta Hobby per ora, poi Pro**; (3) le **6 immagini online sono tutte da marcare come IA**: **fatto il 5/11** con `scripts/marca_immagini_ia.py` (lanciato da Matteo, 3/3 immagini per pezzo), verificato online: `aiGenerated` vero sulle 6 immagini e badge nelle due schede.
- **Elenco unico di ciò che serve da Matteo:** `docs/interventi-richiesti-matteo.md` (voci 4, 6, 8–13).
- Le caselle sotto restano come erano, salvo quelle indicate qui.

Il PRD originale conservato sotto è riferimento storico. Per stato e rettifiche prevalgono questa sezione e il memo `Ecosistema Monili/apps/web/docs/PRD_GDPR_AI_ACT.md`.

## Sorgente corretta
- Vetrina: `C:/Users/matte/Desktop/PROGETTI AI/Ecosistema Monili/apps/web`.
- Repository: `https://github.com/matteforex82-bit/monili-vetrina.git`.
- `monili-deploy-temp` è lo Studio e contiene il PRD: non implementare qui le pagine pubbliche.

## Completato e verificato in locale
- [x] Configurazione legale centralizzata, recapiti reali distinti per negozio; nessun codice fiscale personale dedotto dalla P.IVA.
- [x] Footer globale e pagine `/privacy`, `/cookie`, `/condizioni-vendita`, canonical e sitemap.
- [x] Font WOFF2 locali con licenze, link social statici protetti senza SDK.
- [x] Metadato `images[].aiGenerated` e badge per singola immagine nei flussi dati/gallery; video hero IA etichettato. Catalogo pregresso non classificato automaticamente.
- [x] `docs/OPERAZIONI_NEGOZIO.md`: modelli contatto, conferma ordine, recesso e consenso marketing.
- [x] Rettifiche documentate nel memo: rimborso/recesso, DPA Vercel non universale, immagine IA non automaticamente deepfake, nessuna promessa di cancellazione a sei mesi non approvata.
- [x] Typecheck e lint PASS; 32/32 test PASS; build produzione PASS (25 pagine statiche).
- [x] Audit browser locale: 122 asserzioni, 14 navigazioni/viewport, 648 richieste same-origin; nessun cookie/storage visitatore o errore JS/richiesta fallita osservati.

Test in copia isolata senza .env, dati o DB produzione. Non certificano il sito online o la conformità legale complessiva. Hover fisico desktop non verificato (host hover:none).

## Da completare / decisioni del titolare
- [ ] Confermare piano hosting commerciale, DPA, fornitori e trasferimenti applicabili; nessun acquisto o cambio piano effettuato.
- [ ] Approvare conservazione delle richieste senza ordine e responsabile della pulizia; sei mesi resta una proposta, nessuna cancellazione automatica implementata.
- [ ] Confermare che pagamenti, spedizioni, resi e conferme su supporto durevole corrispondano alla prassi reale; validare i testi rispetto a essa.
- [ ] Verificare provenienza e diritti delle immagini pregresse e assegnare il metadato IA foto per foto. Predisporre il badge non equivale a classificare tutto il catalogo.
- [ ] Configurare e usare operativamente i modelli nel negozio; nessun messaggio WhatsApp inviato o configurato da questo intervento.
- [ ] Approvare il rilascio: commit/push/deploy NON eseguiti. Push su master può pubblicare automaticamente, richiede autorizzazione.
- [ ] Dopo rilascio autorizzato: audit runtime su ambiente effettivo (cookie/storage/richieste), route legali, badge, link e mobile.

## Come continuare
1. Leggere questa checklist e `apps/web/docs/PRD_GDPR_AI_ACT.md`; non rifare il codice completato.
2. Controllare Git e preservare modifiche locali/preesistenti, inclusa `.claude/settings.local.json`.
3. Risolvere le decisioni residue, correggere solo i punti interessati e ripetere i test pertinenti.
4. Pubblicare solo dopo approvazione e verificare il sito reale.

Evidenze: `C:/Users/matte/Desktop/hermes-scratch/monili-gdpr-20261102` (log, SUMMARY.json, final-manifest.json, browser-audit.json). Il manifest dei 40 file riguarda la consegna precedente a questo aggiornamento documentale.

---
# PRD ORIGINALE — storico, con rettifiche sopra

Grazie a queste risposte il quadro è chiaro e permette di impostare il sito in modo snello e conforme.

### 4 Chiarimenti Fondamentali prima del PRD

1. **Vercel DPA (Data Processing Addendum):** Non devi firmare nulla su carta. Vercel include il DPA direttamente nei suoi Termini di Servizio online ed è ufficialmente certificata ai sensi dell'**EU-U.S. Data Privacy Framework**. È sufficiente citare Vercel come fornitore hosting conforme nella Privacy Policy.


2. **Niente Cookie Banner (Grande Vantaggio):** Poiché non hai ancora installato Meta Pixel o Google Analytics e il sito usa solo risorse tecniche, **non devi mostrare alcun banner per i cookie**. Il sito sarà più veloce e privo di ostacoli per i visitatori. Solo se in futuro deciderai di installare tracciatori pubblicitari dovrai integrare una piattaforma di consenso.


3. **Diritto di Recesso Obbligatorio (14 Giorni):** Trattandosi di prodotti già pronti (non personalizzati o realizzati su misura specifica), **il cliente ha il diritto legale di recedere entro 14 giorni dalla ricezione del pacco**. Le spese di spedizione del reso possono essere poste a carico dell'acquirente, a patto che questo sia chiaramente scritto nelle condizioni precontrattuali.


4. **AI Act & Codice del Consumo (Simulazione Indosso con IA):** Le modelle o figure umane generate con IA per mostrare i monili indossati ricadono sotto l'art. 50, par. 4 dell'AI Act (contenuti sintetici) e sotto la tutela contro le pratiche commerciali ingannevoli. È obbligatorio inserire sotto o sopra l'immagine un badge o una dicitura chiara: *"Indosso/abbinamento simulato con Intelligenza Artificiale a scopo illustrativo"*.



---

Ecco il **PRD definitivo** cucito sulla tua attività, pronto per essere passato al tuo agente di coding (Cursor, Claude Code, Copilot o Aider).

---

# PRD: Adeguamento Legale, GDPR, AI Act e Condizioni di Vendita per "I Monili di Sama Barbara"

* **Progetto:** Vetrina Digitale Monili (`monili-vetrina.vercel.app`)
* **Titolare:** I MONILI DI SAMA BARBARA di Barbara Sama
* **Sede:** Via Cavour 17, 48124 Ravenna (RA) | P.IVA: 02052730393
* **Canali di Vendita:** Vetrina web con perfezionamento ordini a distanza tramite WhatsApp Business e Instagram DM
* **Obiettivo:** Massima conformità normativa (GDPR, D.Lgs. 70/2003, DPR 633/1972, Codice del Consumo, AI Act 2024/1689), architettura cookieless a zero banner e protezione legale del titolare.

---

## 1. Modulo Dati Centralizzato: `config/legal.ts`

L'agente deve creare (o aggiornare) il file `config/legal.ts` con i dati anagrafici e commerciali dell'attività:

```typescript
export const LEGAL_CONFIG = {
  businessName: "I MONILI DI SAMA BARBARA",
  ownerName: "Barbara Sama",
  legalForm: "Ditta individuale / Impresa artigiana",
  legalAddress: "Via Cavour 17, 48124 Ravenna (RA), Italia",
  vatNumber: "02052730393",
  taxCode: "02052730393",
  email: "moniliravenna@gmail.com",
  whatsappNumber: "+393400000000", // Sostituire con il numero della SIM aziendale del negozio
  whatsappDisplay: "+39 340 0000000",
  instagramUsername: "moniliravenna", // Inserire username effettivo di Instagram
  instagramUrl: "https://instagram.com/moniliravenna",
  paymentsAccepted: ["Bonifico Bancario SEPA anticipato", "Link di pagamento SumUp (Carte di credito/debito)"],
  withdrawalDays: 14,
  hosting: "Vercel Inc. (San Francisco, CA, USA - Conforme EU-U.S. Data Privacy Framework)",
};

```

---

## 2. Architettura Tecnica e Sanificazione Frontend

### Requisito 2.1: Nessun Cookie Banner e Privacy-by-Design

* **Politica Cookie:** Attualmente il sito non carica tracker di terze parti né script pubblicitari. **Non deve essere mostrato alcun cookie banner**.
* **Font Tipografici:** Verificare che i Google Fonts non siano caricati via CDN remota (`fonts.googleapis.com`). Configurare i font in locale tramite il modulo nativo `@next/font` (se Next.js) o file WOFF2 in `/public/fonts` per evitare la trasmissione non necessaria di IP.
* **Link WhatsApp & Instagram:** I pulsanti di contatto devono essere collegamenti HTML statici (`<a>`), senza librerie o SDK di Meta:
* `href={`[https://wa.me/$](https://wa.me/$){LEGAL_CONFIG.whatsappNumber}?text=Salve,%20desidero%20informazioni%20su%20questo%20monile:`}`
* Attributi obbligatori: `target="_blank" rel="noopener noreferrer"`.



---

## 3. Footer Globale Obbligatorio

Aggiornare il componente Footer in modo che appaia su tutte le pagine con i requisiti di legge:

* **Blocco Dati Legali (DPR 633/1972 e D.Lgs. 70/2003):**
* Ragione sociale: **I MONILI DI SAMA BARBARA di Barbara Sama**
* Sede legale: **Via Cavour 17, 48124 Ravenna (RA)**
* **Partita IVA: 02052730393** (obbligatoria in home page)
* Contatti: E-mail: `moniliravenna@gmail.com` | WhatsApp: `[Numero Negozio]`


* **Link alle Pagine Legali:**
* Link a `/privacy`
* Link a `/cookie`
* Link a `/condizioni-vendita`


* **Dicitura Operativa:**
* *"Sito vetrina con ordini a distanza gestiti tramite WhatsApp Business e Instagram DM nel rispetto del Codice del Consumo."*



---

## 4. Creazione delle Pagine Legali

L'agente di coding deve implementare le tre pagine statiche con i testi legali formalizzati.

### Pagina 4.1: `/privacy` (Informativa sul Trattamento dei Dati Personali - Art. 13 GDPR)

Il testo della pagina deve contenere le seguenti sezioni strutturate:

1. **Titolare del Trattamento:**
* I MONILI DI SAMA BARBARA di Barbara Sama, con sede legale in Via Cavour 17, 48124 Ravenna (RA), P.IVA 02052730393, E-mail: `moniliravenna@gmail.com`.


2. **Finalità del Trattamento e Basi Giuridiche (Art. 6 GDPR):**
* *Risposta a richieste e gestione della compravendita a distanza:* Il trattamento dei dati di contatto (nome, numero di telefono, chat WhatsApp/Instagram, indirizzo di spedizione) è finalizzato all'esecuzione di misure precontrattuali e contrattuali su richiesta dell'utente (Art. 6.1.b GDPR).
* *Adempimenti fiscali e contabili:* Gestione di ricevute, fatture o corrispettivi per obbligo di legge (Art. 6.1.c GDPR).
* *Sicurezza e funzionamento del sito:* I log tecnici di rete sono gestiti per legittimo interesse del titolare alla cybersicurezza (Art. 6.1.f GDPR).


3. **Modalità di Pagamento e Terzi Destinatari:**
* I pagamenti avvengono tramite bonifico bancario SEPA o link SumUp. I dati della carta di credito sono trattati direttamente dalla piattaforma SumUp EU Payments UAB in conformità agli standard PCI-DSS; il titolare non accede né archivia i dati della carta.
* La merce viene spedita tramite corrieri espresso designati, a cui vengono trasmessi unicamente indirizzo e recapito telefonico per la consegna.


4. **Hosting e Trasferimento Dati Extra-UE:**
* Il sito è ospitato sull'infrastruttura di Vercel Inc. I trasferimenti di dati tecnici verso gli Stati Uniti sono tutelati dalla decisione di adeguatezza della Commissione Europea tramite la certificazione di Vercel nell'**EU-U.S. Data Privacy Framework**.


5. **Periodo di Conservazione:**
* Le conversazioni e i contatti per richieste informative che non si traducono in ordine vengono eliminati entro 6 mesi dalla conclusione del contatto.
* I documenti di vendita e i dati fiscali degli acquirenti sono conservati per 10 anni in conformità all'art. 2220 c.c.


6. **Diritti dell'Interessato (Artt. 15-22 GDPR):**
* Possibilità di richiedere accesso, rettifica, cancellazione o limitazione dei dati scrivendo a `moniliravenna@gmail.com`, nonché diritto di reclamo al Garante per la Protezione dei Dati Personali (garanteprivacy.it).



---

### Pagina 4.2: `/cookie` (Informativa Tecnica)

Il testo deve specificare:

* Il sito `monili-vetrina.vercel.app` opera secondo il principio di privacy-by-design.
* **Non vengono utilizzati cookie di profilazione, cookie pubblicitari di terze parti né strumenti di fingerprinting.**
* Il sito impiega unicamente log di rete e marcatori tecnici strettamente necessari all'erogazione del servizio e alla navigazione protetta. Ai sensi dell'art. 122 del D.Lgs. 196/2003 e delle Linee Guida del Garante Privacy del 10 giugno 2021, per questi strumenti non è richiesto il consenso preventivo dell'utente, motivo per cui non compare alcun banner all'accesso.

---

### Pagina 4.3: `/condizioni-vendita` (Condizioni Generali di Vendita a Distanza e Recesso)

1. **Ambito di Applicazione:** Compravendita a distanza di monili e gioielli conclusa tra "I Monili di Sama Barbara" (venditore) e il consumatore finale mediante strumenti di comunicazione a distanza (WhatsApp Business e Instagram Direct), ai sensi del Codice del Consumo (D.Lgs. 206/2005).
2. **Prezzo e Conclusione del Contratto:**
* Le immagini e i prezzi sul sito costituiscono un catalogo informativo.
* Il contratto si intende perfezionato nel momento in cui il cliente riceve in chat il riepilogo formale dell'ordine (con descrizione del monile, prezzo, spese di spedizione ed estremi di pagamento) e conferma espressamente l'acquisto.


3. **Modalità di Pagamento:** Bonifico Bancario anticipato o Link di pagamento sicuro SumUp.
4. **Spedizioni e Consegna:** Spedizione tramite corriere espresso con tracciamento entro i giorni lavorativi concordati nella chat d'ordine.
5. **Diritto di Recesso (Art. 52 Codice del Consumo):**
* Il cliente consumatore ha il diritto di recedere dall'acquisto entro **14 giorni** dal momento in cui entra in possesso fisico del prodotto, senza dover fornire alcuna motivazione.
* Il recesso si esercita inviando comunicazione scritta via e-mail a `moniliravenna@gmail.com` o tramite il canale WhatsApp del negozio.
* **Costi di Restituzione:** Come previsto dall'art. 57 del Codice del Consumo, **le spese dirette di restituzione del bene sono a carico dell'acquirente**. Il prodotto deve essere restituito integro, non indossato, nella confezione originale e con spedizione tracciabile entro 14 giorni dalla comunicazione di recesso.
* Il rimborso dell'importo dell'articolo avverrà tramite lo stesso metodo di pagamento utilizzato (o bonifico) entro 14 giorni dalla ricezione del bene reso.


6. **Garanzia Legale di Conformità:** Tutti i prodotti godono della garanzia legale di 24 mesi per difetti di conformità ai sensi degli artt. 128 e ss. del Codice del Consumo.

---

## 5. Implementazione Trasparenza AI (Art. 50 AI Act & Codice Consumo)

Poiché le foto usano volti o corpi generati con intelligenza artificiale per mostrare i monili indossati, creare un componente badge dedicato:

### Componente: `components/AiWearBadge.tsx`

* Creare un elemento grafico discreto ma chiaramente visibile collocato sulle schede prodotto o sulle immagini che usano indossatrici sintetiche:
* **Testo:** *"Indosso e abbinamenti simulati con Intelligenza Artificiale a scopo illustrativo"*
* **Comportamento UI:** Un piccolo badge semitrasparente in basso a sinistra nell'immagine del prodotto, oppure una didascalia direttamente sotto il visualizzatore foto.
* **Finalità:** Rispetto dell'Art. 50 del Regolamento (UE) 2024/1689 ed eliminazione di ogni rischio di ingannevolezza per il consumatore ai sensi dell'art. 21 del Codice del Consumo.



---

## 6. Documentazione Operativa Negozio: `docs/OPERAZIONI_NEGOZIO.md`

L'agente deve creare questo file per fornire al titolare i modelli pronti da usare ogni giorno nei canali di contatto.

### 6.1 Messaggio di Benvenuto Automatico (WhatsApp Business)

Da configurare nelle impostazioni di WhatsApp Business (Risposta Rapida / Messaggio di benvenuto):

> *"Gentile cliente, grazie per aver contattato I Monili di Sama Barbara! Saremo felici di aiutarti con informazioni o per il tuo ordine.
> Nota Privacy: Utilizziamo i tuoi dati di contatto esclusivamente per rispondere alla tua richiesta e gestire l'eventuale acquisto. Consulta la nostra Privacy Policy completa su: [https://monili-vetrina.vercel.app/privacy](https://monili-vetrina.vercel.app/privacy)"*

### 6.2 Modello di Conferma Ordine su Supporto Durevole (Codice del Consumo)

Testo predefinito da personalizzare e inviare in chat prima di richiedere il pagamento con SumUp o Bonifico:

> **CONFERMA D'ORDINE - I MONILI DI SAMA BARBARA**
> * **Numero/Data Ordine:** [es. ORD-2026-001 del GG/MM/AAAA]
> * **Prodotto:** [Nome e descrizione del monile]
> * **Prezzo Monile:** € [__]
> * **Spese di Spedizione:** € [__]
> * **Totale Dovuto:** € [__]
> * **Modalità di Pagamento:** [Bonifico Bancario IBAN: IT... / Link di Pagamento SumUp]
> * **Dati di Consegna:** [Nome, Cognome, Indirizzo completo, Telefono]
> * **Diritto di Recesso:** Hai diritto di recedere dall'acquisto entro 14 giorni dalla consegna del pacco. Le spese di spedizione per la restituzione sono a tuo carico. Condizioni complete su: [https://monili-vetrina.vercel.app/condizioni-vendita](https://monili-vetrina.vercel.app/condizioni-vendita)
> 
> 
> *Per procedere, inviaci conferma dei tuoi dati di spedizione e ti invieremo le coordinate/link di pagamento.*

### 6.3 Regola sulla Privacy per le Liste Broadcast

* **Promemoria Tassativo:** È vietato inserire i numeri dei clienti che hanno scritto per informazioni o ordini all'interno di liste broadcast pubblicitarie senza aver prima ottenuto un consenso specifico e scritto. I contatti rimangono limitati alla singola trattativa e al supporto post-vendita.

---

## 7. Criteri di Collaudo e Accettazione (Definition of Done)

L'agente di coding deve considerare il compito concluso solo quando:

1. `config/legal.ts` è popolato e centralizzato.
2. La Partita IVA `02052730393` e la denominazione `I MONILI DI SAMA BARBARA di Barbara Sama` sono presenti nel footer di ogni pagina.
3. Le pagine `/privacy`, `/cookie` e `/condizioni-vendita` sono funzionanti, raggiungibili e complete dei testi sopra indicati.
4. Non risultano script o cookie di profilazione attivi nel codice (zero cookie banner).
5. I font sono serviti in locale e i link WhatsApp/Instagram sono tag `<a>` statici.
6. Le immagini con indossatrici sintetiche mostrano il badge di trasparenza AI.
7. Il file `docs/OPERAZIONI_NEGOZIO.md` è presente nel repository per la gestione quotidiana di WhatsApp Business.