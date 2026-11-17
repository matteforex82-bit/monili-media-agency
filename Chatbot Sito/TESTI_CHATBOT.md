# Testi del chatbot (bozza 1)

Bozza del 17/11/2026, scritta con la skill humanizer e il tono del brand. Le parti tra [parentesi quadre] vengono riempite dal sito con dati veri (orari, prezzi, numero, link). Le cifre e le regole vengono dalle condizioni di vendita e dal PRD journey: se cambiano lì, cambiano qui.

## 1. Apertura

> Ciao! Sono l'assistente automatico dei Monili. Posso aiutarti a scegliere un regalo e dirti dove siamo, a che ora apriamo e come spediamo. Se hai bisogno di una persona, ti ci porto subito.

Bottoni del menu:

1. Cerco un regalo
2. Voglio sapere se un pezzo è disponibile
3. Dove siamo e orari
4. Spedizioni, cambi e resi
5. Consulenza gratuita (compare solo se la prenotazione è attiva)
6. Parlo con una persona

Sotto ogni risposta restano due bottoni: "Torna al menu" e "Parlo con una persona".

## 2. Cerco un regalo

Domanda 1, il budget (i bottoni sono le fasce del sito):

> Che cifra avevi in mente?

Domanda 2, facoltativa:

> Per chi è? Se non lo sai ancora, scegli l'ultimo.

Bottoni: Mamma · Un'amica · Sorella o figlia · Me stessa · Non lo so ancora

Domanda 3, facoltativa:

> Preferisci un gioiello, una borsa o qualcosa da indossare?

Bottoni: Gioielli · Borse e accessori · Abbigliamento · Scegliete voi

Risultato, con 1 a 3 pezzi:

> Ecco cosa abbiamo online adesso per [fascia]. Se ti piace qualcosa, scrivici e ti diciamo se è disponibile.

Per ogni pezzo: foto, nome, prezzo, negozio, bottoni "Chiedi disponibilità" e "Vedi la scheda".

Risultato con un solo pezzo o nessuno:

> Per questa fascia online ho pochissimo. In negozio abbiamo molto di più: scrivici e ti diciamo cosa c'è.

Dopo i pezzi, se la consulenza è attiva:

> Se preferisci farti consigliare a voce, c'è una videochiamata gratuita di 15 minuti. Nessun obbligo di acquisto.

Bottoni: Prenota la consulenza · Parlo con una persona · Torna al menu

## 3. Voglio sapere se un pezzo è disponibile

> Hai già in mente un pezzo?

Bottoni: L'ho visto sul sito · L'ho visto su Instagram · Non ancora

Se l'ha visto sul sito:

> Apri la sua scheda e premi "Chiedi disponibilità". Il messaggio parte già compilato con il nome del pezzo e il link, così non devi scrivere altro.

Se l'ha visto su Instagram:

> Scrivici su WhatsApp o in DM e dicci quale pezzo è. Se hai una foto o il video, mandalo: ci aiuta a trovarlo in fretta.

Se non ancora:

> Allora ti conviene guardare le idee regalo, oppure dirci cosa cerchi e ti rispondiamo noi.

Bottoni: Idee regalo · Parlo con una persona

Spiegazione che segue sempre una richiesta di disponibilità:

> Il pezzo lo controlliamo in negozio, quindi la risposta può arrivare dopo qualche ora. Ti scriviamo entro la giornata lavorativa. Il pagamento si chiede solo dopo la verifica.

Frase di chiusura da usare ovunque serva: "Scrivici, ti diciamo se è disponibile."

Il bot non scrive mai "te lo mettiamo da parte", "è tuo" o "ce l'abbiamo".

## 4. Dove siamo e orari

> Siamo in via Cavour a Ravenna, ai numeri 17 e 21. Al 17 trovi argento e pietre, al 21 tutto il resto.
>
> [Stato: "Aperto ora, fino alle 19:30" oppure "Chiuso, riapre domani alle 9:30"]
>
> Orari: [orari dal sito]
>
> Puoi passare senza prenotare. Se vuoi vedere un pezzo del sito, porta la foto o il link.

Bottoni: Apri la mappa del 17 · Apri la mappa del 21 · Vedi la pagina dei negozi

## 5. Spedizioni, cambi e resi

Menu delle domande:

