# Impegni dichiarati sul sito e modo di lavorare

Dal 03/11/2026 il sito vetrina (`monili-vetrina.vercel.app`) dichiara pubblicamente ai clienti cosa facciamo con i loro dati, come vendiamo a distanza e come funziona il recesso. Quello che è scritto in `/privacy`, `/cookie` e `/condizioni-vendita` è una promessa: da oggi lo dobbiamo fare davvero, ogni volta.

Questo file elenca le promesse, dice **chi le rispetta e come**, e raccoglie i **messaggi pronti** da copiare nelle chat. Non è consulenza legale: i testi vanno fatti rivedere da un consulente prima di considerarli definitivi.

Testi esatti sul sito: `Ecosistema Monili/apps/web/src/lib/legal-content.ts`. Se cambia la prassi, si cambia il testo del sito **prima** (o insieme), mai il contrario.

---

## 1. Le promesse, una per una

### Vendita a distanza (WhatsApp e Instagram)

| # | Cosa abbiamo dichiarato | Cosa facciamo da oggi | Chi |
|---|---|---|---|
| V1 | Prima del pagamento il cliente riceve un **riepilogo** con prodotto, quantità, prezzo, spese, totale, pagamento, consegna, condizioni e info sul recesso | Si invia sempre il modello **B** (sotto), con tutti i campi compilati, **prima** di dare IBAN o link SumUp | Negozio |
| V2 | L'ordine è concluso solo quando il cliente **conferma espressamente** l'acquisto con obbligo di pagare | Chiedere la frase di conferma del modello B. "Ok va bene" o "conferma l'indirizzo" non bastano | Negozio |
| V3 | Conferma del contratto e condizioni su **supporto durevole** (testo completo in e-mail o PDF, non solo un link) | Dopo la conferma si invia il modello **C** per e-mail, con il testo delle condizioni incollato o allegato in PDF | Negozio |
| V4 | Spedizione in Italia **8 €, gratuita sopra 99 €**; nessun costo extra senza accordo espresso | Indicare sempre le spese nel riepilogo; niente supplementi a sorpresa | Negozio |
| V5 | Consegna entro il termine concordato prima dell'ordine; se non concordato, **entro 30 giorni** | Scrivere il termine nel riepilogo. Corriere tracciato sempre | Negozio |
| V6 | Prezzi in euro, **imposte incluse** | Nessun prezzo "più IVA" | Negozio, Studio |
| V7 | Prodotti pronti, **non personalizzati** (eccezioni da dichiarare prima dell'ordine) | Se un pezzo è su misura o personalizzato, dirlo nel riepilogo prima del pagamento | Negozio |
| V8 | Pagamento solo con bonifico SEPA anticipato o link SumUp | Non accettare altro senza aggiornare le condizioni sul sito | Negozio |

### Recesso e garanzia

| # | Cosa abbiamo dichiarato | Cosa facciamo da oggi | Chi |
|---|---|---|---|
| R1 | Il cliente può recedere **entro 14 giorni** dal possesso fisico del pezzo, senza motivo | Accettare qualsiasi dichiarazione esplicita (e-mail, WhatsApp). **Non** pretendere il modulo | Negozio |
| R2 | Il modulo di recesso è **facoltativo** | Quando il cliente lo chiede, si invia il modello **D**. Chi scrive "voglio rendere" a parole sue vale uguale | Negozio |
| R3 | Il cliente restituisce **entro 14 giorni dalla comunicazione**; le spese di reso sono **a suo carico** | Nel modello **E** si dà l'indirizzo di reso e si ricorda che la spedizione è a sue spese | Negozio |
| R4 | Si può **esaminare il pezzo come in negozio**: niente obbligo di "mai provato" o "confezione originale" | Mai rifiutare un reso perché il pezzo è stato provato o manca la scatola. Si può trattenere solo la diminuzione di valore da uso oltre la prova | Negozio |
| R5 | **Rimborso entro 14 giorni dalla comunicazione**, incluse le spese di consegna standard, con lo stesso mezzo di pagamento | Segnare la data di comunicazione sul registro (§3) e rimborsare entro quella data +14. Si può attendere il pezzo o la prova di spedizione | Negozio, contabilità |
| R6 | **Garanzia legale di 2 anni** sui difetti di conformità, rimedi gratuiti | Se il pezzo è difettoso: riparazione o sostituzione a nostre spese (modello **I**). Non si confonde con il reso per ripensamento | Negozio |

### Dati personali (GDPR)

| # | Cosa abbiamo dichiarato | Cosa facciamo da oggi | Chi |
|---|---|---|---|
| P1 | I dati di contatto servono **solo** a rispondere e gestire l'ordine | Nessun uso diverso. Nessuna lista promozionale per chi ha solo chiesto info o comprato | Tutti |
| P2 | I messaggi di marketing richiedono un **consenso separato, libero, revocabile**, e non è condizione per acquistare | Si chiede con il modello **G**; si registra data, canale, testo e risposta; "STOP" si rispetta subito | Negozio |
| P3 | Non chiediamo dati sanitari o particolari | Non chiederli mai; se arrivano, non conservarli | Tutti |
| P4 | Ai corrieri vanno **solo** nome, indirizzo, recapito | Niente altro nel modulo di spedizione | Negozio |
| P5 | Dati carta **mai raccolti da noi**: li inserisce il cliente su SumUp | Mai chiedere numeri di carta in chat | Negozio |
| P6 | Richieste sui dati (accesso, cancellazione...) **risposta entro un mese** | Segnare data e richiesta nel registro; rispondere con il modello **H** | Titolare |
| P7 | Documenti fiscali conservati **10 anni**; chat e richieste solo per il tempo necessario | Decidere la durata (vedi §4); non conservare tutte le chat per sempre | Titolare |
| P8 | Dati dei clienti **non** nel catalogo pubblico né nei prompt dell'IA | Mai incollare chat, nomi o indirizzi nello Studio, nei prompt o nelle schede | Tutti, Studio |
| P9 | In caso di incidente (accessi non autorizzati, telefono perso con chat) | Limitare subito l'accesso, avvisare il titolare: la notifica al Garante, se dovuta, è **entro 72 ore** | Titolare |

### Cookie e strumenti sul sito

| # | Cosa abbiamo dichiarato | Cosa facciamo da oggi | Chi |
|---|---|---|---|
| C1 | **Nessun** cookie di profilazione, Pixel Meta, Google Analytics o fingerprinting; **nessun banner** | Non aggiungere questi strumenti | Sviluppo |
| C2 | Nessun feed social, mappa interattiva o widget chat di terzi; WhatsApp, Instagram e mappe sono semplici link | Solo tag `<a>` con `rel="noopener noreferrer"`, nessun SDK | Sviluppo |
| C3 | Font serviti dal sito, non da CDN Google | Font solo in locale | Sviluppo |
| C4 | Se un giorno servono strumenti non necessari: **prima** si aggiorna l'informativa e si ottiene il consenso, senza caricarli in anticipo | Qualsiasi nuova integrazione (Analytics, Pixel, chat, mappa incorporata) = cambiare `/cookie` e `/privacy` e aggiungere un banner di consenso **prima** del rilascio | Sviluppo, titolare |

### Immagini generate con l'IA

| # | Cosa abbiamo dichiarato | Cosa facciamo da oggi | Chi |
|---|---|---|---|
| A1 | Le immagini con indosso simulato sono accompagnate da una dicitura; **fanno fede le caratteristiche del pezzo reale** | Lo Studio segna come IA le foto "indossato" quando invia un pezzo al sito (fatto, `aiGenerated`); il sito mostra il badge | Studio |
| A2 | Il badge segue la foto mostrata, non l'intero prodotto | Per ogni nuova foto: IA = `true`, foto reale verificata = `false`, non verificata = **assente** (non significa "reale") | Studio, titolare |
| A3 | Prima di pubblicare si controllano colore, misure e dettagli del pezzo reale rispetto alla foto IA | Controllo umano prima di "Invia al sito" | Titolare |
| A4 | Su Instagram i contenuti IA realistici hanno l'etichetta "Info sull'AI" | Già in `CLAUDE.md`: attivarla sempre | Titolare |

### Identità del negozio sul sito

| # | Cosa abbiamo dichiarato | Cosa facciamo da oggi |
|---|---|---|
| I1 | Footer: ragione sociale, sede, P.IVA, e-mail, WhatsApp dei due negozi | Se cambia un dato (numero, sede, e-mail), si aggiorna `src/config/legal.ts` della vetrina: una sola modifica, vale per tutto il sito |
| I2 | **Aggiornato il 03/11/2026 (PRD Journey cliente §3.1, §11):** tutti i collegamenti WhatsApp del sito vanno al **numero centrale del 21: 375 771 3966**. La scheda del pezzo e il messaggio indicano comunque il **negozio del pezzo** (17: 331 428 5295 resta il telefono reale della sede). Il footer e le pagine dei negozi mantengono i telefoni per sede | Il numero centrale è uno solo e ha una costante sola nel codice (`site-config.ts` della vetrina). Non cambiare il luogo del prodotto né i dati legali della società |

---

## 2. Messaggi pronti da copiare

Si usano in WhatsApp Business (risposte rapide), Instagram DM e e-mail. Le parti tra `[parentesi]` si compilano **sempre** prima di inviare. Nessun IBAN o link di esempio va usato come se fosse vero.

### A. Benvenuto (risposta rapida `/privacy`)

> Ciao, grazie per averci scritto, I Monili di Sama Barbara! Usiamo il tuo numero e quello che ci scrivi solo per risponderti e seguire l'eventuale ordine, non per iscriverti a liste promozionali. Informativa completa: https://monili-vetrina.vercel.app/privacy — per domande sui tuoi dati: moniliravenna@gmail.com

### B. Riepilogo ordine (da inviare **prima** del pagamento)

> **RIEPILOGO ORDINE — I MONILI DI SAMA BARBARA di Barbara Sama**
> Via Cavour 17, 48124 Ravenna (RA) — P.IVA 02052730393 — moniliravenna@gmail.com
> Ordine n. [numero] del [data]
> Negozio di ritiro del pezzo: [Via Cavour 17 / 21] — assistenza WhatsApp: 375 771 3966
> Pezzo: [descrizione, materiali, misura/taglia] × [quantità]
> Prezzo (imposte incluse): € [__]
> Spedizione: € [__] (Italia 8 €, gratuita sopra 99 €)
> **Totale da pagare: € [__]**
> Pagamento: [bonifico SEPA anticipato / link SumUp]
> Consegna: [nome, indirizzo, telefono] — entro [data o giorni concordati]; corriere tracciato
>
> Puoi recedere entro 14 giorni da quando ricevi il pacco, senza dare motivazioni: basta scriverci a moniliravenna@gmail.com o su WhatsApp. La spedizione del reso è a tuo carico. Puoi provare il pezzo come in negozio. Ti rimborsiamo entro 14 giorni dalla tua comunicazione, comprese le spese di spedizione standard. Garanzia legale di 2 anni sui difetti.
> Condizioni complete: https://monili-vetrina.vercel.app/condizioni-vendita
> Privacy: https://monili-vetrina.vercel.app/privacy
>
> **Per acquistare rispondi con questa frase:** "Confermo l'ordine [numero], i dati di consegna e l'acquisto con obbligo di pagare il totale di € [__]"

### C. Conferma del contratto (per **e-mail**, dopo la conferma del cliente)

Oggetto: `Conferma ordine n. [numero] — I Monili Ravenna`

> Grazie [nome]! Abbiamo ricevuto la tua conferma il [data e ora]. Qui sotto trovi il riepilogo dell'ordine e le condizioni di vendita, da conservare.
>
> [incolla il riepilogo del modello B, già compilato]
>
> [incolla il testo integrale di https://monili-vetrina.vercel.app/condizioni-vendita oppure allega il PDF]
>
> Appena vediamo il pagamento, spediamo e ti mandiamo il codice di tracciamento.
> I Monili di Sama Barbara, Via Cavour 17, Ravenna

Un link da solo **non** è supporto durevole: il testo va incollato o allegato.

### D. Modulo di recesso (il cliente lo chiede, o gli serve una traccia)

> Ecco il modulo, ma puoi anche scriverci con parole tue: va bene lo stesso.
>
> "Con la presente comunico il recesso dal contratto relativo al seguente bene: [descrizione]; ordinato il [data], ricevuto il [data]; numero ordine [numero]; nome e indirizzo del consumatore [dati]; data [data]." (La firma serve solo se lo mandi su carta.)
>
> Invialo a moniliravenna@gmail.com oppure rispondi qui. Hai tempo 14 giorni da quando hai ricevuto il pacco.

### E. Risposta quando il cliente comunica il recesso

> Abbiamo ricevuto la tua comunicazione di recesso per l'ordine [numero] il [data]. Nessun problema!
> Spediscici il pezzo **entro 14 giorni da oggi** (cioè entro il [data + 14]) a: I MONILI DI SAMA BARBARA di Barbara Sama, Via Cavour 17, 48124 Ravenna (RA). La spedizione del reso è a tuo carico: ti consigliamo un invio tracciato e di conservare la ricevuta.
> Ti rimborsiamo, comprese le spese di spedizione standard, entro il [data + 14] con lo stesso mezzo di pagamento che hai usato. Se il pezzo non è ancora arrivato, possiamo attendere l'arrivo o la prova della spedizione.

### F. Rimborso eseguito

> Abbiamo rimborsato € [__] per l'ordine [numero] il [data], con [metodo]. Può servire qualche giorno perché compaia sul tuo conto. Grazie, e a presto in via Cavour!

### G. Consenso marketing (facoltativo, mai insieme a un ordine come condizione)

> Se ti va, possiamo scriverti su WhatsApp per novità e proposte di I Monili. Non è necessario per acquistare. Per iscriverti rispondi: "ACCONSENTO a ricevere messaggi promozionali WhatsApp". Puoi smettere quando vuoi scrivendo STOP o a moniliravenna@gmail.com. Informativa: https://monili-vetrina.vercel.app/privacy

Si registra: data, canale, testo inviato e risposta del cliente. Chi non risponde **non** va nelle liste.

### H. Richiesta privacy (accesso, correzione, cancellazione...)

> Abbiamo ricevuto la tua richiesta del [data] sui tuoi dati personali. Ti rispondiamo entro un mese, cioè entro il [data + 30 giorni]. Per sicurezza potremmo chiederti una conferma della tua identità. Se vuoi, puoi anche rivolgerti al Garante per la protezione dei dati personali (garanteprivacy.it).

### I. Difetto di conformità (garanzia)

> Ci dispiace per il difetto! Ti ricordiamo che per due anni dalla consegna il pezzo è coperto da garanzia legale: riparazione o sostituzione sono **gratuite**, anche le spese di spedizione. Mandaci una foto del difetto, il numero ordine [numero] e la data di consegna, e ti diciamo come procedere.

---

## 3. Registro ordini e richieste (da tenere)

Un foglio semplice (Excel o Google Sheets), accessibile solo a chi ne ha bisogno, una riga per ordine. Serve a rispettare le scadenze e a dimostrare cosa abbiamo mandato.

| Colonna | Perché |
|---|---|
| N. ordine, data | Identifica l'ordine |
| Negozio referente | Chi lo segue |
| Pezzo, importo, spese, totale | Corrisponde al riepilogo |
| Data e ora della conferma espressa del cliente | Prova che il contratto è concluso |
| Versione delle condizioni inviata (data) | Prova di cosa abbiamo mandato |
| Data di consegna | Fa partire i 14 giorni |
| Data comunicazione recesso / scadenza reso / scadenza rimborso | Rispettare i 14 giorni |
| Data richiesta privacy / scadenza risposta (+1 mese) | Rispettare il termine |
| Consenso marketing: sì/no, data, canale | Evita invii non autorizzati |

Niente indirizzi o chat copiati dove non servono, e niente di tutto questo nello Studio o nei prompt dell'IA.

---

## 3bis. Promesse nuove del PRD Journey cliente: non ancora dichiarate sul sito

> **Aggiornamento 4/11/2026:** le nuove condizioni sono **online** (commit ac15a12 del sito) (`src/lib/legal-content.ts`, nuove sezioni «Riserva, scadenza e pagamento al ritiro», «Ritiro in negozio di un ordine a distanza», «Cambio commerciale»; test `legal-compliance.test.ts`). **Non sono ancora riviste da un consulente**: da farlo appena possibile. Le righe qui sotto descrivono ciò che le condizioni dichiarano ora. Buoni regalo e Calendly (consulenza) restano fuori dalle condizioni.

Queste regole sono decise (`brainstorming marketing strategie.md`, §8–§10 e §16) ma **erano fuori dalle condizioni di vendita fino al 4/11**; ora il sito le riporta (tranne buoni regalo). Se cambiano, si aggiorna prima `/condizioni-vendita`.

| Nuova prassi | Cosa manca nelle condizioni |
|---|---|
| Pagamento anche **in negozio al ritiro** (oltre a bonifico e link SumUp) | V8 e la sezione «Pagamenti» elencano solo bonifico anticipato e link SumUp |
| **Riserva con scadenza** (max 48 h) e conferma che decade se non si paga | Nessuna clausola sulla scadenza della conferma |
| **Ritiro** di un ordine a distanza (recesso dal ritiro) | Le condizioni parlano solo di consegna con corriere |
| Partenza entro **2–3 giorni lavorativi** dal pagamento verificato | V5: «30 giorni» se non concordato |
| **Scatolina** con supplemento, comunicato prima del pagamento | Non menzionata (V4: nessun costo senza accordo espresso, resta valido) |
| **Cambio commerciale entro 14 giorni**, distinto da recesso e garanzia | Non menzionato |
| **Buoni regalo** (solo dopo collaudo del registro) | Non menzionati |
| Dati di prenotazione su **Calendly** | Non citato nella privacy |

Guida operativa: questo file è la fonte unica. `Ecosistema Monili/apps/web/docs/OPERAZIONI_NEGOZIO.md` (vetrina) contiene una versione precedente dei modelli: se i due testi divergono, vale questo.

---

## 4. Decisioni ancora da prendere (tue, non del codice)

1. **Quanto conservare** chat e richieste senza ordine. La proposta era 6 mesi, ma sul sito non l'abbiamo promessa: scegli una durata e chi fa la pulizia.
2. **Piano hosting** (Vercel, Neon) e contratti per il trattamento dei dati: verificare cosa si applica al piano reale.
3. **Prassi vera su pagamenti, spedizioni e resi**: i testi devono corrispondere a come lavorate davvero. Se non è così, si cambia il sito, non la prassi nascosta.
4. **Classificare le foto già in catalogo** (35 immagini senza flag): IA o reali, foto per foto.
5. **Configurare le risposte rapide** A, B, D, E, G, I su WhatsApp Business (a mano, sull'account centrale del 21; il 17 solo se continua a ricevere messaggi).
6. **Far rivedere i testi** a un consulente.

---

## 5. Come lo integriamo nel lavoro con l'AI

- `CLAUDE.md` richiama queste regole: chi sviluppa le deve rispettare senza che serva ricordarlo.
- **Studio**: già segna le foto "indossato" come IA quando invia al sito. Quando si aggiunge un nuovo tipo di foto generata, va deciso il flag.
- **Mai** dati di clienti nello Studio, nei prompt, nel catalogo, nei log.
- **Nuove integrazioni sul sito** (analytics, pixel, chat, mappe, form): prima si aggiornano `/cookie` e `/privacy`.
- **Cambi di prassi** (nuovo metodo di pagamento, nuove spese, resi diversi): prima si aggiorna `/condizioni-vendita` e i modelli B-E di questo file.
- Possibile passo successivo, se lo vuoi: una pagina dello Studio con questi messaggi e un pulsante "copia", per averli a portata di mano invece che in un file.
