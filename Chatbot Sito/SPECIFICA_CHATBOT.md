# Chatbot del sito vetrina — Specifica Fase 1 (senza AI)

Bozza del 17/11/2026, da rivedere insieme a Matteo. Il punto 11 elenca le ipotesi che la bozza fa al posto di risposte non ancora date.

## 1. Cosa è e cosa non è

Un assistente a **percorsi guidati**: bottoni, risposte scritte da noi, passaggio a una persona. È un **filtro gentile** davanti a WhatsApp, Instagram, Calendly e ai negozi, non un commesso virtuale.

Non fa mai: promettere disponibilità o riserve, prendere ordini o pagamenti, raccogliere dati personali, dare pareri legali oltre le condizioni pubblicate, inventare prezzi o pezzi.

Si presenta come automatico fin dal primo messaggio: «Sono l'assistente automatico del sito». La Fase 1 non usa AI, ma la dicitura resta, per onestà verso la cliente.

## 2. Obiettivi (in ordine, da confermare)

1. Rispondere subito alle domande ripetitive: dove siamo, orari, spedizioni, cambi e resi, consulenza.
2. Portare chi cerca un regalo a una scelta concreta (pezzi reali con prezzo) e poi a «Chiedi disponibilità».
3. Far arrivare a Matteo richieste **già complete** (pezzo, link, sede) invece di «ciao, quanto costa?».

Misure per il pilota (senza tracker): clic sui link di uscita contati lato server in modo anonimo, solo se compatibile con `/privacy`. Altrimenti nessuna misura automatica: si guarda quanti messaggi WhatsApp arrivano con il testo precompilato.

## 3. Vincoli del progetto (non negoziabili)

| Fonte | Vincolo | Conseguenza sul bot |
|---|---|---|
| `impegni-legali.md` C1-C3 | Nessun cookie, nessun tracker, nessun widget o SDK di terzi, font locali | Widget scritto da noi, solo componenti React del sito |
| C4 | Nuove integrazioni = prima si aggiornano `/cookie` e `/privacy` | Fase 1 non ne richiede. Nessun servizio esterno chiamato dal bot |
| P1, P3, P5, P8 | Nessun dato personale o sanitario, mai dati di carta, niente dati clienti nei prompt | Il bot non ha campi per nome, telefono, e-mail, indirizzo |
| P7 | Durata di conservazione delle chat ancora da decidere | **Il bot non salva nulla.** La conversazione vive solo nella pagina aperta (stato in memoria, niente localStorage, niente cookie) |
| PRD §3.2 | Si risponde entro la giornata lavorativa, nessun pagamento prima della verifica | Il bot non dice «ti rispondiamo subito» e non anticipa conferme |
| PRD §5.3 | CTA «Chiedi disponibilità»; mai «te lo mettiamo da parte» | Frase di chiusura: «Scrivici, ti diciamo se è disponibile» |
| PRD §11 | Calendly, Instagram, WhatsApp si aprono solo con link | Il bot apre link, non incorpora nulla |
| PRD §7 | La consulenza si mostra solo se l'URL reale esiste | Il bot legge `consultationEnabled`: se è falso, il percorso consulenza sparisce |
| I2 | Tutti i WhatsApp vanno al numero centrale del 21 | Usa `whatsappNumber()` di `site-config.ts`, mai numeri scritti a mano |
| AI Act / `prd per GDPR e AI act.md` | Trasparenza su sistemi automatici | Dicitura iniziale e pulsante «Parla con una persona» sempre visibile |

## 4. Tono

Come il resto del brand: caldo, complice, mai formale, un'amica che consiglia. Max 1-2 emoji per messaggio. Frasi brevi. Nessun «Gentile cliente», nessun elenco puntato lungo in chat.

Esempio di apertura:
> Ciao! Sono l'assistente automatico dei Monili. Posso aiutarti a trovare un regalo, dirti dove siamo e come spediamo. Per tutto il resto ti passo a una persona vera.

## 5. Struttura dei percorsi

