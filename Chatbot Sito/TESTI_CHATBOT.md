# Testi del chatbot (bozza 1)

Bozza del 17/11/2026, scritta con la skill humanizer e il tono del brand. Le parti tra [parentesi quadre] vengono riempite dal sito con dati veri (orari, prezzi, numero, link). Le cifre e le regole vengono dalle condizioni di vendita e dal PRD journey: se cambiano lì, cambiano qui.

## 1. Apertura

> Ciao! Sono l'assistente automatico dei Monili. Posso aiutarti a scegliere un regalo e dirti dove siamo, a che ora apriamo e come spediamo. Se ti serve una persona, scrivi "persona".

Bottoni del menu:

1. Cerco un regalo
2. Voglio sapere se un pezzo è disponibile
3. Dove siamo e orari
4. Spedizioni, cambi e resi
5. Consulenza gratuita (compare solo se la prenotazione è attiva)

"Menu" sta in una barra fissa sopra la casella di scrittura. "Una persona" compare nella stessa barra solo quando il percorso si blocca (testo non capito, errore, problema con un ordine, ricerca regalo senza niente online, richiesta esplicita, 8 risposte senza concludere). Chi scrive "persona" arriva comunque ai contatti. Sotto le risposte non si ripetono più "Torna al menu" e "Parlo con una persona". Le scelte della conversazione sono pillole pesca, WhatsApp è scuro, i collegamenti secondari hanno solo il bordo.

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
> [Stato: "Aperto ora, fino alle 19:30" oppure "Chiuso, riapre domani alle 9:30"]. Orari: [orari dal sito].
>
> [Se tra poco cambiano:] Dal 1 dicembre gli orari cambiano: [nuovi orari].
>
> Puoi passare senza prenotare. Se vuoi vedere un pezzo del sito, porta la foto o il link.

Bottoni: Apri la mappa del 17 · Apri la mappa del 21 · Chiama il 17 · Chiama il 21 · Vedi la pagina dei negozi

Non c'è una riga sul parcheggio: non abbiamo una fonte, quindi chi lo chiede arriva a "non ho capito" e a WhatsApp.

## 5. Spedizioni, cambi e resi

Domande (in quest'ordine):

1. Quanto costa spedire?
2. Come posso pagare?
3. Posso restituire o cambiare?
4. Ho un problema con un ordine
5. Prezzi e taglie
6. Posso riservare un pezzo?
7. Fate riparazioni o lavori su misura?
8. Fate pacchetti regalo?
9. Le foto sono vere?
10. Cosa fate con i miei dati?

Ogni risposta che invita a scrivere ha il suo pulsante WhatsApp con un messaggio già pronto (senza dati personali).

**Quanto costa spedire?**
> In Italia spediamo a 8 euro, gratis sopra i 99. Il pacco parte entro 2 o 3 giorni lavorativi da quando vediamo il pagamento. Anche fuori dall'Italia si può spedire, con un costo più alto: te lo indichiamo nel riepilogo prima di pagare.
>
> Se il regalo ti serve per una data precisa, scrivici quando: ti diciamo se è possibile.

Bottone: Chiedi i tempi su WhatsApp. Non si scrivono paesi, cifre per l'estero né date di consegna: non sono ancora definiti.

**Come posso pagare?**
> Con bonifico istantaneo, con Satispay, con un link SumUp oppure in negozio quando ritiri. PayPal non lo usiamo. In chat non ti chiediamo mai i dati della carta.

**Posso restituire o cambiare?**
> Se hai comprato a distanza (sito, WhatsApp o Instagram), puoi ripensarci entro 14 giorni da quando ricevi il pacco, senza darci spiegazioni. Ci scrivi che vuoi rendere il pezzo e lo restituisci entro 14 giorni da quel momento. La spedizione del reso è a tuo carico. Ti rimborsiamo entro 14 giorni da quando ce lo comunichi, appena riceviamo il pezzo o la prova di spedizione.
>
> Il cambio è un servizio a parte, sempre entro 14 giorni: servono lo scontrino e il pezzo con la sua confezione. Se hai comprato in negozio non c'è il recesso e non facciamo rimborsi in denaro per ripensamento, ma puoi cambiare il pezzo. Se il cambio passa dal corriere, le spedizioni sono a tuo carico.

Bottoni: Scrivi su WhatsApp · Leggi le condizioni di vendita

**Ho un problema con un ordine**
> Ci dispiace! Se il pezzo ha un difetto, per due anni dalla consegna c'è la garanzia legale: riparazione o sostituzione sono gratuite. Mandaci una foto del difetto, il numero dell'ordine e la data di consegna.
>
> Il codice di tracciamento te lo mandiamo quando il pacco parte. Se è in ritardo o non lo trovi, scrivici il numero dell'ordine e controlliamo.

Bottone: Scrivi su WhatsApp. Questa risposta fa comparire "Una persona" nella barra.

**Prezzi e taglie**
> I prezzi sono scritti sulle schede, imposte incluse. Le taglie e le misure le confermiamo prima del pagamento: scrivici quella che ti serve.

Bottoni: Scrivi su WhatsApp · Vedi le idee regalo

**Posso riservare un pezzo?**
> Prima controlliamo il pezzo in negozio. Se è disponibile, ti confermiamo la riserva e ti diciamo fino a quando vale: al massimo 48 ore. Se in quel tempo non c'è il pagamento o il ritiro, la riserva decade.
>
> Scrivici il pezzo che ti interessa: ti diciamo se è disponibile.

Bottone: Scrivi su WhatsApp. Mai "te lo mettiamo da parte": nessuna riserva prima della verifica.

**Fate riparazioni o lavori su misura?**
> Sì: le riparazioni si fanno in via Cavour 17, dove c'è il nostro laboratorio. Portaci il pezzo, oppure mandaci una foto su WhatsApp e ti diciamo cosa si può fare.
>
> Per un lavoro su misura scrivici cosa hai in mente: ti diciamo se è possibile.

Bottoni: Scrivi su WhatsApp · Apri la mappa del 17. Non si dicono prezzi né tempi.

**Fate pacchetti regalo?**
> Sì, la confezione base è gratuita e possiamo aggiungere un messaggio. Per alcune scatoline da anello, bracciale o collana può esserci un supplemento, e te lo diciamo prima di pagare.

**Le foto sono vere?**
> Alcune foto dei pezzi indossati sono create con l'intelligenza artificiale e hanno un'etichetta. Il pezzo vero è quello che conta: colori, misure e dettagli te li confermiamo prima del pagamento.

**Cosa fate con i miei dati?**
> Usiamo ciò che ci comunichi solo per risponderti e seguire l'ordine. Niente liste promozionali. Questo assistente non salva la conversazione: quando chiudi la pagina, sparisce.

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