1. Quanto costa spedire?
2. Come posso pagare?
3. Posso restituire o cambiare?
4. Le foto sono vere?
5. Fate pacchetti regalo?
6. Cosa fate con i miei dati?

Risposte:

Quanto costa spedire?
> In Italia spediamo a 8 euro, gratis sopra i 99. Il pacco parte entro 2 o 3 giorni lavorativi da quando vediamo il pagamento. Ti diciamo prima anche quando dovrebbe arrivare, così puoi confrontarlo con la data del regalo.

Come posso pagare?
> Con bonifico istantaneo, con un link SumUp oppure in negozio quando ritiri. In chat non ti chiediamo mai i dati della carta.

Posso restituire o cambiare?
> Se compri a distanza, puoi ripensarci entro 14 giorni da quando ricevi il pacco, senza darci spiegazioni. La spedizione del reso è a tuo carico e ti rimborsiamo entro 14 giorni da quando ce lo comunichi. Se compri in negozio, puoi cambiare il pezzo entro 14 giorni. Sono due regole diverse. Tutti i dettagli sono nelle condizioni di vendita.

Bottone: Leggi le condizioni di vendita

Le foto sono vere?
> Alcune foto dei pezzi indossati sono create con l'intelligenza artificiale e hanno un'etichetta. Il pezzo vero è quello che conta: colori, misure e dettagli sono quelli scritti nella scheda.

Fate pacchetti regalo?
> Sì, la confezione base è gratuita e possiamo aggiungere un messaggio. Per alcune scatoline da anello, bracciale o collana può esserci un supplemento, e te lo diciamo prima di pagare.

Cosa fate con i miei dati?
> Quello che ci scrivi lo usiamo solo per risponderti e seguire l'ordine. Niente liste promozionali. Questo assistente non salva la conversazione: quando chiudi la pagina, sparisce.

Bottone: Leggi la privacy

## 6. Consulenza gratuita

Compare solo se il link di prenotazione è attivo.

> È una videochiamata gratuita di 15 minuti su WhatsApp, in italiano. Ti chiamiamo noi dal numero dei Monili e ti aiutiamo a scegliere. Non c'è nessun obbligo di acquisto. Puoi prenotare anche con tre ore di anticipo.

Bottoni: Prenota la consulenza · Torna al menu

## 7. Parlo con una persona

Negozi aperti:

> Scrivici su WhatsApp o in DM su Instagram. Ti rispondiamo entro la giornata lavorativa.

Negozi chiusi:

> Adesso siamo chiusi, ma scrivici lo stesso: ti rispondiamo entro la giornata lavorativa.

Bottoni: Scrivi su WhatsApp · Scrivi su Instagram · Torna al menu

Messaggi WhatsApp precompilati (nessun dato personale):

- Dalla scheda di un pezzo: "Ciao! Mi piace questo [nome] ([link]). È ancora disponibile? Negozio: [sede]"
- Dal percorso regalo: "Ciao! Cerco un regalo, budget [fascia]. Mi date un consiglio?"
- Da Instagram: "Ciao! Ho visto un pezzo su Instagram e vorrei sapere se è disponibile: [descrivilo qui]"
- Generico: "Ciao! Vorrei un'informazione."

## 8. Quando il bot non sa

Testo libero senza corrispondenza:

> Non ho capito bene. Su questo ti risponde meglio una persona. Ti apro WhatsApp?

Bottoni: Sì, apri WhatsApp · Torna al menu

Pezzo non più disponibile, se la scheda lo segna come venduto:

> Questo pezzo ha già trovato casa. Guarda i simili: ne abbiamo di coerenti con quello che cercavi.

Errore tecnico:

> Qualcosa non ha funzionato. Puoi scriverci direttamente su WhatsApp: ti rispondiamo noi.

## 9. Da non scrivere mai nei testi del bot

- "Te lo mettiamo da parte", "è riservato", "lo abbiamo", "arriva domani", "arriva per Natale".
- Prezzi o disponibilità che non vengono dal sito.
- Buoni regalo, finché il registro non è collaudato.
- Domande su nome, telefono, indirizzo, e-mail o carta.
- Consigli legali oltre quello che dicono le condizioni di vendita.
- Emoji decorative: al massimo una per messaggio, e solo se naturale.