Menu iniziale (6 bottoni, in quest'ordine):

1. **Cerco un regalo** → percorso regalo (§6)
2. **Chiedi disponibilità di un pezzo** → percorso pezzo (§7)
3. **Dove siamo e orari** → negozi (§8)
4. **Spedizioni, cambi e resi** → FAQ (§9)
5. **Consulenza gratuita** → solo se `consultationEnabled`
6. **Parla con noi** → passaggio a una persona (§10)

Ogni risposta finisce con **un solo passo successivo**. «Menu» sta in una barra fissa sopra la casella di scrittura, sempre visibile. **«Una persona» non c'è all'inizio**: compare nella stessa barra solo quando il percorso si blocca o la persona è in difficoltà (decisione di Matteo, 17/11/2026), così le persone provano prima l'assistente invece di scrivere subito a noi. Compare quando: il testo non viene capito, c'è un errore tecnico, la ricerca regalo trova meno di 2 pezzi, la persona chiede esplicitamente di parlare con qualcuno, oppure la conversazione arriva a 8 risposte senza concludere (`helpNeeded` in `chatbot-engine.ts`). I contatti legati all'azione (Chiedi disponibilità, WhatsApp per un pezzo, consulenza) restano sempre nelle risposte.

## 6. Percorso regalo

Domande, un bottone a scelta ciascuna:

1. **Budget**: usa le fasce di `GIFT_BANDS` (fino a 30 · 30-50 · 50-80 · oltre 80). Le fasce vuote non compaiono, come già fa `giftBands()`.
2. **Per chi** (facoltativo, si può saltare): lei · mamma · amica · me stessa · non so.
3. **Che tipo di pezzo** (facoltativo): bijoux · accessori · abbigliamento · lascia scegliere a voi.

Esito: fino a **3 pezzi** reali (foto, nome, prezzo, sede, link alla scheda) presi da `giftBands()` e filtrati per categoria. Se i pezzi sono pochi o nessuno, lo dice senza inventare: «Per questa fascia al momento ho pochi pezzi online. In negozio ne abbiamo di più: vuoi che te lo diciamo su WhatsApp?».

Su ogni pezzo: **Chiedi disponibilità** (WhatsApp con messaggio precompilato, vedi §10) e **Vedi la scheda**.

Chiusura del percorso: proposta della **consulenza gratuita da 15 minuti** se attiva, altrimenti «Parla con noi».

Il bot **non decide** il «per chi» al posto della cliente e non fa psicologia: usa le risposte solo per filtrare e per scrivere il messaggio precompilato.

## 7. Percorso «Chiedi disponibilità di un pezzo»

La cliente di solito arriva già dalla scheda. Il bot:

1. chiede se ha già in mente un pezzo del sito o se lo ha visto su Instagram;
2. nel primo caso propone di aprire la scheda e usare il suo pulsante; nel secondo apre WhatsApp con testo da completare («Ciao! Ho visto su Instagram… [descrivi il pezzo]»);
3. spiega **come funziona**: «Ti rispondiamo entro la giornata lavorativa. Verifichiamo il pezzo in negozio e poi ti confermiamo. Nessun pagamento prima della verifica».

Non dice mai che il pezzo è disponibile o riservato.

## 8. Dove siamo e orari

- Orari dal modulo `shop-hours.ts` (stato «aperto ora» incluso). Non si scrivono a mano nel bot: il cambio del 1° dicembre arriva da solo.
- Due schede negozio: via Cavour 17 (argento e pietre) e via Cavour 21 (il resto), con indirizzo, link a Maps e telefono per chi vuole chiamare.
- Link «Vedi i negozi» alla pagina `/negozi`.
- Nota fissa: la sede di un pezzo si conferma sempre quando scrivi.

## 9. FAQ (contenuto fisso)

Le risposte sono brevi e rimandano alla pagina completa. **Non riscrivono le condizioni**: le riassumono e citano. Fonte unica: `legal-content.ts` e `site-config.ts`. Se un testo cambia lì, deve cambiare anche qui (test al §13).

| Domanda | Risposta in sintesi | Link |
|---|---|---|
| Quanto costa spedire? | Italia 8 €, gratis sopra 99 €. Partenza entro 2-3 giorni lavorativi dal pagamento verificato. Confezione base gratuita; alcune scatoline possono avere un supplemento, che ti diciamo prima | `/condizioni-vendita` |
| Come si paga? | Bonifico istantaneo, link SumUp o in negozio al ritiro. Mai dati di carta in chat | idem |
| Posso restituire? | Acquisti a distanza: recesso entro 14 giorni dalla consegna. In negozio: cambio entro 14 giorni. Sono due cose diverse | idem |
| Il pezzo è davvero come in foto? | Alcune foto «indossato» sono create con l'AI; fanno fede le caratteristiche del pezzo reale. Il badge è sulla foto | `/condizioni-vendita` |
| Fate pacchetti regalo? | Sì, confezione base gratuita; messaggio da concordare | — |
| Che dati usate? | Solo per rispondere e gestire l'ordine, niente liste promozionali | `/privacy` |
| Buoni regalo? | **Da non menzionare** finché il registro non è collaudato (PRD §10) | — |

Domande **fuori elenco** → «Su questo ti risponde meglio una persona» e passaggio (§10). Niente tentativi di indovinare.

## 10. Passaggio a una persona

Tre uscite, sempre a link:

- **WhatsApp** (numero centrale del 21): messaggio precompilato con ciò che è stato scelto, **senza dati personali**. Esempi:
  - Da una scheda: «Ciao! Mi piace questo [nome] ([link]), è ancora disponibile? Negozio: [sede]»
  - Dal percorso regalo: «Ciao! Cerco un regalo, budget [fascia]. Vorrei un consiglio.»
- **Instagram DM** (@imoniliravenna).
- **Consulenza gratuita** su Calendly, se attiva, con la spiegazione già prevista dal PRD (15 minuti, gratis, nessun obbligo).

Fuori dagli orari: «Siamo chiusi, ma puoi scriverci: ti rispondiamo entro la giornata lavorativa». Usa `openNowLabel()`.

## 11. Ipotesi da confermare con Matteo

| # | Ipotesi della bozza | Alternativa |
|---|---|---|
| 1 | L'ordine degli obiettivi del §2 | Per esempio mettere le richieste WhatsApp al primo posto |
| 2 | Fuori orario il bot spiega quando si risponde e non fa altro | Aggiungere un promemoria o un modulo (richiede dati → no per ora) |
| 3 | Il codice va nella repo `monili-vetrina` (`Ecosistema Monili/apps/web`) | Altra posizione |
| 4 | Nessuna misura automatica nel pilota | Contare i clic in modo anonimo (da verificare con `/privacy`) |
| 5 | Orari e testi dal sito, nessun duplicato | — |
| 6 | Buoni regalo non menzionati | Menzionarli dopo il collaudo del registro |

## 12. Come si costruisce (tecnica)

- **Contenuti** in un solo file tipizzato `src/lib/chatbot-content.ts`: nodi con id, testo, opzioni. Si modifica senza toccare l'interfaccia. Matteo può chiedere ritocchi ai testi in chat.
- **Motore** in una funzione pura `chatbot-engine.ts` che, dato lo stato e la scelta, restituisce il prossimo messaggio. Facile da testare senza browser.
- **Interfaccia**: un componente client `chatbot-widget.tsx`, caricato in modo lazy, con apertura da un pulsante. Stato in memoria React. Nessun localStorage né cookie.
- **Dati dinamici** (pezzi, orari, numero, consulenza) letti dai moduli del sito, mai copiati.
- **Posizione**: sul desktop esiste già `floating-whatsapp-desktop.tsx`; il launcher del bot deve convivere con quel pulsante senza coprirlo, e su telefono non deve coprire il pulsante «Chiedi disponibilità» della scheda.
- **Digitazione** (17/11/2026): prima i puntini "sta scrivendo" per 1,2 secondi (`TYPING_DELAY_MS`), poi la risposta si scrive lettera per lettera a circa 40-50 caratteri al secondo, con una pausa dopo virgole e punti e un tetto di 4,5 secondi per le risposte lunghe (`chatbot-typing.ts`). Scelte e pezzi compaiono a fine scrittura. Un tocco sulla conversazione o un nuovo passo mostrano subito la risposta intera. Con «riduci movimento» attivo la risposta compare subito. Il testo intero è nella pagina fin dall'inizio (la parte non ancora scritta è trasparente), così un lettore di schermo lo legge una volta sola.
- **Accessibilità** (il sito oggi ha Lighthouse 100): `role="dialog"`, focus trattenuto e restituito alla chiusura, uso da tastiera, `Esc` per chiudere, `prefers-reduced-motion` rispettato, aree cliccabili ≥ 44 px, contrasti ≥ 4,5:1.
- **Testo libero locale (facoltativo)**: una casella che riconosce parole chiave (es. «spedizione», «orari», «anello») **nel browser**, senza inviare nulla. Se non riconosce: passaggio a persona. Non è AI e non richiede cambi di privacy.

## 13. Come si verifica

- Test unitari del motore: ogni percorso raggiunge un esito, nessun vicolo cieco (ogni risposta mostra qualcosa da fare oltre a Menu e Una persona), e «Una persona» che compare solo nei casi della regola del §5.
- Test come `legal-compliance.test.ts`: le cifre del bot (8 €, 99 €, 14 giorni, 2-3 giorni) coincidono con quelle di `legal-content.ts`; nessun testo contiene «te lo mettiamo da parte»; nessun numero di telefono diverso da quello centrale; nessun campo che chieda dati personali.
- Prova a mano su telefono e desktop, con tastiera e lettore di schermo, con `consultationEnabled` acceso e spento.
- Nessuna richiesta di rete in uscita dal widget (controllo nella scheda rete del browser).
- Lighthouse accessibilità resta 100.

## 14. Fuori da questa fase (Fase 2, solo dopo il pilota)

- Comprensione del testo libero con un modello AI, su contenuti approvati e con risposte non generate liberamente. Prima: aggiornare `/privacy` e `/cookie`, avviso chiaro che il testo viene inviato a un fornitore, nessun dato cliente nei prompt, scelta del fornitore e della conservazione.
- Salvataggio o analisi delle conversazioni (dipende dalla decisione di Matteo sulla conservazione, voce 8 degli interventi).
- Buoni regalo nel bot, dopo il collaudo del registro.
- Lingue diverse dall'italiano (PRD §1).

## 15. Ordine di lavoro proposto

1. Matteo conferma o corregge il §11.
2. Si scrive `chatbot-content.ts` con i testi: da rivedere insieme, è la parte che dà il tono.
3. Motore e test.
4. Interfaccia e accessibilità.
5. Prova su telefono, poi pubblicazione.

## 16. Dopo l'audit del 17/11/2026: decisioni e punti aperti

Un revisore indipendente ha provato il bot online come cliente (circa 100 prove). Cosa è stato deciso e cambiato:

**Decisioni di Matteo**
- **Spedizione fuori dall'Italia: sì, con un costo più alto.** Il bot lo dice, senza cifre né paesi, e rimanda al riepilogo prima del pagamento. Paesi e prezzi sono da definire; la frase nelle condizioni di vendita è neutra ("fuori dall'Italia").
- **Pagamenti: Satispay sì, PayPal no.** Aggiornati insieme: condizioni di vendita (sezione pagamenti), informativa privacy, `LEGAL_CONFIG.paymentsAccepted`, `impegni-legali.md` (V4, V8, modello B) e PRD §8.1 e §9.
- **Riparazioni: solo al civico 17.** Il bot lo dice senza prezzi né tempi; per i lavori su misura rimanda a WhatsApp.
- **CAP: 48121 ovunque** (sede legale e indirizzo dei resi inclusi). La scheda aziendale in PDF e `prd per GDPR e AI act.md` riportano ancora 48124: vanno corretti a mano, e va verificato che la sede in visura camerale coincida.
- **Traduzione del sito: da progettare a parte**, non nel bot. Prima si decide come tradurre il sito intero (lingue, URL, SEO, testi legali), poi il bot segue.

**Corretto nel bot**
- "Chiedi disponibilità" sui pezzi suggeriti ora chiede se il pezzo è ancora disponibile (prima, per alcuni pezzi, chiedeva orari e sede). La scheda del pezzo sul sito era già giusta.
- Nessuna risposta dice più "scrivici" senza il pulsante per farlo; il saluto non promette più una persona che non c'è.
- Il testo libero ora conta le parole riconosciute per argomento, con una priorità (un problema con un ordine batte la spedizione) e tollera i refusi. Nuovi argomenti: problema con un ordine, riserva, riparazioni, prezzi e taglie. Resi divisi tra acquisto a distanza e in negozio.
- La ricerca regalo propone solo fasce e tipi che hanno almeno un pezzo online; con zero pezzi lo dice chiaramente.
- Chiamate ai due negozi, orari di dicembre annunciati prima del cambio, nomi accessibili sui pulsanti dei pezzi, cursore che resta nella casella dopo una domanda scritta.
- "Una persona" compare anche dopo "problema con un ordine", e il conteggio delle 8 risposte riparte dal Menu.

**Ancora aperto**
- Attesa totale per le risposte lunghe (circa 6 secondi con puntini e scrittura): lasciata come chiesto; tetto riducibile in `chatbot-typing.ts`.
- Nessuna riga su parcheggio, festivi e data limite degli ordini per Natale: mancano le fonti.
- Buoni regalo non menzionati finché il registro non è collaudato. Inglese rimandato al progetto di traduzione.
- Condizioni, privacy e testi del bot non ancora rivisti dal consulente (Satispay e spedizioni all'estero compresi).
